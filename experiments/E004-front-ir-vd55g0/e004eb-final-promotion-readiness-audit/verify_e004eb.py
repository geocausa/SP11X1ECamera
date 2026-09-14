#!/usr/bin/env python3
from pathlib import Path
import json,subprocess
D=Path(__file__).resolve().parent;R=D.parents[2]
def need(v,m):
    if not v:raise AssertionError(m)
r=json.loads((D/'RESULT.json').read_text());ready=json.loads((R/'src/sp11-camera-stack/READINESS.json').read_text())
need(r['status']=='PASS_NONPROTECTED_PRODUCT_READY_FULL_1TO1_DEFAULT_HELD','status')
need(ready['promotion_decision']=='HOLD_FULL_1TO1_DEFAULT','decision')
need(ready['nonprotected_product']['status']=='READY_NONDEFAULT','nonprotected')
need(ready['nonprotected_product']['rear_rgb']=='PASS' and ready['nonprotected_product']['front_rgb']=='PASS','RGB')
need(ready['nonprotected_product']['ir_receiver_windows_readback']=='PASS_96_OF_96','IR receiver')
need(ready['protected_path']['canonical_windows_exact_worker_source']=='PASS_OFFLINE','worker source')
need(ready['protected_path']['worker_signed'] is False and ready['protected_path']['worker_production_admitted'] is False and ready['protected_path']['runtime_authorized'] is False,'trust')
need(ready['remaining_proofs']['protected_ir_windows_hello_end_to_end']=='BLOCKED_ON_PRODUCTION_WORKER_ADMISSION','Hello blocker')
need(ready['remaining_proofs']['front_post_g3_changed_native_feedback']=='IMPLEMENTED_BUT_LIVE_PROOF_SCENE_GATED','front proof')
checks={
 'e004dp-unified-rgb-ir-receiver-coexistence':'PASS_THREE_CAMERA_BIND_CSIPHY0_WINDOWS_96_OF_96_GOLDEN_RETURN_RETIRED',
 'e004dr-unified-rgb-ir-rear-regression-r2':'PASS_REAR_RGB_UNDER_THREE_CAMERA_AUTHORITY_GOLDEN_RETURN_RETIRED',
 'e004ds-unified-rgb-ir-front-regression':'PASS_FRONT_RGB_UNDER_THREE_CAMERA_AUTHORITY_GOLDEN_RETURN_RETIRED',
 'e004dt-front-post-g3-current-scene-cap-audit':'PASS_CURRENT_SCENE_CAP_ACTIVE_NO_POST_G3_NATIVE_WRITE_OPPORTUNITY',
 'e004dz-canonical-package-rgb-handoff':'PASS_CANONICAL_PACKAGE_RGB_HANDOFF_GOLDEN_RETURN_RETIRED_UNINSTALLED',
 'e004cz-integrated-golden-protected-provider-build-closure':'PASS_INTEGRATED_GOLDEN_PROTECTED_INTERNAL_PATH_COMPILES_LINKS_FAILS_CLOSED',
 'e004da-external-cpz-sample-backing':'PASS_EXTERNAL_CPZ_BACKING_LIFETIME_COMPILES_LINKS_IMPORT_HANDOFF_STILL_EXPLICIT',
 'e004db-external-protected-sample-fastrpc-handoff-authority':'PASS_REAL_FASTRPC_FD_HANDOFF_AUTHORITY_COMPILES_MAP_UNMAP_LIFETIME_BOUND',
 'e004dc-cpz-protected-frame-worker-image-and-invoke-abi':'PASS_SECUREPD_WORKER_ADMISSION_AND_PROTECTED_BUFFER_ABI_PROVEN_CAMERA_PARITY_WORKER_NOT_YET_ADMITTED',
 'e004de-cpz-securepd-worker-trust-admission-feasibility':'PASS_NO_AUTHORIZED_SOURCE_CONTROLLED_CPZ_WORKER_ADMISSION_PATH',
 'e004df-parity-worker-admission-alternatives-closure':'PASS_CPZ_IS_ONLY_PARITY_SHAPED_BACKEND_RUNTIME_BLOCKED_ON_WORKER_TRUST_ADMISSION',
 'e004ea-canonical-offline-protected-worker':'PASS_CANONICAL_OFFLINE_PROTECTED_WORKER_EXACT_TRUST_BLOCK_UNCHANGED'}
for rel,status in checks.items():
    j=json.loads((R/'experiments/E004-front-ir-vd55g0'/rel/'RESULT.json').read_text());need(j['status']==status,rel)
subprocess.run(['python3',str(R/'src/sp11-camera-stack/verify-source.py')],check=True,stdout=subprocess.DEVNULL)
subprocess.run(['python3',str(R/'src/sp11-camera-protected-worker/verify-source.py')],check=True,stdout=subprocess.DEVNULL)
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
for p in ('/usr/lib/sp11-front-imx681','/usr/lib/sp11-camera-stack','/var/lib/sp11-camera-stack'):need(not Path(p).exists(),'package path remains '+p)
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0'):need(not Path('/sys/module',m).exists(),'loaded '+m)
print('E004eb VERIFY: PASS (non-protected product ready; full 1:1 default correctly held)')
