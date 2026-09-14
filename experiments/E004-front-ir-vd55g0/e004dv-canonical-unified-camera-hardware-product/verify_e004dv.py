#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
D=Path(__file__).resolve().parent;R=D.parents[2]
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
r=json.loads((D/'RESULT.json').read_text())
need(r['status']=='PASS_CANONICAL_UNIFIED_THREE_CAMERA_HARDWARE_AUTHORITY_EXACT','status')
subprocess.run(['python3',str(R/'src/sp11-camera-stack/verify-source.py')],check=True,stdout=subprocess.DEVNULL)
manifest=D/'evidence/HARDWARE-MANIFEST.sha256'
need(sha(manifest)=='3b84ddcbb5728d04ea0e86d8ae066e1b4436e0f707afca1c4f7fb00e0e4ba140','manifest file hash')
lines={x.split(None,1)[1]:x.split(None,1)[0] for x in manifest.read_text().splitlines() if x.strip()}
expected={
 'bin/front-imx681-bootstrap-controls':'4721ff6510d806ed63ffcb70d9a88441220047ef734ca760cc40bdc5719cd7ce',
 'bin/front-imx681-capture':'70f407f5fd70e6657f9647a33eecde744ac9e1bd19fa9e901a4faf52508e354d',
 'dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb':'3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb',
 'modules/imx681.ko':'ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6',
 'modules/ov13858.ko':'13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309',
 'modules/qcom-camss.ko':'862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7',
 'modules/sp11-vd55g0.ko':'4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72'}
need(lines==expected,'manifest content')
build=(D/'evidence/BUILD.txt').read_text();need('SP11_CAMERA_HARDWARE_AUTHORITY=PASS THREE_SENSORS=YES SECUREISP=NO' in build,'build marker')
for rel,status in (
 ('e004dp-unified-rgb-ir-receiver-coexistence','PASS_THREE_CAMERA_BIND_CSIPHY0_WINDOWS_96_OF_96_GOLDEN_RETURN_RETIRED'),
 ('e004dr-unified-rgb-ir-rear-regression-r2','PASS_REAR_RGB_UNDER_THREE_CAMERA_AUTHORITY_GOLDEN_RETURN_RETIRED'),
 ('e004ds-unified-rgb-ir-front-regression','PASS_FRONT_RGB_UNDER_THREE_CAMERA_AUTHORITY_GOLDEN_RETURN_RETIRED')):
    j=json.loads((R/'experiments/E004-front-ir-vd55g0'/rel/'RESULT.json').read_text());need(j['status']==status,rel)
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'current Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0'):need(not Path('/sys/module',m).exists(),'loaded '+m)
print('E004dv VERIFY: PASS (canonical unified three-camera hardware authority exact)')
