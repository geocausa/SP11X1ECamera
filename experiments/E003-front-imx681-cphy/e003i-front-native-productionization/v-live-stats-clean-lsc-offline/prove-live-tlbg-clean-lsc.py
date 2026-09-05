#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, importlib.util, json, struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
BASE = HERE.parent
NFILE = BASE / 'n-titan680-tlbg-parser' / 'titan680-tlbg-parser.py'
MFILE = BASE / 'm-stats-only-lsc-request-state' / 'generate-stats-only-front-lsc.py'
KFILE = BASE / 'k-cleanroom-lsc-backend' / 'generate-cleanroom-front-lsc-wire.py'
IFILE = BASE / 'i-cleanroom-tintless' / 'cleanroom-tintless-helpers.py'
DEFAULT_U = BASE / 'u-corrected-tlbg-runtime'

X1 = 0x270000003000
X2 = 0x270000010000
D3 = 0x270000030000
D4 = 0x270000031000
IN = 0x270000040000
OUT = 0x270000050000
WRAP = 0x270000001000
CORE = 0x270000100000
ADAPT = 0x270000140000
MAGIC = 0x47424C54
HEADER = struct.Struct('<IHHQIIII')


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(mod)
    return mod


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def need(value, message: str):
    if not value:
        raise RuntimeError(message)


def read_snapshots(snapshot_dir: Path, N):
    out = []
    for index in range(6):
        blob = (snapshot_dir / f'TLBG-{index}.bin').read_bytes()
        need(len(blob) == 0xF020, f'TLBG-{index}: snapshot size drift')
        magic, version, header_bytes, generation, source_seq, slot, raw_bytes, flags = HEADER.unpack_from(blob)
        need(magic == MAGIC and version == 1 and header_bytes == 32,
             f'TLBG-{index}: header identity drift')
        need(raw_bytes == N.RAW_BYTES == 0xF000 and flags == 1,
             f'TLBG-{index}: raw size/flags drift')
        raw = blob[header_bytes:]
        need(len(raw) == N.RAW_BYTES, f'TLBG-{index}: raw extent drift')
        parsed = N.parse_titan680_tlbg(raw)
        need(len(parsed) == N.PARSED_FULL_BYTES, f'TLBG-{index}: parsed size drift')
        need(struct.unpack_from('<II', parsed, 0) == (3, 768), f'TLBG-{index}: parsed header drift')
        out.append({
            'index': index, 'generation': generation, 'source_seq': source_seq,
            'slot': slot, 'snapshot_sha256': sha(blob), 'raw_sha256': sha(raw),
            'parsed_sha256': sha(parsed), 'parsed': parsed,
        })
    need([x['generation'] for x in out] == [1, 2, 3, 4, 5, 6], 'generation sequence drift')
    need([x['source_seq'] for x in out] == [1, 2, 3, 4, 5, 6], 'source_seq sequence drift')
    need([x['slot'] for x in out] == [0, 1, 0, 1, 0, 1], 'slot sequence drift')
    return out


def run_sequence(stats, pre_mesh: bytes, x1: bytes, M, K, C,
                 core_fill: int = 0, out_mode: str = 'zero'):
    mem = K.SparseMemory()
    mem.mem_write(WRAP, bytes(0x1090))
    mem.fill(CORE, C.CORE_BYTES, core_fill)
    mem.mem_write(ADAPT, bytes(0x1000))
    mem.mem_write(X1, x1)
    mem.mem_write(D3, M.descriptor(IN))
    mem.mem_write(D4, M.descriptor(OUT))
    result = []
    for position, item in enumerate(stats, 1):
        mem.mem_write(X2, item['parsed'])
        mem.mem_write(IN, pre_mesh + bytes(0x20))
        seed = K.output_seed(out_mode)
        mem.mem_write(OUT, seed)
        rc = C.wrapper_front_mode2(mem, WRAP, X1, X2, D3, D4,
                                   CORE if position == 1 else 0, ADAPT)
        need(rc == 0, f'clean Tintless rc={rc} at source generation {item["generation"]}')
        output = mem.mem_read(OUT, 0xDF0)
        need(output[0xDD0:] == seed[0xDD0:], 'output tail changed')
        l0, l1, l2, gic = K.wire_from_output(output)
        result.append({
            'generation': item['generation'], 'source_seq': item['source_seq'], 'slot': item['slot'],
            'parsed_sha256': item['parsed_sha256'], 'output_abi_sha256': sha(output[:0xDD0]),
            'lsc0_sha256': sha(l0), 'lsc1_sha256': sha(l1), 'lsc2_sha256': sha(l2),
            'gic_sha256': sha(gic), 'lsc0': l0, 'lsc1': l1, 'lsc2': l2, 'gic': gic,
        })
    return result


