#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
A=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fn/attempt1-pass-fifteen-frame-20260911T1735')
FN=BASE/'fn-fifteen-frame-live-r5-r15'
FH=BASE/'fh-recovered-windows-r18-awb-oracle'/'RESULT.json'
FI=BASE/'fi-windows-r4-r15-tintless-lsc-oracle'/'RESULT.json'
GTM_SHA='074564f99a45d29a5dbe800c18bc0436735f70740cb8f42cd9a5c7b636ffcdfa'
ARCHIVE_MANIFEST_SHA='a12e84d235f5b4af5e313cd36f0f2952356a34ff1e80468ebd89c29355551a62'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)

need(A.is_dir(),'FN archive absent')
need(sha(A/'MANIFEST.sha256')==ARCHIVE_MANIFEST_SHA,'FN archive manifest drift')
fn=json.loads((FN/'ATTEMPT1-PASS.json').read_text())
need(fn['status']=='PASS_CAPTURE_FN_FIFTEEN_FRAME_R5_R15','FN authority')
need(fn['stream_attempts']==1 and fn['same_boot_stream_retry_performed'] is False,'FN retry invariant')
need(fn['golden_return'] is True and fn['candidate_retired'] is True,'FN closure invariant')

fh=json.loads(FH.read_text())
need(fh['status']=='PASS_RECOVERED_WINDOWS_R4_R18_AWB_15_OF_15_BIT_EXACT','FH AWB authority')
fi=json.loads(FI.read_text())
need(fi['status']=='PASS_WINDOWS_ORACLE_CLEANROOM_REPLAY' and fi['requests']==list(range(4,16)),'FI LSC authority')

src=(HERE/'offline-iq-probe.py').read_text()
need("choices=('offline',)" in src,'probe must be CLI-offline-only')
need('for gen in (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15):' in src,'G1..G15 probe loop')
need('elif gen in (4,5,6,7,8,9,10,11,12,13,14,15):' in src,'R7..R18 extended branch')

g={}
run_text=(A/'runtime-output/RUN.txt').read_text()
for m in re.finditer(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+).*?ISP=0x([0-9a-fA-F]{8})',run_text):
    gen,req,b=m.groups(); gen=int(gen); req=int(req)
    if gen<=15:
        need(req==gen+3,f'gain identity G{gen}')
        g[str(gen)]=f'0x{b.lower()}'
need(set(g)=={str(i) for i in range(1,16)},'FN G1..G15 gain coverage')

def one(td:Path):
    out=td/'out';out.mkdir()
    gm=td/'gain.json';mf=td/'manifest.json'
    gm.write_text(json.dumps({'cq_gain_bits':g})+'\n')
    cp=subprocess.run([
        str(HERE/'offline-iq-probe.py'),'--mode','offline',
        '--snapshot-dir',str(A/'runtime-output'),
        '--gain-manifest',str(gm),
        '--output-dir',str(out),
        '--manifest',str(mf),
    ],text=True,capture_output=True)
    if cp.returncode:
        print(cp.stdout);print(cp.stderr);raise SystemExit(cp.returncode)
    need('E003I_FO_OFFLINE_PROBE=PASS' in cp.stdout,'FO pass marker')
    m=json.loads(mf.read_text())
    need(m['schema']=='sp11-e003i-fo-r5-r18-offline-probe-v1' and m['status']=='PASS','FO manifest')
    need([(r['generation'],r['request_target']) for r in m['rows']]==
         [(1,None)]+[(x,x+3) for x in range(2,16)],'G1..G15 mapping')
    return out,m

