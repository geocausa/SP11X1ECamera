#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,importlib.util,json,struct,tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
PROD=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
KDIR=HERE.parent/'k-cleanroom-lsc-backend'
IDIR=HERE.parent/'i-cleanroom-tintless'
TUNING=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.tuned.ffc_imx681.bin')
TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
X1_SHA='8ce68010d1126105ae68490294bc6b3f2598dfe5dfc88ff5df40f8926efd9d86'
STATS_SHA={4:'9778a7315a7f052042252717e5454f4f508bf202a1d301f766183bd40b8c741f',5:'ed4123ce369f614276cc1aca6436636f8dcd19b544063250af12aedeff488d9d',6:'ab2effdc589836fa5d1ab16e2fd68a57d9605e2a024edf9415d1ec8515dbe63c'}
OUT_SHA={4:'7a07b0cd8a4166893ec82809992db1800f1e401cd66faad6e67227d4951c28e0',5:'009e829e3c872396833786cc8806118a14fc0321e32a5cd0cc6fe84cdf9a9dbd',6:'0c368d77a59db21ae1b871498a5a0365154472dae30ff783607ca1317c9bc60b'}

X1=0x260000003000
X2={4:0x260000010000,5:0x260000030000,6:0x260000050000}
D3=0x260000070000;D4=0x260000071000
IN=0x260000080000;OUT=0x260000090000
WRAP=0x260000001000;CORE=0x260000100000;ADAPT=0x260000140000

def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
def sha(b):return hashlib.sha256(b).hexdigest()
def shaf(p):return sha(p.read_bytes())
def need(v,msg):
 if not v:raise RuntimeError(msg)

def find_tintless23_region(dec,blob,hdr,recs):
 obj=hdr['sections'][1]
 roots=[r for r in recs.values() if r['type']=='tintless23_sw_v2']
 need(len(roots)==1,'Tintless23 root not unique')
 seen=set();todo=[roots[0]['symbol_id']];regions=[]
 while todo:
  sid=todo.pop()
  if sid in seen:continue
  seen.add(sid);r=recs[sid]
  if r['type']=='region' and r['data_bytes']:
   regions.append(dec.data_bytes(blob,obj,r));continue
  for ref in dec.child_refs(blob,obj,recs,r):todo.append(ref['symbol_id'])
 cand=[x for x in regions if len(x)==264]
 need(len(cand)==1,'active Tintless23 264-byte region not unique')
 return cand[0]

def build_front_x1():
 dec=load(PROD/'decode_imx681_chromatix.py','e003i_m_dec')
 need(shaf(TUNING)==TUNING_SHA,'front tuning SHA drift')
 blob=TUNING.read_bytes();hdr=dec.parse_header(blob);recs,_=dec.parse_symbol_table(blob,hdr['sections'][0],hdr['sections'][1])
 region=find_tintless23_region(dec,blob,hdr,recs);rv=struct.unpack('<66f',region)
 out=bytearray(0x130)
 def w32(o,v):struct.pack_into('<I',out,o,int(v)&0xffffffff)
 def wf(o,v):struct.pack_into('<f',out,o,float(v))
 # Tintless rolloff ABI: 17x13 table, 30x24 subgrid, 8 subgrids, offsets 0/72.
 for o,v in zip(range(0,0x1c,4),(17,13,30,24,8,0,72)):w32(o,v)
 # Front Tintless-BG config: 3840x2160, 120x90 regions, 32x24 cells, 18-bit, postBayer=0.
 for o,v in zip(range(0x1c,0x58,4),(3840,2160,120,90,32,24,0,0x3fffe,0x3fffe,0x3fffe,0x3fffe,18,0,0,0)):w32(o,v)
 # Surface Tintless23 active-region mapping. First 16 threshold floats become uint8.
 for i in range(16):out[0x58+i]=int(rv[i]+0.5)&0xff
 out[0x68]=int(rv[16]+0.5)&0xff;out[0x69]=int(rv[48]+0.5)&0xff;out[0x6a]=int(rv[49]+0.5)&0xff
 wf(0x6c,rv[50]);wf(0x70,rv[51]);wf(0x74,rv[52])
 w32(0x78,1)              # IFE temporal filtering enabled
 w32(0x7c,2);w32(0x80,2) # validated active mode-2 core
 wf(0x84,16.0)
 for i,v in enumerate(rv[16:32]):wf(0x88+i*4,v)
 for i,v in enumerate(rv[32:48]):wf(0xc8+i*4,v)
 w32(0x108,0)
 for i,v in enumerate(rv[54:62]):wf(0x10c+i*4,v)
 w32(0x12c,2)
 need(sha(out)==X1_SHA,'generated front x1 SHA drift')
 return bytes(out),sha(region)

def descriptor(base):
 b=bytearray(0x28);struct.pack_into('<H',b,0,221)
 for i,o in enumerate((8,0x10,0x18,0x20)):struct.pack_into('<Q',b,o,base+i*0x374)
 return bytes(b)

def normalized_wrapper_target(cap,req):
 b=bytearray((cap/f'req{req}_wrapper_pre.bin').read_bytes());b[:8]=bytes(8);b[0x128:0x130]=struct.pack('<Q',CORE);return bytes(b)

