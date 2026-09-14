#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,json,subprocess
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v:raise AssertionError(m)
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);a=ap.parse_args();r=a.root
need((r/'CAMERA-STACK-MANIFEST.sha256').is_file(),'stack manifest')
cp=subprocess.run(['sha256sum','-c','CAMERA-STACK-MANIFEST.sha256'],cwd=r,text=True,capture_output=True);need(cp.returncode==0,cp.stdout+cp.stderr)
front=r/'usr/lib/sp11-front-imx681';hw=r/'usr/lib/sp11-camera-stack/hardware';meta=r/'usr/lib/sp11-camera-stack/meta'
expected={
 hw/'dtb/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb':'3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb',
 hw/'modules/qcom-camss.ko':'862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7',
 hw/'modules/imx681.ko':'ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6',
 hw/'modules/ov13858.ko':'13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309',
 hw/'modules/sp11-vd55g0.ko':'4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72',
 front/'build/qcom-camss.ko':'862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7',
 front/'build/imx681.ko':'ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6',
 front/'build/front-imx681-capture':'70f407f5fd70e6657f9647a33eecde744ac9e1bd19fa9e901a4faf52508e354d',
 front/'build/front-imx681-bootstrap-controls':'4721ff6510d806ed63ffcb70d9a88441220047ef734ca760cc40bdc5719cd7ce'}
for p,h in expected.items():need(p.is_file() and sha(p)==h,str(p))
prov=json.loads((meta/'PROVENANCE.json').read_text());need(prov['modules']['qcom_camss_sha256']==expected[hw/'modules/qcom-camss.ko'],'meta provenance')
need((r/'usr/bin/sp11-front-imx681').is_file() and (r/'usr/bin/sp11-front-imx681-discover').is_file(),'front wrappers')
need((r/'FRONT-PACKAGE-MANIFEST.sha256').is_file(),'front manifest')
print('SP11 CAMERA STACK PACKAGE VERIFY: PASS ACTIVATED=NO')
