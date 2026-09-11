#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
FN=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fn/attempt1-pass-fifteen-frame-20260911T1735/runtime-output')
FQ=BASE/'fq-r16-r18-content-authority-join'/'RESULT.json'
FR=BASE/'fr-fifteen-generation-gain-feed-publisher'/'RESULT.json'

def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(c,**kw): return subprocess.run(c,check=True,text=True,**kw)

fq=json.loads(FQ.read_text())
need(fq['status']=='PASS_OFFLINE_R16_R18_CONTENT_AUTHORIZED','FQ authority')
fr=json.loads(FR.read_text())
need(fr['status']=='PASS_OFFLINE_G1_G15_C_PUBLISHER','FR authority')
fnp=json.loads((FN/'producer/RESULT.json').read_text())
need(fnp['status']=='PASS','FN producer authority')
need([(r['generation'],r['request_target']) for r in fnp['rows']]==[(1,None)]+[(g,g+3) for g in range(2,13)],'FN rows')

src=(HERE/'live-iq-producer.py').read_text()
for tok in ("choices=('offline','live')",'configure_live_scheduler','LiveControl','GainFeed',
            'elif gen in (4,5,6,7,8,9,10,11,12,13,14,15):',
            'for gen in (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15):'):
    need(tok in src,'live-capable contract '+tok)

g={}
for m in re.finditer(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+).*?ISP=0x([0-9a-fA-F]{8})',(FN/'RUN.txt').read_text()):
    gen,req,b=m.groups(); gen=int(gen); req=int(req)
    if gen<=15:
        need(req==gen+3,f'FN gain identity G{gen}')
        g[str(gen)]=f'0x{b.lower()}'
need(set(g)=={str(i) for i in range(1,16)},'FN G1..G15 gain authority')

def one(root):
    out=root/'out'; out.mkdir(); gm=root/'gain.json'; mf=root/'manifest.json'
    gm.write_text(json.dumps({'cq_gain_bits':g})+'\n')
    cp=run([str(HERE/'live-iq-producer.py'),'--mode','offline','--snapshot-dir',str(FN),
            '--gain-manifest',str(gm),'--output-dir',str(out),'--manifest',str(mf)],capture_output=True)
    need('E003I_FS_PRODUCER=PASS' in cp.stdout,'FS marker')
    m=json.loads(mf.read_text())
    need(m['schema']=='sp11-e003i-fs-r5-r18-producer-v1' and m['status']=='PASS','FS manifest')
    need([(r['generation'],r['request_target']) for r in m['rows']]==[(1,None)]+[(x,x+3) for x in range(2,16)],'G1..G15 mapping')
    return out,m

with tempfile.TemporaryDirectory(prefix='e003i-fs-a-') as ta, tempfile.TemporaryDirectory(prefix='e003i-fs-b-') as tb:
    oa,ma=one(Path(ta)); ob,mb=one(Path(tb))
    hashes={}
    for req in range(5,19):
        pa=oa/f'R{req}-dynamic.bin'; pb=ob/f'R{req}-dynamic.bin'
        need(pa.is_file() and pa.stat().st_size==41088,f'R{req} capsule shape')
        h=sha(pa); need(h==sha(pb),f'R{req} two-run determinism')
        hashes[str(req)]=h

    for req in range(5,16):
        need(hashes[str(req)]==sha(FN/'producer'/f'R{req}-dynamic.bin'),f'R{req} exact FN live regression')
    for req in range(16,19):
        need(hashes[str(req)]==fq['r16_r18_capsule_sha256'][str(req)],f'R{req} FQ authorized hash')

    ra={r['request_target']:r for r in ma['rows'] if r['request_target']}
    rb={r['request_target']:r for r in mb['rows'] if r['request_target']}
    for req in range(5,19):
        for key in ('generation','request_target','cq_isp_gain_bits','final_xy_bits','final_cct_bits',
                    'published_cct','awb_calibration_slot','awb_calibration_region','awb_triangle',
                    'awb_published_gain_bits','capsule_sha256'):
            need(ra[req][key]==rb[req][key],f'R{req} deterministic {key}')
        need(ra[req]['demux_bls']==rb[req]['demux_bls'],f'R{req} deterministic IQ meta')
        la={k:v for k,v in ra[req]['lsc'].items() if not k.endswith('_ms')}
        lb={k:v for k,v in rb[req]['lsc'].items() if not k.endswith('_ms')}
        need(la==lb,f'R{req} deterministic LSC')

    old={r['request_target']:r for r in fnp['rows'] if r['request_target']}
    for req in range(5,16):
        for key in ('capsule_sha256','awb_calibration_slot','awb_calibration_region','awb_triangle',
                    'awb_published_gain_bits','final_xy_bits','final_cct_bits','cq_isp_gain_bits'):
            need(ra[req][key]==old[req][key],f'R{req} FN metadata {key}')

    out={
      'schema':'sp11-e003i-fs-r5-r18-producer-integration-v1',
      'status':'PASS_OFFLINE_R5_R18_AUTHORIZED_INTEGRATION',
      'source':'immutable FN G1..G15 paired stats + CQ gains',
      'requests':list(range(5,19)),
      'source_generations':list(range(2,16)),
      'r5_r15_live_regression':'11/11 exact FN live capsule hashes and key metadata',
      'r16_r18_authority':'FQ PASS',
      'r16_r18_capsule_sha256':{str(r):hashes[str(r)] for r in range(16,19)},
      'all_capsule_sha256':hashes,
      'cq_gain_bits_g1_g15':g,
      'gain_publisher':'FR PASS G1..G15 C publisher',
      'live_capable_code_path_preserved':True,
      'linux_camera_runtime_performed_by_fs':False,
      'continuous_aec_claimed':False,
    }
    (HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps(out,indent=2,sort_keys=True))
