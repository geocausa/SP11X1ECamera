#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Original CC131 common/packer/builder; preserve existing measured Q7 data."""
from pathlib import Path
import hashlib,importlib.util,json,random,resource,struct,subprocess,sys
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
Q=Path(__file__).resolve().parent;R=Q.parents[3]
PRE=R/'src/upstream/isp-config/front-channel-gain-20261014/test-native.py'
NATIVE=R/'src/native-rgb/front-pattern/native-front-cst.inc'
RUN=R.parents[1]/'02-kernel/front-ae-93/run-93.json'
RUN_PIN='a5f27787588c2bb0297b57ff672b912f96ec34e3628be0904bcdc12e37f7e0d1'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('retained_native_map',PRE)
retained=importlib.util.module_from_spec(spec);spec.loader.exec_module(retained)
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
class Fixture:
 def __init__(self):
  self.n=retained.old.Native();self.u=self.n.u;self.base=self.n.base
  pe=retained.old.pefile.PE(str(retained.old.DLL))
  assert struct.unpack('<Q',pe.get_data(0x1620188,8))[0]==self.base+0x9ade70
  self.original=bytes(self.u.mem_read(self.base,pe.OPTIONAL_HEADER.SizeOfImage))
  self.arena=0x78000000;self.u.mem_map(self.arena,0x20000)
  self.phase='idle';self.instructions=0;self.observed=[]
  self.u.hook_add(UC_HOOK_CODE,self.code);self.u.hook_add(UC_HOOK_MEM_WRITE,self.write)
 def code(self,u,address,size,_):
  if self.phase=='idle':return
  self.instructions+=1
  if self.phase=='builder' and address==self.base+0x85ee78:
   cmd,reg,count,values=[u.reg_read(x) for x in [UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,UC_ARM64_REG_X3]]
   assert cmd==self.cmd and (reg,count) in [(0x5860,1),(0x5868,10)]
   assert values==self.image+(0 if count==1 else 4)
   self.observed.append((reg,count,bytes(u.mem_read(values,count*4))))
   u.reg_write(UC_ARM64_REG_X0,0);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR));return
  if self.phase=='common' and self.base+0x14d0<=address<self.base+0x14d8:return
  lo,hi={'common':(0x9ade70,0x9adfd0),'packer':(0xb43910,0xb43ac8),'builder':(0xb43340,0xb43428)}[self.phase]
  assert self.base+lo<=address<self.base+hi,'unmodeled source instruction'
 def write(self,u,access,address,size,value,_):
  if self.phase=='idle':return
  if self.n.stack<=address and address+size<=self.n.stack+0x10000:return
  if self.phase=='common':assert self.common<=address and address+size<=self.common+28
  else:assert self.phase=='packer' and self.image<=address and address+size<=self.image+44
 def invoke(self,rva,phase):
  u=self.u;self.phase=phase
  regs=[globals()['UC_ARM64_REG_X'+str(i)] for i in range(19,30)]
  regs += [globals()['UC_ARM64_REG_D'+str(i)] for i in range(8,16)]
  values=[0x12300000+i*0x101 for i in range(11)]+[0x3ff0000000000000+i for i in range(8)]
  for reg,v in zip(regs,values):u.reg_write(reg,v)
  sp=self.n.stack+0xf000
  args=[self.dep,self.region,self.reserve,self.enable,self.common] if phase=='common' else [self.obj,self.common if phase=='packer' else self.req,0]
  for i,v in enumerate(args):u.reg_write(globals()['UC_ARM64_REG_X'+str(i)],v)
  u.reg_write(UC_ARM64_REG_SP,sp);u.reg_write(UC_ARM64_REG_LR,self.n.end)
  u.emu_start(self.base+rva,self.n.end,count=100000)
  assert u.reg_read(UC_ARM64_REG_PC)==self.n.end and u.reg_read(UC_ARM64_REG_X0)==(1 if phase=='common' else 0)
  assert u.reg_read(UC_ARM64_REG_SP)==sp and [u.reg_read(x) for x in regs]==values
  self.phase='idle'
 def setup(self,placement,seed):
  u=self.u;a=self.arena+placement;u.mem_write(self.arena,bytes(0x20000))
  self.obj=a+0x1000;self.image=a+0x3000;self.common=a+0x5000;self.req=a+0x7000;self.cmd=a+0x9000
  self.dep=a+0xa000;self.region=a+0xb000;self.reserve=a+0xc000;self.enable=a+0xd000
  u.mem_write(self.obj+32,struct.pack('<Q',self.image));u.mem_write(self.req+80,struct.pack('<Q',self.cmd))
  u.mem_write(self.image,struct.pack('<11I',*([seed]*11)))
  for p,n in [(self.image,44),(self.common,28)]:
   u.mem_write(p-16,b'\xa5'*16);u.mem_write(p+n,b'\x5a'*16)
 def pack(self):
  u=self.u;common=bytes(u.mem_read(self.common,28))
  watched=[(self.obj,128),(self.req,128),(self.region,48),(self.reserve,16),(self.dep,64),(self.enable,16)]
  before=[bytes(u.mem_read(p,n)) for p,n in watched]
  self.invoke(0xb43910,'packer');image=bytes(u.mem_read(self.image,44))
  self.observed=[];self.invoke(0xb43340,'builder')
  assert self.observed==[(0x5860,1,image[:4]),(0x5868,10,image[4:])]
  assert bytes(u.mem_read(self.common,28))==common and bytes(u.mem_read(self.image,44))==image
  for (p,n),v in zip(watched,before):assert bytes(u.mem_read(p,n))==v
  for p,n in [(self.image,44),(self.common,28)]:
   assert bytes(u.mem_read(p-16,16))==b'\xa5'*16 and bytes(u.mem_read(p+n,16))==b'\x5a'*16
  return struct.pack('<2I',0x0300000a,0x5868)+image[4:]
 def direct(self,placement,matrix,offsets,q,seed=0):
  self.setup(placement,seed)
  self.u.mem_write(self.common,struct.pack('<14H',0,*[x&0xffff for x in matrix+offsets],q))
  return self.pack()
 def produced(self,placement,matrix,q):
  self.setup(placement,0)
  region=[0.0]*12
  # Existing measured matrix is GBR. Source common consumes RGB ordering.
  for i,j in enumerate([4,5,3,7,8,6,1,2,0]):region[j]=matrix[i]/128
  self.u.mem_write(self.region,struct.pack('<12f',*region))
  self.u.mem_write(self.reserve,struct.pack('<I',q))
  watched=[(self.dep,64),(self.region,48),(self.reserve,16),(self.enable,16)]
  before=[bytes(self.u.mem_read(p,n)) for p,n in watched]
  self.invoke(0x9ade70,'common')
  fields=struct.unpack('<14h',self.u.mem_read(self.common,28))
  assert fields[0]==0 and fields[1:10]==tuple(x*(1<<q) for x in matrix)
  assert fields[10:13]==(0,0,0) and fields[13]==q
  for (p,n),v in zip(watched,before):assert bytes(self.u.mem_read(p,n))==v
  return list(fields[1:10]),self.pack()
 def unchanged(self):assert bytes(self.u.mem_read(self.base,len(self.original)))==self.original
