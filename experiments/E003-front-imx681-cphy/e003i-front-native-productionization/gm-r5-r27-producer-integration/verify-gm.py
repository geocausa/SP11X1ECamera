#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,tempfile
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
A=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gi/attempt1-pass-twentyfour-frame-20260911T2035')
GI=BASE/'gi-twentyfour-frame-live-r5-r24'
GK=BASE/'gk-r25-r27-continuation-authority'
GL=BASE/'gl-twentyfour-generation-gain-feed-publisher'
GG=BASE/'gg-r5-r24-producer-integration'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)

gk=json.loads((GK/'RESULT.json').read_text())
need(gk['status']=='PASS_OFFLINE_R25_R27_COMPOSABLE_AUTHORITY_CLOSED','GK authority')
need(gk['linux_live_r25_plus_allowed'] is True,'GK live gate')
gl=json.loads((GL/'RESULT.json').read_text())
need(gl['status']=='PASS_OFFLINE_G1_G24_C_PUBLISHER','GL authority')
gi=json.loads((GI/'ATTEMPT1-PASS.json').read_text())
need(gi['status']=='PASS_CAPTURE_GI_TWENTYFOUR_FRAME_R5_R24','GI authority')
need(gi['stream_attempts']==1 and gi['golden_return'] is True and gi['candidate_retired'] is True,'GI closure')

src=(HERE/'live-iq-producer.py').read_text(); parent=(GK/'offline-iq-probe.py').read_text()
need("choices=('offline','live')" in src,'GM live CLI not enabled')
need('for gen in (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24):' in src,'G1..G24 loop')
need('elif gen in (4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24):' in src,'R7..R27 branch')
normalized=src.replace("choices=('offline','live')","choices=('offline',)")
normalized=normalized.replace("'sp11-e003i-gm-r5-r27-producer-v1'","'sp11-e003i-gk-r5-r27-offline-probe-v1'")
normalized=normalized.replace('E003I_GM_PRODUCER','E003I_GK_OFFLINE_PROBE')
need(normalized==parent,'GM source delta exceeds live enable + identity')
need(sha(HERE/'v4l2-control-shim.c')==sha(GG/'v4l2-control-shim.c'),'V4L2 shim drift')

g={}
for m in re.finditer(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+).*?ISP=0x([0-9a-fA-F]{8})',(A/'runtime-output/RUN.txt').read_text()):
    gen,req,b=m.groups(); gen=int(gen); req=int(req)
    if gen<=24:
        need(req==gen+3,f'gain identity G{gen}')
        g[str(gen)]=f'0x{b.lower()}'
need(set(g)=={str(i) for i in range(1,25)},'GI G1..G24 gains')

with tempfile.TemporaryDirectory(prefix='e003i-gm-snapshot-') as ts:
    snap=Path(ts)/'snapshot'; snap.mkdir()
    for gen in range(1,25):
        for prefix in ('STATS3A','TLBG'):
            sp=A/'runtime-output'/f'{prefix}-{gen-1}.bin'; dp=snap/sp.name
            with dp.open('wb') as f: subprocess.run(['sudo','-n','cat',str(sp)],check=True,stdout=f)
            need(dp.stat().st_size==sp.stat().st_size,f'{prefix} G{gen} size')
    def one(td):
        td=Path(td); out=td/'out'; out.mkdir(); gm=td/'gain.json'; mf=td/'manifest.json'
        gm.write_text(json.dumps({'cq_gain_bits':g})+'\n')
        cp=subprocess.run([str(HERE/'live-iq-producer.py'),'--mode','offline','--snapshot-dir',str(snap),
                           '--gain-manifest',str(gm),'--output-dir',str(out),'--manifest',str(mf)],
                          text=True,capture_output=True)
        if cp.returncode:
            print(cp.stdout); print(cp.stderr); raise SystemExit(cp.returncode)
        need('E003I_GM_PRODUCER=PASS' in cp.stdout,'GM pass marker')
        m=json.loads(mf.read_text())
        need(m['schema']=='sp11-e003i-gm-r5-r27-producer-v1' and m['status']=='PASS','GM manifest')
        need([(r['generation'],r['request_target']) for r in m['rows']]==[(1,None)]+[(x,x+3) for x in range(2,25)],'mapping')
        return out,m
    with tempfile.TemporaryDirectory(prefix='e003i-gm-a-') as ta, tempfile.TemporaryDirectory(prefix='e003i-gm-b-') as tb:
        oa,ma=one(ta); ob,mb=one(tb); hashes={}
        for req in range(5,25):
            h=sha(oa/f'R{req}-dynamic.bin')
            need(h==sha(A/'runtime-output/producer'/f'R{req}-dynamic.bin'),f'R{req} GI live regression')
            need(h==sha(ob/f'R{req}-dynamic.bin'),f'R{req} deterministic')
            hashes[str(req)]=h
        for req in range(25,28):
            h=sha(oa/f'R{req}-dynamic.bin')
            need(h==gk['r25_r27_capsule_sha256'][str(req)],f'R{req} GK authority')
            need(h==sha(ob/f'R{req}-dynamic.bin'),f'R{req} deterministic')
            hashes[str(req)]=h
        ra={r['request_target']:r for r in ma['rows'] if r['request_target']}
        rb={r['request_target']:r for r in mb['rows'] if r['request_target']}
        for req in range(5,28):
            for k in ('generation','request_target','final_xy_bits','final_cct_bits','published_cct',
                      'awb_calibration_slot','awb_calibration_region','awb_triangle','awb_published_gain_bits','capsule_sha256'):
                need(ra[req][k]==rb[req][k],f'R{req} deterministic {k}')
        result={
          'schema':'sp11-e003i-gm-r5-r27-producer-integration-v1',
          'status':'PASS_OFFLINE_R5_R27_AUTHORIZED_INTEGRATION',
          'source':'immutable GI G1..G24 paired stats + CQ gain observations',
          'requests':list(range(5,28)),'source_generations':list(range(2,25)),
          'r5_r24_live_regression':'20/20 exact GI live capsule hashes',
          'r25_r27_authority':'GK CLOSED',
          'r25_r27_capsule_sha256':{str(r):hashes[str(r)] for r in range(25,28)},
          'all_capsule_sha256':hashes,
          'gain_publisher':'GL PASS G1..G24 C publisher',
          'producer_source_delta':'GK + live CLI enable + GM identity only',
          'v4l2_control_shim_sha256':sha(HERE/'v4l2-control-shim.c'),
          'live_capable_code_path_preserved':True,'linux_camera_runtime_performed_by_gm':False,
          'continuous_aec_claimed':False}
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('GM_R5_R24_LIVE_REGRESSION=20/20 PASS')
print('GM_R25_R27_GK_AUTHORITY=3/3 PASS')
print('GM_LIVE_PATH_DELTA=PASS')
print('GM_VERIFY=PASS')
