#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,importlib.util,json,struct,sys,tempfile,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
EFILE=BASE/'e-template-free-capsule/build-template-free-0076-capsules.py'
FFILE=BASE/'f-native-iq-backends/generate-steady-scalar-state.py'
DVFILE=BASE/'dv-live-residual-isp-demux/demux_bls.py'
ELFILE=BASE/'el-calibrated-awb-scalar-join/awb_scalar.py'
DSFILE=BASE/'ds-live-iq-producer-awb-hold/live-iq-producer.py'
XFILE=BASE/'x-native-live-lsc-deadline/prove-native-live-lsc-deadline.py'
JFILE=BASE/'j-cleanroom-gtm/generate-cleanroom-gtm-wire.py'
EBRESULT=BASE/'eb-windows-r4-r12-gtm-state-oracle/RESULT.json'
ELREPLAY=BASE/'el-calibrated-awb-scalar-join/EA-LIVE-REPLAY.json'
FIX=HERE/'fixtures'

EXPECTED_TLBG={
1:'a1225991c2c7b9182262badf19d681bacc1fce1e1f6c1f1662768efe762434a2',
2:'a24c88ac5d8c95bd1f59887899c1f0611100c599243653caa8e753dfa3ee87b0',
3:'1d199c9cceb7047fc5fd7d3e33383f40a5a9894aa23f72e77533fc9f9e8c77d8',
4:'5960a862c73ebb9ed59e77c44d1a65d730cf20b23895f42f0a474f5322db4b43',
5:'e52f0ba64f578ba6982e98b851507c1a67f952878014d5d192637cdf00fc3652',
6:'d59c9c36315197707990ed331244b8dc1cfee3fe195e7288845dde9f3e2e613e'}
EXPECTED_LSC={
1:['73d785c93e0d3f9c33e3150ac63dc91e8de0415505eb1398fc1f379c46097db3','0fffd3414fd4a70b11b1c06688c87054d93c506887f3ab8a5292be173fbdd2f7','6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e','ee23d4744830d3e92817de00b8ac0cae9b0240bf5fbca08a302986a630fdcb44'],
2:['8d6afac38357b78b429019a388fcb0b7d8c34a2becc228b6fbd06ec365e57947','1c365bf7b94c3bcb339ea5c8de57cca623f221b4ffd24ccb679502f4bd8ed207','6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e','1e660ce6d441d533ad79cbf1501157def2d4a780119f6442de56b3df617c4d16'],
3:['d07c4d1ccfe32e6c2c38e4cf89b13de2ba1e86cce2ce009fa7f9887918992cca','9d92fcc69756d49723f5bc457cd1be2f8342533adc5fc5fb7f5f100de8ca2e03','6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e','0bf2c222476df0cb91d95b8c712333787ec028c9ac66d92284d416a5e12ca20a'],
4:['cb5aa391182d30c13045e60a0e1a77944d3aae5e71ff93ca9802ecc3a379b2ca','c3a97b344f43069d15c0cf9bfbbe97db2d1a06f30fef1015e16d290ce5a87023','6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e','5ac3693e93695357bb6f539421737e4d167157136cdac6e736b5eba8eeed9378'],
5:['08ff95a03dfdecf0590202f2c2e10aa28a14c7e8c492d0410cd825558d350da3','a10497a7127d7de30096ef3a4baf27b83469bfc7a0069efe5290f6b7f57fb7b7','6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e','db71f9bb5fbd74ccf31f9726246a22b3a53f86dc4e797f0a594363d0ae0a354c'],
6:['d284fb8a3424327604971d498b1de62f6ed5ca69a30393a83cb5db2a87ff9b9d','7f02ebe71708ae7f3234cb296db9d56463582206ff8d750fa671d1e07aff05c9','6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e','32ef1abb9b9b9a4012f471118d9f4be34e01b55e70128518d8837b7be7641e03']}
CQ_BITS={1:0x3f802d08,2:0x3f800544,3:0x3f801646,4:0x3f801646,5:0x3f801646,6:0x3f801646}
GTM_SHA='074564f99a45d29a5dbe800c18bc0436735f70740cb8f42cd9a5c7b636ffcdfa'
INVARIANT_DMI={'PDPC0','BPC_ABF0','GAMMA0','GAMMA1','GAMMA2','DSX0','DSX1','DSX2','DSX3'}
PMASK={1:[0],2:[1,2,3],4:[4],5:[5],6:[6],7:[7,8,9],8:[10,11,12,13]}

def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def sha(b):return hashlib.sha256(bytes(b)).hexdigest()
def fbits(u):return struct.unpack('<f',struct.pack('<I',u))[0]
def need(v,m):
 if not v:raise RuntimeError(m)

