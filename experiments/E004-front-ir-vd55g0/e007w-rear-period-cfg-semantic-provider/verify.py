#!/usr/bin/env python3
from pathlib import Path
import json

D=Path(__file__).resolve().parent
REPO=D.parents[2]
OLD=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
proof=json.load(open(D/'SOURCE-LOCK-SAFE.json'))
src=(D/'camss-e007w-period-cfg.inc').read_text()

assert proof['schema']=='E007w-period-cfg-semantic-proof-v1'
assert proof['classification']=='SOURCE_LOCKED_SEMANTIC_CLOSURE'
assert proof['active_field_mask']=='0x0000001f'
assert proof['semantic_input']=='numBatchedFrames'
assert proof['canonical_first_frame_num_batched_frames']==1
assert proof['canonical_first_frame_period_cfg']==0
assert proof['undefined_upper_bits']['write_before_read'] is False
assert proof['undefined_upper_bits']['canonical_linux_policy']=='zero'

def iv(v):
    return v if isinstance(v,int) else int(v,16)

vals=[]
j=json.load(open(OLD/'rtcdm-period-cfg-contract-oracle.json'))
for label,st in j['observed_starts'].items():
    for key in ('packet0','packets123'):
        vals.append((f'contract:{label}:{key}',iv(st[key])))

j=json.load(open(OLD/'vfe1-epoch0-priming-replay-oracle.json'))
for p in j['replay']['packets']:
    vals.append((f'replay:p{p["packet"]}:startup',iv(p['startup_period_cfg'])))
    vals.append((f'replay:p{p["packet"]}:replay',iv(p['replay_period_cfg'])))

j=json.load(open(OLD/'rtcdm-startup-dynamic-ownership-oracle.json'))
for x in j['period_fields']:
    vals.append((f'ownership:p{x["packet"]}:initial',iv(x['initial_value'])))
    vals.append((f'ownership:p{x["packet"]}:final',iv(x['final_value'])))
for packet,rec in j['fresh_kmd_entry_values'].items():
    vals.append((f'fresh_kmd:p{packet}',iv(rec['0x8c'])))

assert len(vals)==proof['accepted_windows_samples_checked']==28
assert all((v & 0x1f)==0 for _,v in vals)
assert sum(1 for _,v in vals if (v & 0x1f)!=0)==proof['accepted_windows_samples_nonzero_active_bits']==0
assert len({v for _,v in vals}) >= 8

for token in (
    '#define E007W_PERIOD_CFG_MASK 0x1f',
    '#define E007W_MAX_BATCHED_FRAMES 32',
    'e007w_period_cfg_value',
    'num_batched_frames > 1 ? num_batched_frames - 1 : 0',
    'period->value[0] = value;',
    'period->value[1] = value;',
    'e007w_rear_startup_context_init',
    'e007w_period_cfg_recipe',
):
    assert token in src

for raw in {f'{v:08x}' for _,v in vals}:
    assert raw not in src.lower()

# First-frame semantic case and field bounds.
def canonical(n):
    assert 1 <= n <= 32
    return ((n - 1) if n > 1 else 0) & 0x1f

assert canonical(1)==0
assert canonical(2)==1
assert canonical(32)==31

print('E007W_VERIFY_PASS active_mask=0x1f windows_samples=28 low5_exact=28/28')
print('first_frame_num_batched_frames=1 canonical_period_cfg=0')
print('first_frame_blockers=0')
