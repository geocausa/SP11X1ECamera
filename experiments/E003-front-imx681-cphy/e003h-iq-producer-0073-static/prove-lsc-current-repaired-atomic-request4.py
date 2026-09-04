#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = Path('/home/geoca/Documents/SP11-PROJECT')
DLL = PROJECT/'00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll'
FRONT = PROJECT/'00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.tuned.ffc_imx681.bin'
CAP = HERE/'oracle-live-20260904-current-repair'
OTP = CAP/'live-front-potp-slot-20260904.bin'
ATOMIC_REQ4 = CAP/'atomic-req4-input-mesh.bin'
OUT = HERE/'lsc-current-repaired-atomic-request4-oracle.json'

DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
FRONT_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
OTP_SHA='2ce64e72ae57bf19a4c60819a242a35bf5a09876862b21387e63b512d5026cdc'
REQ4_SHA='71fdf640e68b5e63cbbf84464a54de3b66f8f2df51cd273c2a9468c868d51879'
REQ5_SHA='6499164c635e70f58a950c0024ea0f35ba9f9d5be1821790fc42b9735700af2a'
REQ5_PAYLOAD_SHA='beea73b4857fc1c39464f6d360a43c5ba4232e22a16fbb190206d5f2d704f7c7'
FRONT_GOLDEN_SHA='b0023db8b7254a9922c60506db58fd9bf2d717e09a8f088d31f33b2316538f6e'
LEAF_A_SHA='bdcf62f46070513ca0d343dda341336fe3953891a2643581e8ee455b77f37a3e' # 0x4bd, req5
LEAF_B_SHA='afc02261b98c3e2655039e29ace838f5780ac26202beda08db74dbd876822a11' # 0x4bf
CURRENT_REQ4_X22_SHA='eb42c05146b3793bd4fc3fc4ca191f384a8832a29cb8da494c48b5573fce8c71'
CURRENT_REQ4_RATIO=0.212
ATOMIC_REQ4_RATIO=0.342


def sha_bytes(b: bytes) -> str: return hashlib.sha256(b).hexdigest()
def sha_file(p: Path) -> str: return sha_bytes(p.read_bytes())
def need(v, msg):
    if not v: raise RuntimeError(msg)
def load(name, path):
    s=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m

dec=load('dec', HERE/'decode_imx681_chromatix.py')
rt=load('rt', HERE/'prove-lsc-runtime-tuning-source.py')
ga=load('ga', HERE/'prove-lsc-live-golden-authority.py')
ca=load('ca', HERE/'prove-lsc-front-rear-calibration-authority.py')
em=load('em', HERE/'prove-gtm-live-exact-replay.py')

need(sha_file(DLL)==DLL_SHA,'DeviceMFT SHA drift')
need(sha_file(FRONT)==FRONT_SHA,'front tuning SHA drift')
need(sha_file(OTP)==OTP_SHA,'front OTP slot SHA drift')
need(sha_file(ATOMIC_REQ4)==REQ4_SHA,'atomic req4 target SHA drift')

blob=FRONT.read_bytes(); h=dec.parse_header(blob); rec,_=dec.parse_symbol_table(blob,h['sections'][0],h['sections'][1]); obj=h['sections'][1]
def region(sid):
    b=dec.data_bytes(blob,obj,rec[sid]); need(len(b)==0xdf0,f'leaf {sid:#x} size drift'); return b
A=region(0x4bd); B=region(0x4bf)
need(sha_bytes(A)==LEAF_A_SHA,'leaf 0x4bd drift')
need(sha_bytes(B)==LEAF_B_SHA,'leaf 0x4bf drift')

# Prove the current request4 x22 fact from the repaired Windows stream.
cur_x22=rt.interpolate_callback(A,B,rt.f32(CURRENT_REQ4_RATIO))
need(sha_bytes(cur_x22)==CURRENT_REQ4_X22_SHA,'current repaired req4 x22 replay drift')

