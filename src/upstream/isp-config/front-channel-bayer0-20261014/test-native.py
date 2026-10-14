#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reuse prior scalar oracle and producers; qualify missing startup fields only."""
from pathlib import Path
import hashlib,importlib.util,json,random,resource,struct,subprocess,sys
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
Q=Path(__file__).resolve().parent;R=Q.parents[3]
PRE=R/'experiments/E004-front-ir-vd55g0'
OLD=PRE/'e011ai-rear-neutral-scalar-full-integration/native-private.py'
PROD=PRE/'e012k-rear-neutral-scalar-clean-producer'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('retained_scalar_native',OLD)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
PRIOR=R/'src/upstream/isp-config/front-channel-gain-20261014/test-native.py'
assert sha(PRIOR)=='8b1fbceb4516d97b141f6cc9fdf3e3ff13fe0bdfa48c0fa5e81ac9ffa6183a0e'
spec=importlib.util.spec_from_file_location('retained_gain_fixture',PRIOR)
retained=importlib.util.module_from_spec(spec);spec.loader.exec_module(retained)
class Fixture(retained.Fixture):
 def derived(self,gain,channel):
  # Own semantic input fixture; original scalar code and prior emulator unchanged.
  u=self.u;h=self.native.heap
  u.mem_write(h,bytes(0x30000));u.mem_write(self.native.stack,bytes(0x10000))
  dep,region,reserve,enable,out=h,h+0x4000,h+0x8000,h+0xc000,h+0x10000
  u.mem_write(dep+0x10,b'\x00')
  u.mem_write(dep+0x1c,struct.pack('<f',gain));u.mem_write(dep+0x48,struct.pack('<I',0x60800))
  u.mem_write(region,struct.pack('<4f',0,0,0,0));u.mem_write(reserve,struct.pack('<4f',*channel))
  u.mem_write(enable,struct.pack('<4I',1,1,1,1))
  for reg,value in [(UC_ARM64_REG_X0,dep),(UC_ARM64_REG_X1,region),(UC_ARM64_REG_X2,reserve),
    (UC_ARM64_REG_X3,enable),(UC_ARM64_REG_X4,out),(UC_ARM64_REG_SP,self.native.stack+0xf000),
    (UC_ARM64_REG_LR,self.native.end)]:u.reg_write(reg,value)
  self.phase='common';u.emu_start(self.base+0x998e70,self.native.end,count=100000);self.phase='idle'
  assert u.reg_read(UC_ARM64_REG_PC)==self.native.end and u.reg_read(UC_ARM64_REG_X0)==1
  common=bytes(u.mem_read(out,52));h=struct.unpack('<26H',common);q=list(h[6:10])
  assert h[0]==1 and h[1]==0 and struct.unpack_from('<2I',common,4)==(0xac,0xc9)
  assert not any(h[10:]) and all(1<=x<=0x7fff for x in q)
  # Verify equal gain outputs without asserting pattern enum equivalence.
  self.phase='common'
  previous=self.native.call(0x998e70,{'demux_gain':gain,'bls':[0.0]*4,'channel':channel})
  self.phase='idle'
  assert q==list(previous)
  return common,q
def common_for(words):
 q,bi,bo=words[:4],words[4:8],words[8:]
 h=[1,0,0xac,0,0xc9,0,*q]+[0]*16
 for i in range(4):h[10+2*i]=bo[i];h[11+2*i]=bi[i]
 return struct.pack('<26H',*h)
