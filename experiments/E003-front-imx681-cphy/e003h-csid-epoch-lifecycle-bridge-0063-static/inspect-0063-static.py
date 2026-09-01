#!/usr/bin/env python3
import hashlib,json,re,subprocess
from pathlib import Path
SRC=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss')
EXP=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-csid-epoch-lifecycle-bridge-0063-static')
BASE=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera/experiments/E003-front-imx681-cphy/e003h-vfe1-cgc-release-0062r1-candidate/runtime-0062r1-analysis.json')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(x): raise SystemExit('FAIL: '+x)
pre={'camss.c':'945a5765667ab6a2bada9395079cd519e7afc038afaa8d57d99926dd38c50795','camss-csid-680.c':'6171b255cfdc6372f46702c150338c6921fa326f3997267e83a4ae47b284955d','camss-csid.h':'5869c6721ebec550d5d3e21e6503fd1f580ebb1aa0991ea25532cfb12156b46d'}
for n,h in pre.items():
    if sha(EXP/'preimage'/n)!=h: die('preimage '+n)
base=json.load(open(BASE)); win=json.load(open(EXP/'WINDOWS-ORACLE.json'))
if sha(BASE)!='e1fc64c2baa82047e4844be1af6254798f7097e22441a84e2c1b4e3615740be3' or not base['accepted']: die('0062r1 base')
if not win['accepted'] or win['live_trace']['true_vfe_raw_epoch_hits']!=0 or win['live_trace']['bus_retarget_hits']!=44 or win['live_trace']['epoch_cdm_consume_hits']!=44: die('Windows live oracle')
if int(win['proof']['epoch_message_snapshot']['field4'],16)&(1<<21)==0: die('Windows field4 bit21')
patch=(EXP/'0063-csid-epoch-lifecycle-bridge.patch').read_text()
adds='\n'.join(x for x in patch.splitlines() if x.startswith('+') and not x.startswith('+++'))
for tok in ('readl','writel','ioread','iowrite'):
    if tok in adds: die('new MMIO token '+tok)
if adds.count('csid680_x1e_front_ipp_poll_epoch0')!=3: die('helper definition/prototype/call count')
if 'CSID_IPP_CAMIF_EPOCH0' not in adds or 'BIT(21)' not in adds: die('bit21 definition')
if 'read_poll_timeout(READ_ONCE, status,' not in adds: die('software latch poll')
cam=(SRC/'camss.c').read_text(); cs=(SRC/'camss-csid-680.c').read_text(); hdr=(SRC/'camss-csid.h').read_text()
window=cam[cam.index('/* First-frame pacing: Epoch0 #0'):cam.index('out_unwind:',cam.index('/* First-frame pacing: Epoch0 #0'))]
if window.count('csid680_x1e_front_ipp_poll_epoch0(csid,')!=1: die('runner CSID wait')
if 'vfe680_x1e_pix_runtime_poll_epoch0' in window: die('obsolete runner VFE epoch wait retained')
if window.count('vfe680_x1e_pix_runtime_bus_update(vfe, pix, 1)')!=1 or window.count('camss_x1e_pix_submit_prime(camss, &materialized->prime, 2)')!=1 or window.count('vfe680_x1e_pix_runtime_poll_video')!=1: die('post-Epoch lifecycle drift')
if cs.count('csid->x1e_ipp_irq_seen_or |= ipp_val;')!=1: die('existing ISR latch drift')
if cs.count('csid->x1e_ipp_irq_seen_or = 0;')!=1: die('existing startup latch reset drift')
if hdr.count('csid680_x1e_front_ipp_poll_epoch0')!=1: die('prototype')
ko=EXP/'qcom-camss.ko'; modsha=sha(ko)
if modsha!='686be619437c5dd476c8733daca2150bed8ba84e8729f3d85e22cae0776f2209': die('module hash')
ver=subprocess.check_output(['modinfo','-F','vermagic',str(ko)],text=True).strip()
if ver!='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64': die('vermagic')
nm=subprocess.check_output(['nm','-n',str(ko)],text=True)
for sym in ('csid680_x1e_front_ipp_poll_epoch0','vfe680_x1e_pix_runtime_poll_video'):
    if sym not in nm: die('binary symbol '+sym)
out={
 'schema':'sp11-e003h-csid-epoch-lifecycle-bridge-0063-static-v1','accepted':True,'runtime_authorized':False,
 'base_0062r1_analysis_sha256':sha(BASE),'windows_oracle_sha256':sha(EXP/'WINDOWS-ORACLE.json'),
 'patch_sha256':sha(EXP/'0063-csid-epoch-lifecycle-bridge.patch'),'module_sha256':modsha,'build_log_sha256':sha(EXP/'CAMSS-0063-BUILD.raw.txt'),
 'preimage_sha256':pre,'postimage_sha256':{n:sha(SRC/n) for n in pre},
 'delta':{'runner_epoch_source':'CSID1_IPP_ISR_latched_bit21','timeout_us':500000,'poll_sleep_us':10,'new_mmio_reads':0,'new_mmio_writes':0,'new_register_values':0,'new_hardware_programming':False,'new_irq_mask_programming':False,'new_state_fields':0,'vfe_epoch_mmio_poll_removed_from_runner':True,'vfe_video_poll_retained':True,'bus_slot1_retarget_retained':True,'prime2_retained':True},
 'windows_authority':{'true_vfe_raw_epoch_hits':0,'bus_retarget_hits':44,'epoch_cdm_consume_hits':44,'epoch_message_field4':'0x00611dd0','field4_bit21':True},
 'base_retained':{'cgc_release':base['linux_bus_cgc_ovd_0062r1']=='0x00000000','ubwc_static_ctrl':base['ubwc_static_ctrl'],'csid_geometry':base['csid_geometry'],'rtcdm_fifo_bl_completed':base['rtcdm_fifo_bl_completed'],'nine_bus_clients_address_status_match':base['nine_bus_clients_address_status_match']},
 'next':'build an unarmed Golden-safe 0063 one-shot candidate; runtime must execute once only and return immediately to Golden'
}
(EXP/'0063-static-inspection.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
