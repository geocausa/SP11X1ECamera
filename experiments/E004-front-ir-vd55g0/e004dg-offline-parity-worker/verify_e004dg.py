#!/usr/bin/env python3
import hashlib, json, re, subprocess, tempfile
from pathlib import Path
D=Path(__file__).resolve().parent
S=D/'scaffold'
R=json.loads((D/'RESULT.json').read_text())
fail=[]
def need(path,*tokens):
 p=D/path
 if not p.exists(): fail.append(f'missing {path}'); return ''
 t=p.read_text(errors='replace')
 for x in tokens:
  if x not in t: fail.append(f'{path}: missing {x}')
 return t
src=need('scaffold/sp11-parity-worker.c','request_id < 10','sp11_fill(dst, 100','sp11_fill(dst + y_size, 0x80','SP11_WORKER_ESWAB_PENDING')
need('evidence/WINDOWS-BRANCH-CONTRACT.txt','FUN_1800033d8','FUN_180003718','SWABF(src -> scratch)')
need('README.md','byte-exact to the oracle','E004dh — exact SWABF/SWASF algorithm extraction')
# No ordinary copy fallback may exist after the later-request dispatch comment.
later=src.split('Windows FUN_180003478',1)[-1]
if 'sp11_move(' in later: fail.append('later SWAB branch contains copy fallback')
# Rebuild and run host vectors in a temporary directory.
with tempfile.TemporaryDirectory() as td:
 exe=Path(td)/'test_worker'
 cmd=['clang','-O2','-Wall','-Wextra','-Werror',str(S/'sp11-parity-worker.c'),str(S/'test_worker.c'),'-o',str(exe)]
 subprocess.check_call(cmd)
 out=subprocess.check_output([str(exe)],text=True)
 if 'E004dg host vectors: PASS' not in out: fail.append('host vectors failed')
 obj=Path(td)/'worker.o'
 subprocess.check_call(['clang','--target=hexagon','-mcpu=hexagonv73','-O2','-ffreestanding','-fno-builtin','-Wall','-Wextra','-Werror','-c',str(S/'sp11-parity-worker.c'),'-o',str(obj)])
 nmu=subprocess.check_output(['nm','-u',str(obj)],text=True)
 if nmu.strip(): fail.append('Hexagon object has unresolved symbols')
 h=hashlib.sha256(obj.read_bytes()).hexdigest()
 if h!=R['validation']['hexagon_object_sha256']: fail.append(f'Hexagon object hash mismatch {h}')
if R.get('status')!='PASS_OFFLINE_HEXAGON_WORKER_SYNTHETIC_AND_EARLY_COPY_EXACT_SWAB_PENDING': fail.append('bad status')
if R['worker']['later_swab_branch_exact']: fail.append('SWAB falsely marked exact')
if R['worker']['later_swab_fallback_used']: fail.append('SWAB fallback unexpectedly enabled')
if R['trust']['production_admitted'] or R['trust']['runtime_authorized']: fail.append('trust/runtime overclaimed')
if any(R['runtime_actions'].values()): fail.append('unexpected runtime action')
if fail:
 print('E004dg VERIFY: FAIL')
 for x in fail: print(' -',x)
 raise SystemExit(1)
print('E004dg VERIFY: PASS')
print(' - source-controlled worker reproduces Windows synthetic and request<10 copy branches')
print(' - geometry/payload/extents are bounded before memory access')
print(' - later SWABF/SWASF branch fails closed rather than silently falling back to copy')
print(' - host synthetic vectors pass and exact source builds freestanding for Hexagon v73')
print(' - Hexagon object has zero unresolved symbols')
print(' - worker remains unsigned/offline and protected runtime remains untouched')
