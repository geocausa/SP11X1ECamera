#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,pefile,capstone
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
DLL=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll')
CM=ROOT/'experiments/E004-front-ir-vd55g0/e011cm-crt-object-producers/BOOTSTRAP-SAFE.json'
EH=ROOT/'experiments/E004-front-ir-vd55g0/e011eh-source-qualified-stream-lifetime-camera-read/RESULT.json'
OUT=Path(__file__).resolve().parent

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

cm=json.loads(CM.read_text()); eh=json.loads(EH.read_text())
assert sha(DLL)==cm['authority']['original_DLL_sha256']
assert eh['startup_stream_state_to_camera_read_join_qualified']
assert eh['camera_stream_pointer_read_qualified']
assert eh['camera_next_dependency_read_RVA']=='0xcc6130'
assert eh['camera_next_dependency_RVA']=='0x16a2a50'
default_caps={x['actual_source_stream_capacity'] for x in cm['cases'] if x['owned_preset_stream_capacity']==0}
assert default_caps=={512}
pe=pefile.PE(str(DLL)); base=pe.OPTIONAL_HEADER.ImageBase
md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM)
ins={i.address-base:(i.mnemonic,i.op_str) for i in md.disasm(pe.get_data(0xcc6120,0x64),base+0xcc6120)}
expected={
  0xcc6120:('ldr','x8, [x8, #0xa58]'),
  0xcc6128:('add','x20, x8, #0x18'),
  0xcc6130:('ldrsw','x8, [x8, #0xa50]'),
  0xcc6134:('sub','x8, x8, #3'),
  0xcc6138:('add','x22, x20, x8, lsl #3'),
  0xcc613c:('b','#0x180cc617c'),
  0xcc617c:('cmp','x20, x22'),
  0xcc6180:('b.ne','#0x180cc6140')
}
for r,v in expected.items(): assert ins[r]==v,(hex(r),ins.get(r),v)
count=512
first_scan_slot=3
scan_slots=count-first_scan_slot
vector_bytes=count*8
scan_start_offset=first_scan_slot*8
scan_end_offset=scan_start_offset+scan_slots*8
assert scan_end_offset==vector_bytes==4096
result={
 'experiment':'E011EI',
 'status':'PASS_SOURCE_QUALIFIED_CAMERA_COUNT_AND_NATIVE_REFERENCE_CORRELATION',
 'original_DLL_sha256':sha(DLL),
 'inherited_E011CM_bootstrap_sha256':sha(CM),
 'inherited_E011EH_result_sha256':sha(EH),
 'camera_stream_pointer_read_RVA':'0xcc6120',
 'camera_count_read_RVA':'0xcc6130',
 'camera_count_global_RVA':'0x16a2a50',
 'source_default_stream_count':count,
 'camera_count_read_source_qualified':True,
 'first_scan_slot':first_scan_slot,
 'last_scan_slot':count-1,
 'scan_slot_count':scan_slots,
 'vector_bytes':vector_bytes,
 'scan_start_offset_bytes':scan_start_offset,
 'scan_end_is_exact_vector_end':True,
 'next_loop_guard_RVA':'0xcc617c',
 'next_loop_body_RVA':'0xcc6140',
 'native_rear_runtime_allowed':False
}
(OUT/'SOURCE-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,sort_keys=True))
