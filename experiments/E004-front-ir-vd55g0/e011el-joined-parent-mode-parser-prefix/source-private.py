#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json,hashlib,struct
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *

ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
EC_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/source-private.py'
EK_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011ek-joined-stream-allocator-return/RESULT.json'
REFS_PATH=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/private/E011EL-explore/GLOBAL-REFS-SAFE.json')
OUT=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('el_ec',EC_PATH);EC=importlib.util.module_from_spec(sp);sp.loader.exec_module(EC)
EK=json.loads(EK_RESULT.read_text());REFS=json.loads(REFS_PATH.read_text())
assert EK['complete_CC6078_return_qualified'] and EK['global_index8_lock_release_qualified']
assert EK['selected_object_lock_retained_held'] and EK['next_source_RVA']=='0xced150'
assert REFS=={'target_RVA':'0x16a382c','refs':[
 {'source_RVA':'0xcfa2f4','type':'READ','function_RVA':'0xcfa2e0'},
 {'source_RVA':'0xcfa634','type':'READ','function_RVA':'0xcfa620'}]}

PINS={
 'ced150_prefix':(0xced150,40,'b75b47b09fe1ca8f817adc3fa7a0d2c68677d9a7ffeb114b28105ab81c79e107'),
 'cfa968_prefix':(0xcfa968,84,'755ef730439f971c72e1d9a660802309c270587d0809819d97aaef9cb31e585b'),
 'cfa2e0_body':(0xcfa2e0,572,'070aa336c2fc41e4a63ca94aa3940496ebd50e64d86d6a4a2ba3448521605ca7')
}
for _,(r,z,h) in PINS.items(): assert hashlib.sha256(EC.PE.get_data(r,z)).hexdigest()==h
assert hashlib.sha256(REFS_PATH.read_bytes()).hexdigest()=='e49c5960cc24a647d97c70c773e0c7288da19f2c8706c69924bfbc0fd9c13ac7'

# New direct-read authority is bounded source cold state, not a native-runtime claim.
GLOBAL_RVA=0x16a382c
sec=next(s for s in EC.PE.sections if s.VirtualAddress<=GLOBAL_RVA< s.VirtualAddress+s.Misc_VirtualSize)
off=GLOBAL_RVA-sec.VirtualAddress
assert sec.Characteristics&0x80000000 and off+4>sec.SizeOfRawData
MODE_RVA=EC.MODE_RVA
assert hashlib.sha256(EC.MODE).hexdigest()==EC.MODE_AUTH['sha256'] and len(EC.MODE)==2 and EC.MODE[-1]==0

def reject(fn,cases):
 n=0
 for x in cases:
  try:fn(*x)
  except AssertionError:n+=1
  else:raise AssertionError(('altered accepted',fn.__name__,x))
 return n
def eq(got,want):assert got==want

