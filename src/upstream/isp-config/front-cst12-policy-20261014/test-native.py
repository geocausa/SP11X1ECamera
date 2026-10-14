#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Bind existing complete CST encoding to original source on owned state only."""
from pathlib import Path
import hashlib,importlib.util,json,random,resource,struct,subprocess,sys
from unicorn.arm64_const import *
Q=Path(__file__).resolve().parent;R=Q.parents[3]
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
PRE=R/'src/upstream/isp-config/front-channel-gain-20261014/test-native.py'
assert sha(PRE)=='8b1fbceb4516d97b141f6cc9fdf3e3ff13fe0bdfa48c0fa5e81ac9ffa6183a0e'
spec=importlib.util.spec_from_file_location('prior_owned_fixture',PRE)
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
class Fixture(prior.Fixture):
 def code(self,u,address,size,unused):
  if self.phase=='idle':return
  self.count+=1
  if self.phase=='builder' and address==self.base+0x85ee78:
   cmd,reg,count,values=(u.reg_read(x) for x in [UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,UC_ARM64_REG_X3])
   assert cmd==self.cmd and (reg,count) in [(0x6160,1),(0x6168,18)]
   assert values==self.image+(0 if count==1 else 4)
   self.observed.append((reg,count,bytes(u.mem_read(values,count*4))))
   u.reg_write(UC_ARM64_REG_X0,0);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR));return
  lo,hi=(0xb4d900,0xb4db60) if self.phase=='packer' else (0xb4d390,0xb4d4a0)
  assert self.base+lo<=address<self.base+hi,'unmodeled original branch'
 def write(self,u,access,address,size,value,unused):
  if self.phase=='idle':return
  if self.native.stack<=address and address+size<=self.native.stack+0x10000:return
  assert self.phase=='packer' and self.image<=address and address+size<=self.image+76,'unowned write'
 def vector(self,placement,values,minimum,maximum,seed=0):
  u=self.u;a=self.arena+placement
  self.obj=a+0x100;request=a+0x1000;self.image=a+0x5000
  self.common=a+0x6000;self.meta=a+0x7000;self.cmd=a+0x8000
  u.mem_write(self.arena,bytes(0x20000))
  u.mem_write(self.obj+32,struct.pack('<Q',self.image))
  u.mem_write(request+80,struct.pack('<Q',self.cmd))
  h=[0,*minimum,*maximum,*values]
  common=struct.pack('<22H',*(x&0xffff for x in h));u.mem_write(self.common,common)
  u.mem_write(self.image-16,b'\xa5'*16);u.mem_write(self.image+76,b'\x5a'*16)
  u.mem_write(self.image,struct.pack('<19I',*([seed]*19)))
  obj=bytes(u.mem_read(self.obj,128));desc=bytes(u.mem_read(request,0x2020))
  self.desc=self.common;self.invoke(0xb4d900,'packer')
  image=bytes(u.mem_read(self.image,76))
  self.desc=request;self.observed=[];self.invoke(0xb4d390,'builder')
  assert self.observed==[(0x6160,1,image[:4]),(0x6168,18,image[4:])]
  assert bytes(u.mem_read(self.obj,128))==obj and bytes(u.mem_read(request,0x2020))==desc
  assert bytes(u.mem_read(self.common,44))==common and bytes(u.mem_read(self.image,76))==image
  assert bytes(u.mem_read(self.image-16,16))==b'\xa5'*16 and bytes(u.mem_read(self.image+76,16))==b'\x5a'*16
  return struct.pack('<2I',0x03000012,0x6168)+image[4:]