gold=ga.parse_golden(FRONT)
need(gold and gold['golden_region_sha256']==FRONT_GOLDEN_SHA,'front golden authority drift')
channels,_=ca.parse_slot(OTP.read_bytes()); eeprom=[float(v) for ch in channels for v in ch]

target4=ATOMIC_REQ4.read_bytes(); tail=target4[0xdd0:]
need(len(tail)==0x20,'atomic target tail size drift')

surface=em.SurfaceEmu(DLL); uc=surface.uc; src=surface.heap+0x10000; dst=surface.heap+0x20000; sp=surface.stack+0x3ff000
uc.mem_write(sp,struct.pack('<QQQQQ',1,1,0,0,0))

def pipeline(ratio: float):
    ratio=rt.f32(ratio)
    x22=rt.interpolate_callback(A,B,ratio)
    x23=ca.calibrate_full(x22,gold['values'],eeprom)
    xf=struct.unpack('<884f',x23[:0xdd0])
    outs=[]
    for ch in range(4):
        uc.mem_write(src,struct.pack('<221f',*xf[ch*221:(ch+1)*221]))
        uc.mem_write(dst,bytes(0x374))
        surface.run(0x9b6048,xargs=(src,dst,4048,3152,3840,2160,104,496),instruction_limit=20_000_000)
        outs.append(bytes(uc.mem_read(dst,0x374)))
    payload=b''.join(outs)
    return ratio,x22,x23,payload,payload+tail

# Mandatory pipeline calibration: req5 is exact serialized leaf 0x4bd (ratio 0).
r5,x22_5,x23_5,p5,full5=pipeline(0.0)
need(sha_bytes(x22_5)==LEAF_A_SHA,'req5 x22 is not leaf 0x4bd')
need(sha_bytes(p5)==REQ5_PAYLOAD_SHA,f'req5 geometry payload mismatch: {sha_bytes(p5)}')
need(sha_bytes(full5)==REQ5_SHA,f'req5 full Tintless input mismatch: {sha_bytes(full5)}')

r4,x22_4,x23_4,p4,full4=pipeline(ATOMIC_REQ4_RATIO)
atomic_equal=(full4==target4)
result={
 'schema':'sp11-e003h-current-repaired-atomic-request4-v1',
 'status':'PASS' if atomic_equal else 'CANDIDATE_MISS',
 'source_authority':{'device_mft_sha256':DLL_SHA,'front_tuning_sha256':FRONT_SHA,'front_golden_sha256':FRONT_GOLDEN_SHA,'front_otp_slot_sha256':OTP_SHA},
 'repaired_windows_validation':{'req5_ratio_float32':r5,'x22_sha256':sha_bytes(x22_5),'x23_sha256':sha_bytes(x23_5),'payload_sha256':sha_bytes(p5),'full_input_sha256':sha_bytes(full5),'byte_exact':True},
 'current_req4_control':{'ratio_float32':rt.f32(CURRENT_REQ4_RATIO),'x22_sha256':sha_bytes(cur_x22),'expected_x22_sha256':CURRENT_REQ4_X22_SHA,'byte_exact':True},
 'atomic_req4_candidate':{'ratio_float32':r4,'x22_sha256':sha_bytes(x22_4),'x23_sha256':sha_bytes(x23_4),'payload_sha256':sha_bytes(p4),'full_input_sha256':sha_bytes(full4),'target_sha256':REQ4_SHA,'byte_differences':sum(a!=b for a,b in zip(full4,target4)),'byte_exact':atomic_equal},
 'geometry':{'full':[4048,3152],'output':[3840,2160],'offset':[104,496],'native_resampler_rva':'0x9b6048'},
 'safety':{'offline_only':True,'linux_camera_runtime':False,'linux_request6_executed':False}
}
OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(json.dumps(result,indent=2,sort_keys=True))
if not atomic_equal: raise SystemExit(2)
