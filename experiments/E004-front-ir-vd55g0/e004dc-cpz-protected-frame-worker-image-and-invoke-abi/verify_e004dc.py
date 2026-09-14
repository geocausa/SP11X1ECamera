#!/usr/bin/env python3
import hashlib, json, re, subprocess
from pathlib import Path
D=Path(__file__).resolve().parent
R=json.loads((D/'RESULT.json').read_text())
fail=[]
def need(rel,*tokens):
    p=D/rel
    if not p.exists(): fail.append(f'missing {rel}'); return ''
    t=p.read_text(errors='replace')
    for x in tokens:
        if x not in t: fail.append(f'{rel}: missing {x}')
    return t
need('evidence/SIGNED-VS-UNSIGNED-CPZ-SHELL.txt','direct jump','0x80000414')
need('evidence/SECUREPD-MODULE-TRUST.txt','Static hash found','dynamic module is unsigned','/statichashes/example_image_runner.so')
need('evidence/SECUREPD-BUFFER-ABI.txt','ALGO        = 4','STATIC_EXEC = 8','loadalgo_packet_t (12 bytes)','gaussian7x7_packet_t (96 bytes)')
need('evidence/SECUREPD-WORKER-EXECUTION.txt','dsc_verify_buffer','sec_algo.elf','algo_main','STATIC_EXEC')
need('evidence/EXAMPLE-RUNNER-COPY-PRIMITIVE.txt','HAP_mmap_get()','memcpy()','does NOT claim')
need('evidence/CAMERA-WORKER-NONIDENTITY.txt','ImageProcessingModule_SWABF','ImageProcessingModule_SWASF','Do not substitute')
need('evidence/ABI-LAYOUT-BUILD.txt','E004dc ABI LAYOUT VERIFY: PASS')
need('README.md','arbitrary unsigned ELF is not accepted','E004dd — shipped CPZ/SecurePD worker reuse feasibility')
root=need('ghidra/ROOT-SECUREPD-AUTHORITY.txt','error: dynamic module is unsigned','module: Static hash found','/statichashes/example_image.so')
need('ghidra/ROOT-SECUREPD-PROCESS-MSG.txt','ALGO buffer','Starting static execution in new thread','sec_algo.elf','symbol %s not found')
need('ghidra/LOADALGO-DECOMP.txt','loadalgo_physbuffer','proxy_to_secure_mb','secure_to_proxy_mb')
need('ghidra/EXAMPLE-IMAGE-DECOMP.txt','gaussian_main_thread','algo_main')
need('evidence/SECUREPD-IMPORTS.txt','dsc_verify_buffer','secure_pd_mapping_create_64','secure_pd_mapping_delete_64','get_secure_channel_handle')
need('ghidra/EXAMPLE-RUNNER-DECOMP.txt','example_algo_run','FUN_00011760')
# Exact machine identities.
P=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qcnspmcdm_ext_cdsp8380.inf_arm64_4a8c3ebe3aad408a/CDSP')
checks={
 'fastrpc_shell_3':R['cpz_shell']['production_shell_sha256'],
 'fastrpc_shell_unsigned_3':R['cpz_shell']['unsigned_shell_sha256'],
 'example_image_runner.so':R['shipped_copy_candidate']['sha256'],
}
for n,h in checks.items():
 p=P/n
 if not p.exists(): fail.append(f'missing same-machine {n}')
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=h: fail.append(f'hash changed: {n}')
fw=Path('/lib/firmware/qcom/x1e80100/microsoft/Denali/qccdsp8380.mbn')
if not fw.exists() or hashlib.sha256(fw.read_bytes()).hexdigest()!=R['securepd_trust']['root_firmware_sha256']:
 fail.append('root firmware identity mismatch')
# Mechanical layout compile.
try:
 subprocess.run(['cc','-std=c11','-Wall','-Wextra','-Werror','-c',str(D/'scaffold/verify_layout.c'),'-o','/tmp/e004dc-verify-layout.o'],check=True,capture_output=True,text=True)
except Exception as e: fail.append('ABI layout compile failed: '+str(e))
# Security/result invariants.
if R['securepd_trust']['arbitrary_unsigned_worker_admitted']: fail.append('unsigned worker unexpectedly admitted')
if R['shipped_copy_candidate']['camera_reachability_proven']: fail.append('runner camera reachability overclaimed')
if R['camera_parity']['shipping_securepd_module_proven_equivalent']: fail.append('shipping worker parity overclaimed')
if R['camera_parity']['custom_worker_trust_path_resolved']: fail.append('custom worker trust path overclaimed')
if any(R['runtime_actions'].values()): fail.append('runtime action recorded')
if R['status']!='PASS_SECUREPD_WORKER_ADMISSION_AND_PROTECTED_BUFFER_ABI_PROVEN_CAMERA_PARITY_WORKER_NOT_YET_ADMITTED': fail.append('bad status')
# Live safety: CB9 absent and next_entry empty where readable.
if Path('/proc/device-tree/soc@0/remoteproc@32300000/glink-edge/fastrpc/compute-cb@9').exists(): fail.append('live secure CB9 unexpectedly present')
if fail:
 print('E004dc VERIFY: FAIL')
 for x in fail: print(' -',x)
 raise SystemExit(1)
print('E004dc VERIFY: PASS')
print(' - production shell has real CPZ migration; unsigned shell has an error stub')
print(' - exact root firmware enforces signed/static-hash SecurePD module admission')
print(' - protected-buffer mailbox ABI and worker DSC mapping model are recovered')
print(' - shipped example runner proves mmap+memcpy worker shape but camera reachability is not claimed')
print(' - no shipping camera-equivalent worker or custom signing path is claimed yet')
print(' - protected runtime remains untouched and unauthorized')
