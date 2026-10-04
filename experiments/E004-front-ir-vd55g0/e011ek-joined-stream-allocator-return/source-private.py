#!/usr/bin/env python3
from pathlib import Path
import importlib.util, json, hashlib, struct
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *

ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
EC_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/source-private.py'
EJ_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011ej-slot3-stream-object-native-front-correlation/RESULT.json'
EJ_SOURCE=ROOT/'experiments/E004-front-ir-vd55g0/e011ej-slot3-stream-object-native-front-correlation/SOURCE-SAFE.json'
OUT=Path(__file__).resolve().parent

spec=importlib.util.spec_from_file_location('ek_ec',EC_PATH);EC=importlib.util.module_from_spec(spec);spec.loader.exec_module(EC)
EJR=json.loads(EJ_RESULT.read_text()); EJS=json.loads(EJ_SOURCE.read_text())
assert EJR['source_null_slot3_lazy_object_path_qualified'] and EJR['complete_CC6108_source_return_qualified']
assert EJS['owned_object_contents_qualified'] and EJS['owned_resource_initialization_and_return_lock_qualified']
assert EJS['source_runtime_CRT_image_flag']=='0x80000000'
assert EJR['next_source_RVA']=='0xcc60a0'

CC6078_PIN={'body_bytes':100,'sha256':'7eca050b7b7a4284ed60cdb2a8d067cb2d4ecd964bbd9da560e5af2a15ff0fe8'}
LEAVE_PIN={'body_bytes':28,'sha256':'ba0fb2d4a1e1a1d1effa82370b5d86970cbf56048020dfd66c1702bb8237af60'}
assert hashlib.sha256(EC.PE.get_data(0xcc6078,100)).hexdigest()==CC6078_PIN['sha256']
assert hashlib.sha256(EC.PE.get_data(0xcb7398,28)).hexdigest()==LEAVE_PIN['sha256']

EXPECTED_TRACE=[
  0xcc60a0,0xcc60a4,0xcc60a8,0xcc60ac,0xcc60b0,0xcc60b4,0xcc60b8,0xcc60bc,
  0xcc60c0,0xcc60c4,0xcb7398,0xcb739c,0xcb73a0,0xcb73a4,0xcb73a8,0xcb73ac,0xcb73b0,
  0xcc60c8,0xcc60cc,0xcc60d0,0xcc60d4,0xcc60d8
]

def reject(fn, cases):
    n=0
    for x in cases:
        try: fn(*x)
        except AssertionError: n+=1
        else: raise AssertionError(('altered contract accepted',fn.__name__,x))
    return n

def check_read(site,at,width,value,expected):
    assert (site,at,width,value)==expected

def check_write(site,at,width,value,expected):
    assert (site,at,width,value)==expected

def check_wrapper(site,ret,sp,index,expected):
    assert (site,ret,sp,index)==expected

def check_api(pc,ret,sp,arg,expected):
    assert (pc,ret,sp,arg)==expected

def check_return(pc,sp,x0,expected):
    assert (pc,sp,x0)==expected

