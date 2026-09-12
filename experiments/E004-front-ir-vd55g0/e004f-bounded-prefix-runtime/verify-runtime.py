#!/usr/bin/env python3
from pathlib import Path
import json, subprocess

D=Path(__file__).resolve().parent

def need(v,m):
    if not v: raise AssertionError(m)

log=(D/'ATTEMPT1-DMESG.txt').read_text()
need(log.count('SP11_VD55G0_PREFIX_BEGIN')==1,'single prefix attempt')
need('patch_bytes=552 patch_sha256=5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321' in log,'Surface patch identity')
need('MCLK_Hz=19200000 expected_Hz=19200000' in log,'MCLK')
need('VDDIO_uV=1800000 expected_uV=1800000' in log,'VDDIO')
need('VCORE_uV=1152000 expected_uV=1152000' in log,'VCORE')
need('VANA_uV=2800000 expected_uV=2800000' in log,'VANA')
need('model_raw=30,47 model_be=0x3047 revision_raw=11,11 revision=0x1111' in log,'identity')
need('ID_GATE=PASS model_be=0x3047 revision=0x1111_CUT1 writes=0' in log,'pre-write identity gate')
poll=[x for x in log.splitlines() if 'SP11_VD55G0_PREFIX_POLL ' in x]
need(len(poll)==4,'four polls')
expected=[
 ('READY_TO_BOOT','0x002c','0x01','6','1'),
 ('PATCH_SETUP_COMPLETE','0x0200','0x00','28','2'),
 ('BOOT_COMPLETE','0x0200','0x00','6','2'),
 ('SW_STBY','0x002c','0x02','4','1'),
]
for line,(name,reg,val,tmo,reads) in zip(poll,expected):
    for token in (f'name={name}',f'reg={reg}',f'expected={val}',f'timeout_ms={tmo}',f'reads={reads}','result=PASS'):
        need(token in line,f'{name}: {token}')
need('PREFIX_PATCH_BEGIN start=0x2000 bytes=552' in log,'patch begin')
need('PREFIX_PATCH_SETUP writes=553 reg=0x0200 value=0x02' in log,'patch setup')
need('PREFIX_BOOT writes=554 reg=0x0200 value=0x01' in log,'boot')
need('PREFIX_COMPLETE writes=554 patch_writes=552 setup_writes=1 boot_writes=1 final_config_writes=0 final_state=SW_STBY stream=0 illumination=0' in log,'prefix complete')
need('PREFIX_POWER_OFF reset_asserted=1' in log,'power off')
need('PREFIX_END status=0 writes=554 powered_off=1 stream=0 illumination=0' in log,'successful powered off end')
for bad in ('writes=555','final_config_writes=1','STREAM_START','ILLUMINATION_ON'):
    need(bad not in log,'forbidden runtime marker '+bad)

a=json.load(open(D/'ATTEMPT1-PASS.json'))
need(a['status']=='PASS_WINDOWS_PREFIX_TO_SW_STBY_POWERED_OFF','attempt pass')
need(a['sensor_data_writes']==554 and a['surface_patch_writes']==552,'write counts')
need(a['final_43_windows_config_writes'] is False,'no final config')
need(a['sensor_gpio1_strobe_configured'] is False,'no strobe selector')
need(a['camss'] is False and a['v4l2'] is False and a['stream'] is False and a['illumination'] is False,'no camera/illumination stack')
need(a['powered_off'] is True and a['retry_authorized'] is False,'poweroff/no retry')

need((D/'ATTEMPT1-CONSUMED.marker').read_text().strip(),'attempt consumed')
pre=(D/'RUNTIME-PREFLIGHT.txt').read_text()
need('status=PASS_READY_FOR_SINGLE_INSMOD' in pre and 'attempt_consumed=NO' in pre,'preflight')
gold=(D/'GOLDEN-RETURN.txt').read_text()
need('status=PASS' in gold and 'saved_entry=sp11-audio-fullio-v19c' in gold and 'next_entry=' in gold,'Golden return')
ret=(D/'RETIRE.txt').read_text()
need('status=PASS_CANDIDATE_RETIRED' in ret,'retired')

cmd=Path('/proc/cmdline').read_text()
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in cmd,'currently Golden')
need('sp11_camera_e004f_prefixprobe=1' not in cmd,'candidate marker absent')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden saved/no next')
need(not Path('/boot/sp11-7.1.5-camera-e004f-prefixprobe').exists(),'candidate boot retired')
need(not Path('/etc/grub.d/99zzzzzz_sp11_camera_e004f_prefixprobe').exists(),'candidate entry retired')
need(not Path('/sys/module/sp11_vd55g0_prefixprobe').exists(),'prefix module absent')
need(not Path('/dev/media0').exists(),'media node absent')

print('E004F_RUNTIME_VERIFY=PASS ATTEMPTS=1 WRITES=554 PATCH=552 PATCH_SETUP=1 BOOT=1 FINAL_STATE=SW_STBY')
print('E004F_POLLS=READY:1read PATCH_SETUP:2reads BOOT:2reads SW_STBY:1read ALL_PASS')
print('E004F_SAFETY=PASS FINAL_CONFIG=0 STROBE_CONFIG=NO CAMSS=NO V4L2=NO STREAM=NO ILLUMINATION=NO POWERED_OFF=YES')
print('E004F_GOLDEN_RETURN=PASS CANDIDATE_RETIRED=YES')
