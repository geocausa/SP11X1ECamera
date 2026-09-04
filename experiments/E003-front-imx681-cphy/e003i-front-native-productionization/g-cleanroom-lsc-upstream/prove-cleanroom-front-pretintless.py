#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,importlib.util,json,struct
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
PROJECT=Path('/home/geoca/Documents/SP11-PROJECT')
TUNING=PROJECT/'00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.tuned.ffc_imx681.bin'
OTP=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/oracle-live-20260904-current-repair/live-front-potp-slot-20260904.bin'
RAW=REPO.parent/'.local-oracles/oracle-live-20260904-front-atomic'
DEC=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/decode_imx681_chromatix.py'
GOLD=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/prove-lsc-live-golden-authority.py'
EXPECTED={4:'25b80b20b5410ac0742a5fd26dbb32ac716cfa41a41965a5aaa98cbba39635e7',5:'beea73b4857fc1c39464f6d360a43c5ba4232e22a16fbb190206d5f2d704f7c7',6:'beea73b4857fc1c39464f6d360a43c5ba4232e22a16fbb190206d5f2d704f7c7'}
TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
OTP_SHA='2ce64e72ae57bf19a4c60819a242a35bf5a09876862b21387e63b512d5026cdc'
GOLD_SHA='b0023db8b7254a9922c60506db58fd9bf2d717e09a8f088d31f33b2316538f6e'
LEAF_A_SHA='bdcf62f46070513ca0d343dda341336fe3953891a2643581e8ee455b77f37a3e'
LEAF_B_SHA='afc02261b98c3e2655039e29ace838f5780ac26202beda08db74dbd876822a11'

def load(name,p):
 s=importlib.util.spec_from_file_location(name,p); m=importlib.util.module_from_spec(s); assert s.loader; s.loader.exec_module(m); return m
def sha(b): return hashlib.sha256(b).hexdigest()
def shaf(p): return sha(p.read_bytes())
def need(v,msg):
 if not v: raise RuntimeError(msg)

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--output-dir',type=Path); ap.add_argument('--manifest',type=Path); a=ap.parse_args()
 cl=load('cl',HERE/'cleanroom-front-lsc.py'); dec=load('dec',DEC); gp=load('gp',GOLD)
 need(shaf(TUNING)==TUNING_SHA,'front tuning SHA drift'); need(shaf(OTP)==OTP_SHA,'front OTP SHA drift')
 blob=TUNING.read_bytes(); h=dec.parse_header(blob); rec,_=dec.parse_symbol_table(blob,h['sections'][0],h['sections'][1]); obj=h['sections'][1]
 def region(sid): return dec.data_bytes(blob,obj,rec[sid])
 A=region(0x4bd); B=region(0x4bf); need(sha(A)==LEAF_A_SHA,'leaf A drift'); need(sha(B)==LEAF_B_SHA,'leaf B drift')
 gold=gp.parse_golden(TUNING); need(gold and gold['golden_region_sha256']==GOLD_SHA,'golden drift')
 otp=cl.parse_otp(OTP.read_bytes())
 ratios={4:0.342,5:0.0,6:0.0}; result={}
 if a.output_dir: a.output_dir.mkdir(parents=True,exist_ok=True)
 for r in (4,5,6):
  x22=cl.interpolate_leaf(A,B,ratios[r]); x23=cl.calibrate(x22,gold['values'],otp); payload=cl.resample_x23(x23)
  target=(RAW/f'req{r}_input_mesh.bin').read_bytes()[:0xdd0]
  got=sha(payload); need(got==EXPECTED[r],f'R{r} generated SHA drift {got}'); need(payload==target,f'R{r} Windows target mismatch')
  if a.output_dir: (a.output_dir/f'E003I_CLEAN_PRETINTLESS_R{r}.bin').write_bytes(payload)
  result[str(r)]={'ratio_float32':struct.unpack('<f',struct.pack('<f',ratios[r]))[0],'x22_sha256':sha(x22),'x23_sha256':sha(x23),'payload_sha256':got,'windows_payload_sha256':sha(target),'byte_exact':True}
 out={'schema':'sp11-e003i-cleanroom-front-pretintless-v1','status':'PASS','inputs':{'front_tuning_sha256':TUNING_SHA,'front_golden_sha256':GOLD_SHA,'physical_front_otp_sha256':OTP_SHA},'geometry':{'full':[4048,3152],'active':[3840,2160],'crop':[104,496],'source_pitch_half':[126.4375,131.25],'target_pitch_half':[120,96],'vertical_center_adjust_half':36,'interior':'Catmull-Rom bicubic','outer_ring':'bilinear'},'requests':result,'native_code_dependency':False,'device_mft_dependency':False,'captured_pretintless_mesh_input':False,'runtime_authorized':False}
 if a.manifest: a.manifest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
 print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
