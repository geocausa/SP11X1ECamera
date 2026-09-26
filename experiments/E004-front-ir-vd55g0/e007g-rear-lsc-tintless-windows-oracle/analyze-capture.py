#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, struct
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
PACK=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/prove-lsc-live-staging-pack.py'
REAR_TUNING=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin')
REAR_SLOT=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/oracle-vss-20260902-local/REQ1_LSC_CAL_SLOT_0DF0.bin'
REAR_TUNING_SHA='4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635'
REAR_SLOT_SHA='fb14d234d55317c9665de39fe93ddeb76ee06b9cffc64bee8d250152ae9dfa18'

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m
def sha(b): return hashlib.sha256(bytes(b)).hexdigest()
def shaf(p): return sha(p.read_bytes())
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def f32(b,o): return struct.unpack_from('<f',b,o)[0]
def need(v,m):
    if not v: raise RuntimeError(m)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('capture_dir',type=Path)
    ap.add_argument('--result',type=Path,default=HERE/'PRIVATE-VALIDATION-SAFE.json')
    a=ap.parse_args()
    need(shaf(REAR_TUNING)==REAR_TUNING_SHA,'rear tuning SHA drift')
    need(shaf(REAR_SLOT)==REAR_SLOT_SHA,'rear calibration-slot SHA drift')
    P=load(PACK,'e007g_pack')
    rows=[]
    for r in range(4,19):
        q=f'{r:02d}'
        sp=a.capture_dir/f'R{q}_TINTLESS_STATS.bin'
        tp=a.capture_dir/f'R{q}_TRIGGER.bin'
        lp=a.capture_dir/f'R{q}_LSC_STAGING.bin'
        need(sp.is_file() and tp.is_file() and lp.is_file(),f'R{r}: missing capture file')
        stats=sp.read_bytes();trig=tp.read_bytes();staging=lp.read_bytes()
        need(len(stats)==0x12bec,f'R{r}: stats size {len(stats)}')
        need(len(trig)==0x100,f'R{r}: trigger size {len(trig)}')
        need(len(staging)==P.STAGING_BYTES,f'R{r}: staging size {len(staging)}')
        need(u32(stats,4)==0x300 and (u32(stats,0)&2),f'R{r}: Tintless stats layout')
        lux=f32(trig,0x38);cct=f32(trig,0x48)
        need(math.isfinite(lux) and math.isfinite(cct),f'R{r}: nonfinite trigger')
        geo,w0,w1,w2=P.pack_live_staging(staging)
        wgic=(w0+w1)[0x22e:0x42e]
        rows.append({
            'request':r,
            'stats_sha256':sha(stats),
            'trigger_sha256':sha(trig),
            'staging_sha256':sha(staging),
            'lux':float(lux),
            'cct':float(cct),
            'trigger_geometry_u32':{
                'b8':u32(trig,0xb8),'bc':u32(trig,0xbc),'c0':u32(trig,0xc0),'c4':u32(trig,0xc4),
                'c8':u32(trig,0xc8),'e8':u32(trig,0xe8),'ec':u32(trig,0xec),'f0':u32(trig,0xf0),
            },
            'staging_geometry':geo,
            'lsc0_sha256':sha(w0),
            'lsc1_sha256':sha(w1),
            'lsc2_sha256':sha(w2),
            'gic_alias_sha256':sha(wgic),
            'lsc2_all_zero':not any(w2),
        })
    need([x['request'] for x in rows]==list(range(4,19)),'request sequence')
    result={
        'schema':'E007g-private-validation-safe-v1',
        'capture_requests':list(range(4,19)),
        'capture_count':len(rows),
        'stats_bytes_each':0x12bec,
        'trigger_bytes_each':0x100,
        'staging_bytes_each':P.STAGING_BYTES,
        'rear_tuning_sha256':REAR_TUNING_SHA,
        'rear_calibration_slot_sha256':REAR_SLOT_SHA,
        'rows':rows,
        'raw_capture_values_committed':False,
        'clean_replay_status':'PENDING_E007G_REAR_ANALYZER',
    }
    a.result.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('E007G_PRIVATE_CAPTURE_STRUCTURE_PASS requests=15')
    print('banks='+','.join(str(x['staging_geometry']['bank']) for x in rows))
    print('raw_capture_values_emitted=false')
if __name__=='__main__': main()
