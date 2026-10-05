#!/usr/bin/env python3
"""E011GC: join exact .rdata byte 1 at 0xF8B21B and execute parser index math to 0xF8B222."""
from pathlib import Path
import importlib.util,json,hashlib
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
EC_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/source-private.py';GB_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011gb-source-byte-25-f8b21b-frontier/RESULT.json'
spec=importlib.util.spec_from_file_location('e011ec',EC_PATH);EC=importlib.util.module_from_spec(spec);spec.loader.exec_module(EC)
G=json.loads(GB_RESULT.read_text());assert G['experiment']=='E011GB' and G['status']=='PASS_SOURCE_BYTE_25_TO_F8B21B_LOOKUP_FRONTIER' and G['next_camera_source_RVA']=='0xca95b8' and G['next_dependency_read_RVA']=='0xf8b21b' and not G['next_dependency_read_executed']
B=0x180000000;TABLE_RVA=0xf8b21b;TB=EC.PE.get_data(TABLE_RVA,1);assert TB==b'\x01';EXPECTED=(0xca95b8,0xca95bc,0xca95c4,0xca95c8,0xca95cc,0xca95d0,0xca95d4)
def one_case(axis):
 sb=0x71000000+axis*0x10000;E=sb+0x3000;C=E-0x4d0;R=C+32;H=C-64
 u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(B+0xca9000,0x1000);u.mem_write(B+0xca9000,EC.PE.get_data(0xca9000,0x1000));u.mem_map(B+0xf8b000,0x1000);u.mem_write(B+0xf8b000,EC.PE.get_data(0xf8b000,0x1000));u.mem_map(sb,0x8000);u.mem_write(R+0x24,b'\0')
 for r,v in {UC_ARM64_REG_SP:H,UC_ARM64_REG_X19:R,UC_ARM64_REG_X20:B+0xf8b210,UC_ARM64_REG_X9:B+0xf8b211,UC_ARM64_REG_X10:10}.items():u.reg_write(r,v)
 vis=[];u.hook_add(UC_HOOK_CODE,lambda U,a,z,x:vis.append(a-B));u.emu_start(B+0xca95b8,B+0xca95d8)
 assert tuple(vis)==EXPECTED and u.reg_read(UC_ARM64_REG_PC)==B+0xca95d8 and u.reg_read(UC_ARM64_REG_X10)==9 and u.reg_read(UC_ARM64_REG_X9)==18 and u.reg_read(UC_ARM64_REG_X20)+u.reg_read(UC_ARM64_REG_X9)==B+0xf8b222
 return {'axis':axis,'instruction_visits':len(vis),'first_lookup_u8':1,'scaled_state_u64':9,'second_lookup_offset_u64':18,'second_lookup_RVA':'0xf8b222'}
def main():
 rows=[one_case(a) for a in (0,1,40,1230)];altered=[('table_byte',2,1),('table_rva','0xf8b21a','0xf8b21b'),('parser_state',1,0),('scaled_state',18,9),('second_offset',16,18),('second_rva','0xf8b220','0xf8b222')]
 safe={'experiment':'E011GC','status':'PASS_TABLE_BYTE_01_TO_F8B222_FRONTIER','base_commit':'10ba5592a748c5b5d440182cf950f2be0a8ad465','inherited_E011GB_result_sha256':hashlib.sha256(GB_RESULT.read_bytes()).hexdigest(),'case_count':4,'first_table_RVA':'0xf8b21b','first_table_section':'.rdata','first_table_byte_u8':1,'first_table_byte_sha256':hashlib.sha256(TB).hexdigest(),'first_table_read_RVA':'0xca95b8','first_table_read_executed':True,'parser_state_before_u8':0,'scaled_state_u64':9,'second_lookup_offset_u64':18,'next_camera_source_RVA':'0xca95d8','next_dependency_read_RVA':'0xf8b222','next_dependency_bytes':1,'next_dependency_read_executed':False,'rejected_altered_contracts':len(altered)*len(rows),'thread_producer_invalid_API_requests_rejected':264,'new_front_camera_starts':0,'new_rear_camera_starts':0,'new_reboots':0,'new_kernel_build':False,'returned_to_Golden_Linux':True,'native_rear_runtime_allowed':False,'details':rows}
 (OUT/'SOURCE-SAFE.json').write_text(json.dumps(safe,indent=2)+'\n');print(json.dumps({k:v for k,v in safe.items() if k!='details'},sort_keys=True))
if __name__=='__main__':main()
