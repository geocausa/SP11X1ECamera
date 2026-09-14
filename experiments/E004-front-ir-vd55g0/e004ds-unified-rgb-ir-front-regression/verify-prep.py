#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
D=Path(__file__).resolve().parent;R=D.parents[2];DR=D.parent/'e004dr-unified-rgb-ir-rear-regression-r2'
def need(v,m):
    if not v:raise AssertionError(m)
for p in D.glob('*.sh'):subprocess.run(['bash','-n',str(p)],check=True)
for p in D.glob('*.py'):
    if p.name!='verify-prep.py':compile(p.read_text(),str(p),'exec')
r=json.loads((D/'RESULT.json').read_text());need(r['attempt_limit']==1 and r['retry_authorized'] is False,'attempt')
need(r['dtb_sha256']=='3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb','dtb')
need(r['ir_gated_camss_sha256']=='862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7','camss')
need(r['front_package_manifest_sha256']=='60a3490177ef2befe61a61905160cec7e0b0b4d152fff4ccf5dccd8bca62cc1a','package')
subprocess.run(['python3',str(DR/'verify-close.py')],check=True,stdout=subprocess.DEVNULL)
run=(D/'run-once.sh').read_text()
need('front-imx681-launcher.py" --execute --post-g3-write-policy shadow' in run,'launcher')
need('"$REARVIDEO"' not in run and '--stream-mmap' not in run,'direct stream command in E004ds')
need('e004t_csiphy_readback_test' not in run and 'insmod "$HARNESS"' not in run,'receiver harness')
need("media-ctl -d \"$MEDIA\" -l '\"msm_csiphy2\":1 -> \"msm_csid1\":0 [0]'" in run,'front off 1')
need("media-ctl -d \"$MEDIA\" -l '\"msm_csid1\":4 -> \"msm_vfe1_pix\":0 [0]'" in run,'front off 2')
v=(D/'verify-live.py').read_text();need("dq==list(range(27))" in v,'27 frame verify');need("'E004J_CSIPHY0_DPHY_WINDOWS_PARITY'" in v,'IR gate nonselection');need("'SP11_VD55G0_NATIVE_STREAM_BLOCK'" in v,'IR nonstream')
pre=(D/'prearm-check.sh').read_text();need('stage-package.sh' in pre and '60a3490177ef2befe61a61905160cec7e0b0b4d152fff4ccf5dccd8bca62cc1a' in pre,'package staging');need('build-authority.sh' in pre,'kernel authority')
# Fresh current state.
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'not Golden');env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
need(not Path('/boot/sp11-7.1.5-camera-e004ds-unified-rgb-ir-front').exists(),'candidate boot');need(not Path('/etc/grub.d/99zzzzzz_sp11_camera_e004ds_unified_rgb_ir_front').exists(),'candidate entry')
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0','e004t_csiphy_readback_test'):need(not Path('/sys/module',m).exists(),'module '+m)
# If prearm material exists, verify exact package and kernel hashes.
if (D/'build').exists():
 expected={'qcom-camss-ir-gated.ko':'862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7','sp11-vd55g0.ko':'4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72','imx681.ko':'ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6','ov13858-production.ko':'13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309'}
 for n,h in expected.items():need(hashlib.sha256((D/'build'/n).read_bytes()).hexdigest()==h,'build '+n)
if (D/'package-root').exists():
 need(hashlib.sha256((D/'package-root/PACKAGE-MANIFEST.sha256').read_bytes()).hexdigest()=='60a3490177ef2befe61a61905160cec7e0b0b4d152fff4ccf5dccd8bca62cc1a','package manifest')
 p=D/'package-root/usr/lib/sp11-front-imx681';need(hashlib.sha256((p/'bin/front-imx681-launcher.py').read_bytes()).hexdigest()=='5583724848f5fc09684a779b90e0a5b4cea4e4cffe2f91859a6332623c1de424','launcher hash')
if (D/'PREARM.txt').exists():need('status=PASS_READY_TO_INSTALL' in (D/'PREARM.txt').read_text(),'prearm')
print('E004ds PREP VERIFY: PASS (accepted front R27 package + IR-gated three-camera kernel authority / front-only stream)')
