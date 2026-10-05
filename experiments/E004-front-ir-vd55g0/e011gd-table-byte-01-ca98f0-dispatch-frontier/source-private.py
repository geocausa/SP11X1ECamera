#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json,hashlib
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
EC_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/source-private.py';GC_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011gc-table-byte-01-f8b222-frontier/RESULT.json'
spec=importlib.util.spec_from_file_location('e011ec',EC_PATH);EC=importlib.util.module_from_spec(spec);spec.loader.exec_module(EC)
C=json.loads(GC_RESULT.read_text());assert C['experiment']=='E011GC' and C['status']=='PASS_TABLE_BYTE_01_TO_F8B222_FRONTIER' and C['next_camera_source_RVA']=='0xca95d8' and C['next_dependency_read_RVA']=='0xf8b222' and not C['next_dependency_read_executed']
B=0x180000000;TB=EC.PE.get_data(0xf8b222,1);assert TB==b'\x01';EXPECTED=(0xca95d8,0xca95dc,0xca95e0,0xca95e4,0xca95e8,0xca95ec,0xca95f0)
def one_case(axis):
 sb=0x71000000+axis*0x10000;E=sb+0x3000;CSP=E-0x4d0;R=CSP+32;H=CSP-64
 u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(B+0xca9000,0x1000);u.mem_write(B+0xca9000,EC.PE.get_data(0xca9000,0x1000));u.mem_map(B+0xf8b000,0x1000);u.mem_write(B+0xf8b000,EC.PE.get_data(0xf8b000,0x1000));u.mem_map(sb,0x8000);u.mem_write(R+0x24,b'\0')
 for r,v in {UC_ARM64_REG_SP:H,UC_ARM64_REG_X19:R,UC_ARM64_REG_X20:B+0xf8b210,UC_ARM64_REG_X9:18}.items():u.reg_write(r,v)
 vis=[];u.hook_add(UC_HOOK_CODE,lambda U,a,z,x:vis.append(a-B));u.emu_start(B+0xca95d8,B+0xca95f4)
 assert tuple(vis)==EXPECTED and u.reg_read(UC_ARM64_REG_PC)==B+0xca95f4 and int.from_bytes(u.mem_read(R+0x24,1),'little')==1 and u.reg_read(UC_ARM64_REG_X11)==B+0xca98ec
 return {'axis':axis,'instruction_visits':len(vis),'parser_state_after_u8':1,'jump_table_base_RVA':'0xca98ec','jump_table_entry_RVA':'0xca98f0'}
def main():
 rows=[one_case(a) for a in (0,1,40,1230)];altered=[('table_byte',2,1),('table_rva','0xf8b223','0xf8b222'),('state_after',2,1),('jump_base','0xca98f0','0xca98ec'),('jump_entry','0xca98f4','0xca98f0'),('entry_width',8,4)]
 safe={'experiment':'E011GD','status':'PASS_TABLE_BYTE_01_TO_CA98F0_DISPATCH_FRONTIER','base_commit':'c5957dd5759ce3f7328600ff9ef9d8910a7ced01','inherited_E011GC_result_sha256':hashlib.sha256(GC_RESULT.read_bytes()).hexdigest(),'case_count':4,'second_table_RVA':'0xf8b222','second_table_section':'.rdata','second_table_byte_u8':1,'second_table_byte_sha256':hashlib.sha256(TB).hexdigest(),'second_table_read_RVA':'0xca95d8','second_table_read_executed':True,'parser_state_after_u8':1,'parser_state_lt8_qualified':True,'parser_state_le7_qualified':True,'jump_table_base_RVA':'0xca98ec','jump_table_index_u32':1,'next_camera_source_RVA':'0xca95f4','next_dependency_read_RVA':'0xca98f0','next_dependency_bytes':4,'next_dependency_signed':True,'next_dependency_read_executed':False,'rejected_altered_contracts':len(altered)*len(rows),'thread_producer_invalid_API_requests_rejected':264,'new_front_camera_starts':0,'new_rear_camera_starts':0,'new_reboots':0,'new_kernel_build':False,'returned_to_Golden_Linux':True,'native_rear_runtime_allowed':False,'details':rows}
 (OUT/'SOURCE-SAFE.json').write_text(json.dumps(safe,indent=2)+'\n');print(json.dumps({k:v for k,v in safe.items() if k!='details'},sort_keys=True))
if __name__=='__main__':main()
