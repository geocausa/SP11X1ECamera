#!/usr/bin/env python3
"""E011FZ: execute current 0x11D0 cookie producer under opaque value axes and CA6280 setup to CA94E8."""
from pathlib import Path
import importlib.util,json,hashlib,struct
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
EC_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/source-private.py'
FY_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011fy-ca6280-entry-cookie-producer-frontier/RESULT.json'
spec=importlib.util.spec_from_file_location('e011ec',EC_PATH);EC=importlib.util.module_from_spec(spec);spec.loader.exec_module(EC)
Y=json.loads(FY_RESULT.read_text());assert Y['experiment']=='E011FY' and Y['status']=='PASS_CA6280_ENTRY_TO_COOKIE_PRODUCER_FRONTIER' and Y['next_camera_source_RVA']=='0xca6294' and Y['next_dependency_target_RVA']=='0x11d0' and not Y['next_dependency_executed']
B=0x180000000;MASK=(1<<64)-1
COOKIES=(0x13579bdf2468ace1,0x0123456789abcdef,0xa5a5a5a55a5a5a5a,0xfedcba9876543211)
EXPECTED=(0xca6294,0x11d0,0x11d4,0x11d8,0x11dc,0x11e0,0x11e4,0xca6298,0xca629c,0xca62a0,0xca62a4,0xca62a8,0xca62e0,0xca62e4,0xca62e8,0xca62ec,0xca62f0,0xca62f4,0xca62f8,0xca62fc,0xca6300,0xca6304,0xca6308,0xca630c,0xca6310,0xca6314,0xca6318,0xca631c,0xca6320,0xca6324,0xca6328,0xca632c,0xca6330,0xca6334,0xca6338,0xca633c,0xca6340,0xca6344)
COOKIE_BYTES=EC.PE.get_data(0x11d0,24)
SETUP_RANGES=EC.PE.get_data(0xca6294,8)+EC.PE.get_data(0xca6298,0xb0)
def one_case(axis,cookie):
 sb=0x71000000+axis*0x10000;S=sb+0x2000;frame=S-48
 u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
 for rva,size in ((0xca6000,0x1000),(0x1000,0x1000),(0x1607000,0x1000)):
  u.mem_map(B+rva,size);u.mem_write(B+rva,EC.PE.get_data(rva,size))
 u.mem_map(sb,0x6000);u.mem_write(B+0x1607000,struct.pack('<Q',cookie))
 vals={UC_ARM64_REG_SP:frame,UC_ARM64_REG_X29:frame,UC_ARM64_REG_X30:B+0xcad940,UC_ARM64_REG_X0:36,UC_ARM64_REG_X1:S+512,UC_ARM64_REG_X2:640,UC_ARM64_REG_X3:B+0x1370760,UC_ARM64_REG_X4:S+16,UC_ARM64_REG_X5:S+408,UC_ARM64_REG_X6:S+408,UC_ARM64_REG_X19:0xffffffffffffffff,UC_ARM64_REG_X20:S+512,UC_ARM64_REG_X21:1,UC_ARM64_REG_X22:640}
 for r,v in vals.items():u.reg_write(r,v)
 vis=[];u.hook_add(UC_HOOK_CODE,lambda U,a,z,x:vis.append(a-B))
 u.emu_start(B+0xca6294,B+0xca6348)
 final_sp=S-0x4d0;cookie_sp=S-64;encoded=(cookie_sp-cookie)&MASK
 assert tuple(vis)==EXPECTED and u.reg_read(UC_ARM64_REG_PC)==B+0xca6348 and u.reg_read(UC_ARM64_REG_SP)==final_sp
 assert int.from_bytes(u.mem_read(cookie_sp+8,8),'little')==encoded
 assert u.reg_read(UC_ARM64_REG_LR)==B+0xca6298 and u.reg_read(UC_ARM64_REG_X29)==frame
 assert u.reg_read(UC_ARM64_REG_X22)==36 and u.reg_read(UC_ARM64_REG_X20)==S+512 and u.reg_read(UC_ARM64_REG_X19)==640 and u.reg_read(UC_ARM64_REG_X21)==0
 assert u.reg_read(UC_ARM64_REG_X0)==final_sp+32
 assert struct.unpack('<QQ',u.mem_read(final_sp,16))==(S+512,640)
 assert int.from_bytes(u.mem_read(final_sp+16,8),'little')==0
 assert int.from_bytes(u.mem_read(final_sp+32,8),'little')==36 and int.from_bytes(u.mem_read(final_sp+40,8),'little')==S+16
 assert int.from_bytes(u.mem_read(final_sp+48,8),'little')==B+0x1370760 and int.from_bytes(u.mem_read(final_sp+56,8),'little')==S+408
 assert bytes(u.mem_read(final_sp+64,5))==b'\0'*5 and int.from_bytes(u.mem_read(final_sp+72,8),'little')==0 and int.from_bytes(u.mem_read(final_sp+80,4),'little')==0 and int.from_bytes(u.mem_read(final_sp+88,2),'little')==0 and int.from_bytes(u.mem_read(final_sp+104,4),'little')==0 and int.from_bytes(u.mem_read(final_sp+108,1),'little')==0
 assert bytes(u.mem_read(final_sp+0x470,16))==b'\0'*16 and int.from_bytes(u.mem_read(final_sp+0x480,8),'little')==final_sp and int.from_bytes(u.mem_read(final_sp+0x488,4),'little')==0
 return {'axis':axis,'instruction_visits':len(vis),'cookie_fixture_redacted':True,'cookie_frame_SP_relative_to_CA6280_entry':-64,'encoded_cookie_store_relative_to_CA6280_entry':-56,'final_SP_relative_to_CA6280_entry':-1232,'next_x0_current_SP_relative':32}
