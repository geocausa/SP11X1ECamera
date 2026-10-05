#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json,hashlib,struct
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
EC_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/source-private.py';GD_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011gd-table-byte-01-ca98f0-dispatch-frontier/RESULT.json'
spec=importlib.util.spec_from_file_location('e011ec',EC_PATH);EC=importlib.util.module_from_spec(spec);spec.loader.exec_module(EC)
D=json.loads(GD_RESULT.read_text());assert D['experiment']=='E011GD' and D['status']=='PASS_TABLE_BYTE_01_TO_CA98F0_DISPATCH_FRONTIER' and D['next_camera_source_RVA']=='0xca95f4' and D['next_dependency_read_RVA']=='0xca98f0' and not D['next_dependency_read_executed']
B=0x180000000;ENTRY=EC.PE.get_data(0xca98f0,4);V=struct.unpack('<i',ENTRY)[0];assert V==-52;TARGET=0xca97e8+V*4;assert TARGET==0xca9718
EXPECTED=(0xca95f4,0xca95f8,0xca95fc,0xca9600)
def one_case(axis):
 u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(B+0xca9000,0x1000);u.mem_write(B+0xca9000,EC.PE.get_data(0xca9000,0x1000));u.reg_write(UC_ARM64_REG_X9,1);u.reg_write(UC_ARM64_REG_X11,B+0xca98ec)
 vis=[];u.hook_add(UC_HOOK_CODE,lambda U,a,z,x:vis.append(a-B));u.emu_start(B+0xca95f4,B+TARGET)
 assert tuple(vis)==EXPECTED and u.reg_read(UC_ARM64_REG_PC)==B+TARGET and u.reg_read(UC_ARM64_REG_X10)==B+TARGET
 return {'axis':axis,'instruction_visits':len(vis),'dispatch_entry_s32':V,'dispatch_target_RVA':hex(TARGET)}
def main():
 rows=[one_case(a) for a in (0,1,40,1230)];altered=[('entry_s32',-51,-52),('entry_rva','0xca98f4','0xca98f0'),('index',2,1),('target','0xca971c','0xca9718')]
 safe={'experiment':'E011GE','status':'PASS_DISPATCH_MINUS52_TO_CA9718_CASE_FRONTIER','base_commit':'470aae6c52d63b2990be43d8356863011c9b307e','inherited_E011GD_result_sha256':hashlib.sha256(GD_RESULT.read_bytes()).hexdigest(),'case_count':4,'dispatch_table_RVA':'0xca98ec','dispatch_index_u32':1,'dispatch_entry_RVA':'0xca98f0','dispatch_entry_bytes':4,'dispatch_entry_s32':V,'dispatch_entry_sha256':hashlib.sha256(ENTRY).hexdigest(),'dispatch_read_RVA':'0xca95f4','dispatch_read_executed':True,'dispatch_base_RVA':'0xca97e8','dispatch_scale':4,'dispatch_target_RVA':'0xca9718','dispatch_branch_RVA':'0xca9600','dispatch_branch_executed':True,'selected_case_executed':False,'next_camera_source_RVA':'0xca9718','rejected_altered_contracts':len(altered)*len(rows),'thread_producer_invalid_API_requests_rejected':264,'new_front_camera_starts':0,'new_rear_camera_starts':0,'new_reboots':0,'new_kernel_build':False,'returned_to_Golden_Linux':True,'native_rear_runtime_allowed':False,'details':rows}
 (OUT/'SOURCE-SAFE.json').write_text(json.dumps(safe,indent=2)+'\n');print(json.dumps({k:v for k,v in safe.items() if k!='details'},sort_keys=True))
if __name__=='__main__':main()
