#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
A=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gc/attempt1-pass-twentyone-frame-20260911T1941')
GC=BASE/'gc-twentyone-frame-live-r5-r21'
GE=BASE/'ge-r22-r24-continuation-authority'
GF=BASE/'gf-twentyone-generation-gain-feed-publisher'
GA=BASE/'ga-r5-r21-producer-integration'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)

ge=json.loads((GE/'RESULT.json').read_text())
need(ge['status']=='PASS_OFFLINE_R22_R24_COMPOSABLE_AUTHORITY_CLOSED','GE authority')
need(ge['linux_live_r22_plus_allowed'] is True,'GE live gate')
gf=json.loads((GF/'RESULT.json').read_text())
need(gf['status']=='PASS_OFFLINE_G1_G21_C_PUBLISHER','GF authority')
gc=json.loads((GC/'ATTEMPT1-PASS.json').read_text())
need(gc['status']=='PASS_CAPTURE_GC_TWENTYONE_FRAME_R5_R21','GC authority')
need(gc['stream_attempts']==1 and gc['golden_return'] is True and gc['candidate_retired'] is True,'GC closure')

src=(HERE/'live-iq-producer.py').read_text()
parent=(GE/'offline-iq-probe.py').read_text()
need("choices=('offline','live')" in src,'GG live CLI not enabled')
need('for gen in (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21):' in src,'G1..G21 loop')
need('elif gen in (4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21):' in src,'R7..R24 branch')
need("FBFILE=BASE/'fy-calibrated-awb-selector-replay/dynamic_awb.py'" in src,'FY dependency')
normalized=src.replace("choices=('offline','live')","choices=('offline',)")
normalized=normalized.replace("'sp11-e003i-gg-r5-r24-producer-v1'","'sp11-e003i-ge-r5-r24-offline-probe-v1'")
normalized=normalized.replace('E003I_GG_PRODUCER','E003I_GE_OFFLINE_PROBE')
need(normalized==parent,'GG source delta exceeds live enable + identity')
need(sha(HERE/'v4l2-control-shim.c')==sha(GA/'v4l2-control-shim.c'),'V4L2 shim drift')

g={}
for m in re.finditer(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+).*?ISP=0x([0-9a-fA-F]{8})',(A/'runtime-output/RUN.txt').read_text()):
    gen,req,b=m.groups(); gen=int(gen); req=int(req)
    if gen<=21:
        need(req==gen+3,f'gain identity G{gen}')
        g[str(gen)]=f'0x{b.lower()}'
need(set(g)=={str(i) for i in range(1,22)},'GC G1..G21 gains')

with tempfile.TemporaryDirectory(prefix='e003i-gg-snapshot-') as ts:
    snap=Path(ts)/'snapshot'; snap.mkdir()
    for gen in range(1,22):
        for prefix in ('STATS3A','TLBG'):
            sp=A/'runtime-output'/f'{prefix}-{gen-1}.bin'; dp=snap/sp.name
            with dp.open('wb') as f: subprocess.run(['sudo','-n','cat',str(sp)],check=True,stdout=f)
            need(dp.stat().st_size==sp.stat().st_size,f'{prefix} G{gen} size')
    def one(td):
        td=Path(td); out=td/'out'; out.mkdir(); gm=td/'gain.json'; mf=td/'manifest.json'
        gm.write_text(json.dumps({'cq_gain_bits':g})+'\n')
        cp=subprocess.run([str(HERE/'live-iq-producer.py'),'--mode','offline',
                           '--snapshot-dir',str(snap),'--gain-manifest',str(gm),
                           '--output-dir',str(out),'--manifest',str(mf)],
                          text=True,capture_output=True)
        if cp.returncode:
            print(cp.stdout); print(cp.stderr); raise SystemExit(cp.returncode)
        need('E003I_GG_PRODUCER=PASS' in cp.stdout,'GG pass marker')
        m=json.loads(mf.read_text())
        need(m['schema']=='sp11-e003i-gg-r5-r24-producer-v1' and m['status']=='PASS','GG manifest')
        need([(r['generation'],r['request_target']) for r in m['rows']]==[(1,None)]+[(x,x+3) for x in range(2,22)],'mapping')
        return out,m
    with tempfile.TemporaryDirectory(prefix='e003i-gg-a-') as ta, tempfile.TemporaryDirectory(prefix='e003i-gg-b-') as tb:
        oa,ma=one(ta); ob,mb=one(tb); hashes={}
        for req in range(5,22):
            h=sha(oa/f'R{req}-dynamic.bin')
            need(h==sha(A/'runtime-output/producer'/f'R{req}-dynamic.bin'),f'R{req} GC live regression')
            need(h==sha(ob/f'R{req}-dynamic.bin'),f'R{req} deterministic')
            hashes[str(req)]=h
        for req in range(22,25):
            h=sha(oa/f'R{req}-dynamic.bin')
            need(h==ge['r22_r24_capsule_sha256'][str(req)],f'R{req} GE authority')
            need(h==sha(ob/f'R{req}-dynamic.bin'),f'R{req} deterministic')
            hashes[str(req)]=h
        ra={r['request_target']:r for r in ma['rows'] if r['request_target']}
        rb={r['request_target']:r for r in mb['rows'] if r['request_target']}
        for req in range(5,25):
            for k in ('generation','request_target','final_xy_bits','final_cct_bits','published_cct',
                      'awb_calibration_slot','awb_calibration_region','awb_triangle',
                      'awb_published_gain_bits','capsule_sha256'):
                need(ra[req][k]==rb[req][k],f'R{req} deterministic {k}')
        out={
          'schema':'sp11-e003i-gg-r5-r24-producer-integration-v1',
          'status':'PASS_OFFLINE_R5_R24_AUTHORIZED_INTEGRATION',
          'source':'immutable GC G1..G21 paired stats + CQ gain observations',
          'requests':list(range(5,25)),'source_generations':list(range(2,22)),
          'r5_r21_live_regression':'17/17 exact GC live capsule hashes',
          'r22_r24_authority':'GE CLOSED',
          'r22_r24_capsule_sha256':{str(r):hashes[str(r)] for r in range(22,25)},
          'all_capsule_sha256':hashes,
          'gain_publisher':'GF PASS G1..G21 C publisher',
          'producer_source_delta':'GE + live CLI enable + GG identity only',
          'v4l2_control_shim_sha256':sha(HERE/'v4l2-control-shim.c'),
          'live_capable_code_path_preserved':True,'linux_camera_runtime_performed_by_gg':False,
          'continuous_aec_claimed':False}
        (HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('GG_R5_R21_LIVE_REGRESSION=17/17 PASS')
print('GG_R22_R24_GE_AUTHORITY=3/3 PASS')
print('GG_LIVE_PATH_DELTA=PASS')
print('GG_VERIFY=PASS')
