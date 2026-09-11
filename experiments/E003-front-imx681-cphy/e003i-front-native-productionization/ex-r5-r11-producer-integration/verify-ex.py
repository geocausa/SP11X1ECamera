#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,tempfile
HERE=Path(__file__).resolve().parent; BASE=HERE.parent
EV=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-ev/attempt1-pass-nine-frame-20260911T1352/runtime-output')
EB=BASE/'eb-windows-r4-r12-gtm-state-oracle'/'RESULT.json'; ED=BASE/'ed-windows-r4-r12-tintless-trigger-staging-oracle'/'RESULT.json'; EL=BASE/'el-calibrated-awb-scalar-join'/'RESULT.json'
def need(x,m):
    if not x: raise AssertionError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
live=json.loads((EV/'LIVE-RESULT.json').read_text()); need(live['status']=='PASS_CAPTURE_EV_NINE_FRAME_R5_R9','EV live authority')
run=(EV/'RUN.txt').read_text(); gains={}
for m in re.finditer(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+).*? ISP=0x([0-9a-fA-F]{8})',run):
    g,req,b=m.groups(); g=int(g); req=int(req)
    if g<=8: need(req==g+3,f'gain request G{g}'); gains[str(g)]=f'0x{b.lower()}'
need(set(gains)=={str(i) for i in range(1,9)},'EV gain coverage G1..G8')
eb=json.loads(EB.read_text()); need(eb['status']=='PASS_WINDOWS_ORACLE' and eb['post_r6_gtm_output_law']=='stable','EB R10/R11 GTM authority')
ed=json.loads(ED.read_text()); need(ed['status'].startswith('PASS') and ed['clean_lsc_replay']=='9/9 byte-exact LSC0/LSC1/LSC2/GIC','ED R10/R11 LSC authority')
el=json.loads(EL.read_text()); need(el['status']=='PASS_OFFLINE_JOIN' and 10 in el['windows_requests'] and 11 in el['windows_requests'],'EL R10/R11 AWB authority')
with tempfile.TemporaryDirectory(prefix='e003i-ex-') as td:
    td=Path(td); gm=td/'gain.json'; out=td/'out'; manifest=td/'manifest.json'; gm.write_text(json.dumps({'cq_gain_bits':gains})+'\n')
    cp=subprocess.run([str(HERE/'live-iq-producer.py'),'--mode','offline','--snapshot-dir',str(EV),'--gain-manifest',str(gm),'--output-dir',str(out),'--manifest',str(manifest)],text=True,capture_output=True)
    if cp.returncode: print(cp.stdout); print(cp.stderr); raise SystemExit(cp.returncode)
    need('E003I_EX_PRODUCER=PASS' in cp.stdout,'EX producer pass marker')
    m=json.loads(manifest.read_text()); need(m['status']=='PASS' and m['schema']=='sp11-e003i-ex-r5-r11-producer-v1','EX manifest')
    rows=m['rows']; need([(r['generation'],r['request_target']) for r in rows]==[(1,None),(2,5),(3,6),(4,7),(5,8),(6,9),(7,10),(8,11)],'mapping through R11')
    for req in range(5,12):
        cap=out/f'R{req}-dynamic.bin'; need(cap.is_file() and cap.stat().st_size==41088,f'R{req} capsule shape')
        row=next(r for r in rows if r['request_target']==req); need(sha(cap)==row['capsule_sha256'],f'R{req} self hash')
    for req in range(5,10):
        need(sha(out/f'R{req}-dynamic.bin')==live['capsules'][str(req)]['sha256'],f'R{req} EV live regression')
    r10=next(r for r in rows if r['request_target']==10); r11=next(r for r in rows if r['request_target']==11)
    for r in (r10,r11):
        need(r['demux_bls']['gtm_sha256']=='074564f99a45d29a5dbe800c18bc0436735f70740cb8f42cd9a5c7b636ffcdfa',f"R{r['request_target']} GTM")
        need(r['awb_triangle']>=0,f"R{r['request_target']} AWB triangle")
        need(r['lsc']['aec_selector_mode']=='lower_aec',f"R{r['request_target']} AEC LSC selector")
        need(r['lsc']['cct_selector_mode']=='leaf_0x4bd',f"R{r['request_target']} CCT selector")
        need(r['awb_triangle']==19,f"R{r['request_target']} EV AWB selector regression")
    result={'schema':'sp11-e003i-ex-r5-r11-producer-integration-v1','status':'PASS_OFFLINE_R5_R11_INTEGRATION','source':'EV attempt1 PASS G1..G8 Linux snapshots + CQ gain feed','requests':[5,6,7,8,9,10,11],'source_generations':[2,3,4,5,6,7,8],'r5_r9_live_regression':'5/5 exact EV live capsule hashes','r10_capsule_sha256':sha(out/'R10-dynamic.bin'),'r11_capsule_sha256':sha(out/'R11-dynamic.bin'),'r10_total_process_ms':r10['total_process_ms'],'r11_total_process_ms':r11['total_process_ms'],'r10_awb_triangle':r10['awb_triangle'],'r11_awb_triangle':r11['awb_triangle'],'r10_lsc':r10['lsc'],'r11_lsc':r11['lsc'],'r10_awb_regs':r10['demux_bls']['awb_regs'],'r11_awb_regs':r11['demux_bls']['awb_regs'],'cq_gain_bits_g1_g8':gains,'windows_component_authority':'EB GTM through R12 + ED LSC through R12 + EL/EG AWB through R11','whole_capsule_windows_r10_r11_byte_oracle':False,'linux_camera_runtime_performed_by_ex':False,'continuous_aec_claimed':False}
    (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(cp.stdout.strip()); print(json.dumps(result,indent=2,sort_keys=True))
