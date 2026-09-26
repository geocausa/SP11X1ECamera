#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, struct, sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
DEC=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/decode_imx681_chromatix.py'
TUNING=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin')
TUNING_SHA='4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635'
ROOT_SID=0x24
TRIGGER_SID=0x268
REGION_SID=0x26e

def sha(b: bytes)->str:
    return hashlib.sha256(b).hexdigest()

def load_decoder():
    s=importlib.util.spec_from_file_location('e007t_dec',DEC)
    m=importlib.util.module_from_spec(s)
    sys.modules['e007t_dec']=m
    assert s.loader
    s.loader.exec_module(m)
    return m

def derive():
    b=TUNING.read_bytes()
    assert sha(b)==TUNING_SHA
    D=load_decoder()
    h=D.parse_header(b)
    assert h['module_name']=='com.surface.tuned.rfc_ov13858'
    recs,_=D.parse_symbol_table(b,h['sections'][0],h['sections'][1])
    root=recs[ROOT_SID]
    assert root['type']=='gamma15_ife_v2'
    assert (root['version_major'],root['version_minor'])==(1,5)
    assert recs[TRIGGER_SID]['type']=='mod_gamma15_trigger_data'
    region=recs[REGION_SID]
    assert region['type']=='region' and region['data_bytes']==3084
    raw=D.data_bytes(b,h['sections'][1],region)
    vals=struct.unpack('<771f',raw)
    ch=[tuple(vals[i*257:(i+1)*257]) for i in range(3)]
    assert ch[0]==ch[1]==ch[2]
    curve=ch[0]
    assert all(math.isfinite(x) and float(x).is_integer() for x in curve)
    ints=[int(x) for x in curve]
    assert ints[0]==0 and ints[-1]==4095
    assert all(0<=x<=4095 for x in ints)
    assert all(ints[i+1]>=ints[i] for i in range(256))
    return {
      'schema':'E007t-rear-gamma151-clean-authority-v1',
      'status':'PASS_DERIVED_SEMANTIC_AUTHORITY',
      'source':{
        'tuning_sha256':TUNING_SHA,
        'module':'com.surface.tuned.rfc_ov13858',
        'gamma_root_symbol':'0x24',
        'gamma_root_version':'1.5',
        'trigger_symbol':'0x268',
        'region_symbol':'0x26e',
        'region_bytes':3084
      },
      'curve':{
        'channels_in_tuning':3,
        'channels_identical':True,
        'entries':257,
        'semantic_bits':12,
        'min':0,'max':4095,
        'integral':True,'monotonic_nondecreasing':True,
        'samples':ints
      },
      'packer':{
        'entries_out':256,
        'word_bits':32,
        'value_bits':12,
        'delta_bits':12,
        'word_formula':'value | ((signed_next_delta & 0xfff) << 12)',
        'delta_min':-2048,'delta_max':2047,
        'payload_bytes':1024
      },
      'policy':{
        'raw_windows_dmi_embedded':False,
        'proprietary_tuning_blob_embedded':False,
        'semantic_tuning_curve_committed':True
      }
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--out',type=Path,default=HERE/'AUTHORITY-SAFE.json')
    a=ap.parse_args()
    x=derive()
    a.out.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
    print('E007T_AUTHORITY_PASS entries=257 bits=12 channels_identical=true')
    print('authority_sha256='+sha(a.out.read_bytes()))

if __name__=='__main__':
    main()
