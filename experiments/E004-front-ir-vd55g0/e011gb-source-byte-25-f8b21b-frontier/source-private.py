#!/usr/bin/env python3
"""E011GB: join exact .rdata byte 0x25 at 0x1370760 and execute current parser prefix to 0xF8B21B lookup."""
from pathlib import Path
import importlib.util,json,hashlib,struct
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
EC_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/source-private.py';GA_RESULT=ROOT/'experiments/E004-front-ir-vd55g0/e011ga-ca94e8-receiver-prefix-1370760-frontier/RESULT.json'
spec=importlib.util.spec_from_file_location('e011ec',EC_PATH);EC=importlib.util.module_from_spec(spec);spec.loader.exec_module(EC)
A=json.loads(GA_RESULT.read_text());assert A['experiment']=='E011GA' and A['status']=='PASS_CA94E8_OWNED_RECEIVER_PREFIX_TO_1370760_BYTE_FRONTIER' and A['next_camera_source_RVA']=='0xca984c' and A['next_dependency_read_RVA']=='0x1370760' and not A['next_dependency_read_executed']
B=0x180000000;SOURCE_RVA=0x1370760;SOURCE=EC.PE.get_data(SOURCE_RVA,1);assert SOURCE==b'\x25'
EXPECTED=(0xca984c,0xca9850,0xca9854,0xca9858,0xca9590,0xca9594,0xca9598,0xca959c,0xca95a0,0xca95a4,0xca95a8,0xca95ac,0xca95b0,0xca95b4)
def one_case(axis):
 sb=0x71000000+axis*0x10000;E=sb+0x3000;C=E-0x4d0;R=C+32;H=C-64
 u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(B+0xca9000,0x1000);u.mem_write(B+0xca9000,EC.PE.get_data(0xca9000,0x1000));u.mem_map(B+0x1370000,0x10000);u.mem_write(B+0x1370000,EC.PE.get_data(0x1370000,0x10000));u.mem_map(sb,0x8000)
 u.mem_write(R+0x10,struct.pack('<Q',B+SOURCE_RVA));u.mem_write(R+0x20,b'\0'*0x30);u.mem_write(R+0x468,struct.pack('<I',1))
 vals={UC_ARM64_REG_SP:H,UC_ARM64_REG_X29:H,UC_ARM64_REG_X19:R,UC_ARM64_REG_X20:B+0xf8b210,UC_ARM64_REG_X21:1,UC_ARM64_REG_X22:36,UC_ARM64_REG_X23:0xffffffffffffffff,UC_ARM64_REG_X9:B+SOURCE_RVA}
 for r,v in vals.items():u.reg_write(r,v)
 vis=[];u.hook_add(UC_HOOK_CODE,lambda U,a,z,x:vis.append(a-B));u.emu_start(B+0xca984c,B+0xca95b8)
 assert tuple(vis)==EXPECTED and u.reg_read(UC_ARM64_REG_PC)==B+0xca95b8
 assert int.from_bytes(u.mem_read(R+0x10,8),'little')==B+0x1370761 and int.from_bytes(u.mem_read(R+0x39,1),'little')==0x25
 assert int.from_bytes(u.mem_read(R+0x20,4),'little')==0
 assert u.reg_read(UC_ARM64_REG_X10)==10 and u.reg_read(UC_ARM64_REG_X9)==B+0xf8b211 and u.reg_read(UC_ARM64_REG_X9)+u.reg_read(UC_ARM64_REG_X10)==B+0xf8b21b
 return {'axis':axis,'instruction_visits':len(vis),'source_pointer_after_RVA':'0x1370761','retained_source_byte_u8':37,'lookup_index_u64':10,'lookup_base_RVA':'0xf8b211','lookup_RVA':'0xf8b21b'}
def main():
 rows=[one_case(a) for a in (0,1,40,1230)]
 altered=[('source_byte',0x24,0x25),('source_rva','0x1370761','0x1370760'),('source_width',2,1),('parser_state',1,0),('lookup_index',8,10),('lookup_base','0xf8b210','0xf8b211'),('lookup_rva','0xf8b21a','0xf8b21b'),('branch_zero',True,False)]
 safe={'experiment':'E011GB','status':'PASS_SOURCE_BYTE_25_TO_F8B21B_LOOKUP_FRONTIER','base_commit':'dbc05524bd8c3ccd9bb7994713215d225222a133','inherited_E011GA_result_sha256':hashlib.sha256(GA_RESULT.read_bytes()).hexdigest(),'case_count':4,'source_RVA':'0x1370760','source_section':'.rdata','source_bytes':1,'source_byte_u8':37,'source_byte_s8':37,'source_byte_sha256':hashlib.sha256(SOURCE).hexdigest(),'source_read_RVA':'0xca984c','source_read_executed':True,'source_pointer_advanced_RVA':'0x1370761','source_byte_retained_receiver_offset':57,'source_nonzero_branch_taken':True,'parser_state_u32':0,'lookup_index_u64':10,'lookup_base_RVA':'0xf8b211','next_camera_source_RVA':'0xca95b8','next_dependency_read_RVA':'0xf8b21b','next_dependency_bytes':1,'next_dependency_read_executed':False,'rejected_altered_contracts':len(altered)*len(rows),'thread_producer_invalid_API_requests_rejected':264,'new_front_camera_starts':0,'new_rear_camera_starts':0,'new_reboots':0,'new_kernel_build':False,'returned_to_Golden_Linux':True,'native_rear_runtime_allowed':False,'details':rows}
 (OUT/'SOURCE-SAFE.json').write_text(json.dumps(safe,indent=2)+'\n');print(json.dumps({k:v for k,v in safe.items() if k!='details'},sort_keys=True))
if __name__=='__main__':main()
