#!/usr/bin/env python3
import hashlib, json, re
from pathlib import Path
D=Path(__file__).resolve().parent
R=json.loads((D/'RESULT.json').read_text())
fail=[]
def need(rel,*tokens):
 p=D/rel
 if not p.exists(): fail.append('missing '+rel); return ''
 t=p.read_text(errors='replace')
 for x in tokens:
  if x not in t: fail.append(f'{rel}: missing {x}')
 return t
need('evidence/TRUSTED-MODULE-INVENTORY.txt','/statichashes/example_image_runner.so','/statichashes/libbenchmark_skel.so','/statichashes/libsysmon_skel.so')
need('evidence/CALLABLE-TRUSTED-MODULE-SURFACE.txt','benchmark_skel_handle_invoke','sysmon_skel_invoke','loadalgo_skel_handle_invoke')
need('evidence/BENCHMARK-SKEL-NONMATCH.txt','neither utility is referenced','no generic copy/fill method')
need('evidence/EXAMPLE-RUNNER-ENTRY-BOUNDARY.txt','sec_gaussian','does not expose the operation-1 memcpy test')
need('evidence/SYSMON-COPY-NONMATCH.txt','only one caller-supplied output buffer','allocates its own source/destination buffers')
need('evidence/LOADALGO-NONMATCH.txt','Gaussian','does not expose a shipping camera-equivalent operation')
need('evidence/CAMERA-TRANSFER-TOKEN-SCAN.txt','NONE','ImageProcessingModule_SWABF','ImageProcessingModule_SWASF')
need('evidence/REUSE-CLOSURE.txt','No already trusted, currently exposed shipping CPZ/SecurePD entrypoint','worker-admission blocker')
bench=need('ghidra/BENCHMARK-DECOMP.txt','benchmark_skel_handle_invoke','addTwoVectorsTogether','Vmemset','benchmark_gaussian7x7')
# Restrict dispatcher section: utilities exist later but must not be called in handler.
handler=bench.split('//// addTwoVectorsTogether',1)[0]
if 'addTwoVectorsTogether(' in handler: fail.append('addTwoVectors unexpectedly dispatched')
if 'Vmemset(' in handler: fail.append('Vmemset unexpectedly dispatched')
runner=need('ghidra/EXAMPLE-RUNNER-ENTRY.txt','//// algo_main','sec_gaussian','//// example_algo_run','mmap_fd_test')
if 'Launched thread' not in runner or 'Gaussian' not in runner: fail.append('runner algo_main boundary missing')
if R['candidates']['example_image_runner']['copy_operation_production_reachable']: fail.append('runner copy reachability overclaimed')
if R['candidates']['libbenchmark_skel']['generic_copy_or_fill_skel_method']: fail.append('benchmark generic transfer overclaimed')
if R['candidates']['libsysmon_skel']['arbitrary_source_and_destination_parameters']: fail.append('sysmon arbitrary copy overclaimed')
if R['negative_scan']['trusted_package_swabf_token'] or R['negative_scan']['trusted_package_swasf_token']: fail.append('negative token result inconsistent')
if any(R['runtime_actions'].values()): fail.append('runtime action recorded')
if Path('/proc/device-tree/soc@0/remoteproc@32300000/glink-edge/fastrpc/compute-cb@9').exists(): fail.append('live secure CB9 unexpectedly present')
if R['status']!='PASS_NO_SHIPPED_TRUSTED_ENTRYPOINT_REPRODUCES_WINDOWS_PROTECTED_FRAME_TRANSFER': fail.append('bad status')
if fail:
 print('E004dd VERIFY: FAIL')
 for x in fail: print(' -',x)
 raise SystemExit(1)
print('E004dd VERIFY: PASS')
print(' - trusted shipping module/invoke surfaces were systematically bounded')
print(' - runner memcpy primitive is not reachable through its proven production entry')
print(' - benchmark/sysmon/loadalgo callable surfaces do not implement arbitrary parity transfer')
print(' - no SWABF/SWASF camera transfer surface exists in the trusted CDSP package')
print(' - remaining blocker is production trust admission of a parity worker')
print(' - no protected runtime action was taken')
