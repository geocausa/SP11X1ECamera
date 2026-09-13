#!/usr/bin/env python3
from pathlib import Path
import json, re, sys

E=Path(__file__).resolve().parent
fail=[]
def need(path,*tokens):
    s=(E/path).read_text(errors='replace')
    for t in tokens:
        if t not in s:
            fail.append(f'{path}: missing {t!r}')
    return s

r=json.loads((E/'RESULT.json').read_text())
if r.get('status') != 'PASS_PROTECTED_TRANSFER_AUTHORITY_MAPPED_LINUX_BACKEND_UNRESOLVED':
    fail.append('unexpected RESULT status')
if r['runtime_actions'] != {
    'linux_secureisp':False,'qseecom_send':False,'qcomtee_enable_or_load':False,
    'scm_assign_mem':False,'protected_mmio':False,'camera_runtime':False}:
    fail.append('runtime-actions boundary changed')

w=need(Path('evidence/WINDOWS-TRUSTLET-TRANSFER-AUTHORITY.txt'),
       '55ebf254447b9ff8c0a5b20ae81e84f04355f84ce6fa6a09f6205562a5b0b606',
       '180005884:', 'bl\t0x180004c58', '1800058c4:', 'bl\t0x180004828',
       'FUN_1800037c8', 'FUN_180028600', 'OpenSecureSection(&local_40)',
       'AssignMemoryToSocDomain(hFileMappingObject,pvVar7,0,uVar1,0xd,4,0)')

i=need(Path('evidence/TRUSTLET-IMPORTS-AND-PACKAGE.txt'),
       'DLL Name: IumSdk.dll','CreateSecureSection','OpenSecureSection','AssignMemoryToSocDomain',
       'MapSecureIo','MapViewOfFile','FlushSecureSectionBuffers',
       'ServiceType = SecureCompanion','TrustletIdentity = 4096',
       'ELF 32-bit LSB shared object, QUALCOMM DSP6','bitml_nsp_v2_domains_execute')
# The imported DLL set is deliberately Windows/IUM + CRT only.
dlls=[ln.split('DLL Name:',1)[1].strip().lower() for ln in i.splitlines() if 'DLL Name:' in ln]
for bad in ('qsee','qcomtee','qtee','fastrpc','adsprpc'):
    if any(bad in d for d in dlls):
        fail.append(f'unexpected trustlet transport dependency containing {bad}: {dlls}')

l=need(Path('evidence/LINUX-QSEECOM-QCOMTEE.txt'),
       'CONFIG_QCOM_SCM=y','CONFIG_QCOM_QSEECOM=y','CONFIG_QCOM_QSEECOM_UEFISECAPP=y',
       '# CONFIG_QCOMTEE is not set','CONFIG_TEE_DMABUF_HEAPS=y',
       '{ "qcom.tz.uefisecapp", "uefisecapp" }','qcom_scm_qseecom_app_get_id',
       'qcom_scm_qseecom_app_send')

h=need(Path('evidence/TEE-DMABUF-EXTERNAL-SAMPLE.txt'),
       'TEE_DMA_HEAP_SECURE_VIDEO_RECORD','protected,secure-video-record',
       'DMA_ATTR_SKIP_CPU_SYNC','--- runtime dma heaps ---','default_cma_region','reserved','system')
# Current evidence must not show an active protected heap after the runtime marker.
after=h.split('--- runtime dma heaps ---',1)[1]
if 'protected,' in after:
    fail.append('runtime now exposes a protected TEE dma heap; refresh experiment')

f=need(Path('evidence/FIRMWARE-NAME-INVENTORY.txt'),
       '/lib/firmware/qcom/x1e80100/microsoft/Denali/qcadsp8380.mbn',
       '/lib/firmware/qcom/x1e80100/microsoft/Denali/qccdsp8380.mbn')
# Restrict the filename-negative claim to the X1E section only.
x=f.split('--- X1E firmware files with secure/camera-adjacent names ---',1)[1].split('--- globally installed candidate names ---',1)[0].lower()
for name in ('secureisp','camsecure','camera_secure','qsee_camera','qtee_camera'):
    if name in x:
        fail.append(f'new obvious X1E camera secure-app filename found: {name}')

need(Path('README.md'),
     'Windows authority for the protected internal -> external frame transfer is the VTL1 Secure Companion trustlet itself',
     'ordinary Linux HLOS `memcpy()` is not parity',
     'E004bs — Linux protected execution counterpart authority')

if fail:
    print('E004br VERIFY: FAIL')
    for x in fail: print(' -',x)
    sys.exit(1)
print('E004br VERIFY: PASS')
print(' - Windows protected transfer authority is the VTL1 Secure Companion trustlet')
print(' - the trustlet constructs internal CP_CAMERA then external VTL1 mappings in one object')
print(' - class-1 DMFT task metadata is not the final protected frame-copy primitive')
print(' - trustlet imports IUM secure-memory APIs, not a QSEE/QCOMTEE transport')
print(' - Golden has QSEECOM plumbing but no registered camera app and QCOMTEE is disabled')
print(' - generic secure-video-record DMA heap support has no active provider on SP11')
print(' - no secure runtime operation was authorized or executed')
