#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,tempfile
HERE=Path(__file__).resolve().parent;BASE=HERE.parent
FF=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-ff/attempt1-pass-twelve-frame-20260911T1630/runtime-output')
FJ=BASE/'fj-r13-r15-content-authority-join'/'RESULT.json'
FK=BASE/'fk-twelve-generation-gain-feed-publisher'/'RESULT.json'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(c,**kw): return subprocess.run(c,check=True,text=True,**kw)

fj=json.loads(FJ.read_text());need(fj['status']=='PASS_OFFLINE_R13_R15_CONTENT_AUTHORIZED','FJ authority')
fk=json.loads(FK.read_text());need(fk['status']=='PASS_OFFLINE_G1_G12_C_PUBLISHER','FK authority')
ffp=json.loads((FF/'producer/RESULT.json').read_text());need(ffp['status']=='PASS','FF producer authority')
need([(r['generation'],r['request_target']) for r in ffp['rows']]==[(1,None),(2,5),(3,6),(4,7),(5,8),(6,9),(7,10),(8,11),(9,12)],'FF rows')

src=(HERE/'live-iq-producer.py').read_text()
for tok in ("choices=('offline','live')",'configure_live_scheduler','LiveControl','GainFeed','elif gen in (4,5,6,7,8,9,10,11,12):','for gen in (1,2,3,4,5,6,7,8,9,10,11,12):'):
    need(tok in src,'live-capable contract '+tok)

g={}
for m in re.finditer(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+).*?ISP=0x([0-9a-fA-F]{8})',(FF/'RUN.txt').read_text()):
    gen,req,b=m.groups();gen=int(gen);req=int(req)
    if gen<=12:
        need(req==gen+3,f'FF gain identity G{gen}')
        g[str(gen)]=f'0x{b.lower()}'
need(set(g)=={str(i) for i in range(1,13)},'FF G1..G12 gain authority')

def one(root):
    out=root/'out';out.mkdir();gm=root/'gain.json';mf=root/'manifest.json'
    gm.write_text(json.dumps({'cq_gain_bits':g})+'\n')
    cp=run([str(HERE/'live-iq-producer.py'),'--mode','offline','--snapshot-dir',str(FF),'--gain-manifest',str(gm),'--output-dir',str(out),'--manifest',str(mf)],capture_output=True)
    need('E003I_FL_PRODUCER=PASS' in cp.stdout,'FL marker')
    m=json.loads(mf.read_text())
    need(m['schema']=='sp11-e003i-fl-r5-r15-producer-v1' and m['status']=='PASS','FL manifest')
    need([(r['generation'],r['request_target']) for r in m['rows']]==[(1,None)]+[(g,g+3) for g in range(2,13)],'G1..G12 mapping')
    return out,m

with tempfile.TemporaryDirectory(prefix='e003i-fl-a-') as ta, tempfile.TemporaryDirectory(prefix='e003i-fl-b-') as tb:
    oa,ma=one(Path(ta));ob,mb=one(Path(tb))
    hashes={}
    for req in range(5,16):
        pa=oa/f'R{req}-dynamic.bin';pb=ob/f'R{req}-dynamic.bin'
        need(pa.is_file() and pa.stat().st_size==41088,f'R{req} capsule shape')
        h=sha(pa);need(h==sha(pb),f'R{req} two-run determinism')
        hashes[str(req)]=h
    for req in range(5,13):
        need(hashes[str(req)]==sha(FF/'producer'/f'R{req}-dynamic.bin'),f'R{req} exact FF live regression')
    for req in range(13,16):
        need(hashes[str(req)]==fj['r13_r15_capsule_sha256'][str(req)],f'R{req} FJ authorized hash')
    ra={r['request_target']:r for r in ma['rows'] if r['request_target']}
    rb={r['request_target']:r for r in mb['rows'] if r['request_target']}
    for req in range(5,16):
        for key in ('generation','request_target','cq_isp_gain_bits','final_xy_bits','final_cct_bits','published_cct','awb_calibration_slot','awb_calibration_region','awb_triangle','awb_published_gain_bits','capsule_sha256'):
            need(ra[req][key]==rb[req][key],f'R{req} deterministic {key}')
        need(ra[req]['demux_bls']==rb[req]['demux_bls'],f'R{req} deterministic IQ meta')
        la={k:v for k,v in ra[req]['lsc'].items() if not k.endswith('_ms')}
        lb={k:v for k,v in rb[req]['lsc'].items() if not k.endswith('_ms')}
        need(la==lb,f'R{req} deterministic LSC')
    # Exact metadata regression to the real FF live producer for already-run requests.
    old={r['request_target']:r for r in ffp['rows'] if r['request_target']}
    for req in range(5,13):
        for key in ('capsule_sha256','awb_calibration_slot','awb_calibration_region','awb_triangle','awb_published_gain_bits','final_xy_bits','final_cct_bits','cq_isp_gain_bits'):
            need(ra[req][key]==old[req][key],f'R{req} FF metadata {key}')
    out={
      'schema':'sp11-e003i-fl-r5-r15-producer-integration-v1',
      'status':'PASS_OFFLINE_R5_R15_AUTHORIZED_INTEGRATION',
      'source':'immutable FF G1..G12 paired stats + CQ gains',
      'requests':list(range(5,16)),
      'source_generations':list(range(2,13)),
      'r5_r12_live_regression':'8/8 exact FF live capsule hashes and key metadata',
      'r13_r15_authority':'FJ PASS',
      'r13_r15_capsule_sha256':{str(r):hashes[str(r)] for r in range(13,16)},
      'all_capsule_sha256':hashes,
      'cq_gain_bits_g1_g12':g,
      'gain_publisher':'FK PASS G1..G12 C publisher',
      'live_capable_code_path_preserved':True,
      'linux_camera_runtime_performed_by_fl':False,
      'continuous_aec_claimed':False,
    }
    (HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
