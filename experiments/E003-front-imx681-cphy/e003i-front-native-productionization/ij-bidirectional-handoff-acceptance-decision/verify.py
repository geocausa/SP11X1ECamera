#!/usr/bin/env python3
from pathlib import Path
import json,subprocess
D=Path(__file__).resolve().parent
BASE=D.parent
REPO=D.parents[3]

def need(v,m):
    if not v:
        raise AssertionError(m)

def load(stage):
    return json.load(open(BASE/stage/'RESULT.json'))

r=json.load(open(D/'RESULT.json'))
ib=load('ib-unified-current-golden-rear-front-dtb')
idp=load('id-unified-dtb-rear-regression-r16')
iep=load('ie-unified-front-production-r27')
ig=load('ig-unified-rear-to-front-r16-r27')
ih=load('ih-unified-front-to-rear-r27-r16')
need(ib['status']=='PASS_OFFLINE_UNIFIED_CURRENT_GOLDEN_REAR_FRONT_DTB','IB')
need(idp['status']=='PASS_CAPTURE_ID_UNIFIED_REAR_R16_GOLDEN_RESTORED_RETIRED','ID')
need(iep['status']=='PASS_CAPTURE_IE_UNIFIED_FRONT_R27_GOLDEN_RESTORED_RETIRED','IE')
need(ig['status']=='PASS_CAPTURE_IG_REAR_TO_FRONT_R16_R27_GOLDEN_RESTORED_RETIRED','IG')
need(ih['status']=='PASS_CAPTURE_IH_FRONT_TO_REAR_R27_R16_GOLDEN_RESTORED_RETIRED','IH')
need(ig['neutral_handoff']=='PASS' and ig['final_route_state']=='front-only','IG neutral/route')
need(ih['neutral_handoff']=='PASS' and ih['final_route_state']=='rear-only','IH neutral/route')
need(ig['same_boot_retry_performed'] is False and ih['same_boot_retry_performed'] is False,'no retries')
need(ig['golden_return']=='PASS' and ih['golden_return']=='PASS','Golden returns')
need(iep['post_g3_policy']=='shadow' and iep['post_g3_native_writes']==0,'front shadow authority')

need(r['status']=='PASS_OFFLINE_BIDIRECTIONAL_HANDOFF_ACCEPTANCE_DECISION','status')
need(r['rear_rgb_front_rgb_bounded_bidirectional_handoff_accepted'] is True,'RGB accept')
need(r['neutral_route_transaction_mandatory'] is True,'neutral mandatory')
need(r['persistent_replacement_of_golden_default_authorized'] is False,'Golden promotion')
need(r['full_camera_stack_default_authorized'] is False,'full stack promotion')
need(r['front_ir_vd55g0_linux_proven'] is False,'IR boundary')
need(r['front_post_g3_native_feedback_proven'] is False,'feedback boundary')
need(r['repeated_alternating_rgb_switch_soak_proven'] is False,'soak boundary')
a=r['unified_rgb_authority']
need(a['dtb_sha256']=='5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321','DTB')
need(a['qcom_camss_sha256']=='7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95','CAMSS')
need(a['imx681_sha256']=='ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6','IMX681')
need(a['ov13858_sha256']=='13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309','OV13858')
need(a['front_post_g3_policy']=='shadow','shadow')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c' in env,'Golden saved')
need(not any(x.startswith('next_entry=') and x!='next_entry=' for x in env.splitlines()),'next empty')
for m in ('qcom_camss','imx681','ov13858'):
    need(not Path('/sys/module',m).exists(),'module '+m)
head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
origin=subprocess.check_output(['git','-C',str(REPO),'rev-parse','origin/experiment/e003-front-imx681-cphy'],text=True).strip()
need(head==origin,'origin')
print('IJ_VERIFY=PASS RGB_BIDIRECTIONAL_BOUNDED=ACCEPTED DEFAULT_PROMOTION=NO')
print('IJ_BLOCKERS=VD55G0+NATIVE_FEEDBACK+ALTERNATING_SWITCH_SOAK')
print('IJ_NEXT=E004_VD55G0_OFFLINE_AUTHORITY_AND_BRINGUP_FOUNDATION')
