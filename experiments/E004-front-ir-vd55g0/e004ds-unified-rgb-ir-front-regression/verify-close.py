#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess
D=Path(__file__).resolve().parent;E=D/'evidence'
def need(v,m):
    if not v:raise AssertionError(m)
r=json.loads((D/'RESULT.json').read_text());s=json.loads((E/'SUMMARY.json').read_text());a=json.loads((E/'ATTEMPT1-PASS.json').read_text());prod=json.loads((E/'FRONT1-PRODUCER-RESULT.json').read_text())
need(r['status']==s['status']=='PASS_FRONT_RGB_UNDER_THREE_CAMERA_AUTHORITY_GOLDEN_RETURN_RETIRED','status')
need(r['candidate_boot_id']==s['candidate_boot_id']==a['boot_id']=='76ea2b42-7589-4e28-bd9e-b08f1f0cc049','candidate boot')
need(r['golden_return_boot_id']==s['golden_return_boot_id']=='dba28692-7f66-49c5-b93d-a3d6cc5b0e2d','Golden boot')
need(r['attempt_count']==1 and r['same_boot_retry_performed'] is False,'attempt')
need(a['status']=='PASS_FRONT_RGB_UNDER_THREE_CAMERA_AUTHORITY' and a['front_sequences']==list(range(27)) and a['front_frames']==27,'front frames')
need(r['front_post_g3_policy']=='shadow' and r['front_post_g3_native_writes']==0,'post G3')
need(prod['status']=='PASS' and len(prod['rows'])==24,'producer')
counts={'triangle':0,'centroid':0,'two_vertex':0}
for row in prod['rows']:
    mode=row.get('awb_selection_mode');need(mode in counts,'mode '+repr(mode));counts[mode]+=1
need(counts==r['awb_selection_modes']==s['awb_selection_modes'],'AWB modes')
need(r['three_sensor_entities_bound'] and r['all_three_runtime_suspended_before'] and r['all_three_runtime_suspended_after'],'bind/PM')
need(r['final_route_state']=='neutral' and r['camss_e004j_parameter_armed'] and r['csiphy0_ir_gate_selected'] is False,'route/gate')
for k in ('rear_stream_performed','ir_stream_performed','illumination_performed','linux_secureisp'):need(r[k] is False,k)
need(r['kernel_health']=='PASS' and r['golden_return_pass'] and r['candidate_retired'],'health/cleanup')
for manifest in ('RAW-TOPLEVEL.sha256','RAW-RUNTIME.sha256','PRODUCER.sha256'):
    cp=subprocess.run(['sha256sum','-c',manifest],cwd=E,text=True,capture_output=True);need(cp.returncode==0,manifest+' '+cp.stdout+cp.stderr)
media=(E/'LOAD-MEDIA.txt').read_text(errors='replace')
for ent in ('sp11-vd55g0 2-0060 (1 pad, 1 link, 0 routes)','ov13858 3-0010 (1 pad, 1 link, 0 routes)','imx681 1-0010 (1 pad, 1 link, 0 routes)'):need(ent in media,'entity '+ent)
for p,e in ((E/'LOAD-MEDIA.txt','neutral'),(E/'ROUTE-FRONT-ON.txt','front-only'),(E/'FINAL-NEUTRAL.txt','neutral')):
    cp=subprocess.run([str(D/'route-state.py'),str(p),'--expect',e],text=True,capture_output=True);need(cp.returncode==0,p.name+' '+cp.stdout+cp.stderr)
for ff,prefix in ((E/'PRE-STREAM-SUSPEND.txt','PRE_STREAM'),(E/'POST-STREAM-SUSPEND.txt','POST_STREAM')):
    t=ff.read_text()
    for x in ('IR','REAR','FRONT'):need(f'{x}_{prefix}_SUSPEND=PASS' in t,x+' '+prefix)
t=(E/'FRONT-F1.txt').read_text(errors='replace')
for tok in ('FRONT_LAUNCHER_RC=0','PROD_POST_G3_POLICY=shadow','STREAMON_OK_ASYNC','STREAMOFF_OK','E003I_GM_PRODUCER=PASS'):need(tok in t,tok)
seq=[int(x) for x in re.findall(r'^DQBUF\d+_INDEX=\d+ BYTESUSED=\d+ SEQUENCE=(\d+)$',t,re.M)];need(seq==list(range(27)),'transcript seq')
log=(E/'DMESG.txt').read_text(errors='replace');need('SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596' in log,'IR bind');need('X1E front PIX completed provider-owned bounded twenty-seven-frame live requeue' in log,'front completion')
for bad in ('E004J_CSIPHY0_DPHY_WINDOWS_PARITY','E004T_','SP11_VD55G0_NATIVE_STREAM_BLOCK','ILLUMINATION_ON','WARNING:','Call trace:','Kernel panic','Unhandled fault'):
    need(bad.lower() not in log.lower(),'forbidden '+bad)
need('status=PASS_GOLDEN_RETURN' in (E/'GOLDEN-RETURN.txt').read_text(),'Golden evidence');need('status=PASS_CANDIDATE_RETIRED' in (E/'RETIRE.txt').read_text(),'retire evidence')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'current Golden');env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
need(not Path('/boot/sp11-7.1.5-camera-e004ds-unified-rgb-ir-front').exists(),'candidate boot');need(not Path('/etc/grub.d/99zzzzzz_sp11_camera_e004ds_unified_rgb_ir_front').exists(),'candidate entry')
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0','e004t_csiphy_readback_test','i2c_qcom_cci'):need(not Path('/sys/module',m).exists(),'active '+m)
print('E004ds CLOSE VERIFY: PASS (front R27 under three-camera authority + IR gate nonselection + Golden retired)')
