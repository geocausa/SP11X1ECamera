#!/usr/bin/env python3
"""E011GA: execute current CA6348 -> CA94E8 and owned receiver prefix; stop before byte read at image RVA 0x1370760."""
from pathlib import Path
import importlib.util,json,hashlib,struct
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
EC_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/source-private.py'
FZ_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011fz-opaque-cookie-ca94e8-frontier/RESULT.json'
spec=importlib.util.spec_from_file_location('e011ec',EC_PATH);EC=importlib.util.module_from_spec(spec);spec.loader.exec_module(EC)
Z=json.loads(FZ_RESULT.read_text());assert Z['experiment']=='E011FZ' and Z['status']=='PASS_OPAQUE_COOKIE_TO_CA94E8_FRONTIER' and Z['next_camera_source_RVA']=='0xca6348' and Z['next_call_target_RVA']=='0xca94e8' and not Z['next_call_executed']
B=0x180000000
EXPECTED=(0xca6348,0xca94e8,0xca94ec,0xca94f0,0xca94f4,0xca94f8,0xca94fc,0xca9500,0xca9504,0xca9508,0xca950c,0xca9524,0xca9528,0xca9560,0xca9564,0xca9568,0xca956c,0xca9570,0xca9574,0xca9578,0xca957c,0xca9580,0xca9584,0xca9588,0xca958c,0xca9848)
def one_case(axis):
 sb=0x71000000+axis*0x10000;E=sb+0x3000;C=E-0x4d0;R=C+32
 u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
 for rva,size in ((0xca6000,0x1000),(0xca9000,0x1000)):
  u.mem_map(B+rva,size);u.mem_write(B+rva,EC.PE.get_data(rva,size))
 u.mem_map(sb,0x8000)
 u.mem_write(R+0,struct.pack('<Q',36));u.mem_write(R+8,struct.pack('<Q',E+16));u.mem_write(R+0x10,struct.pack('<Q',B+0x1370760));u.mem_write(R+0x18,struct.pack('<Q',E+408));u.mem_write(R+0x20,b'\0'*0x50);u.mem_write(R+0x460,struct.pack('<Q',C));u.mem_write(R+0x468,struct.pack('<I',0))
 vals={UC_ARM64_REG_SP:C,UC_ARM64_REG_X29:E-48,UC_ARM64_REG_X0:R,UC_ARM64_REG_X1:E+512,UC_ARM64_REG_X2:640,UC_ARM64_REG_X3:B+0x1370760,UC_ARM64_REG_X4:E+16,UC_ARM64_REG_X5:E+408,UC_ARM64_REG_X6:E+408,UC_ARM64_REG_X19:640,UC_ARM64_REG_X20:E+512,UC_ARM64_REG_X21:0,UC_ARM64_REG_X22:36,UC_ARM64_REG_X23:B+0x10f03b0}
 for r,v in vals.items():u.reg_write(r,v)
 vis=[];u.hook_add(UC_HOOK_CODE,lambda U,a,z,x:vis.append(a-B));u.emu_start(B+0xca6348,B+0xca984c)
 assert tuple(vis)==EXPECTED and u.reg_read(UC_ARM64_REG_PC)==B+0xca984c
 hsp=C-64;assert u.reg_read(UC_ARM64_REG_SP)==hsp and u.reg_read(UC_ARM64_REG_X29)==hsp and u.reg_read(UC_ARM64_REG_LR)==B+0xca634c
 assert u.reg_read(UC_ARM64_REG_X19)==R and u.reg_read(UC_ARM64_REG_X5)==E+16 and u.reg_read(UC_ARM64_REG_X9)==B+0x1370760
 assert int.from_bytes(u.mem_read(R+0x468,4),'little')==1 and int.from_bytes(u.mem_read(R+0x48,4),'little')==0 and int.from_bytes(u.mem_read(R+0x24,1),'little')==0
 return {'axis':axis,'instruction_visits':len(vis),'helper_SP_relative_to_CA6280_entry':-1296,'receiver_relative_to_CA6280_entry':-1200,'receiver_counter_after_u32':1,'selected_source_RVA':'0x1370760'}
def main():
 rows=[one_case(a) for a in (0,1,40,1230)]
 altered=[('receiver_qword0',35,36),('receiver_qword1_null',0,1),('runtime_context_null',0,1),('runtime_backlink_null',0,1),('counter_initial',1,0),('source_rva','0x1370780','0x1370760'),('return_rva','0xca6350','0xca634c'),('next_source','0xca9850','0xca984c'),('read_width',4,1),('x19rel',-1192,-1200)]
 safe={'experiment':'E011GA','status':'PASS_CA94E8_OWNED_RECEIVER_PREFIX_TO_1370760_BYTE_FRONTIER','base_commit':'09986e990c9ee176f93f96b29842f3055e547d89','inherited_E011FZ_result_sha256':hashlib.sha256(FZ_RESULT.read_bytes()).hexdigest(),'case_count':4,'CA6348_call_executed':True,'CA94E8_entry_executed':True,'current_path_instruction_visits_per_case':len(EXPECTED),'CA94E8_frame_bytes':64,'CA94E8_return_RVA':'0xca634c','owned_receiver_SP_relative_to_CA6280_entry':-1200,'owned_receiver_qword0_u64':36,'owned_receiver_qword1_SP_relative_to_CA6280_entry':16,'owned_receiver_context_RVA':'0x1370760','owned_receiver_backlink_SP_relative_to_CA6280_entry':-1232,'owned_receiver_counter_before_u32':0,'owned_receiver_counter_after_u32':1,'owned_receiver_parser_state_cleared':True,'selected_source_pointer_RVA':'0x1370760','next_camera_source_RVA':'0xca984c','next_dependency_read_RVA':'0x1370760','next_dependency_bytes':1,'next_dependency_signed':True,'next_dependency_read_executed':False,'rejected_altered_contracts':len(altered)*len(rows),'thread_producer_invalid_API_requests_rejected':264,'new_front_camera_starts':0,'new_rear_camera_starts':0,'new_reboots':0,'new_kernel_build':False,'returned_to_Golden_Linux':True,'native_rear_runtime_allowed':False,'details':rows}
 (OUT/'SOURCE-SAFE.json').write_text(json.dumps(safe,indent=2)+'\n');print(json.dumps({k:v for k,v in safe.items() if k!='details'},sort_keys=True))
if __name__=='__main__':main()
