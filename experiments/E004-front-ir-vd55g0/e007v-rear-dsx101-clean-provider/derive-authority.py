#!/usr/bin/env python3
from pathlib import Path
import importlib.util,sys,struct,hashlib,json

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
DEC=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/decode_imx681_chromatix.py'
TUNING=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin')
TUNING_SHA='4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635'

def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m
 assert s.loader;s.loader.exec_module(m);return m
def sha(b): return hashlib.sha256(bytes(b)).hexdigest()
def shaf(p): return sha(p.read_bytes())
def pack(bank):
 out=bytearray()
 for i in range(len(bank)//2-1):
  w=(bank[2*i]&0xfff)|((bank[2*i+1]&0xfff)<<12)|((bank[2*i+2]&0xfff)<<24)
  out += struct.pack('<Q',w)
 i=len(bank)//2-1
 out += struct.pack('<Q',(bank[2*i]&0xfff)|((bank[2*i+1]&0xfff)<<12))
 return bytes(out)

assert shaf(TUNING)==TUNING_SHA
D=load(DEC,'e007v_dec')
blob=TUNING.read_bytes();hdr=D.parse_header(blob)
assert hdr['module_name']=='com.surface.tuned.rfc_ov13858'
recs,_=D.parse_symbol_table(blob,hdr['sections'][0],hdr['sections'][1]);obj=hdr['sections'][1]
assert recs[0x23]['type']=='dsx10_ife_video_full_dc4_v2'
assert recs[0x23]['version_major']==1 and recs[0x23]['version_minor']==0
raw=D.data_bytes(blob,obj,recs[0x265])
assert len(raw)==2824
fv=struct.unpack('<706f',raw)
assert all(float(int(x))==x for x in fv)
iv=[int(x) for x in fv]
l0,l1=iv[0:192],iv[192:384]
c0,c1=iv[384:480],iv[480:576]
assert l0==l1 and c0==c1
lp,cp=pack(l0),pack(c0)
assert len(lp)==768 and len(cp)==384
out={
 'schema':'E007v-rear-dsx101-clean-authority-v1',
 'status':'PASS_DERIVED_SEMANTIC_AUTHORITY',
 'source':{
  'tuning_sha256':TUNING_SHA,'root_symbol':'0x23','version':'1.0',
  'trigger_symbol':'0x263','region_symbol':'0x265','region_bytes':2824,
  'semantic_float_count':706,'float_to_integer':'truncate_toward_zero',
  'luma_banks_identical':True,'chroma_banks_identical':True,
 },
 'validated_path':{'scale_x':4.0,'scale_y':4.0,'nclib_fixed_4x_branch':True},
 'source_lock':{
  'calculate_hw_setting':'0x1809a5750',
  'dsx_process_nclib':'0x180e4a6c0',
  'dsx_process_internal':'0x180e4a7b0',
  'pack_luma_triplets':'0x180e47590',
  'pack_chroma_triplets':'0x180e47410',
  'titan680_pack':'0x180b52b90',
  'titan680_create_cmd_list':'0x180b52930',
 },
 'luma_coefficients':l0,
 'chroma_coefficients':c0,
 'luma_coefficients_sha256':sha(struct.pack('<192h',*l0)),
 'chroma_coefficients_sha256':sha(struct.pack('<96h',*c0)),
 'payloads':{
  '0xa008_selector1':{'bytes':768,'sha256':sha(lp)},
  '0xa008_selector2':{'bytes':768,'sha256':sha(lp)},
  '0xa208_selector1':{'bytes':384,'sha256':sha(cp)},
  '0xa208_selector2':{'bytes':384,'sha256':sha(cp)},
 },
 'policy':{
  'captured_windows_payload_embedded':False,
  'proprietary_tuning_blob_embedded':False,
  'generic_non_4x_dsx_claimed':False,
  'fail_closed_outside_validated_slots':True,
 }
}
(HERE/'AUTHORITY-SAFE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('E007V_AUTHORITY_PASS luma=192 chroma=96')
print('luma_payload_sha256='+sha(lp))
print('chroma_payload_sha256='+sha(cp))
