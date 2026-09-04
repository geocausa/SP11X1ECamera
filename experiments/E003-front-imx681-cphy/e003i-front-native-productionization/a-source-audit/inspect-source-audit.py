#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess,tempfile,shutil,sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
G=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-repro/src')
C=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003h-0074-camss-build')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
a=json.loads((HERE/'SOURCE-AUDIT.json').read_text())
assert a['accepted'] is True
assert len(a['camss_0074_oracle']['changed_files'])==14
for e in a['camss_0074_oracle']['changed_files']:
    g=G/'drivers/media/platform/qcom/camss'/e['file']; c=C/e['file']
    assert sha(g)==e['golden_sha256'], ('Golden drift',e['file'])
    assert sha(c)==e['oracle_0074_sha256'], ('0074 drift',e['file'])
imx=REPO/a['imx681_0054_oracle']['source_path']
assert sha(imx)==a['imx681_0054_oracle']['source_sha256']
front=REPO/a['dtb_oracles']['front_0074']['path']
assert sha(front)==a['dtb_oracles']['front_0074']['sha256']
for k in ('golden','rear_r3'):
    assert sha(a['dtb_oracles'][k]['path'])==a['dtb_oracles'][k]['sha256']
# Replay exact CAMSS oracle patch on only the touched Golden files.
with tempfile.TemporaryDirectory(prefix='e003i-audit-') as td:
    root=Path(td)
    dst=root/'drivers/media/platform/qcom/camss'; dst.mkdir(parents=True)
    for e in a['camss_0074_oracle']['changed_files']:
        shutil.copy2(G/'drivers/media/platform/qcom/camss'/e['file'],dst/e['file'])
    r=subprocess.run(['patch','--fuzz=0','-p1','-i',str(HERE/'0074-golden-camss-oracle.patch')],cwd=root,text=True,capture_output=True)
    assert r.returncode==0, r.stdout+r.stderr
    for e in a['camss_0074_oracle']['changed_files']:
        assert sha(dst/e['file'])==e['oracle_0074_sha256'], ('replay mismatch',e['file'])
d=json.loads((HERE/'DT-MERGE-CONTRACT.json').read_text())
assert d['rear']['enabled'] and d['front']['enabled']
assert d['camss_union']['ports']==[1,2]
print('E003I_SOURCE_AUDIT=PASS')
print('CAMSS_ORACLE_FILES=14')
print('DUAL_CAMERA_PORTS=1,2')
print('RUNTIME_AUTHORIZED=false')
