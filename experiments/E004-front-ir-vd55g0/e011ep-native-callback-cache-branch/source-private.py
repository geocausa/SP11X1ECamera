#!/usr/bin/env python3
"""E011EP private candidate: native-qualified callback/cache helper and result-one branch."""
from pathlib import Path
import importlib.util,json,hashlib,struct
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *

ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
EC_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/source-private.py'
EL_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011el-joined-parent-mode-parser-prefix/RESULT.json'
EL_REFS=ROOT/'experiments/E004-front-ir-vd55g0/e011el-joined-parent-mode-parser-prefix/GLOBAL-REFS-SAFE.json'
EM_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011em-cfd550-cfcc18-validation-prefix/RESULT.json'
DY_SOURCE=ROOT/'experiments/E004-front-ir-vd55g0/e011dy-original-cold-runtime-context-receiver/SOURCE-SAFE.json'
EN_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011en-joined-cfd410-cb6520-prefix/RESULT.json'
OUT=Path(__file__).resolve().parent
EO_WINDOWS_SAFE=ROOT/'experiments/E004-front-ir-vd55g0/e011eo-native-selected-field-zero-branch/WINDOWS-SAFE.json'
EO_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011eo-native-selected-field-zero-branch/RESULT.json'
EP_WINDOWS=OUT/'WINDOWS-SAFE.json'

sp=importlib.util.spec_from_file_location('em_ec',EC_PATH);EC=importlib.util.module_from_spec(sp);sp.loader.exec_module(EC)
EL=json.loads(EL_RESULT.read_text()); REFS=json.loads(EL_REFS.read_text()); EM=json.loads(EM_RESULT.read_text()); DY=json.loads(DY_SOURCE.read_text()); EN=json.loads(EN_RESULT.read_text()); WIN=json.loads(EO_WINDOWS_SAFE.read_text()); EO=json.loads(EO_RESULT.read_text()); EPWIN=json.loads(EP_WINDOWS.read_text())
assert EL['status']=='PASS_JOINED_PARENT_MODE_PARSER_PREFIX'
assert EL['CFA2E0_mode_parser_return_qualified'] and EL['next_source_RVA']=='0xcfa9bc'
assert EL['next_call_target_RVA']=='0xcfd550' and not EL['deeper_CFD550_CFCC18_effects_qualified']
assert REFS['target_RVA']=='0x16a382c' and all(x['type']=='READ' for x in REFS['refs'])
assert EM['status']=='PASS_JOINED_CFD550_CFCC18_VALIDATION_PREFIX' and EM['next_source_RVA']=='0xcfcc98' and EM['next_call_target_RVA']=='0xcfd410'
AUTH={x['RVA']:x for x in DY['runtime_initial_value_model_authority']}
assert AUTH['0x16a2a84']['accepted_owned_initial_value']==0 and not AUTH['0x16a2a84']['native_runtime_selection_qualified']
assert AUTH['0x16072d8']['file_initial_sha256']=='507987659945beb7bcd11ae53dece55517a2979fc4e3ea4c9683bdceb5fd0f3f'
assert AUTH['0x16072d8']['initial_pointer_targets_RVA']==['0x1607180','0x1607650'] and not AUTH['0x16072d8']['native_runtime_selection_qualified']
assert EN['status']=='PASS_JOINED_CFD410_CB6520_PREFIX' and EN['next_source_RVA']=='0xcfd46c' and EN['next_dependency_RVA']=='0x160718c'
NATIVE=WIN['native_prestart_after_initialize_before_start']
assert NATIVE['runtime_flag_RVA']=='0x16a2a84' and NATIVE['runtime_flag_value_u32']==0
assert NATIVE['first_pointer_target_RVA']=='0x1607180' and NATIVE['selected_field_RVA']=='0x160718c' and NATIVE['selected_field_value_u32']==0
assert WIN['independent_KD_read_confirmed_selected_field_zero'] and not WIN['exact_CFD46C_instruction_breakpoint_observed']
assert NATIVE['second_pointer_not_file_static_0x1607650'] and NATIVE['global_pointer_0x16a2a88_not_file_static_0x1607180'] and not WIN['broad_file_initial_state_persistence_qualified']
assert EO['status']=='PASS_NATIVE_QUALIFIED_SELECTED_FIELD_ZERO_BRANCH' and EO['next_source_RVA']=='0xcfd498'
assert EPWIN['status']=='PASS_NATIVE_PRESTART_CALLBACK_STATE' and EPWIN['native_prestart_fptable_slot_populated']
assert EPWIN['native_prestart_fptable_target_matches_source_identified_callback'] and EPWIN['native_callback_return_u32']==1
assert EPWIN['native_callback_implementation_process_local_comparison_qualified'] and EPWIN['native_FrameServer_comparison_equal']

