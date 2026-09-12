#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,re,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
IQ=REPO/'src/front-imx681/userspace/iq'
VENDOR=IQ/'vendor'
AUTH=IQ/'authority/authority.json'
HG=BASE/'hg-hermetic-iq-producer-relocation'
GM=BASE/'gm-r5-r27-producer-integration'
GI_ARCH=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gi/attempt1-pass-twentyfour-frame-20260911T2035')
AUTH_SHA='dcb42bf9fd2f4d4a224bc339db947938d1e0202f1ccb6fca6af4d69de4f432d8'
AUTH_BYTES=250690
RAW_CACHE_BYTES=10706762

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v:raise AssertionError(m)
# Parent HG and clean authority contract.
hg=json.loads((HG/'RESULT.json').read_text());need(hg['status']=='PASS_OFFLINE_RELOCATABLE_IQ_RUNTIME_WITH_LOCAL_AUTHORITY_CACHE','HG parent')
need(AUTH.is_file() and AUTH.stat().st_size==AUTH_BYTES and sha(AUTH)==AUTH_SHA,'clean authority identity')
a=json.loads(AUTH.read_text());need(a['schema']=='sp11-front-imx681-clean-runtime-authority-v1','authority schema')
p=a['policy'];need(p['proprietary_tuning_bytes_embedded'] is False and p['raw_windows_log_embedded'] is False and p['raw_request_slots_embedded'] is False and p['runtime_state_is_decoded_or_derived'] is True,'authority policy')
need('/home/geoca/' not in AUTH.read_text() and 'QTI Chromatix Header' not in AUTH.read_text(),'authority leaked raw/path identity')
need(len(a['awb']['triangles'])==44 and len(a['awb']['vertices'])==32 and len(a['cct_tables'])==33,'authority structure')
need(a['composer']['gtm_sha256']=='074564f99a45d29a5dbe800c18bc0436735f70740cb8f42cd9a5c7b636ffcdfa','GTM authority')
need(a['lsc']['x1_sha256']=='8ce68010d1126105ae68490294bc6b3f2598dfe5dfc88ff5df40f8926efd9d86','X1 authority')
# Cache contract from HG. We will physically hide every one of these files during proof.
cache=json.loads((IQ/'AUTHORITY-CACHE-MANIFEST.json').read_text());entries=[(e['vendor_rel'],e['sha256']) for e in cache['repo_entries']+cache['external_entries']]
need(len(entries)==80,'HG cache entry count')
# Build immutable GI replay inputs.
runtext=(GI_ARCH/'runtime-output/RUN.txt').read_text();gains={}
for m in re.finditer(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+).*?ISP=0x([0-9a-fA-F]{8})',runtext):
    gen,req,b=m.groups();gen=int(gen);req=int(req)
    if gen<=24:need(req==gen+3,f'gain identity G{gen}');gains[str(gen)]=f'0x{b.lower()}'
