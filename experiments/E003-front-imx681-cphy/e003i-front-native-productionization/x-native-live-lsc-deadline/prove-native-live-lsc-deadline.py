#!/usr/bin/env python3
from __future__ import annotations
import argparse, ctypes, hashlib, importlib.util, json, statistics, struct, subprocess, tempfile, time
from pathlib import Path

HERE=Path(__file__).resolve().parent; REPO=HERE.parents[3]; BASE=HERE.parent
PROD=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
W=BASE/'w-request-stats-selection-trigger-oracle/ANALYSIS.json'
NFILE=BASE/'n-titan680-tlbg-parser/titan680-tlbg-parser.py'; MFILE=BASE/'m-stats-only-lsc-request-state/generate-stats-only-front-lsc.py'; KFILE=BASE/'k-cleanroom-lsc-backend/generate-cleanroom-front-lsc-wire.py'; IFILE=BASE/'i-cleanroom-tintless/cleanroom-tintless-helpers.py'; GFILE=BASE/'g-cleanroom-lsc-upstream/cleanroom-front-lsc.py'
DECFILE=PROD/'decode_imx681_chromatix.py'; GOLDFILE=PROD/'prove-lsc-live-golden-authority.py'; DEFAULT_U=BASE/'u-corrected-tlbg-runtime'
TUNING=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.tuned.ffc_imx681.bin'); OTP=PROD/'oracle-live-20260904-current-repair/live-front-potp-slot-20260904.bin'
TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'; OTP_SHA='2ce64e72ae57bf19a4c60819a242a35bf5a09876862b21387e63b512d5026cdc'; LEAF_A_SHA='bdcf62f46070513ca0d343dda341336fe3953891a2643581e8ee455b77f37a3e'; LEAF_B_SHA='afc02261b98c3e2655039e29ace838f5780ac26202beda08db74dbd876822a11'; W_PRE_SHA='ec60c6de7557b24493fdeaa8cefe464601e8c383e111985b1ebf99a434b88201'
HEADER=struct.Struct('<IHHQIIII'); MAGIC=0x47424C54; FRAME_MS=1000.0/30.0
X1=0x270000003000;X2=0x270000010000;D3=0x270000030000;D4=0x270000031000;IN=0x270000040000;OUT=0x270000050000;WRAP=0x270000001000;CORE=0x270000100000;ADAPT=0x270000140000

def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
def sha(b):return hashlib.sha256(b).hexdigest()
def shaf(p):return sha(p.read_bytes())
def need(v,msg):
 if not v:raise RuntimeError(msg)
def fs(v):
 v=sorted(v);return {'min':round(v[0],6),'median':round(statistics.median(v),6),'p95':round(v[int(len(v)*.95)-1],6),'max':round(v[-1],6)}
def compile_native(out):
 cmd=['gcc','-O3','-shared','-fPIC','-std=c11','-fno-fast-math','-ffp-contract=off','-Wall','-Wextra','-Werror',str(HERE/'native-tintless-core.c'),'-lm','-o',str(out)];subprocess.run(cmd,check=True);return cmd

def snapshots(d,N):
 out=[]
 for i in range(3):
  b=(d/f'TLBG-{i}.bin').read_bytes();need(len(b)==0xf020,f'TLBG-{i} size');magic,ver,hb,gen,seq,slot,rb,flags=HEADER.unpack_from(b);need((magic,ver,hb,rb,flags)==(MAGIC,1,32,N.RAW_BYTES,1),f'TLBG-{i} header');raw=b[32:];parsed=N.parse_titan680_tlbg(raw);out.append({'generation':gen,'source_seq':seq,'slot':slot,'raw':raw,'parsed':parsed,'snapshot_sha256':sha(b),'parsed_sha256':sha(parsed)})
 need([x['generation'] for x in out]==[1,2,3],'generation drift');return out

def front_authority(D,CL,G):
 need(shaf(TUNING)==TUNING_SHA,'tuning SHA');need(shaf(OTP)==OTP_SHA,'OTP SHA');b=TUNING.read_bytes();h=D.parse_header(b);r,_=D.parse_symbol_table(b,h['sections'][0],h['sections'][1]);o=h['sections'][1]
 need(struct.unpack('<6I',D.data_bytes(b,o,r[0x4b1]))==(8,2,5,100,0,6),'control vector')
 aec=struct.unpack('<12I',D.data_bytes(b,o,r[0x4b6]));need(aec==(0x3f800000,0x43c30000,4,0x4b7,0,0x4c0,0x43f50000,0x447a0000,1,0x4c1,0,0x4c4),'AEC tree')
 cct=struct.unpack('<24I',D.data_bytes(b,o,r[0x4b7]));need(cct==(0x3f800000,0x451c4000,0,0x4b8,1,0x4b9,0x4528c000,0x45480000,0,0x4ba,1,0x4bb,0x45548000,0x458ca000,0,0x4bc,1,0x4bd,0x459c4000,0x461c4000,0,0x4be,1,0x4bf),'CCT tree')
 A=D.data_bytes(b,o,r[0x4bd]);B=D.data_bytes(b,o,r[0x4bf]);need(sha(A)==LEAF_A_SHA and sha(B)==LEAF_B_SHA,'leaf SHA');return A,B,G.parse_golden(TUNING)['values'],CL.parse_otp(OTP.read_bytes())

