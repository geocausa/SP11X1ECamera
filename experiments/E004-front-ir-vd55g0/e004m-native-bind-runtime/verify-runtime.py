#!/usr/bin/env python3
from pathlib import Path
import json, subprocess

D=Path(__file__).resolve().parent

def need(v,m):
    if not v: raise AssertionError(m)

a=json.load(open(D/'ATTEMPT1-FAILURE.json'))
need(a['status']=='FAIL_BOUNDED_NO_RETRY','attempt status')
need(a['precheck_or_load_failure']==1,'bounded early load/check failure')
need(a['camss_receiver_programming_invoked'] is False,'receiver programming')
need(a['capture_stream_performed'] is False,'capture stream')
need(a['sensor_stream_register_write_performed'] is False,'sensor stream write')
need(a['illumination_performed'] is False,'illumination')
need(a['serious_fault'] is False,'serious fault')
need(a['direct_sensor_s_stream_result'] is None,'sensor callback should not run')

log=(D/'RUNTIME-DMESG.txt').read_text()
for bad in ('SP11_VD55G0_NATIVE_ID','SP11_VD55G0_NATIVE_WINDOWS_STATE',
            'SP11_VD55G0_NATIVE_BIND','SP11_VD55G0_NATIVE_STREAM_BLOCK',
            'E004M_STREAM_BLOCK_TEST','E004J_CSIPHY0_DPHY_WINDOWS_PARITY',
            'ILLUMINATION_ON','STREAM_START'):
    need(bad not in log,'unexpected runtime marker '+bad)
need('mc: Linux media interface' in log and 'videodev: Linux video capture interface' in log,
     'media dependency load evidence')

block=(D/'STREAM-BLOCK.txt').read_text()
need('camss_e004j_param=missing' in block,'permission-read symptom')
need('runtime_status=unsupported' in block,'sensor remained unbound')

run=(D/'run-once.sh').read_text()
need('cat /sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity' in run,
     'unprivileged parameter read no longer present in consumed script')
need('sudo -n cat /sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity' not in run,
     'consumed package must remain original')

patch=(D.parent/'e004k-csiphy0-dphy-parity-module/0001-sp11-e004j-csiphy0-dphy-windows-parity.patch').read_text()
need('csiphy_x1e_ir_dphy_windows_parity, bool, 0400' in patch,'parameter mode 0400')

k=D.parent/'e004k-csiphy0-dphy-parity-module/qcom-camss.ko'
need(subprocess.check_output(['modinfo','-F','srcversion',str(k)],text=True).strip()=='B7CF41C55172B14CD629043',
     'pinned CAMSS srcversion')
need(subprocess.check_output(['modinfo','-F','srcversion','qcom_camss'],text=True).strip()=='7FA30D4F4B8441472FBD74C',
     'stock CAMSS srcversion differs')

need('status=PASS' in (D/'GOLDEN-RETURN.txt').read_text(),'Golden return')
need('status=PASS_CANDIDATE_RETIRED' in (D/'RETIRE.txt').read_text(),'candidate retired')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'currently Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')

r=json.load(open(D/'RESULT.json'))
need(r['status']=='FAIL_SAFE_PRE_SENSOR_CAMSS_PARAM_PERMISSION_GOLDEN_RETURN_RETIRED','final result')
need(r['sensor_module_loaded'] is False and r['sensor_data_writes']==0,'sensor untouched')
need(r['golden_return_pass'] is True and r['candidate_retired'] is True,'cleanup')

print('E004M_RUNTIME_VERIFY=PASS CLASS=SAFE_PRE_SENSOR_SCRIPT_PERMISSION_FAILURE')
print('E004M_SENSOR=NOT_LOADED WRITES=0 STREAM_CALLBACK=NO RECEIVER_PROGRAMMING=NO ILLUMINATION=NO')
print('E004M_CAMSS=PINNED_SRCVERSION_B7CF41C55172B14CD629043 STOCK_DIFFERENT=YES')
print('E004M_GOLDEN_RETURN=PASS CANDIDATE_RETIRED=YES RETRY=NO')