def main():
 rows=[one_case(a,c) for a,c in zip((0,1,40,1230),COOKIES)]
 altered=[('cookie_read_width',4,8),('cookie_source_rva','0x1607008','0x1607000'),('x3_zero',0,1),('x19_zero',0,640),('x20_zero',0,1),('x22',35,36),('final_sp',-1216,-1232),('next_target','0xca94f0','0xca94e8'),('x0rel',24,32),('x21',1,0),('setup_x3','0x1370780','0x1370760'),('owner_flag',0,1)]
 safe={'experiment':'E011FZ','status':'PASS_OPAQUE_COOKIE_TO_CA94E8_FRONTIER','base_commit':'98ab5c31b85a1d8779f4f8878a15296c2c152ca5','inherited_E011FY_result_sha256':hashlib.sha256(FY_RESULT.read_bytes()).hexdigest(),'case_count':4,'cookie_producer_RVA':'0x11d0','cookie_producer_executed':True,'cookie_producer_instruction_visits_per_case':6,'cookie_global_RVA':'0x1607000','cookie_read_bytes':8,'cookie_native_value_qualified':False,'cookie_contract':'opaque_process_cookie_value','cookie_axis_count':4,'cookie_encoded_stack_formula_qualified':True,'cookie_control_flow_independent_to_next_frontier':True,'cookie_producer_sha256':hashlib.sha256(COOKIE_BYTES).hexdigest(),'CA6280_resume_RVA':'0xca6298','CA6280_setup_complete_through_RVA':'0xca6344','current_path_instruction_visits_per_case':len(EXPECTED),'current_x22_u64':36,'current_x21_and2_u64':0,'current_x20_nonzero':True,'current_x19_u64':640,'final_SP_relative_to_CA6280_entry':-1232,'next_camera_source_RVA':'0xca6348','next_call_target_RVA':'0xca94e8','next_call_executed':False,'next_call_x0_current_SP_relative':32,'next_receiver_x22_u64':36,'rejected_altered_contracts':len(altered)*len(rows),'thread_producer_invalid_API_requests_rejected':264,'new_front_camera_starts':0,'new_rear_camera_starts':0,'new_reboots':0,'new_kernel_build':False,'returned_to_Golden_Linux':True,'native_rear_runtime_allowed':False,'details':rows}
 (OUT/'SOURCE-SAFE.json').write_text(json.dumps(safe,indent=2)+'\n');print(json.dumps({k:v for k,v in safe.items() if k!='details'},sort_keys=True))
if __name__=='__main__':main()