def w_select():
 w=json.loads(W.read_text());need(w['status']=='PASS' and w['trace']['request_minus_source_generation_unique']==[3] and w['trace']['selection_law']=='request_frame = parser_source_generation + 3','W +3 law');out=[]
 for r in w['request4_6_trigger_oracle']:
  req=int(r['request_frame']);lux=float(r['decoded']['aec_lux_index']);cct=float(r['decoded']['awb_cct']);need(1<=lux<=390,f'R{req} AEC branch');need(5000<=cct<=10000,f'R{req} CCT branch');need(int(r['source_generation'])==req-3,f'R{req} W source generation');out.append({'request':req,'source_generation':req-3,'aec_lux_index':lux,'awb_cct':cct,'selected_front_leaf':'0x4bf','interpolation_required':False})
 need([x['request'] for x in out]==[4,5,6],'W request order');return out

def mem0(K,C,M,x1):
 m=K.SparseMemory();m.mem_write(WRAP,bytes(0x1090));m.fill(CORE,C.CORE_BYTES,0);m.mem_write(ADAPT,bytes(0x1000));m.mem_write(X1,x1);m.mem_write(D3,M.descriptor(IN));m.mem_write(D4,M.descriptor(OUT));return m

def pyseq(stats,pre,x1,K,C,M):
 m=mem0(K,C,M,x1);outs=[]
 for i,x in enumerate(stats):
  m.mem_write(X2,x['parsed']);m.mem_write(IN,pre+bytes(0x20));m.mem_write(OUT,K.output_seed('zero'));need(C.wrapper_front_mode2(m,WRAP,X1,X2,D3,D4,CORE if i==0 else 0,ADAPT)==0,f'Python G{i+1}');outs.append(m.mem_read(OUT,0xdf0))
 return m,outs

def api(so):
 l=ctypes.CDLL(str(so));core=l.tintless_core_mode2_native;core.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_void_p];core.restype=ctypes.c_int;res=l.lsc_resample_x23_native;res.argtypes=[ctypes.POINTER(ctypes.c_float),ctypes.POINTER(ctypes.c_float)];res.restype=ctypes.c_int;return core,res
def resample(res,x23):
 a=(ctypes.c_float*884).from_buffer_copy(x23[:0xdd0]);o=(ctypes.c_float*884)();need(res(a,o)==0,'resampler rc');return bytes(memoryview(o).cast('B'))

