#!/usr/bin/env python3
from pathlib import Path
import json,subprocess
D=Path(__file__).resolve().parent; R=D.parents[2]
def need(v,m):
    if not v: raise AssertionError(m)
r=json.loads((D/'RESULT.json').read_text()); ready=json.loads((R/'src/sp11-camera-stack/READINESS.json').read_text())
need(r['status']=='PASS_NONPROTECTED_PRODUCT_READY_FRONT_FEEDBACK_CLOSED_FULL_1TO1_HELD_ONLY_ON_SECURE_ADMISSION','status')
need(ready['promotion_decision']=='HOLD_FULL_1TO1_DEFAULT','promotion')
need(ready['nonprotected_product']['status']=='READY_NONDEFAULT','nonprotected status')
need(ready['nonprotected_product']['rear_rgb']=='PASS' and ready['nonprotected_product']['front_rgb']=='PASS','RGB')
need(ready['remaining_proofs']['front_post_g3_changed_native_feedback']=='PASS_LIVE_ONE_NATURAL_CHANGED_POST_G3_WRITE','front proof')
need(ready['remaining_proofs']['current_scene_post_g3_state']=='NATURAL_BELOW_CAP_RELEASE_OBSERVED','scene gate closed')
need(ready['resume_conditions']['post_g3_feedback']=='CLOSED_BY_E004EN_NO_FURTHER_SCENE_GATE','resume gate')
need(ready['remaining_proofs']['protected_ir_windows_hello_end_to_end']=='BLOCKED_ON_PRODUCTION_WORKER_ADMISSION','protected blocker')
need(ready['protected_path']['worker_signed'] is False and ready['protected_path']['worker_production_admitted'] is False and ready['protected_path']['runtime_authorized'] is False,'trust stays closed')
en=json.loads((R/'experiments/E004-front-ir-vd55g0/e004en-natural-cap-release-one-shot-runtime/RESULT.json').read_text())
need(en['status']=='PASS_LIVE_ONE_NATURAL_CHANGED_POST_G3_WRITE_GOLDEN_RETURN_RETIRED_UNINSTALLED','E004en status')
need(en['production_native_changed_post_g3_feedback_proven'] is True and en['later_native_writes']==1 and en['second_later_writes']==0,'E004en write proof')
em=json.loads((R/'experiments/E004-front-ir-vd55g0/e004em-windows-dark-plateau-precap-oracle/RESULT.json').read_text())
need(em['status']=='PASS_FRESH_WINDOWS_REQUEST7_BELOW_CAP_CURRENT_AMBIENT' and em['request7_below_cap'] is True,'E004em oracle')
subprocess.run(['python3',str(R/'src/sp11-camera-stack/verify-source.py')],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['python3',str(R/'src/sp11-camera-protected-worker/verify-source.py')],check=True,stdout=subprocess.DEVNULL)
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True); need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
for p in ('/usr/lib/sp11-front-imx681','/usr/lib/sp11-camera-stack','/var/lib/sp11-camera-stack'): need(not Path(p).exists(),'package absent '+p)
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0'): need(not Path('/sys/module',m).exists(),'module absent '+m)
print('E004eo VERIFY: PASS (front feedback closed; sole full-parity blocker is legitimate protected-worker admission)')
