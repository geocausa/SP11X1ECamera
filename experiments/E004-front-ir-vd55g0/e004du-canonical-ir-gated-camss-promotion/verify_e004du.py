#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess
R=Path(__file__).resolve().parents[3];D=Path(__file__).resolve().parent
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
res=json.loads((D/'RESULT.json').read_text())
need(res['status']=='PASS_CANONICAL_CAMSS_PROMOTED_BYTE_EXACT_TO_LIVE_TESTED_IR_GATED_AUTHORITY','status')
cs=R/'src/front-imx681/kernel/camss/camss-csiphy-3ph-1-0.c'
need(sha(cs)=='2ea354304cad721967279a8a0211e97ec2731a71bd945a6ddba6dccdb191a362','canonical csiphy source')
t=cs.read_text()
for tok in ('module_param_named(e004j_ir_dphy_windows_parity','CAMSS_X1E80100','csiphy->id == 0','V4L2_MBUS_CSI2_DPHY','settle_cnt = 0x10','E004J_CSIPHY0_DPHY_WINDOWS_PARITY'):
    need(tok in t,'source token '+tok)
need('static bool csiphy_x1e_ir_dphy_windows_parity;' in t,'default false')
p=R/'experiments/E004-front-ir-vd55g0/e004k-csiphy0-dphy-parity-module/0001-sp11-e004j-csiphy0-dphy-windows-parity.patch'
need(sha(p)=='1fc0f918a2f00e79918cf8bf7164f49cb8df395b8b05c949dc424a7b3824a869','patch')
prov=json.loads((R/'src/front-imx681/PROVENANCE.json').read_text())
need(prov['authority']['camss_module_sha256']=='862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7','prov camss module')
need(prov['authority']['imx681_module_sha256']=='ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6','prov imx module')
ir=prov['ir_receiver_promotion'];need(ir['default_enabled'] is False,'prov gate default');need(ir['source_sha256']==sha(cs),'prov source');need(ir['module_sha256']==prov['authority']['camss_module_sha256'],'prov module')
for x in prov['files']:
    if x['bundle_path']=='kernel/camss/camss-csiphy-3ph-1-0.c':
        need(x['sha256']==sha(cs) and x['authority_kind']=='e004du-promoted-live-tested-ir-gated-camss-source','file provenance');break
else: raise AssertionError('csiphy file provenance missing')
build=(R/'src/front-imx681/build-production.sh').read_text()
for tok in ('KERNEL_SOURCE="${KERNEL_SOURCE:?','KERNEL_BUILD="${KERNEL_BUILD:?','make -C "$KERNEL_SOURCE" O="$KERNEL_BUILD" M="$WORK/camss"','CAMSS_SHA=862732b7','IMX_SHA=ef57ed06','EXACT_ACCEPTED_MODULES=YES'):
    need(tok in build,'build token '+tok)
post=(D/'evidence/POST-FIX-PRODUCTION-BUILD.txt').read_text()
for tok in ('FRONT_IMX681_PRODUCTION_BUILD=PASS EXACT_ACCEPTED_MODULES=YES','862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7','ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6','70f407f5fd70e6657f9647a33eecde744ac9e1bd19fa9e901a4faf52508e354d','4721ff6510d806ed63ffcb70d9a88441220047ef734ca760cc40bdc5719cd7ce'):
    need(tok in post,'post-fix evidence '+tok)
pre=(D/'evidence/PRE-FIX-PRODUCTION-BUILD.txt').read_text()
need('daa1df3ad92eb3f66c64f73b42f922dc3bb297bb47c62995102a65793212e06b' in pre and 'c64c5afda9aa9bc2f14ada2343157a63fcabafef87b709d9a69c9d788e72ced7' in pre,'pre-fix drift evidence')
for rel,status in (
 ('e004dp-unified-rgb-ir-receiver-coexistence','PASS_THREE_CAMERA_BIND_CSIPHY0_WINDOWS_96_OF_96_GOLDEN_RETURN_RETIRED'),
 ('e004dr-unified-rgb-ir-rear-regression-r2','PASS_REAR_RGB_UNDER_THREE_CAMERA_AUTHORITY_GOLDEN_RETURN_RETIRED'),
 ('e004ds-unified-rgb-ir-front-regression','PASS_FRONT_RGB_UNDER_THREE_CAMERA_AUTHORITY_GOLDEN_RETURN_RETIRED')):
    j=json.loads((R/'experiments/E004-front-ir-vd55g0'/rel/'RESULT.json').read_text());need(j['status']==status,rel)
# Current host must still be protected Golden and camera modules absent.
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'current Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0','e004t_csiphy_readback_test'):need(not Path('/sys/module',m).exists(),'loaded '+m)
print('E004du VERIFY: PASS (canonical IR-gated CAMSS source + exact production rebuild + prior live authority)')