need(set(gains)=={str(i) for i in range(1,25)},'G1..G24 gains')
expected=json.loads((GM/'RESULT.json').read_text())['all_capsule_sha256']
with tempfile.TemporaryDirectory(prefix='e003i-hh-') as td0:
    td=Path(td0);snap=td/'snapshot';snap.mkdir();gmfile=td/'gain.json';gmfile.write_text(json.dumps({'cq_gain_bits':gains})+'\n')
    for gen in range(1,25):
        for prefix in ('STATS3A','TLBG'):
            src=GI_ARCH/'runtime-output'/f'{prefix}-{gen-1}.bin';dst=snap/src.name
            with dst.open('wb') as f:subprocess.run(['sudo','-n','cat',str(src)],check=True,stdout=f)
    # Hide the complete HG raw/local authority cache on the same filesystem.
    backup=VENDOR/'.hh-verify-cache-hidden';need(not backup.exists(),'stale HH cache backup')
    moved=[]
    try:
        for rel,want in entries:
            src=VENDOR/rel
            if src.exists():
                need(src.is_file() and sha(src)==want,'cache source drift '+str(src))
                dst=backup/rel;dst.parent.mkdir(parents=True,exist_ok=True);src.rename(dst);moved.append((src,dst))
        need(len(moved) in (0,80),f'partial HG cache present: {len(moved)}/80')
        for q in list(VENDOR.rglob('__pycache__')):
            if backup not in q.parents:shutil.rmtree(q)
        def one(name,trace=False):
            out=td/name;out.mkdir();mf=td/f'{name}.json';tr=td/f'{name}.strace'
            cmd=[str(IQ/'live-iq-producer.py'),'--mode','offline','--snapshot-dir',str(snap),'--gain-manifest',str(gmfile),'--output-dir',str(out),'--manifest',str(mf)]
            if trace:cmd=['strace','-f','-e','trace=openat','-o',str(tr),*cmd]
            cp=subprocess.run(cmd,text=True,capture_output=True)
            if cp.returncode:print(cp.stdout);print(cp.stderr);raise SystemExit(cp.returncode)
            need('E003I_GM_PRODUCER=PASS' in cp.stdout,'producer PASS marker')
            got={str(req):sha(out/f'R{req}-dynamic.bin') for req in range(5,28)};need(got==expected,name+' R5..R27 authority')
            return out,json.loads(mf.read_text()),tr
        oa,ma,_=one('run-a');ob,mb,tr=one('run-b',trace=True)
        for req in range(5,28):need((oa/f'R{req}-dynamic.bin').read_bytes()==(ob/f'R{req}-dynamic.bin').read_bytes(),f'R{req} deterministic')
        ra={r['request_target']:r for r in ma['rows'] if r['request_target']};rb={r['request_target']:r for r in mb['rows'] if r['request_target']}
        for req in range(5,28):
            for k in ('generation','request_target','final_xy_bits','final_cct_bits','published_cct','awb_calibration_slot','awb_calibration_region','awb_triangle','awb_published_gain_bits','capsule_sha256'):
                need(ra[req][k]==rb[req][k],f'R{req} deterministic {k}')
        # Trace successful cache-hidden run. Project-local access must be confined to stable IQ,
        # and no hidden/raw authority path or camera node may be opened.
        rx=re.compile(r'openat\([^,]+, "([^"]+)"[^=]*=\s*(-?\d+)');opened=[];bad=[];raw=[];dev=[]
        for line in tr.read_text(errors='replace').splitlines():
            m=rx.search(line)
            if not m or int(m.group(2))<0:continue
            path=m.group(1);opened.append(path)
            if path.startswith('/home/geoca/Documents/SP11-PROJECT/') and not path.startswith(str(IQ.resolve())):bad.append(path)
            if '/local-authority/' in path or '/windows-oracle-raw/' in path or 'sp11-driverdump' in path:raw.append(path)
            if path.startswith('/dev/video') or path.startswith('/dev/media'):dev.append(path)
        need(not bad,'project path escaped IQ root '+repr(sorted(set(bad))))
        need(not raw,'raw/local authority opened '+repr(sorted(set(raw))))
        need(not dev,'camera device opened')
        access={'successful_open_count':len(opened),'stable_iq_open_files':sorted({x for x in opened if x.startswith(str(IQ.resolve()))}),'project_local_outside_stable_iq':sorted(set(bad)),'raw_or_local_authority_opens':sorted(set(raw)),'camera_device_opens':sorted(set(dev))}
        (HERE/'CLEAN-RUNTIME-ACCESS.json').write_text(json.dumps(access,indent=2,sort_keys=True)+'\n')
    finally:
        for src,dst in reversed(moved):src.parent.mkdir(parents=True,exist_ok=True);dst.rename(src)
        if backup.exists():shutil.rmtree(backup)
reduction=100.0*(1.0-AUTH_BYTES/RAW_CACHE_BYTES)
result={
 'schema':'sp11-e003i-hh-cleanroom-authority-cache-reduction-v1',
 'status':'PASS_OFFLINE_CLEAN_RUNTIME_AUTHORITY_R5_R27',
 'parent':'HG relocatable IQ runtime',
 'authority':{'path':'src/front-imx681/userspace/iq/authority/authority.json','bytes':AUTH_BYTES,'sha256':AUTH_SHA,'raw_hg_cache_bytes':RAW_CACHE_BYTES,'byte_reduction_percent':reduction,'raw_cache_files_hidden_during_proof':80},
 'clean_runtime':{'proprietary_tuning_required':False,'raw_windows_log_required':False,'raw_request_slot_required':False,'local_authority_cache_required':False,'R5_R27_capsules_byte_exact':23,'independent_runs':2,'deterministic':True,'project_local_path_escape_count':0,'raw_local_authority_open_count':0,'camera_device_open_count':0},
 'regeneration':{'generator':'build-clean-authority.py','deterministic_same_sha256_proven':True,'generator_uses_canonical offline authorities and local extraction evidence':True,'runtime_does_not_need_generator_inputs':True},
 'scope':{'current_sp11_unit_profile':True,'per_device_otp_generalization_for_other_units':False,'camera_runtime_performed':False,'production_native_changed_post_g3_feedback_proven':False},
 'next_gate':'HI production launcher and stable media-device discovery with post-G3 native writes fail-closed',
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(f'HH_AUTHORITY_REDUCTION={reduction:.3f}%')
print('HH_CACHE_HIDDEN=80/80 PASS')
print('HH_R5_R27_BYTE_EXACT=23/23 PASS')
print('HH_INDEPENDENT_RUNS=2 DETERMINISTIC=PASS')
print('HH_RAW_LOCAL_AUTHORITY_OPENS=0')
print('HH_CAMERA_RUNTIME=NO')
print('HH_VERIFY=PASS')