def one_case(sel_bias):
    c=EC.Case(0,0,0x80000000,0,0,0,0xa5)
    ancestor=c.run(); u=c.u; n=c.n
    assert u.reg_read(UC_ARM64_REG_PC)==n.base+0xcc6120
    assert c.ec_lock_held and c.ec_frames[-1]['entry']==0xcc6108 and c.ec_frames[-1]['ret']==n.base+0xcc60a0
    assert [f['entry'] for f in c.ec_frames]==[0xced2f0,0xced0d8,0xcc6078,0xcc6108]

    # Source-qualified E011EJ return handoff: restore exact CC6108 caller state and join only the
    # selected-stream object/result that E011EJ proved placement-independent.
    child=c.ec_frames.pop()
    for reg,val in child['saved'].items(): u.reg_write(reg,val)
    local=c.dw_entry_sp-1584
    outer=c.dw_entry_sp-1536
    selected=0x93001000+((sel_bias+15)&~15)
    u.mem_map(0x93000000,0x10000)
    u.mem_write(0x93000000,b'\xa5'*0x10000)
    u.mem_write(selected,b'\x00'*88)
    u.mem_write(selected+20,struct.pack('<I',0x2000))
    u.mem_write(selected+24,struct.pack('<I',0xffffffff))
    u.mem_write(local,struct.pack('<Q',selected))
    assert int.from_bytes(u.mem_read(outer,8),'little')==0
    selected_lock_held=True
    global8_lock_held=True

    before_image=bytes(u.mem_read(n.base,EC.PE.OPTIONAL_HEADER.SizeOfImage))
    before_stack=bytearray(u.mem_read(n.stack,65536))
    before_selected=bytes(u.mem_read(selected,88))
    assert before_selected[20:24]==struct.pack('<I',0x2000) and before_selected[24:28]==struct.pack('<I',0xffffffff)
    assert bytes(u.mem_read(selected-32,32))==b'\xa5'*32
    assert bytes(u.mem_read(selected+88,32))==b'\xa5'*32

    u.reg_write(UC_ARM64_REG_X0,local)
    u.reg_write(UC_ARM64_REG_PC,n.base+0xcc60a0)
    u.reg_write(UC_ARM64_REG_LR,n.base+0xcc60a0)

    reads=[];writes=[];trace=[];wrappers=[];apis=[];neg=0
    final={'hit':False}
    saved_parent=dict(c.ec_frames[-1]['saved'])
    # Current top frame is CC6078; its captured saved set is the ABI contract at entry.
    assert c.ec_frames[-1]['entry']==0xcc6078 and c.ec_frames[-1]['ret']==n.base+0xced150

    def code(uu,pc,z,_):
        nonlocal global8_lock_held,neg
        if pc==c.apis['LeaveCriticalSection']:
            expected=(c.apis['LeaveCriticalSection'],n.base+0xcc60c8,c.dw_entry_sp-1600,n.base+0x16a3000)
            got=(pc,uu.reg_read(UC_ARM64_REG_LR),uu.reg_read(UC_ARM64_REG_SP),uu.reg_read(UC_ARM64_REG_X0))
            check_api(*got,expected)
            neg+=reject(check_api,[
              (pc+0x10,*got[1:],expected),(pc,got[1]+4,*got[2:],expected),
              (pc,got[1],got[2]+16,got[3],expected),(pc,got[1],got[2],got[3]+8,expected),
              (*got, (expected[0],expected[1],expected[2],expected[3]+16))
            ])
            assert global8_lock_held and selected_lock_held
            keep={r:uu.reg_read(r) for r in EC.NONVOL}
            global8_lock_held=False;apis.append('LeaveCriticalSection')
            uu.reg_write(UC_ARM64_REG_X0,c.api_clobber);uu.reg_write(UC_ARM64_REG_PC,got[1])
            assert all(uu.reg_read(r)==v for r,v in keep.items())
            return
        r=pc-n.base
        if r==0xced150:
            expected=(n.base+0xced150,c.dw_entry_sp-1552,outer)
            got=(pc,uu.reg_read(UC_ARM64_REG_SP),uu.reg_read(UC_ARM64_REG_X0))
            check_return(*got,expected)
            neg+=reject(check_return,[
              (pc+4,got[1],got[2],expected),(pc,got[1]+16,got[2],expected),
              (pc,got[1],got[2]+8,expected),(pc,got[1],0,expected),(n.base+0xced150,got[1]+8,got[2],expected)
            ])
            assert not global8_lock_held and selected_lock_held
            assert int.from_bytes(uu.mem_read(outer,8),'little')==selected
            assert all(uu.reg_read(reg)==val for reg,val in saved_parent.items())
            final['hit']=True;uu.emu_stop();return
        assert r in EXPECTED_TRACE,(hex(r),[hex(x) for x in trace])
        if r==0xcb7398:
            expected=(0xcb7398,n.base+0xcc60c8,c.dw_entry_sp-1600,8)
            got=(r,uu.reg_read(UC_ARM64_REG_LR),uu.reg_read(UC_ARM64_REG_SP),uu.reg_read(UC_ARM64_REG_X0)&0xffffffff)
            check_wrapper(*got,expected)
            neg+=reject(check_wrapper,[
              (r+4,*got[1:],expected),(r,got[1]+4,*got[2:],expected),
              (r,got[1],got[2]+16,got[3],expected),(r,got[1],got[2],9,expected),
              (r,got[1],got[2],7,expected)
            ])
            wrappers.append('CB7398:index8')
        trace.append(r)

    def memread(uu,a,at,width,value,_):
        nonlocal neg
        r=uu.reg_read(UC_ARM64_REG_PC)-n.base
        if at==local:
            expected=(0xcc60a0,local,8,selected);got=(r,at,width,int.from_bytes(uu.mem_read(at,width),'little'))
        elif at==n.base+0xf7e0c0:
            expected=(0xcb73ac,n.base+0xf7e0c0,8,c.apis['LeaveCriticalSection']);got=(r,at,width,int.from_bytes(uu.mem_read(at,width),'little'))
        else:return
        check_read(*got,expected)
        neg+=reject(check_read,[
          (got[0]+4,*got[1:],expected),(got[0],got[1]+1,*got[2:],expected),
          (got[0],got[1],got[2]//2,got[3],expected),(got[0],got[1],got[2],got[3]^1,expected),
          (got[0],got[1],got[2],0,expected)
        ])
        reads.append((r,at,width))

    expected_writes=[
      (0xcc60a4,outer,8,selected),
      (0xcc60ac,selected+0x10,4,0),
      (0xcc60b0,selected+0x28,8,0),
      (0xcc60b4,selected+0x00,8,0),
      (0xcc60b4,selected+0x08,8,0),
      (0xcc60bc,selected+0x18,4,0xffffffff),
    ]
    def memwrite(uu,a,at,width,value,_):
        nonlocal neg
        r=uu.reg_read(UC_ARM64_REG_PC)-n.base
        if at!=outer and not (selected<=at<selected+88):return
        value &= (1<<(width*8))-1
        expected=expected_writes[len(writes)]
        got=(r,at,width,value);check_write(*got,expected)
        neg+=reject(check_write,[
          (r+4,at,width,value,expected),(r,at+8,width,value,expected),
          (r,at,width+1,value,expected),(r,at,width,value^1,expected),
          (r,at,width,0x55 & ((1<<(width*8))-1),expected)
        ])
        writes.append(got)

    hooks=[u.hook_add(UC_HOOK_CODE,code),u.hook_add(UC_HOOK_MEM_READ,memread),u.hook_add(UC_HOOK_MEM_WRITE,memwrite)]
    try:u.emu_start(n.base+0xcc60a0,n.end,count=1000)
    finally:
        for h in hooks:u.hook_del(h)

    assert final['hit'] and trace==EXPECTED_TRACE
    assert len(reads)==2 and writes==expected_writes and wrappers==['CB7398:index8'] and apis==['LeaveCriticalSection']
    assert not global8_lock_held and selected_lock_held
    assert bytes(u.mem_read(n.base,EC.PE.OPTIONAL_HEADER.SizeOfImage))==before_image
    after_stack=bytearray(u.mem_read(n.stack,65536))
    expected_stack=bytearray(before_stack)
    oo=outer-n.stack;expected_stack[oo:oo+8]=struct.pack('<Q',selected)
    assert after_stack==expected_stack
    assert bytes(u.mem_read(selected,88))==before_selected
    assert bytes(u.mem_read(selected-32,32))==b'\xa5'*32 and bytes(u.mem_read(selected+88,32))==b'\xa5'*32
    # CC6078 has returned; parents remain live for E011EL.
    c.ec_frames.pop()
    assert [f['entry'] for f in c.ec_frames]==[0xced2f0,0xced0d8]
    return {
      'selected_placement_bias':sel_bias,
      'selected_owned_offset':selected-0x93000000,
      'source_selected_object_state_from_E011EJ':True,
      'exact_dependency_reads':2,
      'exact_source_store_chunks':6,
      'exact_leave_wrapper_entries':1,
      'owned_LeaveCriticalSection_calls':1,
      'rejected_altered_contracts':neg,
      'global_index8_lock_released':True,
      'selected_object_lock_retained_held':True,
      'selected_object_bytes_unchanged_by_normalization':True,
      'outer_result_published_exact':True,
      'complete_CC6078_ABI_return_exact':True,
      'next_source_RVA':'0xced150',
      'parent_frames_retained':['0xced2f0','0xced0d8']
    }

def main():
    rows=[one_case(x) for x in (0,1,40,1230)]
    for r in rows: print(json.dumps(r),flush=True)
    assert all(x['rejected_altered_contracts']==55 for x in rows),[x['rejected_altered_contracts'] for x in rows]
    result={
      'experiment':'E011EK',
      'status':'PASS_JOINED_ORIGINAL_STREAM_ALLOCATOR_RETURN',
      'base_commit':'e5a5ae1cd49320b303740a15af29bd3875962824',
      'inherited_E011EC_source_sha256':hashlib.sha256(EC_PATH.read_bytes()).hexdigest(),
      'inherited_E011EJ_result_sha256':hashlib.sha256(EJ_RESULT.read_bytes()).hexdigest(),
      'inherited_E011EJ_source_sha256':hashlib.sha256(EJ_SOURCE.read_bytes()).hexdigest(),
      'cc6078_pin':CC6078_PIN,'leave_wrapper_pin':LEAVE_PIN,
      'case_count':len(rows),
      'exact_dependency_reads':sum(x['exact_dependency_reads'] for x in rows),
      'exact_source_store_chunks':sum(x['exact_source_store_chunks'] for x in rows),
      'rejected_altered_contracts':sum(x['rejected_altered_contracts'] for x in rows),
      'global_index8_lock_release_qualified':True,
      'selected_object_lock_retained_held':True,
      'result_record_normalization_qualified':True,
      'complete_CC6078_return_qualified':True,
      'next_source_RVA':'0xced150',
      'next_pending_parent_return_RVA':'0xced330',
      'retained_parent_frames':['0xced2f0','0xced0d8'],
      'native_CRT_resource_initialization_qualified':False,
      'native_mutex_bytes_or_concurrency_qualified':False,
      'native_rear_runtime_allowed':False,
      'new_camera_starts':0,'new_reboots':0,'new_kernel_build':False,
      'details':rows
    }
    (OUT/'SOURCE-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='details'},sort_keys=True),flush=True)

if __name__=='__main__': main()