def run(cap,K,C,pre,x1,core_fill=0,out_mode='zero'):
 m=K.SparseMemory();m.mem_write(WRAP,bytes(0x1090));m.fill(CORE,C.CORE_BYTES,core_fill);m.mem_write(ADAPT,bytes(0x1000));m.mem_write(X1,x1)
 d3=descriptor(IN);d4=descriptor(OUT);m.mem_write(D3,d3);m.mem_write(D4,d4)
 result={}
 for req in (4,5,6):
  if req>4:
   need(m.mem_read(WRAP,0x1090)==normalized_wrapper_target(cap,req),f'R{req} generated wrapper carry drift')
   wantc=(cap/f'req{req}_core_pre.bin').read_bytes();need(m.mem_read(CORE,len(wantc))==wantc,f'R{req} generated core carry drift')
  stats=(cap/f'req{req}_x2_stats.bin').read_bytes();need(sha(stats)==STATS_SHA[req],f'R{req} stats SHA drift')
  need(len(stats)==0x12bec and struct.unpack_from('<I',stats,0)[0]==3 and struct.unpack_from('<I',stats,4)[0]==0x300,f'R{req} stats layout drift')
  m.mem_write(X2[req],stats);m.mem_write(IN,pre[req]+bytes(0x20));seed=K.output_seed(out_mode);m.mem_write(OUT,seed)
  rc=C.wrapper_front_mode2(m,WRAP,X1,X2[req],D3,D4,CORE if req==4 else 0,ADAPT);need(rc==0,f'R{req} Tintless rc={rc}')
  got=m.mem_read(OUT,0xdf0);need(sha(got[:0xdd0])==OUT_SHA[req],f'R{req} output drift');need(got[0xdd0:]==seed[0xdd0:],f'R{req} output tail changed')
  want=(cap/f'req{req}_output_mesh_post.bin').read_bytes();need(got[:0xdd0]==want[:0xdd0],f'R{req} Windows output mismatch')
  l0,l1,l2,gic=K.wire_from_output(got);obs={'lsc0':sha(l0),'lsc1':sha(l1),'gic':sha(gic)};need(obs==K.WIRE_EXPECTED[req],f'R{req} wire drift')
  result[req]={'output_abi':got[:0xdd0],'lsc0':l0,'lsc1':l1,'lsc2':l2,'gic':gic}
 return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--capture-dir',type=Path,default=REPO.parent/'.local-oracles/oracle-live-20260904-front-atomic');ap.add_argument('--output-dir',type=Path,default=Path('/tmp/e003i-m-stats-only-lsc'));ap.add_argument('--manifest',type=Path);a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
 K=load(KDIR/'generate-cleanroom-front-lsc-wire.py','e003i_m_k');C=load(IDIR/'cleanroom-tintless-helpers.py','e003i_m_c');pre,pre_detail=K.build_pretintless(REPO);x1,region_sha=build_front_x1()
 # Captured x1 is validation only: prove constructor identity, never feed it to run().
 for req in (4,5,6):need((a.capture_dir/f'req{req}_x1_config.bin').read_bytes()==x1,f'R{req} x1 constructor validation drift')
 cases=[('zero',0),('a5',0),('ones',0),('zero',0xa5)];runs={(mode,fill):run(a.capture_dir,K,C,pre,x1,fill,mode) for mode,fill in cases};base=runs[('zero',0)]
 for req in (4,5,6):
  for rr in runs.values():
   for key in ('output_abi','lsc0','lsc1','lsc2','gic'):need(rr[req][key]==base[req][key],f'R{req} counterfactual drift {key}')
  for name in ('lsc0','lsc1','lsc2','gic'):(a.output_dir/f'R{req}_{name.upper()}.bin').write_bytes(base[req][name])
  print(f'R{req} STATS_ONLY_LSC PASS stats={STATS_SHA[req]} LSC0={sha(base[req]["lsc0"])}')
 man={'schema':'sp11-e003i-stats-only-front-lsc-v1','accepted':True,'generated_x1_sha256':sha(x1),'tintless23_region_sha256':region_sha,'production_inputs':['front tuning','front OTP','LSC interpolation ratio/request trigger state','raw 768-region Tintless statistics'],'constructed_internally':['fresh wrapper/core state','x1 Tintless configuration','x3 input descriptor','x4 output descriptor','pre-Tintless mesh','Tintless temporal carry','Titan680 LSC/GIC wire'],'validation_only':['captured x1 config','captured x3/x4 descriptors','captured request5/6 wrapper/core carry','captured output mesh post'],'device_mft_required':False,'unicorn_required':False,'request_stats_sha256':{str(k):v for k,v in STATS_SHA.items()},'remaining_lsc_live_input':'raw Tintless statistics plus ordinary trigger state for tuning interpolation','safety':{'offline_only':True,'linux_camera_runtime':False}}
 mp=a.manifest or a.output_dir/'MANIFEST.json';mp.write_text(json.dumps(man,indent=2,sort_keys=True)+'\n');print('STATS_ONLY_FRONT_LSC=PASS');print('MANIFEST',mp)
if __name__=='__main__':main()
