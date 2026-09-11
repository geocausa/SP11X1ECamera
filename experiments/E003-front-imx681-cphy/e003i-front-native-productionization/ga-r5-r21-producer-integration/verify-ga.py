#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
A=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fu/attempt1-pass-eighteen-frame-20260911T1822')
FU=BASE/'fu-eighteen-frame-live-r5-r18'
FV=BASE/'fv-r19-r21-continuation-authority'
FZ=BASE/'fz-eighteen-generation-gain-feed-publisher'
FS=BASE/'fs-r5-r18-producer-integration'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)

fv=json.loads((FV/'RESULT.json').read_text())
need(fv['status']=='PASS_OFFLINE_R19_R21_COMPOSABLE_AUTHORITY_CLOSED','FV authority')
need(fv['linux_live_r19_plus_allowed'] is True,'FV live gate')
fz=json.loads((FZ/'RESULT.json').read_text())
need(fz['status']=='PASS_OFFLINE_G1_G18_C_PUBLISHER','FZ authority')
fu=json.loads((FU/'ATTEMPT1-PASS.json').read_text())
need(fu['status']=='PASS_CAPTURE_FU_EIGHTEEN_FRAME_R5_R18','FU authority')
need(fu['stream_attempts']==1 and fu['golden_return'] is True and fu['candidate_retired'] is True,'FU closure')

src=(HERE/'live-iq-producer.py').read_text()
parent=(FV/'offline-iq-probe.py').read_text()
need("choices=('offline','live')" in src,'GA live CLI not enabled')
need('for gen in (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18):' in src,'G1..G18 producer loop')
need('elif gen in (4,5,6,7,8,9,10,11,12,13,14,15,16,17,18):' in src,'R7..R21 extended branch')
need("FBFILE=BASE/'fy-calibrated-awb-selector-replay/dynamic_awb.py'" in src,'FY selector dependency')
normalized=src.replace("choices=('offline','live')","choices=('offline',)")
normalized=normalized.replace("'sp11-e003i-ga-r5-r21-producer-v1'","'sp11-e003i-fv-r5-r21-offline-probe-v1'")
normalized=normalized.replace('E003I_GA_PRODUCER','E003I_FV_OFFLINE_PROBE')
need(normalized==parent,'GA source delta exceeds live enable + identity')
need(sha(HERE/'v4l2-control-shim.c')==sha(FS/'v4l2-control-shim.c'),'V4L2 shim drift')

g={}
for m in re.finditer(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+).*?ISP=0x([0-9a-fA-F]{8})',(A/'runtime-output/RUN.txt').read_text()):
    gen,req,b=m.groups();gen=int(gen);req=int(req)
    if gen<=18:
        need(req==gen+3,f'gain identity G{gen}')
        g[str(gen)]=f'0x{b.lower()}'
need(set(g)=={str(i) for i in range(1,19)},'FU G1..G18 gains')

with tempfile.TemporaryDirectory(prefix='e003i-ga-snapshot-') as ts:
    snap=Path(ts)/'snapshot';snap.mkdir()
    for gen in range(1,19):
        for prefix in ('STATS3A','TLBG'):
            sp=A/'runtime-output'/f'{prefix}-{gen-1}.bin';dp=snap/sp.name
            with dp.open('wb') as f: subprocess.run(['sudo','-n','cat',str(sp)],check=True,stdout=f)
            need(dp.stat().st_size==sp.stat().st_size,f'{prefix} G{gen} size')
    def one(td):
        td=Path(td);out=td/'out';out.mkdir();gm=td/'gain.json';mf=td/'manifest.json'
        gm.write_text(json.dumps({'cq_gain_bits':g})+'\n')
        cp=subprocess.run([str(HERE/'live-iq-producer.py'),'--mode','offline','--snapshot-dir',str(snap),
                           '--gain-manifest',str(gm),'--output-dir',str(out),'--manifest',str(mf)],
                          text=True,capture_output=True)
        if cp.returncode:
            print(cp.stdout);print(cp.stderr);raise SystemExit(cp.returncode)
        need('E003I_GA_PRODUCER=PASS' in cp.stdout,'GA pass marker')
        m=json.loads(mf.read_text())
        need(m['schema']=='sp11-e003i-ga-r5-r21-producer-v1' and m['status']=='PASS','GA manifest')
        need([(r['generation'],r['request_target']) for r in m['rows']]==[(1,None)]+[(x,x+3) for x in range(2,19)],'mapping')
        return out,m
    with tempfile.TemporaryDirectory(prefix='e003i-ga-a-') as ta, tempfile.TemporaryDirectory(prefix='e003i-ga-b-') as tb:
        oa,ma=one(ta);ob,mb=one(tb)
        hashes={}
        for req in range(5,19):
            h=sha(oa/f'R{req}-dynamic.bin')
            need(h==sha(A/'runtime-output/producer'/f'R{req}-dynamic.bin'),f'R{req} FU live regression')
            need(h==sha(ob/f'R{req}-dynamic.bin'),f'R{req} deterministic')
            hashes[str(req)]=h
        for req in range(19,22):
            h=sha(oa/f'R{req}-dynamic.bin')
            need(h==fv['r19_r21_capsule_sha256'][str(req)],f'R{req} FV authority')
            need(h==sha(ob/f'R{req}-dynamic.bin'),f'R{req} deterministic')
            hashes[str(req)]=h
        ra={r['request_target']:r for r in ma['rows'] if r['request_target']}
        rb={r['request_target']:r for r in mb['rows'] if r['request_target']}
        for req in range(5,22):
            for k in ('generation','request_target','final_xy_bits','final_cct_bits','published_cct',
                      'awb_calibration_slot','awb_calibration_region','awb_triangle',
                      'awb_published_gain_bits','capsule_sha256'):
                need(ra[req][k]==rb[req][k],f'R{req} deterministic {k}')
        out={
          'schema':'sp11-e003i-ga-r5-r21-producer-integration-v1',
          'status':'PASS_OFFLINE_R5_R21_AUTHORIZED_INTEGRATION',
          'source':'immutable FU G1..G18 paired stats + CQ gains',
          'requests':list(range(5,22)),
          'source_generations':list(range(2,19)),
          'r5_r18_live_regression':'14/14 exact FU live capsule hashes',
          'r19_r21_authority':'FV CLOSED',
          'r19_r21_capsule_sha256':{str(r):hashes[str(r)] for r in range(19,22)},
          'all_capsule_sha256':hashes,
          'gain_publisher':'FZ PASS G1..G18 C publisher',
          'producer_source_delta':'FV + live CLI enable + GA identity only',
          'v4l2_control_shim_sha256':sha(HERE/'v4l2-control-shim.c'),
          'live_capable_code_path_preserved':True,
          'linux_camera_runtime_performed_by_ga':False,
          'continuous_aec_claimed':False,
        }
        (HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('GA_R5_R18_LIVE_REGRESSION=14/14 PASS')
print('GA_R19_R21_FV_AUTHORITY=3/3 PASS')
print('GA_LIVE_PATH_DELTA=PASS')
print('GA_VERIFY=PASS')