PINS={
 'ced150_prefix':(0xced150,40,'b75b47b09fe1ca8f817adc3fa7a0d2c68677d9a7ffeb114b28105ab81c79e107'),
 'cfa968_prefix':(0xcfa968,84,'755ef730439f971c72e1d9a660802309c270587d0809819d97aaef9cb31e585b'),
 'cfa2e0_body':(0xcfa2e0,572,'070aa336c2fc41e4a63ca94aa3940496ebd50e64d86d6a4a2ba3448521605ca7'),
 'cfd550_wrapper':(0xcfd550,32,'6753ebc03040f6e33599e13fce3985bc2a9baaf2b61d53ee3c004d1ad48d712f'),
 'cfcc18_prefix':(0xcfcc18,128,'98d2d102534288426b43734dc1049ac15596f0418fc6245ca950ba8a1b3c774b'),
 'cfd410_to_pointed_field_frontier':(0xcfd410,92,'a6e8a04d21a424fd31b63e8ca8609e3bfa78ea32bf6f30420b471815957b974e'),
 'cb6520_body':(0xcb6520,160,'663db5108d386bc5f9d14b5fdfaca9f9a5166dbfde19b498f8d99d054d1c9381'),
 'cfd46c_zero_field_branch':(0xcfd46c,44,'935bed6536b1e422108e988195f412c78652b11b4f5f1427c0bf12492d068158'),
 'cb9f68_callback_cache_helper':(0xcb9f68,96,'bcccce70775ee06c49deff53f1ebd475a949e303992537b81bc6a0d5bf113a73'),
 'cfg_nop':(0x1a8c0,4,'110f46b5b35c069160560c6ad6786f647dd44e8760a52a46fc22dbbcd7630b91'),
 'cfd498_native_callback_branch':(0xcfd498,80,'e4e1851f56a7171079a7a999579f0997af573bb19f23911fe5650987eda6287c'),
}
for _,(r,z,h) in PINS.items(): assert hashlib.sha256(EC.PE.get_data(r,z)).hexdigest()==h

GLOBAL_RVA=0x16a382c
sec=next(s for s in EC.PE.sections if s.VirtualAddress<=GLOBAL_RVA<s.VirtualAddress+s.Misc_VirtualSize)
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
def eq(got,want): assert got==want