with tempfile.TemporaryDirectory(prefix='e003i-fo-a-') as ta, tempfile.TemporaryDirectory(prefix='e003i-fo-b-') as tb:
    oa,ma=one(Path(ta)); ob,mb=one(Path(tb))

    live_reg={}
    for req in range(5,16):
        got=sha(oa/f'R{req}-dynamic.bin')
        exp=sha(A/'runtime-output/producer'/f'R{req}-dynamic.bin')
        need(got==exp,f'R{req} FN live regression')
        need(got==sha(ob/f'R{req}-dynamic.bin'),f'R{req} two-run determinism')
        live_reg[str(req)]=got

    new_hash={}
    for req in range(16,19):
        pa=oa/f'R{req}-dynamic.bin';pb=ob/f'R{req}-dynamic.bin'
        need(pa.is_file() and pa.stat().st_size==41088,f'R{req} capsule shape')
        h=sha(pa);need(h==sha(pb),f'R{req} two-run determinism')
        new_hash[str(req)]=h

    ra={r['request_target']:r for r in ma['rows'] if r['request_target']}
    rb={r['request_target']:r for r in mb['rows'] if r['request_target']}
    for req in range(5,19):
        for k in ('generation','request_target','final_xy_bits','final_cct_bits',
                  'published_cct','awb_calibration_slot','awb_calibration_region',
                  'awb_triangle','awb_published_gain_bits','capsule_sha256'):
            need(ra[req][k]==rb[req][k],f'R{req} deterministic {k}')
        need(ra[req]['demux_bls']==rb[req]['demux_bls'],f'R{req} deterministic IQ meta')
        la={k:v for k,v in ra[req]['lsc'].items() if not k.endswith('_ms')}
        lb={k:v for k,v in rb[req]['lsc'].items() if not k.endswith('_ms')}
        need(la==lb,f'R{req} deterministic LSC state')

    for req in range(16,19):
        r=ra[req]
        need(r['demux_bls']['gtm_sha256']==GTM_SHA,f'R{req} GTM stable law')
        need(r['lsc']['aec_selector_mode']=='lower_aec',f'R{req} AEC LSC selector')
        need(r['lsc']['cct_selector_mode']=='leaf_0x4bd',f'R{req} CCT LSC selector')

    seq=[ra[r] for r in (15,16,17,18)]
    awb_regs=[json.dumps(r['demux_bls']['awb_regs'],sort_keys=True) for r in seq]
    tint=[r['lsc']['tintless_output_sha256'] for r in seq]
    lsc0=[r['lsc']['lsc0_sha256'] for r in seq]
    lsc1=[r['lsc']['lsc1_sha256'] for r in seq]
    gic=[r['lsc']['gic_sha256'] for r in seq]

    rows={}
    for req in range(15,19):
        r=ra[req]
        rows[str(req)]={
            'generation':r['generation'],
            'capsule_sha256':sha(oa/f'R{req}-dynamic.bin'),
            'awb_calibration_slot':r['awb_calibration_slot'],
            'awb_calibration_region':r['awb_calibration_region'],
            'awb_triangle':r['awb_triangle'],
            'awb_regs':r['demux_bls']['awb_regs'],
            'published_cct':r['published_cct'],
            'gtm_sha256':r['demux_bls']['gtm_sha256'],
            'lsc':{k:r['lsc'][k] for k in (
                'aec_selector_mode','cct_selector_mode','x22_sha256',
                'pretintless_sha256','tintless_output_sha256',
                'lsc0_sha256','lsc1_sha256','lsc2_sha256','gic_sha256')},
        }

    result={
        'schema':'sp11-e003i-fo-r16-r18-continuation-authority-v1',
        'status':'PASS_OFFLINE_R16_R18_COMPOSABLE_LSC_AUTHORITY_OPEN',
        'source':'immutable FN attempt1 archive G1..G15 stats + AEC gain observations',
        'fn_archive_manifest_sha256':ARCHIVE_MANIFEST_SHA,
        'r5_r15_live_regression':'11/11 exact FN live capsule hashes',
        'r16_r18_deterministic':'3/3 two-run capsule hashes exact',
        'r16_r18_capsule_sha256':new_hash,
        'gtm_post_r6_stable_through_probe':True,
        'awb_windows_authority_through_request':18,
        'awb_windows_authority_source':'FH recovered Windows R4-R18 15/15 bit-exact',
        'lsc_windows_authority_through_request':15,
        'r16_r18_lsc_windows_differential':False,
        'awb_evolving_r15_r18':len(set(awb_regs))>1,
        'tintless_evolving_r15_r18':len(set(tint))>1,
        'lsc_gic_evolving_r15_r18':len(set(lsc0))>1 or len(set(lsc1))>1 or len(set(gic))>1,
        'linux_live_r16_plus_allowed':False,
        'camera_runtime_performed':False,
        'continuous_aec_claimed':False,
        'rows_r15_r18':rows,
    }
    (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(result,indent=2,sort_keys=True))
