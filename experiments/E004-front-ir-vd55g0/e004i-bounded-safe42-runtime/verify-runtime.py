#!/usr/bin/env python3
from pathlib import Path
import json, re, subprocess

D=Path(__file__).resolve().parent

def need(v,m):
    if not v: raise AssertionError(m)

log=(D/'ATTEMPT1-DMESG.txt').read_text()
need(log.count('SP11_VD55G0_CONFIG42_BEGIN')==1,'single attempt')
need('patch_sha256=5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321' in log,'patch identity')
need('safe42_sha256=159647774f45331210044d0680e50bf16e8aaeeb8c3e98449d2cef7adeffacb2' in log,'safe42 identity')
need('full43_sha256=9664529aab0c65d6f3ae9778c8c31f54fa1675bde748fdaafc8e2d2ab4ea387c' in log,'full43 identity')
need('MCLK_Hz=19200000 expected_Hz=19200000' in log,'MCLK')
need('VDDIO_uV=1800000 expected_uV=1800000' in log,'VDDIO')
need('VCORE_uV=1152000 expected_uV=1152000' in log,'VCORE')
need('VANA_uV=2800000 expected_uV=2800000' in log,'VANA')
need('model_raw=30,47 model_be=0x3047 revision_raw=11,11 revision=0x1111' in log,'identity')
need('ID_GATE=PASS model_be=0x3047 revision=0x1111_CUT1 writes=0' in log,'prewrite identity gate')

poll=[x for x in log.splitlines() if 'SP11_VD55G0_CONFIG42_POLL ' in x]
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

need('PATCH_SETUP writes=553 reg=0x0200 value=0x02' in log,'patch setup')
need('BOOT writes=554 reg=0x0200 value=0x01' in log,'boot')
mb=re.search(r'STROBE_ISOLATION_BEFORE reg=0x0468 value=0x([0-9a-fA-F]{2}) write_authorized=0',log)
ma=re.search(r'STROBE_ISOLATION_AFTER reg=0x0468 before=0x([0-9a-fA-F]{2}) after=0x([0-9a-fA-F]{2}) unchanged=1 write_authorized=0',log)
need(mb and ma,'strobe isolation lines')
need(mb.group(1).lower()=='02','post-boot GPIO1 already 0x02')
need(ma.group(1).lower()==ma.group(2).lower()=='02','GPIO1 unchanged at 0x02')
need('READBACK=PASS extclk=19200000 mipi=840000000 line=1200 frame=1955 roi=644x604 gpio=01,02,01,01' in log,'full safe42 readback')
need('COMPLETE writes=596 patch_writes=552 setup_writes=1 boot_writes=1 safe_config_writes=42 isolated_strobe_writes=0 final_state=SW_STBY stream=0 illumination=0' in log,'complete')
need('POWER_OFF reset_asserted=1' in log,'power off')
need('END status=0 writes=596 powered_off=1 stream=0 illumination=0' in log,'end')
for bad in ('writes=597','isolated_strobe_writes=1','strobe_write=1','STREAM_START','ILLUMINATION_ON'):
    need(bad not in log,'forbidden marker '+bad)

a=json.load(open(D/'ATTEMPT1-PASS.json'))
need(a['status']=='PASS_SAFE42_WINDOWS_CONFIG_STROBE_UNCHANGED_POWERED_OFF','attempt status')
need(a['sensor_data_writes']==596 and a['surface_patch_writes']==552 and a['safe_config_writes']==42,'write counts')
need(a['isolated_strobe_before']=='0x02' and a['isolated_strobe_after']=='0x02','strobe state')
need(a['isolated_strobe_unchanged'] is True and a['isolated_strobe_writes']==0,'strobe isolation')
need(a['gpio_readback']==['01','02','01','01'],'GPIO readback')
need(a['windows_config_readback_pass'] is True,'config readback')
need(a['camss'] is False and a['v4l2'] is False and a['stream'] is False and a['illumination'] is False,'no camera/illumination stack')
need(a['powered_off'] is True and a['retry_authorized'] is False,'powered off/no retry')

need((D/'ATTEMPT1-CONSUMED.marker').read_text().strip(),'attempt consumed')
need('status=PASS_READY_FOR_SINGLE_INSMOD' in (D/'RUNTIME-PREFLIGHT.txt').read_text(),'preflight')
gold=(D/'GOLDEN-RETURN.txt').read_text()
need('status=PASS' in gold and 'saved_entry=sp11-audio-fullio-v19c' in gold and 'next_entry=' in gold,'Golden return')
need('status=PASS_CANDIDATE_RETIRED' in (D/'RETIRE.txt').read_text(),'retired')

cmd=Path('/proc/cmdline').read_text()
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in cmd,'currently Golden')
need('sp11_camera_e004i_config42=1' not in cmd,'candidate marker absent')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')
need(not Path('/boot/sp11-7.1.5-camera-e004i-config42').exists(),'candidate boot retired')
need(not Path('/etc/grub.d/99zzzzzz_sp11_camera_e004i_config42').exists(),'candidate entry retired')
need(not Path('/sys/module/sp11_vd55g0_config42probe').exists(),'module absent')
need(not Path('/dev/media0').exists(),'media absent')

print('E004I_RUNTIME_VERIFY=PASS ATTEMPTS=1 WRITES=596 PREFIX=554 SAFE_CONFIG=42 STROBE_WRITES=0')
print('E004I_POST_BOOT_GPIO1=0x02 BEFORE_SAFE42=0x02 AFTER_SAFE42=0x02 UNCHANGED=YES')
print('E004I_WINDOWS_CONFIG_READBACK=PASS GPIO=01,02,01,01 EXTCLK=19200000 MIPI=840000000 LINE=1200 FRAME=1955 ROI=644x604')
print('E004I_SAFETY=PASS CAMSS=NO V4L2=NO STREAM=NO ILLUMINATION=NO POWERED_OFF=YES')
print('E004I_GOLDEN_RETURN=PASS CANDIDATE_RETIRED=YES')
