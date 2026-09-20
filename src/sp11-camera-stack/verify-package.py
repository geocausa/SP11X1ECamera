#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,json,subprocess
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v:raise AssertionError(m)
ap=argparse.ArgumentParser();ap.add_argument('root',type=Path);ap.add_argument('--require-r4',action='store_true',help='require front RGB production R4 bootstrap sidecar');a=ap.parse_args();r=a.root
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
 front/'build/front-imx681-capture':'4735e81c25c3feff6f595480296e54da358622603c5e711cdabff3caddcd9934',
 front/'build/front-imx681-bootstrap-controls':'4721ff6510d806ed63ffcb70d9a88441220047ef734ca760cc40bdc5719cd7ce'}
for p,h in expected.items():need(p.is_file() and sha(p)==h,str(p))
prov=json.loads((meta/'PROVENANCE.json').read_text());need(prov['modules']['qcom_camss_sha256']==expected[hw/'modules/qcom-camss.ko'],'meta provenance')
need((r/'usr/bin/sp11-front-imx681').is_file() and (r/'usr/bin/sp11-front-imx681-discover').is_file(),'front wrappers')
need((r/'FRONT-PACKAGE-MANIFEST.sha256').is_file(),'front manifest')
if a.require_r4:
    # Historical 50-file packages did not include this ignored capsule.
    # All NEW production front RGB builds must contain it and name it in
    # BOTH independently generated package manifests.
    from stat import S_IMODE
    r4rel='usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin'
    r4=r/r4rel
    r4sha='1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa'
    need(r4.is_file() and not r4.is_symlink() and r4.stat().st_size==41088 and sha(r4)==r4sha,'R4 bootstrap not present or checksum drift')
    need(S_IMODE(r4.stat().st_mode)==0o600,'R4 capsule sidecar requires mode 0600')
    m=json.loads((front/'userspace/iq/authority/r4-bootstrap.json').read_text())
    need(m['bytes']==41088 and m['sha256']==r4sha and
         m['derived_normalized_capsule'] is True and
         m['raw_request_slot'] is False,'R4 provenance metadata drift')
    def named_manifest(name):
        rows=(r/name).read_text().splitlines()
        need(rows and all(len(x)>=67 and x[64:66]=='  ' for x in rows),'manifest format '+name)
        names=[x[66:] for x in rows]
        need(len(names)==len(set(names)),'duplicate manifest paths '+name)
        need(any(x[:64]==r4sha and x[66:]==r4rel for x in rows),'R4 omitted from '+name)
        return set(names)
    all_paths=named_manifest('CAMERA-STACK-MANIFEST.sha256')
    front_paths=named_manifest('FRONT-PACKAGE-MANIFEST.sha256')
    usr=r/'usr'
    need(all(not f.is_symlink() for f in usr.rglob('*')),'symlink in staged package')
    need(all_paths=={str(x.relative_to(r)) for x in usr.rglob('*') if x.is_file()},
         'package contains file omitted from full manifest')
    need(r4rel in front_paths,'R4 missing from front manifest')
print('SP11 CAMERA STACK PACKAGE VERIFY: PASS ACTIVATED=NO')
