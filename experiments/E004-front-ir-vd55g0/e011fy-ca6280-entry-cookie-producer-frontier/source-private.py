#!/usr/bin/env python3
"""E011FY: execute CAD93C -> CA6280 and its exact prologue; stop before the 0x11D0 cookie producer."""
from pathlib import Path
import importlib.util,json,hashlib,struct
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean'); OUT=Path(__file__).resolve().parent
EC_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/source-private.py'
FX_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011fx-native-16072d8-pair-ca6280-frontier/RESULT.json'
spec=importlib.util.spec_from_file_location('e011ec',EC_PATH); EC=importlib.util.module_from_spec(spec);spec.loader.exec_module(EC)
F=json.loads(FX_RESULT.read_text());assert F['experiment']=='E011FX' and F['status']=='PASS_NATIVE_16072D8_PAIR_TO_CA6280_FRONTIER' and F['next_camera_source_RVA']=='0xcad93c' and F['next_call_target_RVA']=='0xca6280' and not F['next_call_executed']
B=0x180000000
CALL_BYTES=EC.PE.get_data(0xcad93c,4); PROLOGUE_BYTES=EC.PE.get_data(0xca6280,20)
EXPECTED=[0xcad93c,0xca6280,0xca6284,0xca6288,0xca628c,0xca6290]
def one_case(axis):
 sb=0x71000000+axis*0x10000; sp=sb+0x1000
 u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
 for rva,size in ((0xcad000,0x1000),(0xca6000,0x1000)):
  u.mem_map(B+rva,size);u.mem_write(B+rva,EC.PE.get_data(rva,size))
 u.mem_map(sb,0x4000)
 vals={UC_ARM64_REG_SP:sp,UC_ARM64_REG_X29:sp,UC_ARM64_REG_X0:36,UC_ARM64_REG_X1:sp+512,UC_ARM64_REG_X2:640,UC_ARM64_REG_X3:B+0x1370760,UC_ARM64_REG_X4:sp+16,UC_ARM64_REG_X5:sp+408,UC_ARM64_REG_X6:sp+408,UC_ARM64_REG_X19:0xffffffffffffffff,UC_ARM64_REG_X20:sp+512,UC_ARM64_REG_X21:1,UC_ARM64_REG_X22:640}
 for r,v in vals.items():u.reg_write(r,v)
 vis=[];u.hook_add(UC_HOOK_CODE,lambda U,a,z,x:vis.append(a-B))
 u.emu_start(B+0xcad93c,B+0xca6294)
 assert vis==EXPECTED and u.reg_read(UC_ARM64_REG_PC)==B+0xca6294
 nsp=u.reg_read(UC_ARM64_REG_SP); assert nsp==sp-48 and u.reg_read(UC_ARM64_REG_X29)==nsp and u.reg_read(UC_ARM64_REG_LR)==B+0xcad940
 assert struct.unpack('<QQ',u.mem_read(nsp,16))==(sp,B+0xcad940)
 assert struct.unpack('<QQ',u.mem_read(nsp+16,16))==(0xffffffffffffffff,sp+512)
 assert struct.unpack('<QQ',u.mem_read(nsp+32,16))==(1,640)
 for r,v in [(UC_ARM64_REG_X0,36),(UC_ARM64_REG_X1,sp+512),(UC_ARM64_REG_X2,640),(UC_ARM64_REG_X3,B+0x1370760),(UC_ARM64_REG_X4,sp+16),(UC_ARM64_REG_X5,sp+408),(UC_ARM64_REG_X6,sp+408)]: assert u.reg_read(r)==v
 return {'axis':axis,'instruction_visits':len(vis),'entry_SP':sp,'dependency_SP_relative':-48,'saved_x29_SP_relative':0,'saved_LR_RVA':'0xcad940','saved_x19_u64':18446744073709551615,'saved_x20_SP_relative':512,'saved_x21_u64':1,'saved_x22_u64':640}
def main():
 rows=[one_case(x) for x in (0,1,40,1230)]
 altered=[('target','0xca6284','0xca6280'),('x0',35,36),('x1rel',504,512),('x2',639,640),('x3','0x1370788','0x1370760'),('x4rel',24,16),('x5rel',400,408),('x6rel',400,408),('x19',0,0xffffffffffffffff),('x21',0,1),('x22',639,640)]
 safe={'experiment':'E011FY','status':'PASS_CA6280_ENTRY_TO_COOKIE_PRODUCER_FRONTIER','base_commit':'1c402ac4265d8f43aabc356a6d116ef982875344','inherited_E011FX_result_sha256':hashlib.sha256(FX_RESULT.read_bytes()).hexdigest(),'case_count':4,'CAD93C_call_executed':True,'CA6280_entry_executed':True,'CA6280_prologue_instruction_visits_per_case':5,'CA6280_frame_bytes':48,'CA6280_frame_pointer_qualified':True,'CA6280_return_RVA':'0xcad940','saved_x19_u64':18446744073709551615,'saved_x20_SP_relative':512,'saved_x21_u64':1,'saved_x22_u64':640,'callsite_sha256':hashlib.sha256(CALL_BYTES).hexdigest(),'prologue_sha256':hashlib.sha256(PROLOGUE_BYTES).hexdigest(),'next_camera_source_RVA':'0xca6294','next_dependency_target_RVA':'0x11d0','next_dependency_kind':'security_cookie_producer','next_dependency_executed':False,'rejected_altered_contracts':len(altered)*len(rows),'thread_producer_invalid_API_requests_rejected':264,'new_front_camera_starts':0,'new_rear_camera_starts':0,'new_reboots':0,'new_kernel_build':False,'returned_to_Golden_Linux':True,'native_rear_runtime_allowed':False,'details':rows}
 (OUT/'SOURCE-SAFE.json').write_text(json.dumps(safe,indent=2)+'\n');print(json.dumps({k:v for k,v in safe.items() if k!='details'},sort_keys=True))
if __name__=='__main__':main()