def build_gtm(J):
 eb=json.loads(EBRESULT.read_text());need(eb['status']=='PASS_WINDOWS_ORACLE','EB authority');need(eb['post_r6_tmc_state_law']=='stable' and eb['post_r6_gtm_output_law']=='stable','EB post-R6 GTM law')
 row=next(x for x in eb['rows'] if x['request']==6)
 ranges={'HDR':(0x8,0xc),'MODE':(0x74,4),'BLEND':(0x109c,8),'SRC':(0x5104,0x1c),'DST':(0x5120,0x1c),'COEF':(0x51b0,0x3c),'DOMAIN':(0x6228,0x1000)}
 t=bytearray(0x7228)
 for n,(o,l) in ranges.items():
  b=(FIX/f'EB-R6-TMC-{n}.bin').read_bytes();need(len(b)==l,f'TMC {n} size');t[o:o+l]=b
 dyn=t[0x74:0x78]+t[0x109c:0x10a4]+t[0x5104:0x5120]+t[0x5120:0x513c]+t[0x51b0:0x51ec]+t[0x6228:0x7228]
 need(sha(dyn)==row['tmc_dynamic_sha256'],'EB R6 TMC fixture drift')
 need(struct.unpack_from('<III',t,8)==(5,0x60800,1) and struct.unpack_from('<I',t,0x74)[0]==2 and t[0x109c:0x10a4]==b'\0'*8,'EB R6 GTM branch')
 got=J.generate(bytes(t),J.load_domain(BASE/'j-cleanroom-gtm'));need(sha(got)==GTM_SHA,'post-R6 clean GTM mismatch');return got,sha(dyn)

def base_payloads(E,raw4,slot4):
 slots={}
 for req in (4,5,6):
  _,slot,_=E.raw_request(REPO,req,raw4,slot4);slots[req]=slot
 for name,o,n in E.DMI_SOURCE:
  if name in INVARIANT_DMI:
   vals=[slots[r][o:o+n] for r in (4,5,6)];need(vals[0]==vals[1]==vals[2],f'{name} not invariant')
 _,slot6,_=E.raw_request(REPO,6,raw4,slot4)
 return [slot6[o:o+n] for _,o,n in E.DMI_SOURCE]

def module_state(E,F,DV,req,isp_gain_bits,awb_output):
 regs={};regs.update(F.banks(req));dm=DV.calculate(fbits(isp_gain_bits));regs.update({0x3b70:dm['reg_3b70'],0x3b74:dm['reg_3b74']})
 a=awb_output; regs.update({k:v for k,v in a['registers'].items() if k in E.REG_SLOT})
 needed=set(E.REG_SLOT);need(set(regs)==needed,f'R{req} module register ownership missing={needed-set(regs)} extra={set(regs)-needed}')
 values=[[0]*6 for _ in E.MODULES];vmask=[0]*len(E.MODULES)
 for r in E.static_recipe(REPO)[1]['dynamic_register_fields']:
  ro=int(r['register_offset'],16);mi,si=E.REG_SLOT[ro];values[mi][si]=regs[ro];vmask[mi]|=1<<si
 pmask=[0]*len(E.MODULES)
 for mi,indices in PMASK.items():
  for j,_ in enumerate(indices):pmask[mi]|=1<<j
 mod=bytearray()
 for i in range(len(E.MODULES)):mod+=struct.pack('<BBH6I4x',vmask[i],pmask[i],0,*values[i])
 need(len(mod)==0x120,'module size')
 return bytes(mod),regs,dm,a

