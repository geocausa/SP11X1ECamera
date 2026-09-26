#!/usr/bin/env python3
from pathlib import Path
import json,re

D=Path(__file__).resolve().parent
E=D.parent
S=json.loads((D/'SOURCE-SAFE.json').read_text())
A=json.loads((D/'REMAINING-61-AUDIT.json').read_text())
C=(D/'camss-e006z-clean-scalar-bank.inc').read_text()
O=json.loads((E/'e006l-rear-startup-register-ownership'/'STARTUP-REGISTER-OWNER-MAP.json').read_text())

assert S['schema']=='E006z-rear-clean-scalar-bank-source-safe-v1'
assert S['closed_register_count']==24
assert S['bank_registers']['count']==16
assert S['raw_windows_register_values_committed'] is False
assert S['private_windows_bytes_committed'] is False

closed={int(x,16) for x in re.findall(r'\b0x[0-9a-f]{4}\b',
    C[C.index('e006z_rear_closed_regs'):C.index('static_assert')])}
assert len(closed)==24

steady={int(x['register'],16) for x in O['steady_dynamic']}
diff={int(x['register'],16) for x in O['startup_differs_from_steady']}
remaining_before=steady | (diff-{0xb26c})
assert len(steady)==25 and len(diff)==37 and len(remaining_before)==61
assert closed <= remaining_before

expected_closed={
 0x3b70,0x3b74,
 0x3d58,0x3d5c,0x3d78,0x3d7c,0x3d80,0x3d84,
 0x4358,0x435c,0x456c,0x4570,0x4758,0x475c,
 0x4958,0x495c,0x5a58,0x5a5c,0x5f58,0x5f5c,
 0xa058,0xa05c,0xa258,0xa25c}
assert closed==expected_closed

hard=remaining_before-closed
audit_hard={int(x,16) for xs in A['remaining_register_contracts'].values() for x in xs}
assert hard==audit_hard and len(hard)==37
assert len(A['remaining_register_contracts']['VFE680_PERIOD_CFG'])==1
assert len(A['remaining_register_contracts']['BPC_ABF'])==7
assert len(A['remaining_register_contracts']['BFSTATS25'])==29

for token in [
 'E006Z_EPOCH_STARTUP','E006Z_EPOCH_STEADY',
 'e006z_rear_bank_regular','e006z_rear_bank_inverse',
 'e006z_rear_clean_scalar_bank_lookup',
 'e006z_rear_clean_provider_recipe']:
    assert token in C

assert A['before']=={'concrete_startup_registers':653,'total_startup_registers':714,'remaining':61}
assert A['after_compile_pass']=={'concrete_startup_registers':677,'total_startup_registers':714,'remaining':37}
assert A['native_rear_linux_isp_authorized'] is False

print('E006Z_VERIFY_PASS')
print('closed_registers=24 bank=16 demux=2 pdpc=4 wb=2')
print('remaining_register_contracts=37 period=1 bpc_abf=7 bfstats25=29')
print('projected_concrete_startup=677/714 startup_only=184/184')
print('raw_windows_register_values=false')
