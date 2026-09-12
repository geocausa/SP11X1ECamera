#!/usr/bin/env python3
from pathlib import Path
import json, subprocess

D=Path(__file__).resolve().parent

def need(v,m):
    if not v: raise AssertionError(m)

need((D/'ARM.txt').exists(),'ARM evidence')
need((D/'PREARM.txt').exists(),'PREARM evidence')
need((D/'INSTALL.txt').exists(),'INSTALL evidence')
need(not (D/'RUNTIME-PREFLIGHT.txt').exists(),'runtime preflight unexpectedly passed')
need(not (D/'ATTEMPT1-CONSUMED.marker').exists(),'camera attempt unexpectedly consumed')
need(not (D/'RUNTIME-DMESG.txt').exists(),'camera runtime unexpectedly started')

arm=(D/'ARM.txt').read_text()
need('next_entry=sp11-camera-e004r-ir-only-bind-r3-one-shot' in arm,'arm target')
pre=(D/'PREARM.txt').read_text()
need('status=PASS_READY_TO_INSTALL' in pre,'prearm pass')
ins=(D/'INSTALL.txt').read_text()
need('status=INSTALLED_UNARMED' in ins,'install pass')

rp=(D/'runtime-preflight.sh').read_text()
need('[ -e /sys/bus/i2c/devices/2-0060 ] || fail i2c_client_2_0060' in rp,
     'consumed preflight did not hardcode 2-0060')
need('[ ! -e /sys/bus/i2c/devices/2-0060/driver ] || fail unexpected_sensor_driver' in rp,
     'consumed preflight driver test')
h=(D/'e004r_stream_block_test.c').read_text()
need('bus_find_device_by_name(&i2c_bus_type, NULL, "2-0060")' in h,
     'consumed harness did not hardcode 2-0060')

gold=(D/'GOLDEN-RETURN.txt').read_text()
need('status=PASS' in gold,'Golden return')
need('camera_modules=absent' in gold and 'media_nodes=absent' in gold,'Golden clean')
need('status=PASS_CANDIDATE_RETIRED' in (D/'RETIRE.txt').read_text(),'retire')

# Previous boot must be the E004r candidate, current boot Golden.
prev=subprocess.check_output(['journalctl','-b','-1','-k','--no-pager'],text=True,errors='replace')
need('sp11_camera_e004r_ir_only_bind_r3=1' in prev,'previous boot was not E004r candidate')
need('/boot/sp11-7.1.5-camera-e004r-ir-only-bind-r3/' in prev,'previous boot path')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'current boot not Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden default/no next')
for m in ('qcom_camss','sp11_vd55g0','e004r_stream_block_test','i2c_qcom_cci'):
    need(not Path('/sys/module',m).exists(),'camera module active on Golden '+m)

r=json.load(open(D/'RESULT.json'))
need(r['status']=='ABORT_PRE_ATTEMPT_I2C_ADAPTER_NUMBER_DRIFT_GOLDEN_RETURN_RETIRED','result status')
need(r['camera_attempt_started'] is False and r['attempt_consumed'] is False,'attempt classification')
need(r['sensor_data_writes']==0 and r['sensor_module_loaded'] is False,'sensor untouched')
need(r['golden_return_pass'] is True and r['candidate_retired'] is True,'cleanup')

print('E004R_RUNTIME_VERIFY=PASS CLASS=PRE_ATTEMPT_I2C_ADAPTER_NUMBER_DRIFT')
print('E004R_CAMERA_ATTEMPT=NO SENSOR_WRITES=0 CAMSS=NO STREAM_CALLBACK=NO')
print('E004R_DISCOVERY_BUG=HARDCODED_2_0060 OBSERVED_CANDIDATE=3_0060')
print('E004R_GOLDEN_RETURN=PASS CANDIDATE_RETIRED=YES')
