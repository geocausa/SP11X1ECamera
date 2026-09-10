#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, subprocess, tempfile

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[3]
AB = BASE / 'ab-clean-lux-reconstruction'
DC = BASE / 'dc-windows-aec-t681-error-fallback-oracle/windows-evidence/extracted/E003I-DC-oracle.log'
CV = BASE / 'cv-native-aec-offline-sensor-control-join'
CU = BASE / 'cu-native-aec-raw-stats-request-loop'
CQ = BASE / 'cq-aec-output-imx681-control-adapter'
CR = BASE / 'cr-native-aec-effective-analyzer-producer'
CT = BASE / 'ct-native-aec-bhist-bank4-replay'
CF = BASE / 'cf-native-aec-final-exposure-si'
CE = BASE / 'ce-native-aec-final-target-producer'
CC = BASE / 'cc-native-aec-adrc-darkboost-tail'
BY = BASE / 'by-native-aec-method11-point-aggregation'
CG = BASE / 'cg-native-aec-qword-convergence-input'
CH = BASE / 'ch-native-aec-t681-preview-arbitration'
BK = BASE / 'bk-native-aec-history-state'
BJ = BASE / 'bj-native-aec-log103-coordinate'
DI = Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-di-windows-warmup-predgain-oracle-20260910')
DBA = Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-db/attempt2-live-g3-fail-20260910T130118/producer')
DI_SHA = '5155e355b08b8c65153d3548568c5223a230e1d88c85711b47f8eef7b11e27b0'
STATS_SHA = [
    'c040530a44201cd4ffb9b78749166523f03c44ea1f4474da0b5992344b8664e9',
    '51d101ca1fb8d6fb2c38254e0bc82e7663d34b8fe3b2f545499ea9b68df4ec25',
    '06346e9f34bec70b976a76c4e72e0fb76ec21d7acb6d5f09f4417edef052fd64',
]

def need(v, msg):
    if not v:
        raise AssertionError(msg)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