def hybrid(stats,pre,x1,K,C,M,core):
 m=mem0(K,C,M,x1);state=None;outs=[];times=[]
 for i,x in enumerate(stats):
  t0=time.perf_counter_ns();dirty=C.update_wrapper_config_front(m,WRAP,X1);ca=struct.unpack('<Q',m.mem_read(WRAP+0x128,8))[0]
  if ca==0:ca=CORE;m.mem_write(WRAP+0x128,struct.pack('<Q',ca));dirty=True
  if dirty:C.initialize_core_front_mode2(m,CORE,WRAP);state=bytearray(m.mem_read(CORE,C.CORE_BYTES))
  t1=time.perf_counter_ns();seed=K.output_seed('zero');outb=bytearray(seed[:0xdd0]);SA=(ctypes.c_ubyte*len(state)).from_buffer(state);p=x['parsed'];PA=(ctypes.c_ubyte*len(p)).from_buffer_copy(p);FA=(ctypes.c_float*884).from_buffer_copy(pre);OA=(ctypes.c_float*884).from_buffer(outb);need(core(SA,len(state),PA,len(p),FA,OA)==0,f'native G{i+1}');t2=time.perf_counter_ns();m.mem_write(IN,pre+bytes(0x20));m.mem_write(OUT,outb+seed[0xdd0:]);C._wrapper_temporal_blend(m,WRAP,D3,D4);outs.append(m.mem_read(OUT,0xdf0));t3=time.perf_counter_ns();times.append((t3-t0)/1e6)
 return m,state,outs,times

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--snapshot-dir',type=Path,default=DEFAULT_U);ap.add_argument('--manifest',type=Path,default=HERE/'RESULT.json');ap.add_argument('--iterations',type=int,default=100);a=ap.parse_args()
 N=load(NFILE,'xN');M=load(MFILE,'xM');K=load(KFILE,'xK');C=load(IFILE,'xI');CL=load(GFILE,'xG');D=load(DECFILE,'xD');G=load(GOLDFILE,'xGold');sel=w_select();A,B,gold,otp=front_authority(D,CL,G);ss=snapshots(a.snapshot_dir,N);x1,_=M.build_front_x1()
 with tempfile.TemporaryDirectory(prefix='e003i-x-') as td:
  so=Path(td)/'libe003i_tintless.so';cmd=compile_native(so);core,res=api(so);x23=CL.calibrate(CL.interpolate_leaf(A,B,1.0),gold,otp);pre=CL.resample_x23(x23);need(resample(res,x23)==pre and sha(pre)==W_PRE_SHA,'W leaf-B resample')
  ratios=[0.0,0.001,0.1234567,0.212,0.342,0.5,0.6770310997962952,0.999,1.0];rp=[]
  for ratio in ratios:
   xx=CL.calibrate(CL.interpolate_leaf(A,B,ratio),gold,otp);py=CL.resample_x23(xx);na=resample(res,xx);need(py==na,f'ratio {ratio}');rp.append({'ratio':ratio,'sha256':sha(na),'byte_exact':True})
  pm,po=pyseq(ss,pre,x1,K,C,M);hm,hs,ho,_=hybrid(ss,pre,x1,K,C,M,core);need(po==ho,'output sequence');need(pm.mem_read(WRAP,0x1090)==hm.mem_read(WRAP,0x1090),'wrapper state');need(pm.mem_read(CORE,C.CORE_BYTES)==hs,'core state')
  gens=[]
  for i,o in enumerate(ho,1):
   l0,l1,l2,gic=K.wire_from_output(o);gens.append({'generation':i,'output_abi_sha256':sha(o[:0xdd0]),'lsc0_sha256':sha(l0),'lsc1_sha256':sha(l1),'gic_sha256':sha(gic)})
  for _ in range(10):N.parse_titan680_tlbg(ss[1]['raw']);hybrid(ss,pre,x1,K,C,M,core)
  pt=[];dt=[];ht=[[],[],[]]
  for it in range(a.iterations):
   t=time.perf_counter_ns();N.parse_titan680_tlbg(ss[1]['raw']);pt.append((time.perf_counter_ns()-t)/1e6);ratio=(it%97)/96;t=time.perf_counter_ns();xx=CL.calibrate(CL.interpolate_leaf(A,B,ratio),gold,otp);resample(res,xx);dt.append((time.perf_counter_ns()-t)/1e6);_,_,_,tt=hybrid(ss,pre,x1,K,C,M,core)
   for i,v in enumerate(tt):ht[i].append(v)
  ps,ds,hsx=fs(pt),fs(dt),[fs(x) for x in ht];cached=ps['p95']+hsx[1]['p95']+0.25;dynamic=ps['p95']+ds['p95']+hsx[1]['p95']+0.25;need(cached<FRAME_MS,'cached deadline');need(dynamic<FRAME_MS,'dynamic deadline')
  result={'schema':'sp11-e003i-x-native-live-lsc-deadline-v1','status':'PASS','offline_only':True,'runtime_performed':False,'source_generation_is_request_id':False,'dynamic_linux_r5_r6_substitution_authorized':False,'frame_budget_ms':FRAME_MS,'w_selection':sel,'front_authority':{'tuning_sha256':TUNING_SHA,'otp_sha256':OTP_SHA,'leaf_a_sha256':LEAF_A_SHA,'leaf_b_sha256':LEAF_B_SHA,'w_selected_leaf':'0x4bf','w_pretintless_sha256':W_PRE_SHA},'native_build':{'command':' '.join(cmd),'source_sha256':shaf(HERE/'native-tintless-core.c'),'library_sha256':shaf(so)},'resampler_differential':rp,'sequential_differential':{'g1_g3_outputs_exact':True,'wrapper_state_exact':True,'core_state_exact':True,'generations':gens},'timing_ms':{'iterations':a.iterations,'parser':ps,'dynamic_interp_cal_native_resample':ds,'hybrid_g1':hsx[0],'hybrid_g2':hsx[1],'hybrid_g3':hsx[2],'wire_allowance_ms':0.25,'w_cached_conservative_p95_ms':round(cached,6),'dynamic_conservative_p95_ms':round(dynamic,6)},'deadline':{'w_cached_branch_pass':True,'arbitrary_ratio_dynamic_branch_pass':True},'classification':'Scheduling/ABI proof only: W trigger state and U Linux statistics are independent streams. This proves the producer can meet the +3 scheduling law and preserves clean-room bytes; it does not claim W/U output parity.','next_gate':'Acquire Linux request-local AEC lux/CCT state early enough to select the front LSC tree, then perform a bounded live producer-to-existing-V4L2-IQ FIFO integration proof. Do not substitute dynamic R5/R6 before that trigger-state gate is closed.'}
  a.manifest.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result,indent=2,sort_keys=True));print('E003I_X_NATIVE_LIVE_LSC_DEADLINE=PASS')
if __name__=='__main__':main()