def main():
 O=Path(sys.argv[1]);O.mkdir()
 rng=random.Random(681141);fixture=Fixture();records=[];producer=0
 inputs=[(g,[1.0]*4) for g in [0.5,1.0,2.0,4.0]]
 inputs += [(1.0,[0.5,1.0,2.0,3.0]),(2.0,[2.0,0.5,1.0,3.0])]
 for i in range(64):inputs.append((rng.choice([0.5,1.0,2.0,4.0]),[rng.uniform(0.5,3.9) for j in range(4)]))
 vectors=[[1024]*4+[0]*8,[0x7fff]*4+[0x3fff]*8,[1,2,3,4]+list(range(1,9))]
 for f in range(4):
  for bit in range(15):
   w=[1]*4+[0]*8;w[f]=1<<bit;vectors.append(w)
 for f in range(8):
  for bit in range(14):
   w=[1024]*4+[0]*8;w[4+f]=1<<bit;vectors.append(w)
 for i in range(64):vectors.append([rng.randrange(1,0x8000) for j in range(4)]+[rng.randrange(0x4000) for j in range(8)])
 for placement in [0,128,512]:
  for gain,channel in inputs:
   values=struct.unpack('<5f',struct.pack('<5f',gain,*channel))
   common,q=fixture.derived(values[0],list(values[1:]))
   w=q+[0]*8;oracle=fixture.vector(placement,common)
   records.append(struct.pack('<I5f12I',1,*values,*w)+oracle);producer+=1
  for w in vectors:
   oracle=fixture.vector(placement,common_for(w))
   records.append(struct.pack('<I5f12I',2,1.0,1.0,1.0,1.0,1.0,*w)+oracle)
 # Explicit old-image counterexample: native retains lower unnamed bits.
 clean=fixture.vector(0,common_for([1024]*4+[0]*8))
 inherited=fixture.vector(0,common_for([1024]*4+[0]*8),0xffffffff)
 assert clean!=inherited
 words=struct.unpack('<12I',inherited[8:])
 assert all((w&0x3ffff)==0x3ffff for w in words[4:])
 fixture.unchanged()
 headers={
  'sp11-front-channel-bayer0.h':Q/'sp11-front-channel-bayer0.h',
  'sp11-front-channel-gain.h':R/'src/upstream/isp-config/front-channel-gain-20261014/sp11-front-channel-gain.h',
  'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
  'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
  'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():(O/n).write_bytes(p.read_bytes())
 for p in [PROD/'rear-neutral-scalar.h',PROD/'rear-neutral-scalar.c',R/'src/native-rgb/native-front-params.h',Q/'test-native-c.c']:
  (O/p.name).write_bytes(p.read_bytes())
 original=(Q/'sp11-front-channel-bayer0.h').read_text()
 mutations={
  'source_bayer2_pattern':original.replace('tmp + 8, 0xc9U','tmp + 8, 0xcaU'),
  'wrong_pattern_order':original.replace('tmp + 12, 0xacU','tmp + 12, 0xc9U'),
  'early_publication':original.replace('\tif (!out || !policy || !state)','\tif (out)\n\t\tout[0] = 0;\n\tif (!out || !policy || !state)',1),
  'bypass_existing_fields':original.replace('ret = sp11_front_channel_gain_config(tmp, sizeof(tmp), policy, state);','memset(tmp, 0, sizeof(tmp));\n\tret = 0;'),
  'missing_output_overlap':original.replace('sp11_cdm_overlap(out, sizeof(tmp), state, sizeof(*state))','false')}
 assert all(x!=original for x in mutations.values())
 data=b''.join(records);runs=[]
 for cc in ['gcc','clang']:
  for label,source in [('actual',original),*mutations.items()]:
   (O/'sp11-front-channel-bayer0.h').write_text(source);exe=O/(cc+'-'+label)
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror',
    '-fsanitize=address,undefined','-fno-omit-frame-pointer','-ffp-contract=off','-I'+str(O),
    str(O/'test-native-c.c'),str(O/'rear-neutral-scalar.c'),'-lm','-o',str(exe)],capture_output=True,text=True)
   assert p.returncode==0,p.stderr[-2500:]
   p=subprocess.run([str(exe)],input=data,capture_output=True,timeout=20)
   (O/(cc+'-'+label+'.log')).write_bytes(p.stdout+p.stderr)
   if label=='actual':
    assert p.returncode==0,p.stderr[-2500:].decode()
    res=json.loads(p.stdout);assert res['native_vectors']==len(records) and res['prior_producer_vectors']==producer
    runs.append({'compiler':cc,'ASan_UBSan':True,'result':res})
   else:assert p.returncode!=0,'unsafe compiled mutation survived '+label
 (O/'sp11-front-channel-bayer0.h').write_text(original)
 refs=[str(OLD.relative_to(R)),str((PROD/'rear-neutral-scalar.h').relative_to(R)),
 str((PROD/'rear-neutral-scalar.c').relative_to(R)),'src/native-rgb/native-front-params.h',str(PRIOR.relative_to(R)),
 'experiments/E004-front-ir-vd55g0/e006z-rear-clean-scalar-bank-providers/camss-e006z-clean-scalar-bank.inc']
 result={'schema':'sp11-channel-bayer0-native-config-v1',
 'status':'PASS_FRONT_BAYER0_ADAPTER_RETAINED_SOURCE_FIELDS_AND_PRODUCERS',
 'original_PE_sha256':old.DLL_SHA,'original_executable_and_other_image_bytes_immutable':True,'original_PE_exported':False,
 'source_owned_writable_nonexecuting_data_cells':[{'rva':hex(rva),'bytes':n} for rva,n in fixture.global_cells],
 'native_cases':len(records),'prior_producer_cases':producer,'native_instructions':fixture.count,
 'placements':3,'SP_callee_saved_restored':True,'image_canaries_intact':True,
 'prior_bayer2_gain_arithmetic_matches_front_bayer0_checked':True,
 'native_entries':{'common':'0x998e70','packer':'0xb42840','builder':'0xb41ff0'},
 'intercepted_helpers':['0x85ee78 command arguments observer/success status'],
 'packing_arithmetic_or_field_shims':False,'constructor_executed':False,
 'public_address_metadata_owned':{'module':'0x3b60','configuration':'0x3b68'},
 'scope':{'descriptor_slots':[0,0],'source_bayer':0,'period':0,'initial_register_image':'zero',
 'producer_black_offsets':[0,0,0,0],'producer_max_gain_below_normalization':True},
 'nonzero_old_image_counterexample_checked':True,
 'compiler_runs':runs,'compiled_mutations_rejected_each':list(mutations),
 'header_pins':{n:sha(p) for n,p in headers.items()},'prior_reference_pins':{n:sha(R/n) for n in refs},
 'private_profile_read':False,'private_tuning_read':False,'pixels_read':False,
 'calibration_remeasured':False,'runtime_changed':False,'hardware':False,
 'limits':['Source Bayer0 front adapter; no new physical front pattern/precision/domain proof',
 'Builder address metadata is owned public input, not a source constructor binding',
 'Zero initial image/lower unnamed bits/neutral channel BLS are independent policies, not inherited tuning equivalence',
 'Existing producer is reused only in the non-normalizing synthetic zero-BLS domain',
 'No module activation or separate DEMUX0x3968/0x396c setup or runtime loader replacement']}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','native_cases','prior_producer_cases','native_instructions','runtime_changed']}))
if __name__=='__main__':main()