def main():
 O=Path(sys.argv[1]);O.mkdir()
 p=subprocess.run(['python3',str(Q/'generate-policy.py'),'--check'],capture_output=True,text=True);assert p.returncode==0,p.stderr
 f=Fixture()
 pe=prior.old.pefile.PE(str(prior.old.DLL))
 for target,name in [(0x151bda0,'CamX::IFECST12Titan680::PackIQRegisterSetting'),(0x151be48,'CamX::IFECST12Titan680::CreateCmdList')]:
  assert pe.get_data(target,len(name)+1)==name.encode()+b'\0'
 default=[601,117,306,-339,512,-173,-429,-83,512]
 matrices=[default,[0]*9,[4095]*9,[-4096]*9,[123,-234,345,-456,567,-678,789,-890,901]]
 for field in range(9):
  for bit in range(13):
   m=[0]*9;m[field]=-(1<<12) if bit==12 else 1<<bit;matrices.append(m)
 rng=random.Random(681612)
 for _ in range(64):matrices.append([rng.randrange(-4096,4096) for i in range(9)])
 states=[(1,m+[0,2048,2048]+[0]*3,[0]*3,[4095]*3) for m in matrices]
 # Existing encoder's auxiliary/offset/clamp fields still source-match; policy rejects them.
 for lane in range(3):
  for v in [-4096,-1,1,4095]:
   for start in [9,12]:
    values=default+[0,2048,2048]+[0]*3;values[start+lane]=v
    if values[9:12]==[0,2048,2048] and values[12:]==[0]*3:continue
    states.append((0,values,[0]*3,[4095]*3))
  for v in [0,1,1023,4094]:
   high=[4095]*3;high[lane]=v;states.append((0,default+[0,2048,2048]+[0]*3,[0]*3,high))
  low=[0]*3;low[lane]=1;states.append((0,default+[0,2048,2048]+[0]*3,low,[4095]*3))
 records=[];admitted=0;rejected=0
 for placement in [0,128,512]:
  for admit,values,low,high in states:
   oracle=f.vector(placement,values,low,high)
   records.append(struct.pack('<I15h6I',admit,*values,*low,*high)+oracle)
   admitted+=admit;rejected+=not admit
 clean=f.vector(0,default+[0,2048,2048]+[0]*3,[0]*3,[4095]*3)
 inherited=f.vector(0,default+[0,2048,2048]+[0]*3,[0]*3,[4095]*3,0xffffffff)
 assert clean!=inherited,'old image residual-bit counterexample absent'
 assert bytes(f.u.mem_read(f.base,len(f.original)))==f.original
 closure={
 'sp11-front-cst12-config.h':Q/'sp11-front-cst12-config.h',
 'sp11-front-cst12-policy.h':Q/'sp11-front-cst12-policy.h',
 'sp11-cst-stats.h':R/'src/upstream/isp-config/sp11-cst-stats.h',
 'sp11-front-fields.h':R/'src/upstream/isp-config/sp11-front-fields.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in closure.items():(O/n).write_bytes(p.read_bytes())
 (O/'test-host.c').write_bytes((Q/'test-host.c').read_bytes())
 source=(Q/'sp11-front-cst12-config.h').read_text()
 mutations={
 'wrong_configuration_slice':source.replace('memcpy(out, tmp + 12,','memcpy(out, tmp + 8,'),
 'premature_output':source.replace('\tif (!out || !policy || !state)','\tif (out)\n\t\tout[0] = 0;\n\tif (!out || !policy || !state)',1),
 'allow_foreign_precision':source.replace('gamma_bits != SP11_FRONT_CST12_BITS','gamma_bits > 31'),
 'bypass_calibration_policy':source.replace('ret = sp11_front_cold_fields(checked, sizeof(checked), policy);','ret = 0;\n\t(void)checked;')}
 assert all(s!=source for s in mutations.values())
 runs=[];data=b''.join(records)
 for cc in ['gcc','clang']:
  for label,s in [('actual',source),*mutations.items()]:
   (O/'sp11-front-cst12-config.h').write_text(s);exe=O/(cc+'-'+label)
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(O),str(O/'test-host.c'),'-o',str(exe)],capture_output=True,text=True)
   assert p.returncode==0,p.stderr[-2500:]
   p=subprocess.run([str(exe)],input=data,capture_output=True,timeout=15)
   (O/(cc+'-'+label+'.log')).write_bytes(p.stdout+p.stderr)
   if label=='actual':
    assert p.returncode==0,p.stderr[-2500:].decode()
    result=json.loads(p.stdout);assert result['accepted_native_configurations']==admitted and result['rejected_native_nonpolicy_states']==rejected
    runs.append({'compiler':cc,'ASan_UBSan':True,'result':result})
   else:assert p.returncode!=0,'unsafe mutation survived '+label
 (O/'sp11-front-cst12-config.h').write_text(source)
 refs=[str(PRE.relative_to(R)),'src/upstream/isp-config/open_config.py',
 'src/upstream/isp-config/CST-STATS-PROVENANCE-20261011.md',
 'experiments/E004-front-ir-vd55g0/e006r-rear-cst12-tuning-packer/camss-e006r-cst12.inc']
 result={'schema':'sp11-front-cst12-native-policy-v1',
 'status':'PASS_REUSED_CST_ENCODER_ORIGINAL_NATIVE_CONFIGURATION_AND_OWN_POLICY',
 'original_PE_sha256':prior.old.DLL_SHA,'original_image_immutable':True,'original_PE_exported':False,
 'native_packer':'0xb4d900','native_builder':'0xb4d390','source_declared_module_config':'0x6160',
 'source_declared_configuration':'0x6168','source_configuration_words':18,
 'native_instructions':f.count,'native_cases':len(records),'policy_admitted_cases':admitted,
 'policy_rejected_generic_source_cases':rejected,'placements':3,
 'original_named_callee_saved_and_SP_restored':True,'owned_inputs_and_canaries_intact':True,
 'nonzero_old_image_residual_counterexample':True,'constructor_executed':False,'initial_image_owned_zero_policy':True,
 'intercepted_helpers':['PacketBuilder0x85ee78 argument observation/success status'],
 'field_or_branch_shims':False,'compiler_runs':runs,'compiled_mutations_rejected_each':list(mutations),
 'header_pins':{n:sha(p) for n,p in closure.items()},'prior_reference_pins':{n:sha(R/n) for n in refs},
 'private_tuning_or_startup_read':False,'private_matrix_or_reserve_imported':False,
 'calibration_remeasured':False,'hardware':False,'runtime_changed':False,
 'limits':['Own full-range12-bit BT.601/zero suboffset policy is not inherited-front equality or physical precision proof',
 'Suboffset mathematical placement in the hardware datapath remains unqualified; only zero is admitted',
 'No activation/DMI/MMIO/core/rounding integration/private loader replacement; constructor not executed']}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','native_cases','policy_admitted_cases','policy_rejected_generic_source_cases','native_instructions','runtime_changed']}))
if __name__=='__main__':main()
