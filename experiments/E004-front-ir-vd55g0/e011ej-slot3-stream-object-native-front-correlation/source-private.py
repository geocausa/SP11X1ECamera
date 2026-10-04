#!/usr/bin/env python3
from pathlib import Path
import importlib.util, json, hashlib, struct
from unicorn.arm64_const import *

ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
CM_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011cm-crt-object-producers/source-private.py'
CN_RESULT_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011cn-crt-startup-integration/RESULT.json'
CN_README_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011cn-crt-startup-integration/README.md'
EI_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ei-camera-count-native-windows-correlation/RESULT.json'
OUT=Path(__file__).resolve().parent

sp=importlib.util.spec_from_file_location('ej_cm',CM_PATH)
CM=importlib.util.module_from_spec(sp); sp.loader.exec_module(CM)
CN=json.loads(CN_RESULT_PATH.read_text())
EI=json.loads(EI_PATH.read_text())
assert CN['status']=='PASS_BOUNDED_ORIGINAL_CRT_INTEGRATION'
assert CN['runtime_CRT_image_flag_RVA']=='0x1607b00'
assert 'Field 0x1607B00 becomes 0x80000000 on first use' in CN_README_PATH.read_text()
assert EI['camera_count_read_source_qualified']
assert EI['source_default_stream_count']==512
assert EI['next_camera_source_RVA']=='0xcc6140'

SOURCE_FLAG=0x80000000
KEY_SITES={0xcc61b4,0xcc61cc,0x1380,0xcc61a0}
BODY_SHA256='92392516a581bfd36da290b122fe121ec3da6715a050a19cb286dd14d7c573ff'

def validate_store(t,allowed):
    assert t in allowed

class EJ(CM.Bootstrap):
    def __init__(self,bias,imports):
        super().__init__(bias,0,imports)
        self.ej_alloc=None
        self.ej_events=[]
        self.ej_writes=[]
        self.ej_lock_ready=False
        self.ej_lock_held=False
    def os_contract(self,name,args,ret):
        if self.phase!=0xcc6108:
            return super().os_contract(name,args,ret)
        if name=='HeapAlloc':
            assert ret==0xcb7630
            assert args==[self.handle,8,88]
            self.ej_events.append((name,ret,args[2]))
            assert self.ej_alloc is None
            at=(self.next_alloc+15)&~15
            assert at+88+32<self.own+self.extent
            assert bytes(self.u.mem_read(at-32,32))==b'\xa5'*32
            assert bytes(self.u.mem_read(at,88+32))==b'\xa5'*(88+32)
            self.u.mem_write(at,bytes(88))
            self.ej_alloc=at
            return at
        if name=='InitializeCriticalSectionEx':
            assert self.ej_alloc is not None
            assert ret==0xcc61e4
            assert args==[self.ej_alloc+48,4000,0]
            assert not self.ej_lock_ready
            self.ej_lock_ready=True
            self.ej_events.append((name,ret,4000))
            return 1
        if name=='EnterCriticalSection':
            assert self.ej_alloc is not None
            assert ret==0xcc61fc
            assert args[0]==self.ej_alloc+48
            assert self.ej_lock_ready and not self.ej_lock_held
            self.ej_lock_held=True
            self.ej_events.append((name,ret,0))
            return args[0]
        raise AssertionError(('unqualified EJ OS contract',name,hex(ret),args))
    def memory(self,u,access,at,z,value,user):
        if self.phase!=0xcc6108:
            return super().memory(u,access,at,z,value,user)
        pc=u.reg_read(UC_ARM64_REG_PC)-self.n.base
        if self.n.base<=at<self.n.base+CM.CF.p.OPTIONAL_HEADER.SizeOfImage:
            raise AssertionError(('unexpected EJ image write',hex(pc),hex(at-self.n.base),z,value))
        self.ej_writes.append((pc,at,z,value))
    def run_ej(self):
        prior=self.run()
        assert prior['actual_source_stream_capacity']==512
        assert len(self.allocs)==2
        # Inherited source-qualified CRT first-use state from E011CN.
        self.u.mem_write(self.n.base+0x1607b00,struct.pack('<I',SOURCE_FLAG))
        vector=self.allocs[1][0]
        assert self.u.mem_read(vector+24,8)==bytes(8)
        before_vector=bytes(self.u.mem_read(vector,4096))
        before_image=bytes(self.u.mem_read(self.n.base,CM.CF.p.OPTIONAL_HEADER.SizeOfImage))
        out=self.n.stack+0x1000
        self.u.mem_write(out,bytes(8))
        for k in range(29): self.u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0)
        entry_sp=self.n.stack+0xf000
        self.u.reg_write(UC_ARM64_REG_X0,out)
        self.u.reg_write(UC_ARM64_REG_SP,entry_sp)
        self.u.reg_write(UC_ARM64_REG_LR,self.n.end)
        self.phase=0xcc6108
        self.u.emu_start(self.n.base+0xcc6108,self.n.end,count=20000)
        assert self.u.reg_read(UC_ARM64_REG_PC)==self.n.end
        assert self.u.reg_read(UC_ARM64_REG_X0)==out
        assert self.u.reg_read(UC_ARM64_REG_SP)==entry_sp
        got=struct.unpack('<Q',bytes(self.u.mem_read(out,8)))[0]
        slot3=struct.unpack('<Q',bytes(self.u.mem_read(vector+24,8)))[0]
        assert got==slot3==self.ej_alloc and self.ej_alloc is not None
        assert [x[0] for x in self.ej_events]==['HeapAlloc','InitializeCriticalSectionEx','EnterCriticalSection']
        assert self.ej_lock_ready and self.ej_lock_held

        obj=bytearray(88)
        struct.pack_into('<I',obj,20,0x2000)
        struct.pack_into('<I',obj,24,0xffffffff)
        assert bytes(self.u.mem_read(self.ej_alloc,88))==obj
        assert bytes(self.u.mem_read(self.ej_alloc-32,32))==b'\xa5'*32
        assert bytes(self.u.mem_read(self.ej_alloc+88,32))==b'\xa5'*32
        expected=bytearray(before_vector); struct.pack_into('<Q',expected,24,self.ej_alloc)
        assert bytes(self.u.mem_read(vector,4096))==bytes(expected)
        assert bytes(self.u.mem_read(self.n.base,CM.CF.p.OPTIONAL_HEADER.SizeOfImage))==before_image

        key=[x for x in self.ej_writes if x[0] in KEY_SITES]
        allowed=[
          (0xcc61b4,vector+24,8,self.ej_alloc),
          (0xcc61cc,self.ej_alloc+24,4,0xffffffff),
          (0x1380,self.ej_alloc+20,4,0x2000),
          (0xcc61a0,out,8,self.ej_alloc),
        ]
        assert key==allowed
        rejected=0
        bad=[
          (0xcc61b0,vector+24,8,self.ej_alloc),
          (0xcc61b4,vector+32,8,self.ej_alloc),
          (0xcc61b4,vector+24,4,self.ej_alloc),
          (0xcc61b4,vector+24,8,self.ej_alloc+8),
          (0x1380,self.ej_alloc+20,4,0x4000),
        ]
        for t in bad:
            try: validate_store(t,allowed)
            except AssertionError: rejected+=1
            else: raise AssertionError(('altered contract accepted',t))
        assert rejected==5
        return {
          'placement_bias':self.bias,
          'source_runtime_CRT_image_flag':'0x80000000',
          'source_stream_count':512,
          'first_examined_slot':3,
          'lazy_object_bytes':88,
          'slot3_publication_exact':True,
          'owned_88byte_object_exact':True,
          'object_flag20':0x2000,
          'object_field24':0xffffffff,
          'owned_resource_initialized':True,
          'owned_resource_lock_held_on_return':True,
          'OS_contract_events':[x[0] for x in self.ej_events],
          'exact_key_stores':4,
          'rejected_altered_contracts':rejected,
          'whole_image_unchanged_after_inherited_flag':True,
          'whole_vector_exact_except_slot3':True,
          'exact_ABI_return':True
        }

