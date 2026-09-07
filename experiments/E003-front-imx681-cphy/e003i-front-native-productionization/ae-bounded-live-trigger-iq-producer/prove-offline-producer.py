#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,importlib.util,json,statistics,struct,tempfile,time
HERE=Path(__file__).resolve().parent
EXPECTED={5:'350fed1aaa4c6c3e9fbed8d3e63f14fcaf7a6cf80be9e8f800536a0ddfa14795',6:'e85dbe7b8b46837e09207586b56e4e648d674ea4663d18ea6b46d1b1f885dd8c'}
def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(b):return hashlib.sha256(bytes(b)).hexdigest()
def fs(v):
 s=sorted(v);return {'mean_ms':statistics.mean(v),'p95_ms':s[int(len(s)*.95)-1],'p99_ms':s[int(len(s)*.99)-1],'max_ms':max(v)}
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--snapshot-dir',type=Path,required=True);ap.add_argument('--iterations',type=int,default=200);ap.add_argument('--manifest',type=Path,default=HERE/'RESULT.json');a=ap.parse_args();assert a.iterations>=20
 P=load(HERE/'live-iq-producer.py','aeprod')
 snaps=[((a.snapshot_dir/f'STATS3A-{i}.bin').read_bytes(),(a.snapshot_dir/f'TLBG-{i}.bin').read_bytes()) for i in range(3)]
 with tempfile.TemporaryDirectory(prefix='e003i-ae-proof-') as td:
  prod=P.Producer(Path(td));first=[];caps={};descs={}
  for s,t in snaps:
   row,cap,desc=prod.process(s,t);first.append(row)
   if cap is not None:caps[row['request_target']]=cap;descs[row['request_target']]=desc
  for req in (5,6):
   assert sha(caps[req])==EXPECTED[req],f'R{req} dynamic capsule drift'
  # Compare to compatibility capsules generated from individual E sources only; captured full capsules are never opened.
  E=prod.composer.E;packer=E.load_py(P.REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/prove-lsc-live-staging-pack.py','ae_pack')
  diff={}
  for req in (5,6):
   cs=E.request_state(P.REPO,req,prod.composer.variant,prod.composer.raw4,prod.composer.slot4,packer);ccap,_=E.compose(req,prod.composer.main,prod.composer.startup,prod.composer.payloads,prod.composer.sp,prod.composer.pp,cs)
   ds=caps[req];dd=descs[req];idx=[i for i,(x,y) in enumerate(zip(ds,ccap)) if x!=y];changed=set();outside=[]
   for q in idx:
    owners=[(typ,si) for typ,si,o,n,h in dd if o<=q<o+n];changed.update(owners)
    if not any(typ==E.TYPE_STEADY_PAYLOAD and si in (1,2,4) and o<=q<o+n for typ,si,o,n,h in dd):outside.append(q)
   assert not outside and changed.issubset({(E.TYPE_STEADY_PAYLOAD,1),(E.TYPE_STEADY_PAYLOAD,2),(E.TYPE_STEADY_PAYLOAD,4)})
   diff[str(req)]={'dynamic_sha256':sha(ds),'compatibility_sha256':sha(ccap),'different_bytes':len(idx),'changed_sections':[list(x) for x in sorted(changed)],'outside_lsc0_lsc1_gic0_bytes':len(outside)}
  per=[[],[],[]];seq=[]
  for _ in range(a.iterations):
   prod.trigger.prev_x=P.frombits(P.INITIAL_PREV_X_BITS);prod.trigger.prev_y=P.frombits(P.INITIAL_PREV_Y_BITS);prod.lsc.reset();prod.rows=[];t0=time.perf_counter_ns()
   for i,(s,t) in enumerate(snaps):
    row,cap,desc=prod.process(s,t);per[i].append(row['total_process_ms']);
    if cap is not None:assert sha(cap)==EXPECTED[row['request_target']]
   seq.append((time.perf_counter_ns()-t0)/1e6)
  out={'schema':'sp11-e003i-ae-offline-producer-proof-v1','status':'PASS','runtime_performed':False,'captured_full_capsule_inputs':0,'selection_law':'R5<-G2, R6<-G3','bounded_baseline_bits':f'0x{P.BASELINE_BITS:08x}','continuous_aec_claimed':False,'first_sequence':first,'capsule_differential':diff,'timing':{'iterations':a.iterations,'G1':fs(per[0]),'G2_R5':fs(per[1]),'G3_R6':fs(per[2]),'G1_G3_sequence':fs(seq),'frame_budget_ms':1000/30},'deadline_pass':fs(per[1])['p95_ms']<1000/30 and fs(per[2])['p95_ms']<1000/30,'safety':{'offline_only':True,'source_generation_is_request_id':False,'bounded_live_runtime_next':True}}
  a.manifest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n');print(f"G2_R5_P95_MS={out['timing']['G2_R5']['p95_ms']:.4f}");print(f"G3_R6_P95_MS={out['timing']['G3_R6']['p95_ms']:.4f}");print('E003I_AE_OFFLINE_PRODUCER=PASS')
if __name__=='__main__':main()