def comparable(run):
    keys = ('generation', 'source_seq', 'slot', 'parsed_sha256', 'output_abi_sha256',
            'lsc0_sha256', 'lsc1_sha256', 'lsc2_sha256', 'gic_sha256')
    return [{k: x[k] for k in keys} for x in run]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot-dir', type=Path, default=DEFAULT_U)
    ap.add_argument('--output-dir', type=Path, default=Path('/tmp/e003i-v-live-stats-clean-lsc'))
    ap.add_argument('--manifest', type=Path)
    args = ap.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    N = load(NFILE, 'e003i_v_n')
    M = load(MFILE, 'e003i_v_m')
    K = load(KFILE, 'e003i_v_k')
    C = load(IFILE, 'e003i_v_i')
    snapshots = read_snapshots(args.snapshot_dir, N)
    x1, tintless_region_sha = M.build_front_x1()
    pre, pre_detail = K.build_pretintless(REPO)
    need(pre[5] == pre[6], 'zero-ratio pre-Tintless fixture diverged between R5/R6')

    trigger_fixtures = {
        'ratio_0p342_fixture': {'ratio': 0.342, 'pre': pre[4]},
        'ratio_0p000_fixture': {'ratio': 0.0, 'pre': pre[5]},
    }
    manifest = {
        'schema': 'sp11-e003i-v-live-tlbg-clean-lsc-offline-v1',
        'status': 'PASS', 'offline_only': True, 'runtime_performed': False,
        'source_generation_is_request_id': False,
        'dynamic_r5_r6_substitution_authorized': False,
        'raw_authority_bytes': N.RAW_BYTES,
        'parsed_bytes': N.PARSED_FULL_BYTES,
        'generated_x1_sha256': sha(x1),
        'tintless23_region_sha256': tintless_region_sha,
        'source_snapshots': [{k: x[k] for k in ('index','generation','source_seq','slot','snapshot_sha256','raw_sha256','parsed_sha256')} for x in snapshots],
        'trigger_fixtures': {},
        'proofs': {
            'hostile_initial_state_counterfactuals': True,
            'source_order_sensitivity_required': True,
            'all_source_payloads_consumed_in_temporal_sequence': True,
        },
    }

    cases = [('zero', 0x00), ('a5', 0x00), ('ones', 0x00), ('zero', 0xA5)]
    for label, fixture in trigger_fixtures.items():
        runs = {}
        for mode, fill in cases:
            runs[(mode, fill)] = run_sequence(snapshots, fixture['pre'], x1, M, K, C, fill, mode)
        base = runs[('zero', 0x00)]
        base_cmp = comparable(base)
        for key, run in runs.items():
            need(comparable(run) == base_cmp, f'{label}: hostile-state drift for {key}')
        reversed_stats = list(reversed(snapshots))
        reverse = run_sequence(reversed_stats, fixture['pre'], x1, M, K, C, 0, 'zero')
        forward_l0 = [x['lsc0_sha256'] for x in base]
        reverse_l0 = [x['lsc0_sha256'] for x in reverse]
        need(forward_l0 != reverse_l0, f'{label}: source order did not affect LSC sequence')
        need(base[-1]['lsc0_sha256'] != reverse[-1]['lsc0_sha256'],
             f'{label}: final temporal LSC insensitive to source order')
        # At least two outputs must differ across the six live generations; this
        # proves the live stats are not being ignored without assuming requests.
        need(len(set(forward_l0)) > 1, f'{label}: all live LSC0 outputs identical')
        for item in base:
            prefix = f"{label}-G{item['generation']}"
            for name in ('lsc0','lsc1','lsc2','gic'):
                (args.output_dir / f'{prefix}-{name.upper()}.bin').write_bytes(item[name])
        manifest['trigger_fixtures'][label] = {
            'ratio_fixture': fixture['ratio'],
            'pretintless_sha256': sha(fixture['pre']),
            'forward': base_cmp,
            'reverse_final_lsc0_sha256': reverse[-1]['lsc0_sha256'],
            'unique_forward_lsc0_outputs': len(set(forward_l0)),
            'counterfactual_cases': [{'output_seed': mode, 'core_fill': fill} for mode, fill in cases],
        }
        print(label, 'PASS', 'unique_lsc0=', len(set(forward_l0)), 'final=', base[-1]['lsc0_sha256'])

    # The two trigger fixtures are intentionally separate inputs; prove at least
    # one same-generation output changes when trigger state changes.
    a = manifest['trigger_fixtures']['ratio_0p342_fixture']['forward']
    b = manifest['trigger_fixtures']['ratio_0p000_fixture']['forward']
    changed = [x['generation'] for x, y in zip(a, b) if x['lsc0_sha256'] != y['lsc0_sha256']]
    need(changed, 'trigger fixture did not affect any LSC0 output')
    manifest['proofs']['trigger_state_is_separate_effective_input'] = True
    manifest['proofs']['trigger_fixture_changed_generations'] = changed
    manifest['next_boundary'] = ('select a proven source-generation for each steady request without equating source_seq with request ID; '
                                 'then compose the selected clean LSC wire into template-free capsules')
    mp = args.manifest or HERE / 'MANIFEST.json'
    mp.write_text(json.dumps(manifest, indent=2, sort_keys=True) + '\n')
    print('E003I_V_LIVE_STATS_CLEAN_LSC=PASS')
    print('MANIFEST', mp)


if __name__ == '__main__':
    main()
