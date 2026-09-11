#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
A=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gi/attempt1-pass-twentyfour-frame-20260911T2035')
GI=BASE/'gi-twentyfour-frame-live-r5-r24'
GJ=BASE/'gj-windows-r4-r27-combined-awb-lsc-oracle'/'RESULT.json'
GTM_SHA='074564f99a45d29a5dbe800c18bc0436735f70740cb8f42cd9a5c7b636ffcdfa'
ARCHIVE_MANIFEST_SHA='2de0d7051bbbad7df1380f2325d1fef00e74353c30c1fc2c4e2502abd7a77571'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)

need(A.is_dir(),'GI archive absent')
need(sha(A/'MANIFEST.sha256')==ARCHIVE_MANIFEST_SHA,'GI archive manifest drift')

gi=json.loads((GI/'ATTEMPT1-PASS.json').read_text())
need(gi['status']=='PASS_CAPTURE_GI_TWENTYFOUR_FRAME_R5_R24','GI authority')
need(gi['stream_attempts']==1 and gi['same_boot_stream_retry_performed'] is False,'GI retry invariant')
need(gi['golden_return'] is True and gi['candidate_retired'] is True,'GI closure invariant')
need(gi['frames']==24 and gi['producer_generations']==21,'GI generation contract')

gj=json.loads(GJ.read_text())
need(gj['status']=='PASS_WINDOWS_COMBINED_R4_R27_AWB_LSC','GJ combined authority')
need(gj['requests']==list(range(4,28)) and gj['windows_stream_count']==1,'GJ R4-R27 one-stream coverage')
need(gj['same_stream_awb_and_lsc'] is True and gj['combined_r27_completion'] is True,'GJ same-stream R27 closure')
need(gj['awb_result']['bit_exact']=='24/24','GJ AWB authority')
need(gj['lsc_result']['clean_lsc_replay']=='24/24 byte-exact LSC0/LSC1/LSC2/GIC','GJ LSC authority')

src=(HERE/'offline-iq-probe.py').read_text()
need("choices=('offline',)" in src,'probe must be offline-only')
need('for gen in (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24):' in src,'G1..G24 probe loop')
need('elif gen in (4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24):' in src,'R7..R27 extended branch')
need("FBFILE=BASE/'fy-calibrated-awb-selector-replay/dynamic_awb.py'" in src,'FY selector dependency')

g={}
run_text=(A/'runtime-output/RUN.txt').read_text()
for m in re.finditer(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+).*?ISP=0x([0-9a-fA-F]{8})',run_text):
    gen,req,b=m.groups(); gen=int(gen); req=int(req)
    if gen<=24:
        need(req==gen+3,f'gain identity G{gen}')
        g[str(gen)]=f'0x{b.lower()}'
need(set(g)=={str(i) for i in range(1,25)},'GI G1..G24 gain coverage')

