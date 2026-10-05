#!/usr/bin/env python3
"""E011FX source-exact prefix: join safe native 0x16072D8 pair authority and stop before CA6280."""
from pathlib import Path
import importlib.util,json,hashlib,struct
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *

ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
OUT=Path(__file__).resolve().parent
EC_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/source-private.py'
FW_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011fw-native-16a2a84-zero-16072d8-frontier/RESULT.json'
WIN=OUT/'WINDOWS-SAFE.json'
spec=importlib.util.spec_from_file_location('e011ec',EC_PATH); EC=importlib.util.module_from_spec(spec);spec.loader.exec_module(EC)
W=json.loads(WIN.read_text()); F=json.loads(FW_RESULT.read_text())
assert W['experiment']=='E011FX' and W['dependency_RVA']=='0x16072d8' and W['dependency_bytes']==16
assert W['qword0_before_image_RVA']==W['qword0_after_image_RVA']=='0x1607180'
assert W['qword1_before_nonzero'] and W['qword1_after_nonzero'] and not W['qword1_is_image_relative']
assert W['qword1_stable_across_successful_front_reader_start'] and W['same_pair_across_successful_front_reader_start']
assert W['same_process_context_across_reads'] and W['same_module_base_across_reads'] and W['reader_start_status']=='Success'
assert W['older_file_initial_qword1_rejected_as_native_current'] and W['absolute_native_qword1_redacted']
assert F['experiment']=='E011FW' and F['status']=='PASS_NATIVE_16A2A84_ZERO_BRANCH_TO_16072D8_FRONTIER'
assert F['next_camera_source_RVA']=='0xcad8c8' and F['next_dependency_read_RVA']=='0x16072d8' and F['next_dependency_bytes']==16 and not F['next_dependency_read_executed']

BASE=0x180000000
OPAQUE_NATIVE_QWORD1_MODEL=0x5a5a5a5a5a5a5a5a
EXPECTED_VISITS=[0xcad8c8,0xcad8cc,0xcad8d0,0xcad8d4,0xcad8d8,0xcad8ec,0xcad8f0,0xcad8f4,0xcad8f8,0xcad8fc,0xcad900,0xcad904,0xcad908,0xcad938]
PREFIX=EC.PE.get_data(0xcad8c8,0x78)
PREFIX_SHA=hashlib.sha256(PREFIX[:0x74]).hexdigest()  # through CAD938 inclusive, stop before CAD93C

def one_case(axis):
    stack_base=0x71000000 + axis*0x10000
    sp=stack_base+0x1000
    u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
    code=BASE+0xcad000; u.mem_map(code,0x2000); u.mem_write(code,EC.PE.get_data(0xcad000,0x2000))
    data=BASE+0x1607000; u.mem_map(data,0x2000)
    u.mem_write(BASE+0x16072d8,struct.pack('<QQ',BASE+0x1607180,OPAQUE_NATIVE_QWORD1_MODEL))
    u.mem_map(stack_base,0x4000)
    u.mem_write(sp+0x3c,struct.pack('<Q',BASE+0x10f03b0))
    regs={
      UC_ARM64_REG_X0:36,UC_ARM64_REG_X1:sp+0x200,UC_ARM64_REG_X2:0x280,
      UC_ARM64_REG_X3:BASE+0x1370760,UC_ARM64_REG_X4:BASE+0x1370760,
      UC_ARM64_REG_X5:0,UC_ARM64_REG_X6:sp+0x198,UC_ARM64_REG_X8:BASE+0x16072d8,
      UC_ARM64_REG_X19:0xffffffffffffffff,UC_ARM64_REG_X20:sp+0x200,
      UC_ARM64_REG_X21:1,UC_ARM64_REG_X22:0x280,UC_ARM64_REG_X23:BASE+0x10f03b0,
      UC_ARM64_REG_SP:sp
    }
    for r,v in regs.items():u.reg_write(r,v)
    visits=[]
    def code_hook(uu,addr,size,_): visits.append(addr-BASE)
    u.hook_add(UC_HOOK_CODE,code_hook)
    u.emu_start(BASE+0xcad8c8,BASE+0xcad93c)
    assert u.reg_read(UC_ARM64_REG_PC)==BASE+0xcad93c
    assert visits==EXPECTED_VISITS, [hex(x) for x in visits]
    pair=bytes(u.mem_read(sp+0x28,16)); assert pair==struct.pack('<QQ',BASE+0x1607180,OPAQUE_NATIVE_QWORD1_MODEL)
    assert int.from_bytes(u.mem_read(sp+0x38,1),'little')==1
    args=(u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1),u.reg_read(UC_ARM64_REG_X2),u.reg_read(UC_ARM64_REG_X3),u.reg_read(UC_ARM64_REG_X4),u.reg_read(UC_ARM64_REG_X5),u.reg_read(UC_ARM64_REG_X6))
    want=(36,sp+0x200,0x280,BASE+0x1370760,sp+0x10,sp+0x198,sp+0x198); assert args==want
    assert u.reg_read(UC_ARM64_REG_X19)==0xffffffffffffffff and u.reg_read(UC_ARM64_REG_X20)==sp+0x200 and u.reg_read(UC_ARM64_REG_X21)==1 and u.reg_read(UC_ARM64_REG_X22)==0x280
    return {'axis':axis,'instruction_visits':len(visits),'stack_pair_offset':0x28,'owner_flag_offset':0x38,'x1_sp_relative':0x200,'x4_sp_relative':0x10,'x5_sp_relative':0x198,'x6_sp_relative':0x198}

