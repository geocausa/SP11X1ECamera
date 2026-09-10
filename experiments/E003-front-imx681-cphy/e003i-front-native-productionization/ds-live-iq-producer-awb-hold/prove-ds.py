#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,importlib.util,json,statistics,struct,tempfile,time

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
EXPECTED={5:'350fed1aaa4c6c3e9fbed8d3e63f14fcaf7a6cf80be9e8f800536a0ddfa14795',6:'e85dbe7b8b46837e09207586b56e4e648d674ea4663d18ea6b46d1b1f885dd8c'}
DEFAULT_DP=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-dp/attempt1-iq-awb-zero-weight-20260910T2020/runtime-output/producer')

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(b): return hashlib.sha256(bytes(b)).hexdigest()
def bits(x): return struct.unpack('<I',struct.pack('<f',float(x)))[0]
def fs(v):
    s=sorted(v); return {'mean_ms':statistics.mean(v),'p95_ms':s[int(len(s)*.95)-1],'p99_ms':s[int(len(s)*.99)-1],'max_ms':max(v)}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot-dir',type=Path,required=True)
    ap.add_argument('--dp-dir',type=Path,default=DEFAULT_DP)
    ap.add_argument('--iterations',type=int,default=100)
    ap.add_argument('--manifest',type=Path,default=HERE/'RESULT.json')
    a=ap.parse_args(); assert a.iterations>=20
    P=load(HERE/'live-iq-producer.py','dsprod')
    snaps=[((a.snapshot_dir/f'STATS3A-{i}.bin').read_bytes(),(a.snapshot_dir/f'TLBG-{i}.bin').read_bytes()) for i in range(3)]
    with tempfile.TemporaryDirectory(prefix='e003i-ds-proof-') as td:
        td=Path(td); prod=P.Producer(td/'normal')
        rows=[]; caps={}
        for s,t in snaps:
            row,cap,desc=prod.process(s,t); rows.append(row)
            assert row['awb_hold_previous'] is False
            if cap is not None: caps[row['request_target']]=cap
        for req in (5,6): assert sha(caps[req])==EXPECTED[req],f'normal R{req} drift'
        assert [sha(caps[5]),sha(caps[6])]==[EXPECTED[5],EXPECTED[6]]

        # Exact preserved DP G1 branch.
        s=(a.dp_dir/'STATS3A-G1.bin').read_bytes(); t=(a.dp_dir/'TLBG-G1.bin').read_bytes()
        assert sha(s)=='1344836e819a28d4a9aef5f9d91908ca6806d59b08bec0f2c185fb56149087ea'
        assert sha(t)=='23fc2d68996c4b0aa5722a1041e71641aa5e3bc0c49dc29243cdf0bd41a0877d'
        holdprod=P.Producer(td/'hold')
        row,cap,desc=holdprod.process(s,t)
        assert cap is None and row['request_target'] is None
        assert row['awb_hold_previous'] is True
        assert row['final_xy_bits']==['0x3f1129ca','0x3f00e486']
        assert row['final_cct_bits']=='0x459c3ffb' and row['published_cct']==4999
        assert row['fresh_cct_bits']=='0x00000000' and row['p01']==8 and row['valid']==0
        assert row['lux_bits']=='0x43fcf636' and row['measured_luma_bits']=='0x3f21a52b'
        assert bits(holdprod.trigger.prev_x)==P.INITIAL_PREV_X_BITS and bits(holdprod.trigger.prev_y)==P.INITIAL_PREV_Y_BITS

        # Hold path remains comfortably inside one frame budget.
        times=[]; hp=P.Producer(td/'timing')
        for _ in range(a.iterations):
            hp.reset_sequence()
            t0=time.perf_counter_ns(); r,_,_=hp.process(s,t); times.append((time.perf_counter_ns()-t0)/1e6)
            assert r['awb_hold_previous'] is True and r['final_cct_bits']=='0x459c3ffb'
        timing=fs(times)
        out={'schema':'sp11-e003i-ds-live-iq-producer-awb-hold-proof-v1','status':'PASS','runtime_performed':False,'normal_ae_capsules_unchanged':{'R5':EXPECTED[5],'R6':EXPECTED[6]},'normal_rows_hold_flags':[r['awb_hold_previous'] for r in rows],'dp_attempt1_g1_hold':row,'hold_timing_ms':timing,'frame_budget_ms':1000/30,'hold_deadline_pass':timing['p95_ms']<1000/30,'windows_authority':'DQ','native_hold_authority':'DR','continuous_aec_claimed':False,'next_gate':'stage a fresh bounded live candidate using DS producer; no DP candidate reuse'}
        a.manifest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
        print('DS_NORMAL_R5_R6_UNCHANGED=PASS')
        print('DS_DP_G1_HOLD_XY=0x3f1129ca/0x3f00e486')
        print('DS_DP_G1_HELD_CCT=4999')
        print(f"DS_HOLD_P95_MS={timing['p95_ms']:.4f}")
        print('DS_VERIFY=PASS')
if __name__=='__main__': main()
