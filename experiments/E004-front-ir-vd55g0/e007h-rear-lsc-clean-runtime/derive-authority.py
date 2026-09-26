#!/usr/bin/env python3
from __future__ import annotations
import base64, hashlib, importlib.util, json, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
GFILE=REPO/'experiments/E004-front-ir-vd55g0/e007g-rear-lsc-tintless-windows-oracle/replay-clean.py'

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p)
    m=importlib.util.module_from_spec(s)
    sys.modules[n]=m
    assert s.loader
    s.loader.exec_module(m)
    return m
def sha(b): return hashlib.sha256(bytes(b)).hexdigest()
def shaf(p): return sha(Path(p).read_bytes())
def b64(b): return base64.b64encode(bytes(b)).decode('ascii')
def need(v,m):
    if not v: raise RuntimeError(m)

G=load(GFILE,'e007h_e007g')
need(shaf(G.TUNING)==G.TUNING_SHA,'rear tuning SHA')
need(shaf(G.OTP)==G.OTP_SHA,'rear OTP SHA')
need(shaf(G.REAR_X1)==G.X1_SHA,'rear x1 SHA')
D=load(G.DECFILE,'e007h_dec')
CL=load(G.CLFILE,'e007h_cl')
GP=load(G.GOLDFILE,'e007h_gold')
blob=G.TUNING.read_bytes();hdr=D.parse_header(blob)
need(hdr['module_name']=='com.surface.tuned.rfc_ov13858','rear tuning module')
recs,_=D.parse_symbol_table(blob,hdr['sections'][0],hdr['sections'][1]);obj=hdr['sections'][1]
raw=D.data_bytes(blob,obj,recs[0x29a]);words=struct.unpack('<18I',raw)
need(words==(0x3f800000,0x4541c000,0,0x29b,1,0x29c,0x455ac000,0x45834000,0,0x29d,1,0x29e,0x45960000,0x461c4000,0,0x29f,1,0x2a0),'lower CCT topology')
leaves={sid:G.rec_bytes(blob,hdr,recs,sid,D) for sid in (0x29c,0x29e,0x2a0)}
gold=tuple(int(v) for v in GP.parse_golden(G.TUNING)['values'])
otp=CL.parse_otp(G.OTP.read_bytes());x1=G.REAR_X1.read_bytes()
need(len(gold)==884 and sum(len(x) for x in otp)==884,'calibration shape')
out={
 'schema':'sp11-rear-ov13858-lsc-clean-authority-v1',
 'status':'PASS_DERIVED_CLEAN_RUNTIME_AUTHORITY',
 'derived_from':{'rear_tuning_sha256':G.TUNING_SHA,'rear_calibration_slot_sha256':G.OTP_SHA,'rear_x1_sha256':G.X1_SHA,'e007g_clean_replay_commit':'ad6c9e4088e7f4c4751a5f6916a788cb5ede6b85'},
 'domain':{'aec_branch':'lower_only','lux_min_inclusive':1.0,'lux_max_inclusive':340.0,'cct_min_inclusive':1.0,'cct_max_inclusive':10000.0},
 'geometry':{'full':[4076,2806],'output':[4064,2286],'crop':[6,260],'scale':1,'half_steps':[128,96],'residual':[16,9]},
 'leaf_b64':{f'0x{k:x}':b64(v) for k,v in leaves.items()},
 'leaf_sha256':{f'0x{k:x}':sha(v) for k,v in leaves.items()},
 'golden_int':list(gold),'otp_int_channels':[[int(v) for v in ch] for ch in otp],
 'x1_b64':b64(x1),'x1_sha256':G.X1_SHA,
 'policy':{'proprietary_tuning_bytes_embedded':False,'raw_windows_capture_embedded':False,'raw_request_dmi_embedded':False,'runtime_inputs':'parsed_tintless_stats+lux+cct','outside_validated_aec_domain_fails_closed':True}
}
p=HERE/'authority.json';p.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('E007H_AUTHORITY_PASS bytes=%d sha256=%s'%(p.stat().st_size,shaf(p)))