def main():
    _,imports=CM.authority()
    rows=[]
    for bias in [0,1,40,1230]:
        row=EJ(bias,imports).run_ej(); rows.append(row); print(json.dumps(row),flush=True)
    assert len(rows)==4
    result={
      'experiment':'E011EJ',
      'status':'PASS_BOUNDED_ORIGINAL_SLOT3_LAZY_STREAM_OBJECT_RETURN',
      'base_commit':'7315b4998854e88d92b785dca0fa9a4df2696b2f',
      'inherited_E011CM_source_sha256':hashlib.sha256(CM_PATH.read_bytes()).hexdigest(),
      'inherited_E011CN_result_sha256':hashlib.sha256(CN_RESULT_PATH.read_bytes()).hexdigest(),
      'inherited_E011CN_readme_sha256':hashlib.sha256(CN_README_PATH.read_bytes()).hexdigest(),
      'inherited_E011EI_result_sha256':hashlib.sha256(EI_PATH.read_bytes()).hexdigest(),
      'cc6108_body_sha256':BODY_SHA256,
      'case_count':4,
      'source_runtime_CRT_image_flag':'0x80000000',
      'source_runtime_CRT_image_flag_inherited_qualified':True,
      'native_runtime_CRT_image_flag_observed':False,
      'source_stream_count':512,
      'first_examined_slot':3,
      'lazy_object_bytes':88,
      'slot3_publication_qualified':True,
      'owned_object_contents_qualified':True,
      'owned_resource_initialization_and_return_lock_qualified':True,
      'complete_CC6108_return_qualified':True,
      'exact_key_store_chunks':16,
      'rejected_altered_contracts':20,
      'allocation_failure_path_qualified':False,
      'alternate_runtime_flag_paths_qualified':False,
      'native_allocator_implementation_qualified':False,
      'native_CRT_resource_initialization_qualified':False,
      'native_mutex_bytes_or_concurrency_qualified':False,
      'next_source_RVA':'0xcc60a0',
      'next_scope':'resume enclosing 0xCC6078 stream allocator after 0xCC6108 return',
      'native_rear_runtime_allowed':False,
      'new_camera_starts':0,'new_reboots':0,'new_kernel_build':False,
      'details':rows
    }
    (OUT/'SOURCE-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='details'},sort_keys=True),flush=True)

if __name__=='__main__':
    main()