def one_case(sel_bias):
 c=EC.Case(0,0,0x80000000,0,0,0,0xa5);c.run();u=c.u;n=c.n
 assert [f['entry'] for f in c.ec_frames]==[0xced2f0,0xced0d8,0xcc6078,0xcc6108]
 # Join already-qualified E011EJ/E011EK return state, then replay original E011EL path.
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
 callback_page=0x94000000; callback_target=callback_page+0x100
 u.mem_map(callback_page,0x1000);u.mem_write(callback_page,b'\xa7'*0x1000)
 fptable_slot=n.base+0x1b60000
 assert int.from_bytes(u.mem_read(fptable_slot,8),'little')==0
 u.mem_write(fptable_slot,struct.pack('<Q',callback_target))
 assert int.from_bytes(u.mem_read(n.base+0xf7e7b8,8),'little')==n.base+0x1a8c0
 result_slot=c.dw_entry_sp-1536
 u.mem_write(result_slot,struct.pack('<Q',selected))
 u.reg_write(UC_ARM64_REG_X0,result_slot);u.reg_write(UC_ARM64_REG_PC,n.base+0xced150);u.reg_write(UC_ARM64_REG_LR,n.base+0xced150)

 assert int.from_bytes(u.mem_read(n.base+GLOBAL_RVA,4),'little')==0
 assert hashlib.sha256(bytes(u.mem_read(n.base+MODE_RVA,2))).hexdigest()==EC.MODE_AUTH['sha256']
 before_image=bytes(u.mem_read(n.base,EC.PE.OPTIONAL_HEADER.SizeOfImage))
 before_selected=bytes(u.mem_read(selected,88))
 before_output=bytes(u.mem_read(c.dw_entry_sp-1392,640))

 calls=[];reads=[];mode_reads=[];keywrites=[];en_reads=[];en_writes=[];pointed_reads=[];callback_reads=[];cfg_reads=[];neg=0;parser_saved=None;cfd_saved=None;cb_saved=None;cb9_saved=None;callback_invocations=0;callback_returns=0;stop={'hit':False}
 expected_en_writes=[
  (0xcfd430,-1800,8,0),(0xcfd430,-1792,8,0),
  (0xcfd438,-1784,8,0),(0xcfd438,-1776,8,0),
  (0xcfd440,-1768,8,0),(0xcfd448,-1760,1,0),
  (0xcb6534,-1808,1,0),
  (0xcb655c,-1824,8,n.base+0x1607180),(0xcb655c,-1816,8,n.base+0x1607650),
 ]
 expected_keywrites=[
   (0xcfa9a8,-1600,4,0),
   (0xcfcc30,-1656,8,c.dw_entry_sp-1600),
   (0xcfcc64,-1600,4,0xffffffff),
   (0xcfcc78,-1664,4,0),
   (0xcfcc78,-1660,4,0),
 ]
 def check_args(got,want,bads):
  nonlocal neg
  eq(got,want); neg+=reject(eq,[(x,want) for x in bads])

 def code(uu,pc,z,_):
  nonlocal neg,parser_saved,cfd_saved,cb_saved,cb9_saved,callback_invocations,callback_returns
  if pc==callback_target:
   got=(pc,uu.reg_read(UC_ARM64_REG_LR),EPWIN['native_callback_return_u32'],True);want=(callback_target,n.base+0xcb9fb4,1,True);eq(got,want)
   neg+=reject(eq,[((pc+4,got[1],got[2],True),want),((pc,got[1]+4,got[2],True),want),((pc,got[1],0,True),want),((pc,got[1],got[2],False),want)])
   saved={reg:uu.reg_read(reg) for reg in EC.NONVOL}
   uu.reg_write(UC_ARM64_REG_W0,1);uu.reg_write(UC_ARM64_REG_PC,got[1])
   assert all(uu.reg_read(reg)==v for reg,v in saved.items())
   callback_invocations+=1;calls.append('NATIVE_CALLBACK:RETURN_1');return
  r=pc-n.base
  if r==0xced174:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_X2)&0xffffffff,uu.reg_read(UC_ARM64_REG_X3))
   want=(c.dw_entry_sp-1392,n.base+MODE_RVA,128,selected)
   check_args(got,want,[(got[0]+8,*got[1:]),(got[0],got[1]+1,got[2],got[3]),(got[0],got[1],127,got[3]),(got[0],got[1],got[2],got[3]+8),(0,*got[1:])])
   calls.append('CED174:CFA968')
  elif r==0xcfa2e0:
   assert uu.reg_read(UC_ARM64_REG_X0)==n.base+MODE_RVA and uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcfa990
   parser_saved={reg:uu.reg_read(reg) for reg in EC.NONVOL};calls.append('CFA98C:CFA2E0')
  elif r==0xcfa990:
   assert parser_saved is not None
   assert uu.reg_read(UC_ARM64_REG_X0)==0x100000000 and (uu.reg_read(UC_ARM64_REG_X1)&0xffffffff)==1
   assert uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1616
   assert all(uu.reg_read(reg)==v for reg,v in parser_saved.items())
  elif r==0xcfa9bc:
   local=c.dw_entry_sp-1600
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_X2)&0xffffffff,uu.reg_read(UC_ARM64_REG_X3)&0xffffffff,uu.reg_read(UC_ARM64_REG_X4)&0xffffffff)
   want=(local,c.dw_entry_sp-1392,0,128,384)
   check_args(got,want,[(got[0]+4,*got[1:]),(got[0],got[1]+8,*got[2:]),(got[0],got[1],1,got[3],got[4]),(got[0],got[1],got[2],127,got[4]),(got[0],got[1],got[2],got[3],385)])
   calls.append('CFA9BC:CFD550')
  elif r==0xcfd550:
   local=c.dw_entry_sp-1600
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_X2)&0xffffffff,uu.reg_read(UC_ARM64_REG_X3)&0xffffffff,uu.reg_read(UC_ARM64_REG_X4)&0xffffffff)
   want=(local,c.dw_entry_sp-1392,0,128,384)
   check_args(got,want,[(got[0]+8,*got[1:]),(got[0],got[1]+1,*got[2:]),(got[0],got[1],2,got[3],got[4]),(got[0],got[1],got[2],129,got[4]),(got[0],got[1],got[2],got[3],383)])
   calls.append('CFD550:TAIL_CFCC18')
  elif r==0xcfcc18:
   local=c.dw_entry_sp-1600
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1)&0xffffffff,uu.reg_read(UC_ARM64_REG_X2)&0xffffffff,uu.reg_read(UC_ARM64_REG_X3)&0xffffffff,uu.reg_read(UC_ARM64_REG_X4),uu.reg_read(UC_ARM64_REG_X5)&0xffffffff)
   want=(c.dw_entry_sp-1392,0,128,384,local,1)
   check_args(got,want,[(got[0]+8,*got[1:]),(got[0],1,*got[2:]),(got[0],got[1],127,*got[3:]),(got[0],got[1],got[2],385,got[4],got[5]),(got[0],got[1],got[2],got[3],got[4]+4,got[5])])
   calls.append('CFCC18:VALIDATION_PREFIX')
  elif r==0xcfcc98:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_X2),uu.reg_read(UC_ARM64_REG_X3)&0xffffffff,uu.reg_read(UC_ARM64_REG_X4)&0xffffffff,uu.reg_read(UC_ARM64_REG_X5)&0xffffffff,uu.reg_read(UC_ARM64_REG_X6)&0xffffffff)
   want=(c.dw_entry_sp-1664,c.dw_entry_sp-1600,c.dw_entry_sp-1392,0,128,384,1)
   check_args(got,want,[(got[0]+4,*got[1:]),(got[0],got[1]+4,*got[2:]),(got[0],got[1],got[2]+8,*got[3:]),(got[0],got[1],got[2],1,*got[4:]),(got[0],got[1],got[2],got[3],got[4],got[5],0)])
   assert int.from_bytes(uu.mem_read(c.dw_entry_sp-1600,4),'little')==0xffffffff
   assert int.from_bytes(uu.mem_read(c.dw_entry_sp-1664,8),'little')==0
   assert selected_lock_held and not c.ec_lock_held
   calls.append('CFCC98:CFD410')
  elif r==0xcfd410:
   cfd_saved={reg:uu.reg_read(reg) for reg in EC.NONVOL}
   assert uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1680
   calls.append('CFD410:ENTRY')
  elif r==0xcb6520:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_SP),uu.reg_read(UC_ARM64_REG_LR))
   want=(c.dw_entry_sp-1832,0,c.dw_entry_sp-1856,n.base+0xcfd464)
   check_args(got,want,[(got[0]+8,*got[1:]),(got[0],1,*got[2:]),(got[0],got[1],got[2]+16,got[3]),(got[0],got[1],got[2],got[3]+4)])
   cb_saved={reg:uu.reg_read(reg) for reg in EC.NONVOL};calls.append('CFD460:CB6520')
  elif r==0xcfd464:
   assert cb_saved is not None and all(uu.reg_read(reg)==v for reg,v in cb_saved.items())
   assert uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1856 and uu.reg_read(UC_ARM64_REG_X0)==c.dw_entry_sp-1832
   calls.append('CB6520:RETURN')
  elif r==0xcfd46c:
   assert cfd_saved is not None and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1856
   assert uu.reg_read(UC_ARM64_REG_X8)==n.base+0x1607180 and (uu.reg_read(UC_ARM64_REG_W9)&0xffffffff)==0xfde9
   calls.append('CFD46C:NATIVE_QUALIFIED_SELECTED_FIELD_READ')
  elif r==0xcfd470:
   assert pointed_reads==[(0xcfd46c,0x160718c,4,0)]
   assert (uu.reg_read(UC_ARM64_REG_W8)&0xffffffff)==0 and (uu.reg_read(UC_ARM64_REG_W9)&0xffffffff)==0xfde9
   calls.append('CFD470:ZERO_FIELD_COMPARE')
  elif r==0xcfd498:
   assert pointed_reads==[(0xcfd46c,0x160718c,4,0)] and selected_lock_held and not c.ec_lock_held
   calls.append('CFD498:CB9F68_CALL')
  elif r==0xcb9f68:
   assert uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcfd49c and uu.reg_read(UC_ARM64_REG_SP)==c.dw_entry_sp-1856
   cb9_saved={reg:uu.reg_read(reg) for reg in EC.NONVOL};calls.append('CB9F68:ENTRY_POPULATED_SLOT')
  elif r==0xf5d430:
   assert uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcb9fb0 and uu.reg_read(UC_ARM64_REG_X15)==callback_target
   calls.append('CB9FAC:CFG_CHECK')
  elif r==0x1a8c0:
   assert uu.reg_read(UC_ARM64_REG_LR)==n.base+0xcb9fb0
   calls.append('CFG:NOP_RETURN')
  elif r==0xcb9fb4:
   assert uu.reg_read(UC_ARM64_REG_W0)==1 and callback_invocations==1
   callback_returns+=1;calls.append('CB9FB4:CALLBACK_RETURN_1')
  elif r==0xcfd49c:
   assert cb9_saved is not None and all(uu.reg_read(reg)==v for reg,v in cb9_saved.items())
   assert uu.reg_read(UC_ARM64_REG_W0)==1 and callback_returns==1
   calls.append('CB9F68:RETURN_NATIVE_1')
  elif r==0xcfd4c0:
   assert uu.reg_read(UC_ARM64_REG_W0)==1 and (uu.reg_read(UC_ARM64_REG_W8)&0xff)==0
   calls.append('CFD4C0:NATIVE_RESULT_ONE_BRANCH')
  elif r==0xcfd4d4:
   assert (uu.reg_read(UC_ARM64_REG_W8)&0xff)==0
   calls.append('CFD4D4:SELECT_MODE_ZERO')
  elif r==0xcfd4e4:
   got=(uu.reg_read(UC_ARM64_REG_X0),uu.reg_read(UC_ARM64_REG_X1),uu.reg_read(UC_ARM64_REG_X2),uu.reg_read(UC_ARM64_REG_W3))
   want=(c.dw_entry_sp-1392,c.dw_entry_sp-1800,c.dw_entry_sp-1840,0);eq(got,want)
   neg+=reject(eq,[((got[0]+8,*got[1:]),want),((got[0],got[1]+8,got[2],got[3]),want),((got[0],got[1],got[2]+8,got[3]),want),((got[0],got[1],got[2],1),want)])
   calls.append('CFD4E4:CB76B0_FRONTIER');stop['hit']=True;uu.emu_stop()

 def memread(uu,a,at,width,value,_):
  nonlocal neg
  r=uu.reg_read(UC_ARM64_REG_PC)-n.base
  if at==n.base+GLOBAL_RVA:
   got=(r,at,width,int.from_bytes(uu.mem_read(at,width),'little'));want=(0xcfa2f4,n.base+GLOBAL_RVA,4,0);eq(got,want)
   neg+=reject(eq,[((r+4,at,width,0),want),((r,at+4,width,0),want),((r,at,8,0),want),((r,at,width,1),want),((r,at,width,0xffffffff),want)])
   reads.append(('global',r))
  elif n.base+MODE_RVA<=at<n.base+MODE_RVA+2:
   assert bytes(uu.mem_read(at,width))==bytes(u.mem_read(at,width))
   mode_reads.append((r,at-(n.base+MODE_RVA),width))
  elif r==0xcb6548:
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));want=(0xcb6548,0x16a2a84,4,0);eq(got,want)
   neg+=reject(eq,[((r+4,got[1],width,0),want),((r,got[1]+4,width,0),want),((r,got[1],8,0),want),((r,got[1],width,1),want)])
   en_reads.append(got)
  elif r==0xcb6558:
   k=len([x for x in en_reads if x[0]==0xcb6558]); expected=[(0xcb6558,0x16072d8,8,n.base+0x1607180),(0xcb6558,0x16072e0,8,n.base+0x1607650)][k]
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));eq(got,expected)
   neg+=reject(eq,[((r+4,got[1],width,got[3]),expected),((r,got[1]+8,width,got[3]),expected),((r,got[1],4,got[3]&0xffffffff),expected),((r,got[1],width,got[3]^8),expected)])
   en_reads.append(got)
  elif r==0xcb9f78:
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));expected=(0xcb9f78,0x1b60000,8,callback_target);eq(got,expected)
   neg+=reject(eq,[((r+4,got[1],width,got[3]),expected),((r,got[1]+8,width,got[3]),expected),((r,got[1],4,got[3]&0xffffffff),expected),((r,got[1],width,got[3]+8),expected)])
   callback_reads.append(got)
  elif r==0xf5d434:
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little'));expected=(0xf5d434,0xf7e7b8,8,n.base+0x1a8c0);eq(got,expected)
   cfg_reads.append(got)
  elif r==0xcfd46c:
   got=(r,at-n.base,width,int.from_bytes(uu.mem_read(at,width),'little')); expected=(0xcfd46c,0x160718c,4,0);eq(got,expected)
   neg+=reject(eq,[((r+4,got[1],width,0),expected),((r,got[1]+4,width,0),expected),((r,got[1],8,0),expected),((r,got[1],width,1),expected),((r,got[1],width,0xfde9),expected)])
   assert NATIVE['selected_field_value_u32']==got[3] and NATIVE['first_pointer_target_RVA']=='0x1607180'
   pointed_reads.append(got)

 def memwrite(uu,a,at,width,value,_):
  nonlocal neg
  r=uu.reg_read(UC_ARM64_REG_PC)-n.base
  assert n.stack<=at and at+width<=n.stack+65536,(hex(r),hex(at),width)
  rel=at-c.dw_entry_sp;value&=(1<<(8*width))-1
  if r in (0xcfa9a8,0xcfcc30,0xcfcc64,0xcfcc78):
   got=(r,rel,width,value)
   want=expected_keywrites[len(keywrites)]
   eq(got,want)
   neg+=reject(eq,[((r+4,rel,width,value),want),((r,rel+4,width,value),want),((r,rel,width+1,value),want),((r,rel,width,value^1),want),((r,rel,width,0x55 & ((1<<(8*width))-1)),want)])
   keywrites.append(got)
  elif r in (0xcfd430,0xcfd438,0xcfd440,0xcfd448,0xcb6534,0xcb655c):
   got=(r,rel,width,value);want=expected_en_writes[len(en_writes)];eq(got,want)
   neg+=reject(eq,[((r+4,rel,width,value),want),((r,rel+4,width,value),want),((r,rel,width+1,value),want),((r,rel,width,value^1),want)])
   en_writes.append(got)

 hs=[u.hook_add(UC_HOOK_CODE,code),u.hook_add(UC_HOOK_MEM_READ,memread),u.hook_add(UC_HOOK_MEM_WRITE,memwrite)]
 try:u.emu_start(n.base+0xced150,n.end,count=6000)
 finally:
  for h in hs:u.hook_del(h)

 assert stop['hit']
 assert calls==['CED174:CFA968','CFA98C:CFA2E0','CFA9BC:CFD550','CFD550:TAIL_CFCC18','CFCC18:VALIDATION_PREFIX','CFCC98:CFD410','CFD410:ENTRY','CFD460:CB6520','CB6520:RETURN','CFD46C:NATIVE_QUALIFIED_SELECTED_FIELD_READ','CFD470:ZERO_FIELD_COMPARE','CFD498:CB9F68_CALL','CB9F68:ENTRY_POPULATED_SLOT','CB9FAC:CFG_CHECK','CFG:NOP_RETURN','NATIVE_CALLBACK:RETURN_1','CB9FB4:CALLBACK_RETURN_1','CB9F68:RETURN_NATIVE_1','CFD4C0:NATIVE_RESULT_ONE_BRANCH','CFD4D4:SELECT_MODE_ZERO','CFD4E4:CB76B0_FRONTIER']
 assert reads==[('global',0xcfa2f4)]
 assert mode_reads==[(0xcfa300,0,1),(0xcfa360,1,1),(0xcfa4d4,1,1),(0xcfa4ec,1,1)]
 assert keywrites==expected_keywrites and en_writes==expected_en_writes
 assert en_reads==[(0xcb6548,0x16a2a84,4,0),(0xcb6558,0x16072d8,8,n.base+0x1607180),(0xcb6558,0x16072e0,8,n.base+0x1607650)]
 assert pointed_reads==[(0xcfd46c,0x160718c,4,0)]
 assert callback_reads==[(0xcb9f78,0x1b60000,8,callback_target)] and cfg_reads==[(0xf5d434,0xf7e7b8,8,n.base+0x1a8c0)]
 assert callback_invocations==callback_returns==1
 assert hashlib.sha256(bytes(u.mem_read(n.base+0x16072d8,16))).hexdigest()==AUTH['0x16072d8']['file_initial_sha256']
 assert bytes(u.mem_read(n.base,EC.PE.OPTIONAL_HEADER.SizeOfImage))==before_image
 assert bytes(u.mem_read(selected,88))==before_selected
 assert bytes(u.mem_read(c.dw_entry_sp-1392,640))==before_output
 assert int.from_bytes(u.mem_read(n.base+GLOBAL_RVA,4),'little')==0
 assert selected_lock_held and not c.ec_lock_held
 return {
  'selected_placement_bias':sel_bias,'selected_owned_offset':selected-0x93000000,
  'CFA9BC_CFD550_arguments_exact':True,'CFD550_register_reshape_exact':True,
  'CFCC18_validation_prefix_qualified':True,'CFCC18_local_result_initialized_minus1':True,
  'CFCC18_local_pair_zero_initialized':True,
  'CFCC98_CFD410_arguments_exact':True,'CFD410_executed':True,'CFD410_local_setup_qualified':True,
  'CB6520_owned_cold_zero_path_qualified':True,'CB6520_return_qualified':True,
  'runtime_dependency_reads_qualified':len(en_reads),'exact_EN_local_store_chunks':len(en_writes),
  'pointed_object_field_read_executed':True,'native_front_selected_field_authority_joined':True,'native_front_runtime_flag_zero_correlated':True,'native_front_first_pointer_target_correlated':True,'exact_wrapper_key_stores':len(keywrites),
  'selected_object_unchanged':True,'formatted_output_unchanged':True,
  'selected_object_lock_retained_held':True,'global_index8_lock_released':True,
  'selected_field_zero_branch_taken':True,'native_callback_cache_slot_read_qualified':True,'native_callback_return_one_qualified':True,'callback_result_one_branch_qualified':True,'original_CFG_nop_executed':True,'broad_file_initial_state_persistence_qualified':False,'next_source_RVA':'0xcfd4e4','next_call_target_RVA':'0xcb76b0',
  'rejected_altered_contracts':neg
 }

