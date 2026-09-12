#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,re,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
IQ=REPO/'src/front-imx681/userspace/iq'
VENDOR=IQ/'vendor'
GM=BASE/'gm-r5-r27-producer-integration'
HF=BASE/'hf-stable-front-imx681-source-bundle'
GI_ARCH=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gi/attempt1-pass-twentyfour-frame-20260911T2035')
TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
# Parent authority.
need(json.loads((HF/'RESULT.json').read_text())['status']=='PASS_OFFLINE_STABLE_FRONT_IMX681_SOURCE_BUNDLE','HF')
# Stable producer differs from GM only in root/path bindings.
s=(IQ/'live-iq-producer.py').read_text(); gm=(GM/'live-iq-producer.py').read_text()
new="HERE=pathlib.Path(__file__).resolve().parent\nVENDOR=HERE/'vendor'\nBASE=VENDOR/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization'\nREPO=VENDOR\n"
old="HERE=pathlib.Path(__file__).resolve().parent\nBASE=HERE.parent\nREPO=HERE.parents[3]\n"
need(s.count(new)==1,'stable path block')
need(s.replace(new,old,1)==gm,'stable producer algorithm drift')
need(sha(IQ/'v4l2-control-shim.c')==sha(GM/'v4l2-control-shim.c'),'V4L2 shim drift')
# Vendor source closure / cache contract.
vp=json.loads((IQ/'VENDOR-SOURCE-PROVENANCE.json').read_text());need(vp['file_count']==23 and vp['patched_file_count']==6,'vendor provenance shape')
for r in vp['files']:
    need((VENDOR/r['path']).is_file(),'vendor source '+r['path'])
    need(sha(VENDOR/r['path'])==r['vendor_sha256'],'vendor hash '+r['path'])
    if r['relocation_patch'] is None: need(r['byte_exact'] is True,'unpatched source drift '+r['path'])
cache=json.loads((IQ/'AUTHORITY-CACHE-MANIFEST.json').read_text());need(cache['repo_entry_count']==79 and cache['external_entry_count']==1,'cache manifest shape')
marker=VENDOR/'local-authority/PREPARED.json';need(marker.is_file(),'authority cache not prepared')
pm=json.loads(marker.read_text());need(pm['status']=='PASS' and pm['manifest_sha256']==sha(IQ/'AUTHORITY-CACHE-MANIFEST.json'),'cache marker')
# No runtime data/proprietary cache is tracked in vendor: only source + .gitignore.
tracked=subprocess.check_output(['git','ls-files',str(VENDOR.relative_to(REPO))],cwd=REPO,text=True).splitlines()
allowed={'.py','.c'}
for f in tracked:
    p=Path(f)
    if p.name=='.gitignore': continue
    need(p.suffix in allowed,'unexpected tracked vendor data '+f)
# Snapshot GI inputs and gain feed once, then run stable producer independently twice.
runtext=(GI_ARCH/'runtime-output/RUN.txt').read_text(); gains={}
for m in re.finditer(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+).*?ISP=0x([0-9a-fA-F]{8})',runtext):
    gen,req,b=m.groups();gen=int(gen);req=int(req)
    if gen<=24:
        need(req==gen+3,f'gain identity G{gen}');gains[str(gen)]=f'0x{b.lower()}'