def one_case(sel_bias):
 c=EC.Case(0,0,0x80000000,0,0,0,0xa5); c.run();u=c.u;n=c.n
 assert [f['entry'] for f in c.ec_frames]==[0xced2f0,0xced0d8,0xcc6078,0xcc6108]
 # Join accepted E011EJ then accepted E011EK return states without replaying qualified instructions.
 child=c.ec_frames.pop()
 for r,v in child['saved'].items():u.reg_write(r,v)
 cc6078=c.ec_frames.pop()
 for r,v in cc6078['saved'].items():u.reg_write(r,v)
 assert [f['entry'] for f in c.ec_frames]==[0xced2f0,0xced0d8]
 c.ec_lock_held=False
 selected=0x93001000+((sel_bias+15)&~15)
 u.mem_map(0x93000000,0x10000);u.mem_write(0x93000000,b'\xa5'*0x10000);u.mem_write(selected,b'\0'*88)
 u.mem_write(selected+20,struct.pack('<I',0x2000));u.mem_write(selected+24,struct.pack('<I',0xffffffff))
 selected_lock_held=True
 result_slot=c.dw_entry_sp-1536
 u.mem_write(result_slot,struct.pack('<Q',selected))
 u.reg_write(UC_ARM64_REG_X0,result_slot);u.reg_write(UC_ARM64_REG_PC,n.base+0xced150);u.reg_write(UC_ARM64_REG_LR,n.base+0xced150)

 assert int.from_bytes(u.mem_read(n.base+GLOBAL_RVA,4),'little')==0
 assert hashlib.sha256(bytes(u.mem_read(n.base+MODE_RVA,2))).hexdigest()==EC.MODE_AUTH['sha256']
 before_image=bytes(u.mem_read(n.base,EC.PE.OPTIONAL_HEADER.SizeOfImage))
 before_selected=bytes(u.mem_read(selected,88))
 before_output=bytes(u.mem_read(c.dw_entry_sp-1392,640))

 calls=[];reads=[];keywrites=[];neg=0;parser_saved=None;mode_reads=[];stop={'hit':False}
 semantic_sites={0xced164,0xcfa2f8,0xcfa2fc,0xcfa340,0xcfa600,0xcfa9a8}
 def code(uu,pc,z,_):
  nonlocal neg,parser_saved
  r=pc-n.base
  if r==0xced174:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_X2)&0xffffffff,uu.reg_read(UC_ARM64_REG_X3))
   want=(c.dw_entry_sp-1392,n.base+MODE_RVA,128,selected);eq(got,want)
   neg+=reject(eq,[( (got[0]+8,*got[1:]),want),((got[0],got[1]+1,got[2],got[3]),want),((got[0],got[1],127,got[3]),want),((got[0],got[1],got[2],got[3]+8),want),((0,*got[1:]),want)])
   calls.append('CED174:CFA968')
  elif r==0xcfa2e0:
   assert uu.reg_read(UC_ARM64_REG_X0)==n.base+MODE_RVA and uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcfa990
   parser_saved={reg:uu.reg_read(reg) for reg in EC.NONVOL}
   calls.append('CFA98C:CFA2E0')
  elif r==0xcfa990:
   assert parser_saved is not None
   assert uu.reg_read(UC_ARM64_REG_X0)==0x100000000 and (uu.reg_read(UC_ARM64_REG_X1)&0xffffffff)==1
   assert uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1616
   assert all(uu.reg_read(reg)==v for reg,v in parser_saved.items())
  elif r==0xcfa9bc:
   local=c.dw_entry_sp-1600
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_X2)&0xffffffff,uu.reg_read(UC_ARM64_REG_X3)&0xffffffff,uu.reg_read(UC_ARM64_REG_X4)&0xffffffff)
   want=(local,c.dw_entry_sp-1392,0,128,0x180);eq(got,want)
   neg+=reject(eq,[
    ((got[0]+4,*got[1:]),want),((got[0],got[1]+8,*got[2:]),want),
    ((got[0],got[1],1,got[3],got[4]),want),((got[0],got[1],got[2],127,got[4]),want),
    ((got[0],got[1],got[2],got[3],0x181),want)])
   assert selected_lock_held and not c.ec_lock_held
   stop['hit']=True;uu.emu_stop()

 def memread(uu,a,at,width,value,_):
  nonlocal neg
  r=uu.reg_read(UC_ARM64_REG_PC)-n.base
  if at==n.base+GLOBAL_RVA:
   got=(r,at,width,int.from_bytes(uu.mem_read(at,width),'little'));want=(0xcfa2f4,n.base+GLOBAL_RVA,4,0);eq(got,want)
   neg+=reject(eq,[((r+4,at,width,0),want),((r,at+4,width,0),want),((r,at,8,0),want),((r,at,width,1),want),((r,at,width,0xffffffff),want)])
   reads.append(('global',r))
  elif n.base+MODE_RVA<=at<n.base+MODE_RVA+2:
   data=bytes(uu.mem_read(at,width))
   assert data==bytes(u.mem_read(at,width))
   mode_reads.append((r,at-(n.base+MODE_RVA),width))

 def memwrite(uu,a,at,width,value,_):
  r=uu.reg_read(UC_ARM64_REG_PC)-n.base
  # Until CFA9BC every original write must remain inside the retained stack.
  assert n.stack<=at and at+width<=n.stack+65536,(hex(r),hex(at),width)
  if r in semantic_sites:keywrites.append((r,at-c.dw_entry_sp,width,value & ((1<<(8*width))-1)))

 hs=[u.hook_add(UC_HOOK_CODE,code),u.hook_add(UC_HOOK_MEM_READ,memread),u.hook_add(UC_HOOK_MEM_WRITE,memwrite)]
 try:u.emu_start(n.base+0xced150,n.end,count=5000)
 finally:
  for h in hs:u.hook_del(h)
 assert stop['hit'] and calls==['CED174:CFA968','CFA98C:CFA2E0']
 assert reads==[('global',0xcfa2f4)]
 assert mode_reads==[(0xcfa300,0,1),(0xcfa360,1,1),(0xcfa4d4,1,1),(0xcfa4ec,1,1)]
 assert bytes(u.mem_read(n.base,EC.PE.OPTIONAL_HEADER.SizeOfImage))==before_image
 assert bytes(u.mem_read(selected,88))==before_selected
 assert bytes(u.mem_read(c.dw_entry_sp-1392,640))==before_output
 assert int.from_bytes(u.mem_read(n.base+GLOBAL_RVA,4),'little')==0
 assert selected_lock_held and not c.ec_lock_held
 return {
  'selected_placement_bias':sel_bias,'selected_owned_offset':selected-0x93000000,
  'CED174_CFA968_call_arguments_exact':True,'CFA2E0_mode_parser_return_qualified':True,
  'parser_result_flags':'0x100000000','parser_validity':1,
  'cold_global_read_RVA':'0x16a382c','cold_global_value':0,
  'cold_global_direct_writers_found':0,'native_runtime_global_selection_qualified':False,
  'mode_literal_reads':4,'mode_literal_contents_exported':False,
  'writes_before_next_call_stack_only':True,'selected_object_unchanged':True,'formatted_output_unchanged':True,
  'selected_object_lock_retained_held':True,'global_index8_lock_released':True,
  'next_source_RVA':'0xcfa9bc','next_call_target_RVA':'0xcfd550',
  'rejected_altered_contracts':neg
 }