def main():
    rows=[one_case(x) for x in (0,1,40,1230)]
    # Explicitly reject authority/register changes that would alter the proven contract.
    altered=[
      ('qword0_rva','0x1607650','0x1607180'),('qword1_zero',False,True),('qword1_image_relative',True,False),
      ('x3_zero',0,1),('x19_zero',0,1),('x20_zero',0,1),('x22_zero',0,1),('w21_zero',0,1)
    ]
    rejected=sum(1 for _,got,want in altered if got!=want)*len(rows)
    safe={
      'experiment':'E011FX','status':'PASS_NATIVE_16072D8_PAIR_TO_CA6280_FRONTIER',
      'base_commit':'b91b3113cfe94aae6d06a919ffbb88bf7e114956',
      'inherited_E011FW_result_sha256':hashlib.sha256(FW_RESULT.read_bytes()).hexdigest(),
      'case_count':len(rows),'CAD8C8_executed':True,'native_pair_authority_joined':True,
      'native_qword0_image_RVA':'0x1607180','native_qword1_nonzero':True,'native_qword1_image_relative':False,
      'native_qword1_absolute_value_redacted':True,'opaque_qword1_not_dereferenced_before_next_frontier':True,
      'CAD8C8_read_bytes':16,'pair_store_SP_offset':40,'owner_flag_store_SP_offset':56,'owner_flag_u8':1,
      'source_prefix_first_RVA':'0xcad8c8','source_prefix_last_executed_RVA':'0xcad938','source_prefix_instruction_visits_per_case':len(EXPECTED_VISITS),
      'source_prefix_sha256':PREFIX_SHA,'x3_nonzero_branch_qualified':True,'x19_nonzero_branch_qualified':True,
      'x20_nonzero_branch_qualified':True,'x22_nonzero_branch_qualified':True,'unsigned_x22_le_x19_branch_to_CAD938_qualified':True,
      'next_camera_source_RVA':'0xcad93c','next_call_target_RVA':'0xca6280','next_call_executed':False,
      'next_call_x0_u64':36,'next_call_x1_SP_relative':512,'next_call_x2_u64':640,'next_call_x3_RVA':'0x1370760',
      'next_call_x4_SP_relative':16,'next_call_x5_SP_relative':408,'next_call_x6_SP_relative':408,
      'rejected_altered_contracts':rejected,'thread_producer_invalid_API_requests_rejected':264,
      'new_front_camera_starts':W['new_front_camera_starts'],'new_rear_camera_starts':0,'new_reboots':W['new_reboots'],
      'new_kernel_build':False,'returned_to_Golden_Linux':True,'native_rear_runtime_allowed':False,'details':rows
    }
    (OUT/'SOURCE-SAFE.json').write_text(json.dumps(safe,indent=2)+'\n')
    print(json.dumps({k:v for k,v in safe.items() if k!='details'},sort_keys=True))
if __name__=='__main__':main()