def main():
 rows=[one_case(x) for x in (0,1,40,1230)]
 for r in rows:print(json.dumps(r),flush=True)
 assert len(rows)==4 and len({x['rejected_altered_contracts'] for x in rows})==1,[x['rejected_altered_contracts'] for x in rows]
 result={
  'experiment':'E011EP','status':'PASS_NATIVE_QUALIFIED_CALLBACK_CACHE_BRANCH',
  'base_commit':'e854309752780b9922e9c1e25d7c9d48398245de',
  'inherited_E011EN_result_sha256':hashlib.sha256(EN_RESULT.read_bytes()).hexdigest(),
  'inherited_E011EO_result_sha256':hashlib.sha256(EO_RESULT.read_bytes()).hexdigest(),
  'inherited_E011EO_windows_safe_sha256':hashlib.sha256(EO_WINDOWS_SAFE.read_bytes()).hexdigest(),
  'windows_callback_authority_sha256':hashlib.sha256(EP_WINDOWS.read_bytes()).hexdigest(),
  'inherited_E011DY_source_safe_sha256':hashlib.sha256(DY_SOURCE.read_bytes()).hexdigest(),
  'pins':PINS,'case_count':4,
  'pointed_object_field_read_executed':True,'native_front_selected_field_authority_joined':True,
  'native_front_prestart_flag_zero_qualified':True,'native_front_first_pointer_target_qualified':True,'native_front_selected_field_zero_qualified':True,
  'selected_field_zero_branch_taken':True,'native_callback_cache_slot_read_qualified':True,'native_callback_return_one_qualified':True,'callback_result_one_branch_qualified':True,'original_CFG_nop_executed':True,'exact_CB9F68_native_instruction_breakpoint_observed':False,'broad_callback_table_state_qualified':False,'next_source_RVA':'0xcfd4e4','next_call_target_RVA':'0xcb76b0',
  'broad_file_initial_state_persistence_qualified':False,'native_second_pointer_matches_file_static':False,'native_global_pointer_matches_file_static':False,
  'exact_CFD46C_native_instruction_breakpoint_observed':False,'independent_KD_read_confirmed_selected_field_zero':True,
  'selected_object_lock_retained_held':True,'global_index8_lock_released':True,
  'rejected_altered_contracts':sum(x['rejected_altered_contracts'] for x in rows),
  'new_front_camera_starts':EPWIN['new_front_camera_starts'],'new_rear_camera_starts':0,'new_reboots':EPWIN['new_reboots'],'new_kernel_build':False,
  'returned_to_Golden_Linux':EPWIN['returned_to_Golden_Linux'],'native_rear_runtime_allowed':False,'details':rows}
 (OUT/'SOURCE-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if k!='details'},sort_keys=True),flush=True)
if __name__=='__main__':main()