def run(output_dir:Path,result_path:Path):
 E=load(EFILE,'em_e');F=load(FFILE,'em_f');DV=load(DVFILE,'em_dv');EL=load(ELFILE,'em_el');DS=load(DSFILE,'em_ds');X=load(XFILE,'em_x');J=load(JFILE,'em_j')
 _,variant,main,raw4,slot4,startup,start_payloads,sp,pp=E.static_recipe(REPO);base=base_payloads(E,raw4,slot4);gtm,tmc_sha=build_gtm(J)
 replay=json.loads(ELREPLAY.read_text());need(replay['source_capture']=='EA_attempt1_pass_20260911T0348' and replay['all_generations_hold_previous'],'EA replay authority');rows={int(x['generation']):x for x in replay['rows']};need(set(rows)==set(range(1,7)),'EA row coverage')
 output_dir.mkdir(parents=True,exist_ok=True);caps={};manifest_rows=[];awb=EL.CalibratedAWB()
 with tempfile.TemporaryDirectory(prefix='em-tintless-') as td:
  so=Path(td)/'libtintless.so';X.compile_native(so);lsc=DS.DynamicLsc(so)
  for gen in range(1,7):
   tb=(FIX/f'TLBG-G{gen}.bin').read_bytes();need(sha(tb)==EXPECTED_TLBG[gen],f'G{gen} TLBG drift');idt,raw=DS.parse_tlbg(tb);need(idt[0]==gen,f'G{gen} identity')
   row=rows[gen];lux=fbits(int(row['lux_bits'],16));cct=fbits(int(row['cct_bits'],16));wire,lm=lsc.run(raw,lux,cct);wh=[sha(x) for x in wire];need(wh==EXPECTED_LSC[gen],f'G{gen} LSC sequential drift')
   # Advance GainAdj selector state on every generation, even before the first EM target.
   dec=[int(x,16) for x in row['decision_bits']];awarm=awb.run(fbits(dec[0]),fbits(dec[1]),lux,cct,1.0)
   if gen<4:continue
   req=gen+3;need(req in (7,8,9),'target law');module,regs,dm,a=module_state(E,F,DV,req,CQ_BITS[gen],awarm)
   pay=list(base);pay[1],pay[2],pay[3],pay[4]=wire;pay[6]=gtm
   state={'module':module,'payload':pay,'source':'template-free: invariant R4-R6 payload oracles + sequential EA LSC + clean stable EB GTM + CQ/EL scalars'}
   t0=time.perf_counter_ns();cap,desc=E.compose(req,main,startup,start_payloads,sp,pp,state);compose_ms=(time.perf_counter_ns()-t0)/1e6;need(len(cap)==41088,'capsule size')
   op=output_dir/f'E003I_EM_R{req}.bin';op.write_bytes(cap);caps[req]=cap
   manifest_rows.append({'generation':gen,'request':req,'capsule_sha256':sha(cap),'module_sha256':sha(module),'compose_ms':compose_ms,
    'cq_isp_gain_bits':f'0x{CQ_BITS[gen]:08x}','demux':{'0x3b70':f"0x{regs[0x3b70]:08x}",'0x3b74':f"0x{regs[0x3b74]:08x}"},
    'awb_triangle':a['gain_adjust']['triangle'],'awb_dynamic_regs':{f'0x{k:04x}':f'0x{regs[k]:08x}' for k in (0x3d78,0x3d7c,0x3d80,0x3d84,0x456c,0x4570)},
    'bank_regs':{f'0x{k:04x}':regs[k] for k in sorted(F.banks(req))},'lsc_payload_sha256':wh,'gtm_sha256':sha(gtm),
    'section_sha256':[{'type':t,'index':i,'bytes':n,'sha256':h} for t,i,o,n,h in desc]})
 # Strong cross-request laws.
 need(len({sha(caps[r]) for r in caps})==3,'R7-R9 capsules should differ')
 need([manifest_rows[i]['bank_regs']['0x5a58'] for i in range(3)]==[1,0,1],'GTM bank parity')
 need(all(r['gtm_sha256']==GTM_SHA for r in manifest_rows),'GTM carry')
 result={'schema':'sp11-e003i-em-r7-r9-template-free-composer-v1','status':'PASS_OFFLINE_COMPONENT_COMPOSITION','requests':[7,8,9],
  'capsule_template_reads':0,'raw_r7_r9_capsule_reads':0,'raw_r7_r9_dmi_slot_reads':0,'capsule_bytes':41088,
  'selection_law':'R7<-EA G4, R8<-EA G5, R9<-EA G6','ea_sequential_lsc':'G1..G6 replayed in order',
  'post_r6_tmc_dynamic_sha256':tmc_sha,'post_r6_clean_gtm_sha256':GTM_SHA,'post_r6_gtm_law':'stable payload + parity bank',
  'invariant_payloads':sorted(INVARIANT_DMI),'lsc2_invariant_sha256':EXPECTED_LSC[6][2],
  'component_authority':{'banks':'F parity backend','demux':'DV exact CQ residual-gain backend','awb_scalars':'EL calibrated stateful GainAdj + PDPC/WB','lsc':'DS clean sequential Tintless/LSC on EA TLBG','gtm':'J clean packer on EB-proven stable R6 TMC carry','transport':'E template-free capsule composer'},
  'whole_capsule_windows_r7_r9_byte_oracle':False,'linux_camera_runtime':False,'continuous_aec_claimed':False,'rows':manifest_rows}
 result_path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');return result

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,default=Path('/tmp/e003i-em-r7-r9'));ap.add_argument('--result',type=Path,default=HERE/'RESULT.json');a=ap.parse_args();o=run(a.output_dir,a.result);print('EM_R7_R9=PASS');print('CAPSULES',','.join(f"R{x['request']}:{x['capsule_sha256']}" for x in o['rows']))
if __name__=='__main__':main()