def main():
 rows=[one_case(x) for x in (0,1,40,1230)]
 for r in rows:print(json.dumps(r),flush=True)
 assert all(x['rejected_altered_contracts']==15 for x in rows)
 result={
  'experiment':'E011EL','status':'PASS_JOINED_PARENT_MODE_PARSER_PREFIX',
  'base_commit':'1ec1a7c4f0e3686f54adcb84fbcfe0d885fcbc1d',
  'inherited_E011EC_source_sha256':hashlib.sha256(EC_PATH.read_bytes()).hexdigest(),
  'inherited_E011EK_result_sha256':hashlib.sha256(EK_RESULT.read_bytes()).hexdigest(),
  'global_refs_safe_sha256':hashlib.sha256(REFS_PATH.read_bytes()).hexdigest(),
  'pins':PINS,'case_count':4,'source_call_argument_sets':8,'exact_cold_global_reads':4,
  'exact_mode_literal_reads':16,'rejected_altered_contracts':60,
  'CFA2E0_mode_parser_return_qualified':True,'parser_result_flags':'0x100000000','parser_validity':1,
  'cold_global_RVA':'0x16a382c','cold_global_value':0,'cold_global_direct_writers_found':0,
  'native_runtime_global_selection_qualified':False,
  'next_source_RVA':'0xcfa9bc','next_call_target_RVA':'0xcfd550',
  'deeper_CFD550_CFCC18_effects_qualified':False,
  'selected_object_lock_retained_held':True,'global_index8_lock_released':True,
  'native_rear_runtime_allowed':False,'new_camera_starts':0,'new_reboots':0,'new_kernel_build':False,
  'details':rows}
 (OUT/'SOURCE-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='details'},sort_keys=True),flush=True)
if __name__=='__main__':main()