need(subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'], cwd=REPO, text=True).strip() == 'experiment/e003-front-imx681-cphy', 'branch')
need(sha(DI / 'E003I-DI-EVIDENCE.zip') == DI_SHA, 'DI archive hash')
notes = (DI / 'unpacked/E003I-DI-NOTES.txt').read_text(encoding='utf-8-sig')
for f in (1, 2, 3):
    need(f'F{f} short=33312452 PredGain=0x3f800000 (1.0f)' in notes, f'DI request {f}')
ab22 = (AB / 'E003I-AB22-REQUEST-ASSOCIATION.txt').read_text()
for marker in ('req=1 lux=4365b24a', 'req=2 lux=4365acdd', 'req=3 lux=4365acdd', 'req=4 lux=4365acdd'):
    need(marker in ab22, 'AB22 ' + marker)
ab26 = (AB / 'E003I-AB26-CLOSURE.txt').read_text()
for r in ('R1', 'R2', 'R3'):
    need(f'{r} baseline 4365acdd' in ab26, 'AB26 ' + r)
dc = DC.read_text(errors='replace')
for f in (1, 2, 3):
    marker = f'DC_POSTCAP hit={f-1} F={f} flag=0'
    pos = dc.find(marker)
    need(pos >= 0, f'DC request {f} marker')
    end = dc.find(f'DC_PUBLISH hit={f-1} req={f}', pos)
    need(end > pos, f'DC request {f} publish boundary')
    block = dc[pos:end]
    need(block.count('00000000`01fc4ec4') == 7, f'DC request {f} seven compact warm-up lanes')
paths = [DBA / f'STATS3A-G{i}.bin' for i in (1, 2, 3)]
for i, p in enumerate(paths):
    need(p.is_file(), f'archived G{i+1}')
    need(sha(p) == STATS_SHA[i], f'archived G{i+1} hash')
src = (HERE / 'native-aec-request-loop.c').read_text() + (HERE / 'native-aec-request-loop.h').read_text()
for marker in ('E003I_WINDOWS_REQUEST4_ENTRY_LUX_BITS', 'E003I_WINDOWS_WARMUP_REQUESTS', 'E003I_WINDOWS_WARMUP_EXPOSURE', 'E003I_WINDOWS_WARMUP_PRED_GAIN_BITS', 'local_to_history_frame'):
    need(marker in src, 'DJ source ' + marker)

with tempfile.TemporaryDirectory(prefix='e003i-dj-') as td:
    exe = Path(td) / 'dj-replay'
    cmd = ['cc', '-O2', '-std=c11', '-Wall', '-Wextra', '-Werror', '-fno-fast-math', '-ffp-contract=off',
           '-I', str(HERE), '-I', str(CV), '-I', str(CU), '-I', str(CQ), '-I', str(CR), '-I', str(CT), '-I', str(CF), '-I', str(CE), '-I', str(CC), '-I', str(BY), '-I', str(CG), '-I', str(CH), '-I', str(BK), '-I', str(BJ),
           str(HERE / 'replay-archived-g123.c'), str(CV / 'native-raw-control-join.c'), str(CU / 'native-raw-aec-loop.c'), str(CU / 'native-stats3a.c'), str(CQ / 'native-imx681-control.c'), str(CR / 'native-effective-analyzers.c'), str(CT / 'native-bhist-bank4.c'), str(HERE / 'native-aec-request-loop.c'), str(CF / 'native-final-exposure.c'), str(CE / 'native-final-target.c'), str(CC / 'native-aec-tail.c'), str(BY / 'native-target-aggregate.c'), str(CG / 'native-convergence.c'), str(CH / 'native-t681.c'), str(BK / 'native-aec-state.c'), str(BJ / 'native-log103.c'), '-lm', '-o', str(exe)]
    subprocess.run(cmd, check=True)
    out = subprocess.check_output([str(exe), *(str(p) for p in paths)], text=True)
need('DJ_VERIFY=PASS' in out, 'DJ replay harness')

lines = [
    'DI_ZIP_SHA256=' + DI_SHA,
    'WINDOWS_WARMUP=F1,F2,F3 compact7=33312452 predGain=0x3f800000',
    'WINDOWS_REQUEST4_ENTRY_LUX=0x4365acdd',
    'LOCAL_REBASE=G1/local0 -> request4/internal3; h1=request3 h2=request2 h3=request1',
    'ARCHIVED_DB_STATS_SHA256=' + ','.join(STATS_SHA),
] + out.strip().splitlines()
(HERE / 'VERIFY-RESULT.txt').write_text('\n'.join(lines) + '\n')
result = {
    'schema': 'sp11-e003i-dj-request4-warmup-rebase-v1',
    'status': 'PASS_OFFLINE',
    'windows': {
        'di_zip_sha256': DI_SHA,
        'warmup_requests': [1, 2, 3],
        'warmup_compact_and_retained_exposure': 33312452,
        'warmup_pred_gain_bits': '0x3f800000',
        'request1_lux_bits': '0x4365b24a',
        'request2_request3_request4_entry_lux_bits': '0x4365acdd',
    },
    'local_mapping': {
        'generation1_local_frame': 0,
        'generation1_windows_request': 4,
        'history_frame_bias': 3,
        'g1_history_offsets': {'F-1': 'request3', 'F-2': 'request2', 'F-3': 'request1'},
    },
    'prior_live_failure': {'db_attempt': 2, 'generation': 3, 'rc': -142, 'eliminated_offline': True, 'stats_sha256': STATS_SHA},
    'replay': {
        'requests': [4, 5, 6],
        'short_target': [2922393002, 2683504659, 2678810946],
        'short_convergence': [160604061, 745178717, 2407243907],
        'short_retained': [160604073, 745178701, 2407244072],
        'controls': [
            {'fll': 3562, 'exposure': 3554, 'again': 811, 'dgain': 256},
            {'fll': 3562, 'exposure': 3554, 'again': 960, 'dgain': 357},
            {'fll': 3839, 'exposure': 3830, 'again': 960, 'dgain': 1072},
        ],
    },
    'runtime_side_effects': 'none',
}
(HERE / 'RESULT.json').write_text(json.dumps(result, indent=2) + '\n')
print('\n'.join(lines))
