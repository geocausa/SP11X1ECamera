#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess
D=Path(__file__).resolve().parent;E=D/'evidence'
def need(v,m):
    if not v: raise AssertionError(m)
r=json.loads((D/'RESULT.json').read_text());s=json.loads((E/'SUMMARY.json').read_text());a=json.loads((E/'ATTEMPT1-PASS.json').read_text())
need(r['status']==s['status']=='PASS_REAR_RGB_UNDER_THREE_CAMERA_AUTHORITY_GOLDEN_RETURN_RETIRED','status')
need(r['candidate_boot_id']==s['candidate_boot_id']=='0c4bf47c-0dcf-4ff5-bde9-6e5c039189fe','candidate boot')
need(r['golden_return_boot_id']==s['golden_return_boot_id']=='5e583b57-765c-4bc2-8ff7-4285ac776be8','Golden boot')
need(a['boot_id']==r['candidate_boot_id'],'raw attempt boot')
need(a['status']=='PASS_REAR_RGB_UNDER_THREE_CAMERA_AUTHORITY','raw attempt status')
need(a['raw_attempt_schema'] if 'raw_attempt_schema' in a else True,'noop')
need(r['attempt_count']==1 and r['same_boot_retry_performed'] is False,'attempt policy')
need(r['rear_colorbar_exact'] and r['rear_colorbar_sha256']=='6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346','colorbar')
need(r['rear_sequences']==list(range(8)) and r['rear_frames']==8,'frames')
need(28.5<=r['rear_mean_fps']<=31.5,'fps')
need(r['three_sensor_entities_bound'] and r['all_three_runtime_suspended_before'] and r['all_three_runtime_suspended_after'],'coexistence PM')
need(r['final_route_state']=='neutral' and r['camss_e004j_parameter_armed'] and r['csiphy0_ir_gate_selected'] is False,'route/gate')
for k in ('front_stream_performed','ir_stream_performed','receiver_harness_performed','illumination_performed','linux_secureisp'):
    need(r[k] is False,k)
need(r['kernel_health']=='PASS' and r['golden_return_pass'] and r['candidate_retired'],'health/cleanup')
for manifest in ('RAW-TOPLEVEL.sha256','RAW-RUNTIME.sha256'):
    cp=subprocess.run(['sha256sum','-c',manifest],cwd=E,text=True,capture_output=True);need(cp.returncode==0,manifest+' '+cp.stdout+cp.stderr)
need((E/'REAR-COLORBAR.sha256').read_text().split()[0]=='6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346','colorbar manifest')
media=(E/'LOAD-MEDIA.txt').read_text(errors='replace')
for ent in ('sp11-vd55g0 2-0060 (1 pad, 1 link, 0 routes)','ov13858 3-0010 (1 pad, 1 link, 0 routes)','imx681 1-0010 (1 pad, 1 link, 0 routes)'):need(ent in media,'entity '+ent)
for ff,prefix in ((E/'PRE-STREAM-SUSPEND.txt','PRE_STREAM'),(E/'POST-STREAM-SUSPEND.txt','POST_STREAM')):
    t=ff.read_text()
    for x in ('IR','REAR','FRONT'):need(f'{x}_{prefix}_SUSPEND=PASS' in t,x+' '+prefix)
cp=subprocess.run([str(D/'route-state.py'),str(E/'FINAL-NEUTRAL.txt'),'--expect','neutral'],text=True,capture_output=True);need(cp.returncode==0,'final route')
t=(E/'REAR-NORMAL8.txt').read_text();seq=[int(x) for x in re.findall(r'seq:\s*(\d+)\s+bytesused:\s*14321824',t)];need(seq==list(range(8)),'raw seq')
ts=[float(x) for x in re.findall(r'ts:\s*([0-9]+\.[0-9]+)',t)];need(len(ts)==8,'timestamps');fps=1/(sum(b-a for a,b in zip(ts,ts[1:]))/7);need(28.5<=fps<=31.5,'raw fps')
log=(E/'DMESG.txt').read_text(errors='replace');need('SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596' in log,'IR bind authority')
for bad in ('E004J_CSIPHY0_DPHY_WINDOWS_PARITY','E004T_','MODE_SELECT=1 front transmission started','SP11_VD55G0_NATIVE_STREAM_BLOCK','ILLUMINATION_ON','WARNING:','Call trace:','Kernel panic','Unhandled fault'):
    need(bad.lower() not in log.lower(),'forbidden '+bad)
need('status=PASS_GOLDEN_RETURN' in (E/'GOLDEN-RETURN.txt').read_text(),'Golden evidence');need('status=PASS_CANDIDATE_RETIRED' in (E/'RETIRE.txt').read_text(),'retire evidence')
# Current machine remains protected Golden and candidate is gone.
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'current boot')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
need(not Path('/boot/sp11-7.1.5-camera-e004dr-unified-rgb-ir-rear-r2').exists(),'candidate boot present');need(not Path('/etc/grub.d/99zzzzzz_sp11_camera_e004dr_unified_rgb_ir_rear_r2').exists(),'candidate entry present')
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0','e004t_csiphy_readback_test','i2c_qcom_cci'):need(not Path('/sys/module',m).exists(),'active module '+m)
need(s['raw_attempt_schema']=='sp11-camera-e004dq-attempt1-pass-v1' and 'stale E004dq label' in s['raw_attempt_schema_note'],'stale label disclosure')
print('E004dr CLOSE VERIFY: PASS (rear RGB under three-camera authority + IR gate nonselection + Golden retired)')
