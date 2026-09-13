#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, struct, sys
import pefile

D=Path(__file__).resolve().parent
G=D/'ghidra'
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump')
K=ROOT/'qccamsecureisp8380.inf_arm64_e0daad652520462e/qccamsecureisp8380.sys'
T=ROOT/'qccamsecureisp8380.inf_arm64_e0daad652520462e/QcISPTrustlet8380.dll'
I=ROOT/'qccamsecureisp8380.inf_arm64_e0daad652520462e/qccamsecureisp8380.inf'
Q=ROOT/'qctree.inf_arm64_b90c225f258c030c/QcTrEE.sys'
QI=ROOT/'qctree.inf_arm64_b90c225f258c030c/qctree.inf'
R=D/'RESULT.json'

H={
 K:'47c944fa497477751073ec79a27a589a55e884178c1859d6f27388ec7af2ad53',
 T:'55ebf254447b9ff8c0a5b20ae81e84f04355f84ce6fa6a09f6205562a5b0b606',
 I:'22bffc4795803de62825ee8eab6bd13cdd2d18e505a39b410eecad52b092e05f',
 Q:'9cd8252c1b501c1d58e4c49d020d526a5b9bc41a3f5de2ec08e866c3a26c16a2',
 QI:'9e6d38df0b0ff8f766a4b67084f1d55e3bf44ddac766c5466b179e99adda8d6b',
 G/'KMD-TASK-XREFS.txt':'e8d3c72e387cb6ab94afe33129542934148b7f538e1a1450656fca5ca4c3fa7b',
 G/'TRUSTLET-TASK-XREFS.txt':'d2a5a38dcc5568cb65edf1699cd5e9fd8f833fac08d0353c5988eff3ceaeea2a',
 G/'KMD-DECOMP-SECURE-LANE.txt':'280d90d779aca24a23e8c7bd8d0c80491dc0bc0b2429899eb216b548ce0c0039',
 G/'KMD-IOTARGET-XREFS.txt':'a2120aa31de409fbea6b7aa4d7dd289b4e2940602128ca883d6b47665b42652a',
 G/'KMD-FUNCTION-XREFS.txt':'e59fd52885ff2778663da085b5508a94e8e39ff2ab01d9343b6c5500f14d5ca2',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(x,m):
    if not x: raise AssertionError(m)
for p,h in H.items(): need(sha(p)==h,'hash drift '+str(p))

# INF authority.
inf=I.read_bytes().decode('utf-16le')
for tok in ('ServiceType = SecureCompanion','TrustletIdentity = 4096','QcISPTrustlet8380.dll',
            'libbitml_nsp_v2_skel.so','bm3a68v08s11n52.bin','ACPI\\QCOM0CCC'):
    need(tok in inf,'SecureISP INF '+tok)
qinf=QI.read_bytes().decode('utf-16le')
need('PassThroughService.RegKey' in qinf and 'AE865C08-4A07-404D-BE51-D9A0465E23E5' in qinf,
     'QcTrEE PassThrough GUID')

# Read exact KMD VA bytes through PE mapping.
pe=pefile.PE(str(K),fast_load=True)
base=pe.OPTIONAL_HEADER.ImageBase
def va_bytes(va,n):
    rva=va-base
    off=pe.get_offset_from_rva(rva)
    return K.read_bytes()[off:off+n]
guidb=va_bytes(0x140011030,16)
d1,d2,d3=struct.unpack('<IHH',guidb[:8])
guid=f'{{{d1:08X}-{d2:04X}-{d3:04X}-{guidb[8]:02X}{guidb[9]:02X}-'+''.join(f'{x:02X}' for x in guidb[10:])+'}'
need(guid=='{AE865C08-4A07-404D-BE51-D9A0465E23E5}','GUID bytes '+guid)
need(struct.unpack('<I',va_bytes(0x140001d08,4))[0]==0x02001807,'pass-through request dword')
need(struct.unpack('<I',va_bytes(0x140001d10,4))[0]==0x00568004,'QcTrEE IOCTL')

kmd=(G/'KMD-TASK-XREFS.txt').read_text()
trust=(G/'TRUSTLET-TASK-XREFS.txt').read_text()
lane=(G/'KMD-DECOMP-SECURE-LANE.txt').read_text()
iot=(G/'KMD-IOTARGET-XREFS.txt').read_text()
fx=(G/'KMD-FUNCTION-XREFS.txt').read_text()

# Class-1 task callsites and meanings.
calls={
 0:'ISPTRUSTLET', # INIT established by trustlet case0 ISPDriverInit/Config
 1:'ISPTRUSTLET_DEINIT',
 2:'ISPTRUSTLET_START',
 3:'ISPTRUSTLET_STOP',
 4:'ISPTRUSTLET_PROCESS_DMFT_SURFACE',
 5:'ISPTRUSTLET_PROCESS_CMD_BUFFER',
 6:'ISPTRUSTLET_PROCESS_DMI_BUFFER',
 7:'ISPTRUSTLET_PROCESS_CSL_PACKET',
 8:'1000', 9:'ISPTRUSTLET_GET_SWABF_DATA',10:'ISPTRUSTLET_GET_SWASF_DATA',13:'ISPTRUSTLET_NOTIFY_EVENT'
}
for n in (0,1,2,3,4,5,6,7,8,9,10):
    need(f'FUN_140004a90({n},' in kmd, f'KMD missing task {n}')
need('FUN_140004a90(0xd,' in kmd,'KMD missing task 13')
for n in range(0,11):
    need(f'case {n}:' in trust,f'trustlet missing case {n}')
need('case 0xd:' in trust,'trustlet missing task 13')
need('case 11:' not in trust and 'case 12:' not in trust,'unexpected explicit task 11/12')
for tok in ('ISPDriverInit','ISPDriverConfig','ISPTRUSTLET_PROCESS_DMI_BUFFER','ISPTRUSTLET_PROCESS_CSL_PACKET',
            'FUN_1800196f0(1','FUN_1800196f0(0'):
    need(tok in trust,'trustlet behavior '+tok)

# Task class selector: KMD helper maps selector 0/1/2 -> WDF task class 1/2/3.
for tok in ('if (param_2 == 0)','uVar2 = 1','else if (param_2 == 1)','uVar2 = 2',
            'if (param_2 != 2)','uVar2 = 3'):
    need(tok in kmd,'task class map '+tok)
# Normal control sends are selector 0; debug image retrieval uses task 1 selector 2.
need('FUN_140004a90(1,2,' in fx,'class-3 image retrieval proof')

# Outer operation cases/names.
ops={
 '0x801':'SecureISPDriver_GetInitParams','0x802':'SecureISPDriver_DeviceConfig',
 '0x803':'SecureISPDriver_SendCSLPacket','0x804':'SecureISPDriver_DeviceStart',
 '0x80c':'SecureISPDriver_GetDeviceInfo','0x80d':'SecureISPDriver_Init',
 '0x80f':'SecureISPDriver_SupplementalDeviceConfig','0x810':'SecureISPDriver_NotifyEvent'
}
for c,n in ops.items():
    need(f'case {c}:' in kmd and n in kmd, 'operation '+c)
need('case 0x805:' in kmd and 'FUN_140005208(' in kmd,'0x805 stop helper')
need('SecureISPDriver_DeviceStop' in kmd,'DeviceStop name')
need('case 0x80e:' in kmd and 'FUN_140004f10(' in kmd,'0x80e deinit helper')
need('SecureISPDriver_DeInit' in kmd and 'SecureISPDriver_PowerOff' in kmd,'DeInit/PowerOff names')
for x in range(0x806,0x80c):
    need(f'case 0x{x:x}:' not in kmd,'unexpected implemented operation '+hex(x))

# Secure-lane ordering and exported dispatcher.
need('if (param_2 == 0x2e)' in fx and 'bVar1 = 1' in fx,'0x2e protect')
need('param_2 != 0x2f' in fx and 'bVar1 = 0' in fx,'0x2f unprotect')
need('FUN_140001b08(param_1,*param_4,bVar1' in fx,'dispatcher to ConfigSecureCamera')
need('FUN_140004b88(param_1,1' in kmd,'protect before START path')
need('FUN_140004a90(2,0,' in kmd,'START task')
need('FUN_140004a90(3,0,' in kmd,'STOP task')
need('FUN_140004b88(param_1,0' in kmd,'unprotect after STOP path')
need('IoGetDeviceInterfaces(&DAT_140011030' in iot,'QcTrEE interface open')
need('Successfully Config Secure Camera - SecureLaneCpCtrl' in iot,'secure-lane config')

# Trustlet secure memory and internal secure CSID/IFE handlers.
for tok in ('DAL_csid_process_iq_packet','DAL_secure_ife_process_iq_packet'):
    need(tok in trust,'secure handler '+tok)
# Imports are independently visible in exact binary strings/import table enough for this static gate.
import subprocess
imp=subprocess.check_output(['llvm-readobj','--coff-imports',str(T)],text=True,stderr=subprocess.DEVNULL)
for tok in ('CreateSecureSection','OpenSecureSection','AssignMemoryToSocDomain','MapSecureIo',
            'MapViewOfFile','UnmapViewOfFile','FlushSecureSectionBuffers'):
    need(tok in imp,'trustlet import '+tok)

r=json.load(open(R))
need(r['status']=='PASS_SECUREISP_HOST_TRUSTLET_ABI_STATIC_RECONSTRUCTED','result status')
need(r['secure_lane_control']['qctree_service_guid']==guid,'result GUID')
need(r['secure_lane_control']['qctree_ioctl']=='0x00568004','result IOCTL')
need(r['parity_boundary']['linux_secureisp_runtime_authorized'] is False,'runtime overclaim')

# Current machine safety.
need(Path('/proc/sys/kernel/osrelease').read_text().strip()=='7.1.5-sp11-render-parity-v4+','Golden kernel')
cmd=Path('/proc/cmdline').read_text()
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in cmd,'Golden boot image')
print('E004Z_VERIFY=PASS')
print('E004Z_SECURE_COMPANION=TRUSTLET_ID_4096 CLASS1_TASKS=0..10,13 TASKS11_12=DEFAULT')
print('E004Z_SECURE_LANE=START:0x2e->TASK2 STOP:TASK3->0x2f')
print('E004Z_QCTREE=PASSTHROUGH GUID='+guid+' IOCTL=0x00568004 REQUEST=0x02001807')
print('E004Z_LINUX_SECUREISP_RUNTIME=NOT_AUTHORIZED')
