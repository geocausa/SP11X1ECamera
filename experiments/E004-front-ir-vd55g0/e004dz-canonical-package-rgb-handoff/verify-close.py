#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess
D=Path(__file__).resolve().parent;E=D/'evidence'
def need(v,m):
    if not v:raise AssertionError(m)
r=json.loads((D/'RESULT.json').read_text());s=json.loads((E/'SUMMARY.json').read_text());a=json.loads((E/'ATTEMPT1-PASS.json').read_text());prod=json.loads((E/'FRONT1-PRODUCER-RESULT.json').read_text())
need(r['status']==s['status']=='PASS_CANONICAL_PACKAGE_RGB_HANDOFF_GOLDEN_RETURN_RETIRED_UNINSTALLED','status')
need(r['candidate_boot_id']==s['candidate_boot_id']==a['boot_id']=='cf96bf28-1793-4240-a6b5-7a5c1a94fa1c','candidate boot')
need(r['golden_return_boot_id']==s['golden_return_boot_id']=='63e0ee9f-959a-445e-b27b-a73c25d52bad','Golden boot')
need(r['attempt_count']==1 and r['same_boot_retry_performed'] is False,'attempt')
need(a['status']=='PASS_CANONICAL_PACKAGE_SAME_BOOT_REAR_TO_FRONT_HANDOFF','attempt status')
need(a['package_manifest_sha256']=='d1d0eb4c504378643630f6975a08d9c15d2b8ac0bedca2f1205bbfb51f885373','package manifest')
need(a['rear_colorbar_exact'] and a['rear_sequences']==list(range(8)) and a['rear_frames']==8,'rear')
need(28.5<=a['rear_mean_fps']<=31.5,'rear fps')
need(a['between_route_state']=='neutral','handoff neutral')
need(a['front_sequences']==list(range(27)) and a['front_frames']==27,'front frames')
need(prod['status']=='PASS' and len(prod['rows'])==24,'producer')
counts={'triangle':0,'centroid':0,'two_vertex':0}
for row in prod['rows']:
    mode=row.get('awb_selection_mode');need(mode in counts,'AWB '+repr(mode));counts[mode]+=1
need(counts==a['awb_selection_modes']==r['awb_selection_modes'],'AWB modes')
need(a['front_post_g3_policy']=='shadow' and a['front_post_g3_native_writes']==0,'post G3')
need(a['all_three_suspended_before'] and a['all_three_suspended_after_rear'] and a['all_three_suspended_after_front'],'PM')
need(a['final_route_state']=='neutral' and a['camss_e004j_parameter_armed'] and a['csiphy0_ir_gate_selected'] is False,'route/gate')
for k in ('ir_stream_performed','illumination_performed','linux_secureisp'):need(a[k] is False,k)
need(a['kernel_health']=='PASS' and r['golden_return_pass'] and r['candidate_retired'] and r['package_uninstalled'],'cleanup')
for manifest in ('RAW-TOPLEVEL.sha256','RAW-RUNTIME.sha256','PRODUCER.sha256'):
    cp=subprocess.run(['sha256sum','-c',manifest],cwd=E,text=True,capture_output=True);need(cp.returncode==0,manifest+' '+cp.stdout+cp.stderr)
need((E/'REAR-COLORBAR.sha256').read_text().split()[0]=='6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346','colorbar manifest')
media=(E/'LOAD-MEDIA.txt').read_text(errors='replace')
for ent in ('sp11-vd55g0 2-0060 (1 pad, 1 link, 0 routes)','ov13858 3-0010 (1 pad, 1 link, 0 routes)','imx681 1-0010 (1 pad, 1 link, 0 routes)'):need(ent in media,'entity '+ent)
for p,e in ((E/'LOAD-MEDIA.txt','neutral'),(E/'ROUTE-REAR-ON.txt','rear-only'),(E/'BETWEEN-NEUTRAL.txt','neutral'),(E/'ROUTE-FRONT-ON.txt','front-only'),(E/'FINAL-NEUTRAL.txt','neutral')):
    cp=subprocess.run([str(D/'route-state.py'),str(p),'--expect',e],text=True,capture_output=True);need(cp.returncode==0,p.name+' '+cp.stdout+cp.stderr)
