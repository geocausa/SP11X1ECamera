#!/usr/bin/env python3
import hashlib, json, subprocess, tempfile
from pathlib import Path
D=Path(__file__).resolve().parent
S=D/'scaffold'
DH=D.parent/'e004dh-swab-exact-offline-port'
HS=DH/'scaffold'
O=DH/'oracle/windows-sync-oracle'
R=json.loads((D/'RESULT.json').read_text())
fail=[]

def need(path,*tokens):
    p=D/path
    if not p.exists(): fail.append(f'missing {path}'); return ''
    t=p.read_text(errors='replace')
    for x in tokens:
        if x not in t: fail.append(f'{path}: missing {x}')
    return t

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

src=need('scaffold/sp11-parity-worker.c','request_id < 10','sp11_fill(dst, 100','sp11_fill(dst + y_size, 0x80','sp11_swab_two_pass_exact')
need('evidence/WINDOWS-BRANCH-CONTRACT.txt','FUN_1800033d8','FUN_180003718','SWABF(src -> scratch)')
need('evidence/FULLFRAME-WINDOWS-DIFFERENTIAL.txt','WORKER_FULL_LUMA_DIFF=0','WORKER_NEUTRAL_TAIL_DIFF=0')
need('README.md','all three Windows transfer branches','zero unresolved symbols')
if 'SP11_WORKER_ESWAB_PENDING' in src or 'SP11_WORKER_ESWAB_PENDING' in (S/'sp11-parity-worker.h').read_text():
    fail.append('pending marker still present after full-frame closure')
later=src.split('Windows FUN_180003478',1)[-1]
if 'sp11_move(' in later: fail.append('later SWAB branch contains copy fallback')

sources=[
    S/'sp11-parity-worker.c',
    HS/'sp11-swabf-reference.c',
    HS/'sp11-swasf-reference.c',
    HS/'sp11-swasf-windows-tuning.c',
    HS/'sp11-swasf-helpers.c',
    HS/'sp11-swasf-c230.c',
    HS/'sp11-swasf-c3e8.c',
    HS/'sp11-swasf-cd90.c',
]

with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    common=['clang','-std=c11','-O2','-Wall','-Wextra','-Werror',f'-I{S}',f'-I{HS}']+[str(x) for x in sources]
    exe=td/'test_worker'
    subprocess.check_call(common+[str(S/'test_worker.c'),'-o',str(exe)])
    out=subprocess.check_output([str(exe)],text=True)
    if 'E004dg host vectors: PASS' not in out: fail.append('host vectors failed')

    full=td/'test_worker_fullframe'
    subprocess.check_call(common+[str(S/'test_worker_fullframe.c'),'-o',str(full)])
    image=td/'worker-output.bin'
    out=subprocess.check_output([str(full),str(O/'input-644x604-nv12.bin'),
                                 str(O/'windows-trustlet-sync-swasf-644x604-stable.bin'),str(image)],text=True)
    if 'WORKER_FULL_LUMA_DIFF=0' not in out: fail.append('full-frame luma differential failed')
    if 'WORKER_NEUTRAL_TAIL_DIFF=0' not in out: fail.append('worker tail differential failed')
    h=sha(image)
    if h!=R['validation']['worker_full_output_sha256']:
        fail.append(f'worker output hash mismatch {h}')

    # Freestanding non-PIC Hexagon-v73 partial link of the exact constituent sources.
    objs=[]
    for sp in sources:
        obj=td/(sp.stem+'.o')
        subprocess.check_call(['clang','--target=hexagon','-mcpu=hexagonv73','-O2',
            '-ffreestanding','-fno-builtin','-fno-pic','-fno-pie','-Wall','-Wextra','-Werror',
            f'-I{S}',f'-I{HS}','-c',str(sp),'-o',str(obj)])
        objs.append(obj)
    combined=td/'sp11-parity-worker-combined.hexagon-v73.o'
    subprocess.check_call(['ld.lld','-m','hexagonelf','-r']+[str(x) for x in sorted(objs,key=lambda p:p.name)]+['-o',str(combined)])
    nmu=subprocess.check_output(['llvm-nm','-u',str(combined)],text=True)
    if nmu.strip(): fail.append('Hexagon combined object has unresolved symbols: '+nmu.strip())
    h=sha(combined)
    if h!=R['validation']['hexagon_object_sha256']:
        fail.append(f'Hexagon combined object hash mismatch {h}')

if R.get('status')!='PASS_OFFLINE_HEXAGON_WORKER_FULL_WINDOWS_SWABF_SWASF_EXACT': fail.append('bad status')
if not R['worker']['later_swab_branch_exact']: fail.append('later SWAB branch not marked exact')
if R['worker']['later_swab_fallback_used']: fail.append('SWAB fallback unexpectedly enabled')
if R['validation']['full_frame_luma_diff_bytes']!=0 or R['validation']['full_frame_tail_diff_bytes']!=0: fail.append('nonzero recorded differential')
if R['trust']['production_admitted'] or R['trust']['runtime_authorized']: fail.append('trust/runtime overclaimed')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')

if fail:
    print('E004dg VERIFY: FAIL')
    for x in fail: print(' -',x)
    raise SystemExit(1)
print('E004dg VERIFY: PASS')
print(' - synthetic, request<10 copy, and request>=10 SWABF->SWASF branches are closed')
print(' - integrated 644x604 Windows stable-luma differential is byte exact')
print(' - worker-specific neutral tail is exact and kept distinct from standalone trustlet UV preservation')
print(' - freestanding non-PIC Hexagon-v73 combined object has zero unresolved symbols')
print(' - protected runtime remains untouched and unauthorized')