need(set(gains)=={str(i) for i in range(1,25)},'G1..G24 gains')
expected=json.loads((GM/'RESULT.json').read_text())['all_capsule_sha256']
with tempfile.TemporaryDirectory(prefix='e003i-hg-') as td0:
    td=Path(td0);snap=td/'snapshot';snap.mkdir()
    for gen in range(1,25):
        for prefix in ('STATS3A','TLBG'):
            src=GI_ARCH/'runtime-output'/f'{prefix}-{gen-1}.bin';dst=snap/src.name
            with dst.open('wb') as f: subprocess.run(['sudo','-n','cat',str(src)],check=True,stdout=f)
    gmfile=td/'gain.json';gmfile.write_text(json.dumps({'cq_gain_bits':gains})+'\n')
    def one(name,trace=False):
        out=td/name;out.mkdir();manifest=td/f'{name}.json';cmd=[str(IQ/'live-iq-producer.py'),'--mode','offline','--snapshot-dir',str(snap),'--gain-manifest',str(gmfile),'--output-dir',str(out),'--manifest',str(manifest)]
        tr=td/f'{name}.strace'
        if trace: cmd=['strace','-f','-e','trace=openat','-o',str(tr),*cmd]
        cp=subprocess.run(cmd,text=True,capture_output=True)
        if cp.returncode:
            print(cp.stdout);print(cp.stderr);raise SystemExit(cp.returncode)
        need('E003I_GM_PRODUCER=PASS' in cp.stdout,'producer pass marker')
        hashes={str(req):sha(out/f'R{req}-dynamic.bin') for req in range(5,28)}
        need(hashes==expected,f'{name} capsule authority')
        return out,json.loads(manifest.read_text()),tr
    oa,ma,_=one('run-a');ob,mb,tr=one('run-b',trace=True)
    for req in range(5,28): need((oa/f'R{req}-dynamic.bin').read_bytes()==(ob/f'R{req}-dynamic.bin').read_bytes(),f'R{req} deterministic')
    ra={r['request_target']:r for r in ma['rows'] if r['request_target']};rb={r['request_target']:r for r in mb['rows'] if r['request_target']}
    for req in range(5,28):
        for k in ('generation','request_target','final_xy_bits','final_cct_bits','published_cct','awb_calibration_slot','awb_calibration_region','awb_triangle','awb_published_gain_bits','capsule_sha256'):
            need(ra[req][k]==rb[req][k],f'R{req} deterministic {k}')
    # Hermetic runtime path proof: project-local opens must remain inside stable IQ root.
    bad=[];dev=[]
    rx=re.compile(r'openat\([^,]+, "([^"]+)"[^=]*=\s*(-?\d+)')
    for line in tr.read_text(errors='replace').splitlines():
        m=rx.search(line)
        if not m or int(m.group(2))<0:continue
        p=m.group(1)
        if p.startswith('/dev/video') or p.startswith('/dev/media'):dev.append(p)
        if p.startswith('/home/geoca/Documents/SP11-PROJECT/') and not p.startswith(str(IQ.resolve())):bad.append(p)
    need(not bad,'runtime escaped stable IQ root: '+repr(sorted(set(bad))))
    need(not dev,'offline verifier opened camera devices')
result={
 'schema':'sp11-e003i-hg-hermetic-iq-producer-relocation-v1',
 'status':'PASS_OFFLINE_RELOCATABLE_IQ_RUNTIME_WITH_LOCAL_AUTHORITY_CACHE',
 'parent':'HF stable front IMX681 source bundle',
 'stable_iq_root':'src/front-imx681/userspace/iq',
 'vendor_source_files':23,'vendor_path_only_patched_files':6,
 'authority_cache':{'repo_entries':79,'external_entries':1,'manifest_sha256':sha(IQ/'AUTHORITY-CACHE-MANIFEST.json'),'proprietary_tuning_committed':False,'cache_committed':False},
 'regression':{'R5_R27_capsules_byte_exact':23,'independent_runs':2,'deterministic':True,'GM_authority_match':True},
 'runtime_path_closure':{'project_local_opens_outside_stable_iq_root':0,'camera_device_opens':0,'pass':True},
 'stable_producer_algorithm_delta':'GM path binding only',
 'v4l2_control_shim_byte_exact_GM':True,
 'camera_runtime_performed':False,
 'production_native_changed_post_g3_feedback_proven':False,
 'scope_limit':'runtime is path-hermetic after authority-cache provisioning; the cache still contains the SHA-pinned local proprietary tuning blob and other local oracle data and is intentionally ignored/not committed',
 'next_gate':'HH reduce local authority cache to clean-room redistributable runtime assets, then production launcher/device discovery',
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HG_R5_R27_BYTE_EXACT=23/23 PASS')
print('HG_INDEPENDENT_RUNS=2 DETERMINISTIC=PASS')
print('HG_RUNTIME_PATH_CLOSURE=PASS')
print('HG_PROPRIETARY_CACHE_TRACKED=NO')
print('HG_CAMERA_RUNTIME=NO')
print('HG_VERIFY=PASS')
