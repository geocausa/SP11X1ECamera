#!/usr/bin/env python3
from pathlib import Path
import json, subprocess

D=Path(__file__).resolve().parent


def need(v,m):
    if not v: raise AssertionError(m)

log=(D/'ATTEMPT1-DMESG.txt').read_text()
need(log.count('SP11_VD55G0_IDPROBE_BEGIN')==1,'single probe begin')
need(log.count('SP11_VD55G0_IDPROBE_MODEL ')==1,'single model read')
need(log.count('SP11_VD55G0_IDPROBE_REVISION ')==1,'single revision read')
need('MCLK_Hz=19200000 expected_Hz=19200000' in log,'MCLK')
need('VDDIO_uV=1800000 expected_uV=1800000' in log,'VDDIO')
need('VCORE_uV=1152000 expected_uV=1152000' in log,'VCORE')
need('VANA_uV=2800000 expected_uV=2800000' in log,'VANA')
need('MODEL raw=30,47 le=0x4730 be=0x3047 windows_qti_expected_be=0x3047' in log,'model identity')
need('REVISION raw=11,11 le=0x1111 be=0x1111' in log,'CUT1 revision')
need('READS_COMPLETE sensor_data_writes=0 patch=0 boot=0 configure=0 stream=0 illumination=0' in log,'write-free marker')
need('POWER_OFF reset_asserted=1' in log,'power-off marker')
need('END status=0 powered_off=1' in log,'successful powered-off end')
for bad in ('PATCH_', 'STREAM_', 'ILLUMINATION_', 'sensor_data_writes=1'):
    need(bad not in log,'forbidden runtime marker '+bad)

attempt=json.load(open(D/'ATTEMPT1-PASS.json'))
need(attempt['status']=='PASS_IDENTITY_REVISION_ONLY_POWERED_OFF','attempt pass')
need(attempt['sensor_data_register_writes']==0 and attempt['patch_upload'] is False,'no writes/patch')
need(attempt['sensor_boot'] is False and attempt['sensor_configure'] is False,'no boot/config')
need(attempt['stream'] is False and attempt['illumination'] is False,'no stream/illumination')
need(attempt['powered_off'] is True and attempt['retry_authorized'] is False,'poweroff/no retry')

pre=(D/'RUNTIME-PREFLIGHT.txt').read_text()
need('status=PASS_READY_FOR_SINGLE_INSMOD' in pre,'runtime preflight')
need('i2c_client=/sys/bus/i2c/devices/3-0060' in pre,'CCI client')
need('attempt_consumed=NO' in pre,'pre-consume state')
need((D/'ATTEMPT1-CONSUMED.marker').read_text().strip(),'consume marker')

gold=(D/'GOLDEN-RETURN.txt').read_text()
need('status=PASS' in gold and 'saved_entry=sp11-audio-fullio-v19c' in gold and 'next_entry=' in gold,'Golden return')
ret=(D/'RETIRE.txt').read_text()
need('status=PASS_CANDIDATE_RETIRED' in ret,'retired')

cmd=Path('/proc/cmdline').read_text()
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in cmd,'currently Golden')
need('sp11_camera_e004c_ir_idprobe=1' not in cmd,'candidate marker absent')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env,'saved Golden')
need('next_entry=\n' in env,'next empty')
need(not Path('/boot/sp11-7.1.5-camera-e004c-ir-idprobe').exists(),'candidate boot retired')
need(not Path('/etc/grub.d/99zzzzzz_sp11_camera_e004c_ir_idprobe').exists(),'candidate grub entry retired')
need(not Path('/sys/module/sp11_vd55g0_idprobe').exists(),'probe module absent')
need(not Path('/dev/media0').exists(),'media node absent')

print('E004C_RUNTIME_VERIFY=PASS ATTEMPTS=1 MODEL_BE=0x3047 MODEL_LE=0x4730 REVISION=0x1111_CUT1')
print('E004C_RUNTIME_SAFETY=PASS SENSOR_DATA_WRITES=0 PATCH=0 BOOT=0 CONFIGURE=0 STREAM=0 ILLUMINATION=0 POWERED_OFF=YES')
print('E004C_GOLDEN_RETURN=PASS CANDIDATE_RETIRED=YES')