for f,prefix in ((E/'PRE-STREAM-SUSPEND.txt','PRE_STREAM'),(E/'POST-REAR-SUSPEND.txt','POST_REAR'),(E/'POST-FRONT-SUSPEND.txt','POST_FRONT')):
    t=f.read_text()
    for x in ('IR','REAR','FRONT'):need(f'{x}_{prefix}_SUSPEND=PASS' in t,x+' '+prefix)
t=(E/'REAR-NORMAL8.txt').read_text(errors='replace');seq=[int(x) for x in re.findall(r'seq:\s*(\d+)\s+bytesused:\s*14321824',t)];need(seq==list(range(8)),'rear raw seq');ts=[float(x) for x in re.findall(r'ts:\s*([0-9]+\.[0-9]+)',t)];need(len(ts)==8,'rear timestamps');fps=1/(sum(b-a for a,b in zip(ts,ts[1:]))/7);need(28.5<=fps<=31.5,'raw fps')
ft=(E/'FRONT-F1.txt').read_text(errors='replace')
for tok in ('FRONT_LAUNCHER_RC=0','PROD_POST_G3_POLICY=shadow','STREAMON_OK_ASYNC','STREAMOFF_OK','E003I_GM_PRODUCER=PASS'):need(tok in ft,tok)
dq=[int(x) for x in re.findall(r'^DQBUF\d+_INDEX=\d+ BYTESUSED=\d+ SEQUENCE=(\d+)$',ft,re.M)];need(dq==list(range(27)),'front transcript seq')
log=(E/'DMESG.txt').read_text(errors='replace');need('SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596' in log,'IR bind');need('X1E front PIX completed provider-owned bounded twenty-seven-frame live requeue' in log,'front completion')
for bad in ('E004J_CSIPHY0_DPHY_WINDOWS_PARITY','E004T_','SP11_VD55G0_NATIVE_STREAM_BLOCK','ILLUMINATION_ON','WARNING:','Call trace:','Kernel panic','Unhandled fault'):
    need(bad.lower() not in log.lower(),'forbidden '+bad)
need('SP11_CAMERA_STACK_LIVE_INSTALL=PASS ACTIVATED=NO' in (E/'PACKAGE-INSTALL.txt').read_text(),'package install')
need('SP11_CAMERA_STACK_LIVE_UNINSTALL=PASS ACTIVATED=NO' in (E/'PACKAGE-UNINSTALL.txt').read_text(),'package uninstall')
need('status=PASS_GOLDEN_RETURN' in (E/'GOLDEN-RETURN.txt').read_text(),'Golden evidence');need('status=PASS_CANDIDATE_RETIRED' in (E/'RETIRE.txt').read_text(),'retire evidence')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'current Golden');env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
need(not Path('/boot/sp11-7.1.5-camera-e004dz-canonical-package-rgb-handoff').exists(),'candidate boot');need(not Path('/etc/grub.d/99zzzzzz_sp11_camera_e004dz_canonical_package_rgb_handoff').exists(),'candidate entry')
for p in ('/usr/lib/sp11-front-imx681','/usr/lib/sp11-camera-stack','/usr/bin/sp11-front-imx681','/usr/bin/sp11-front-imx681-discover','/var/lib/sp11-camera-stack'):need(not Path(p).exists(),'package path '+p)
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0','e004t_csiphy_readback_test','i2c_qcom_cci'):need(not Path('/sys/module',m).exists(),'active '+m)
print('E004dz CLOSE VERIFY: PASS (canonical package same-boot rear->front + Golden + retired + uninstalled)')