with tempfile.TemporaryDirectory(prefix='e003i-gk-snapshot-') as ts:
    snap=Path(ts)/'snapshot'; snap.mkdir()
    for gen in range(1,25):
        for prefix in ('STATS3A','TLBG'):
            srcp=A/'runtime-output'/f'{prefix}-{gen-1}.bin'
            dst=snap/srcp.name
            with dst.open('wb') as f:
                subprocess.run(['sudo','-n','cat',str(srcp)],check=True,stdout=f)
            need(dst.stat().st_size==srcp.stat().st_size,f'{prefix} G{gen} size')

    def one(td):
        td=Path(td); out=td/'out'; out.mkdir()
        gm=td/'gain.json'; mf=td/'manifest.json'
        gm.write_text(json.dumps({'cq_gain_bits':g})+'\n')
        cp=subprocess.run([str(HERE/'offline-iq-probe.py'),'--mode','offline',
                           '--snapshot-dir',str(snap),'--gain-manifest',str(gm),
                           '--output-dir',str(out),'--manifest',str(mf)],
                          text=True,capture_output=True)
        if cp.returncode:
            print(cp.stdout); print(cp.stderr); raise SystemExit(cp.returncode)
        need('E003I_GK_OFFLINE_PROBE=PASS' in cp.stdout,'GK pass marker')
        m=json.loads(mf.read_text())
        need(m['schema']=='sp11-e003i-gk-r5-r27-offline-probe-v1' and m['status']=='PASS','GK manifest')
        need([(r['generation'],r['request_target']) for r in m['rows']]==
             [(1,None)]+[(x,x+3) for x in range(2,25)],'G1..G24 mapping')
        return out,m

    with tempfile.TemporaryDirectory(prefix='e003i-gk-a-') as ta, tempfile.TemporaryDirectory(prefix='e003i-gk-b-') as tb:
        oa,ma=one(ta); ob,mb=one(tb)
        live_reg={}
        for req in range(5,25):
            got=sha(oa/f'R{req}-dynamic.bin')
            exp=sha(A/'runtime-output/producer'/f'R{req}-dynamic.bin')
            need(got==exp,f'R{req} GI live regression')
            need(got==sha(ob/f'R{req}-dynamic.bin'),f'R{req} determinism')
            live_reg[str(req)]=got

        new_hash={}
        for req in range(25,28):
            pa=oa/f'R{req}-dynamic.bin'; pb=ob/f'R{req}-dynamic.bin'
            need(pa.is_file() and pa.stat().st_size==41088,f'R{req} capsule shape')
            h=sha(pa); need(h==sha(pb),f'R{req} determinism')
            new_hash[str(req)]=h

        ra={r['request_target']:r for r in ma['rows'] if r['request_target']}
        rb={r['request_target']:r for r in mb['rows'] if r['request_target']}
        for req in range(5,28):
            for k in ('generation','request_target','final_xy_bits','final_cct_bits',
                      'published_cct','awb_calibration_slot','awb_calibration_region',
                      'awb_triangle','awb_published_gain_bits','capsule_sha256'):
                need(ra[req][k]==rb[req][k],f'R{req} deterministic {k}')
            need(ra[req]['demux_bls']==rb[req]['demux_bls'],f'R{req} deterministic IQ meta')
            la={k:v for k,v in ra[req]['lsc'].items() if not k.endswith('_ms')}
            lb={k:v for k,v in rb[req]['lsc'].items() if not k.endswith('_ms')}
            need(la==lb,f'R{req} deterministic LSC')

        for req in range(25,28):
            need(ra[req]['demux_bls']['gtm_sha256']==GTM_SHA,f'R{req} GTM stable law')

        seq=[ra[r] for r in (24,25,26,27)]
        awb_regs=[json.dumps(r['demux_bls']['awb_regs'],sort_keys=True) for r in seq]
        tint=[r['lsc']['tintless_output_sha256'] for r in seq]
        lsc0=[r['lsc']['lsc0_sha256'] for r in seq]
        lsc1=[r['lsc']['lsc1_sha256'] for r in seq]
        gic=[r['lsc']['gic_sha256'] for r in seq]

        rows={}
        for req in range(24,28):
            row=ra[req]
            rows[str(req)]={
              'generation':row['generation'],'capsule_sha256':sha(oa/f'R{req}-dynamic.bin'),
              'awb_calibration_slot':row['awb_calibration_slot'],
              'awb_calibration_region':row['awb_calibration_region'],
              'awb_triangle':row['awb_triangle'],'awb_regs':row['demux_bls']['awb_regs'],
              'published_cct':row['published_cct'],'gtm_sha256':row['demux_bls']['gtm_sha256'],
              'lsc':{k:row['lsc'][k] for k in (
                'aec_selector_mode','cct_selector_mode','x22_sha256','pretintless_sha256',
                'tintless_output_sha256','lsc0_sha256','lsc1_sha256','lsc2_sha256','gic_sha256')},
            }

        result={
          'schema':'sp11-e003i-gk-r25-r27-continuation-authority-v1',
          'status':'PASS_OFFLINE_R25_R27_COMPOSABLE_AUTHORITY_CLOSED',
          'source':'immutable GI attempt1 archive G1..G24 stats + AEC gain observations',
          'gi_archive_manifest_sha256':ARCHIVE_MANIFEST_SHA,
          'r5_r24_live_regression':'20/20 exact GI live capsule hashes',
          'r25_r27_deterministic':'3/3 two-run capsule hashes exact',
          'r25_r27_capsule_sha256':new_hash,
          'gtm_post_r6_stable_through_probe':True,
          'awb_windows_authority_through_request':27,
          'awb_windows_authority_source':'GJ Windows R4-R27 24/24 bit-exact via FY',
          'lsc_windows_authority_through_request':27,
          'lsc_windows_authority_source':'GJ Windows R4-R27 clean-room 24/24 byte-exact',
          'r25_r27_awb_windows_differential':True,
          'r25_r27_lsc_windows_differential':True,
          'awb_evolving_r24_r27':len(set(awb_regs))>1,
          'tintless_evolving_r24_r27':len(set(tint))>1,
          'lsc_gic_evolving_r24_r27':len(set(lsc0))>1 or len(set(lsc1))>1 or len(set(gic))>1,
          'linux_live_r25_plus_allowed':True,
          'linux_live_scope':'bounded fresh R5-R27 successor only; one stream; no continuous/unrestricted AEC claim',
          'camera_runtime_performed':False,'continuous_aec_claimed':False,
          'rows_r24_r27':rows,
        }
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print(json.dumps(result,indent=2,sort_keys=True))