def main():
 O=Path(sys.argv[1]);O.mkdir();assert sha(RUN)==RUN_PIN
 cfg=json.loads(RUN.read_text());items=[s for s in cfg['camss_params'] if s.startswith('native_front_ccm_q7=')];assert len(items)==1
 measured=[int(x) for x in items[0].split('=',1)[1].split(',')];assert len(measured)==9
 f=Fixture();records=[];source_cases=0;producer=0;rng=random.Random(681131)
 matrices=[measured,[128,0,0,0,128,0,0,0,128],[-2048]*9,[2047]*9]
 for field in range(9):
  for bit in range(11):
   m=[0]*9;m[field]=1<<bit;matrices.append(m)
 for i in range(32):matrices.append([rng.randrange(-2048,2048) for j in range(9)])
 def add(m,o,q,oracle):records.append(struct.pack('<I12h',q+7,*m,*o)+oracle)
 for placement in [0,128,512]:
  for q in range(4):
   m,oracle=f.produced(placement,measured,q);add(m,[0]*3,q,oracle);source_cases+=1;producer+=1
  for m in matrices:
   oracle=f.direct(placement,m,[0]*3,0);add(m,[0]*3,0,oracle);source_cases+=1
  for field in range(3):
   for val in [-4096,-1,1,4095]:
    offsets=[0]*3;offsets[field]=val
    oracle=f.direct(placement,measured,offsets,0);add(measured,offsets,0,oracle);source_cases+=1
 # Original common accepts q4, but the original packer's two-bit field wraps to0.
 m,alias=f.produced(0,measured,4);source_cases+=1
 assert struct.unpack_from('<I',alias,44)[0]==0 and any(abs(v)>2047 for v in m)
 # Nonzero residual image differs; own zero software state is a policy.
 clean=f.direct(0,measured,[0]*3,0);residual=f.direct(0,measured,[0]*3,0,0xffffffff);source_cases+=2
 assert clean!=residual
 f.unchanged()
 headers={
 'sp11-front-ccm-config.h':Q/'sp11-front-ccm-config.h',
 'sp11-front-ccm-measured.h':Q/'sp11-front-ccm-measured.h',
 'sp11-front-fields.h':R/'src/upstream/isp-config/sp11-front-fields.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():(O/n).write_bytes(p.read_bytes())
 (O/'test-host.c').write_bytes((Q/'test-host.c').read_bytes())
 original=(Q/'sp11-front-ccm-config.h').read_text()
 mutations={
 'uncleared_reserved_sign_bits':original.replace('&= 0x0fU;', '&= 0xffU;'),
 'wrong_slice':original.replace('coefficients + 8, 24','coefficients + 4, 24'),
 'early_publication':original.replace('\tif (!out || !policy || !state)','\tif (out)\n\t\tout[0] = 0;\n\tif (!out || !policy || !state)',1),
 'foreign_precision':original.replace('state->fractional_bits != 7','state->fractional_bits > 32'),
 'bypass_offsets':original.replace('if (state->offset[i])','if (state->offset[i] == 32767)'),
 'bypass_domain':original.replace('ret = sp11_front_cold_fields(checked, sizeof(checked), policy);','ret = 0;\n\t(void)checked;')}
 assert all(s!=original for s in mutations.values());runs=[];data=b''.join(records)
 for cc in ['gcc','clang']:
  for label,source in [('actual',original),*mutations.items()]:
   (O/'sp11-front-ccm-config.h').write_text(source);exe=O/(cc+'-'+label)
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
    '-fno-omit-frame-pointer','-I'+str(O),str(O/'test-host.c'),'-o',str(exe)],capture_output=True,text=True)
   assert p.returncode==0,p.stderr[-2500:]
   p=subprocess.run([str(exe)],input=data,capture_output=True,timeout=20)
   (O/(cc+'-'+label+'.log')).write_bytes(p.stdout+p.stderr)
   if label=='actual':
    assert p.returncode==0,p.stderr[-2500:].decode()
    res=json.loads(p.stdout);assert res['admitted_native_cases']+res['rejected_other_policy_cases']==len(records)
    runs.append({'compiler':cc,'ASan_UBSan':True,'result':res})
   else:assert p.returncode!=0,'unsafe compiled mutation survived '+label
 (O/'sp11-front-ccm-config.h').write_text(original)
 result={'schema':'sp11-front-ccm-source-v1','status':'PASS_OWN_MEASURED_Q7_COMPLETE_CONFIGURATION',
 'original_PE_sha256':retained.old.DLL_SHA,'original_PE_immutable':True,'original_PE_exported':False,
 'source_cases':source_cases,'comparison_records':len(records),'original_common_cases':producer+1,'original_common_comparison_cases':producer,
 'native_instructions':f.instructions,'placements':3,'SP_callee_saved_restored':True,'canaries_intact':True,
 'native_entries':{'common':'0x9ade70','packer':'0xb43910','builder':'0xb43340','original_FRINTA':'0x14d0'},
 'CC131_source_dispatch_table_rva':'0x1620188','original_common_scale_relation':'fractional_bits = qfactor + 7',
 'packer_factor_bits':2,'source_common_qfactor4_packer_wrap_counterexample':True,
 'source_unpacked_fields':'enable, nine GBR coefficients, three offsets, scale control',
 'source_coefficient_field_bits':12,'retained_coefficient_encoder_bits':13,
 'coefficient_numeric_values_unchanged':True,'canonicalized_reserved_sign_fill':True,
 'source_offset_field_bits':13,'source_offset_shift':19,
 'intercepted_helpers':['0x85ee78 command observer/success only'],'arithmetic_or_branch_shims':False,
 'original_builder_fixed_addresses_observed':True,'addresses_substituted':False,'constructor_executed':False,
 'initial_image':'own zero','nonzero_residual_counterexample_checked':True,
 'own_measured_matrix_q7':measured,'own_run93_sha256':RUN_PIN,
 'new_optical_fit':False,'own_policy_offsets':[0,0,0],'own_policy_scale_control':0,
 'configuration_words':10,'configuration_bytes':48,'module_control_commands_emitted':0,
 'compiler_runs':runs,'compiled_mutations_rejected_each':list(mutations),
 'header_pins':{n:sha(p) for n,p in headers.items()},
 'prior_reference_pins':{str(PRE.relative_to(R)):sha(PRE),str(NATIVE.relative_to(R)):sha(NATIVE)},
 'private_profile_read':False,'private_tuning_read':False,'pixels_read':False,'calibration_remeasured':False,
 'installed':False,'loaded':False,'runtime_changed':False,'hardware':False,
 'limits':['Source binds coefficient Q7 to scale0; it does not establish physical CCM input/output sample precision',
 'Zero offsets and software image are own policies, not equality with inherited private startup or physical reset',
 'No module enable, whole colour-chain precision, core/Gamma/Crop12/DMI/startup ownership integration',
 'Existing measured matrix is reused only in its admitted native2160-to1440 calibration domain; physical new-path image parity remains required']}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','source_cases','comparison_records','original_common_cases','native_instructions','hardware']}))
if __name__=='__main__':main()
