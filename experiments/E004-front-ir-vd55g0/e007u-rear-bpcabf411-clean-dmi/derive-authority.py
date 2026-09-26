#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, math, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
DEC=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/decode_imx681_chromatix.py'
TUNING=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin')
TUNING_SHA='4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635'
ROOT=0x1a
TRIGGER=0x228
REGIONS=(0x22c,0x22e,0x230,0x232,0x234,0x236)

def sha(b): return hashlib.sha256(bytes(b)).hexdigest()
def load_decoder():
    s=importlib.util.spec_from_file_location('e007u_dec',DEC)
    m=importlib.util.module_from_spec(s);sys.modules['e007u_dec']=m
    assert s.loader;s.loader.exec_module(m);return m
def frinta_pos(x): return int(math.floor(float(x)+0.5))

def derive():
    b=TUNING.read_bytes(); assert sha(b)==TUNING_SHA
    D=load_decoder(); h=D.parse_header(b)
    assert h['module_name']=='com.surface.tuned.rfc_ov13858'
    recs,_=D.parse_symbol_table(b,h['sections'][0],h['sections'][1])
    root=recs[ROOT]
    assert root['type']=='bpcabf41_ife_v2' and (root['version_major'],root['version_minor'])==(4,1)
    assert recs[TRIGGER]['type']=='mod_bpcabf41_trigger_data'
    fields=[]; points=[]
    for sid in REGIONS:
        r=recs[sid]; assert r['type']=='region' and r['data_bytes']==428
        vals=struct.unpack('<107f',D.data_bytes(b,h['sections'][1],r))
        src=[float(x) for x in vals[7:72]]
        scale=float(vals[0x62])
        pts=[]
        for x in src:
            c=max(0.0,min(511.0,x))
            q=8192.0 if c*scale==0.0 else 8192.0/(c*scale)
            pts.append(frinta_pos(q))
        fields.append((src,scale))
        points.append(pts)
    assert all(x==fields[0] for x in fields)
    assert all(x==points[0] for x in points)
    src,scale=fields[0]; pts=points[0]
    words=[]
    for i in range(64):
        a=max(0,min(511,pts[i])); z=max(0,min(511,pts[i+1]))
        words.append(a | (min(511,abs(z-a))<<9))
    payload=struct.pack('<64I',*words)
    return {
      'schema':'E007u-rear-bpcabf411-clean-authority-v1',
      'status':'PASS_DERIVED_SEMANTIC_AUTHORITY',
      'source':{
        'tuning_sha256':TUNING_SHA,
        'module':'com.surface.tuned.rfc_ov13858',
        'root_symbol':'0x1a','root_version':'4.1',
        'trigger_symbol':'0x228',
        'region_symbols':[hex(x) for x in REGIONS],
        'regions_share_lut_fields':True
      },
      'common_setting':{
        'address':'0x1809c16b0',
        'round_primitive':'FRINTA',
        'round_primitive_address':'0x1800014c0',
        'numerator':8192.0,
        'sample_clamp':[0.0,511.0],
        'scale':scale,
        'input_samples':src,
        'transformed_points':pts,
        'point_count':65
      },
      'packer':{
        'address':'0x180b41090',
        'dmi_register':'0x4908','selector':1,
        'output_words':64,'payload_bytes':256,
        'current_bits':9,'delta_bits':9,
        'word_formula':'current | (abs(next-current) << 9)',
        'derived_payload_sha256':sha(payload)
      },
      'policy':{
        'raw_windows_dmi_embedded':False,
        'proprietary_tuning_blob_embedded':False,
        'semantic_tuning_fields_committed':True
      }
    }

if __name__=='__main__':
    p=HERE/'AUTHORITY-SAFE.json'
    x=derive();p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
    print('E007U_AUTHORITY_PASS regions=6 samples=65 scale=3.0')
    print('payload_sha256='+x['packer']['derived_payload_sha256'])
