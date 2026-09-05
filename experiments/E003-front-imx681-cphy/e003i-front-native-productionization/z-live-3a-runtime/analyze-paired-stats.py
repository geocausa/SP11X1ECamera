#!/usr/bin/env python3
import argparse, hashlib, json, struct
from pathlib import Path

TLBG_MAGIC = 0x47424C54
TLBG_HEADER = 32
TLBG_RAW = 0xF000
TLBG_TOTAL = TLBG_HEADER + TLBG_RAW
S3_MAGIC = 0x54534133
S3_HEADER = 64
S3_AEC = 0x14000
S3_BHIST = 0x1000
S3_AWB = 0x3C000
S3_RAW = S3_AEC + S3_BHIST + S3_AWB
S3_TOTAL = S3_HEADER + S3_RAW
EXPECTED_SLOT = [0,1,0,1,0,1]

def sha(b): return hashlib.sha256(b).hexdigest()
def nz(b): return sum(x != 0 for x in b)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot-dir', type=Path, default=Path(__file__).resolve().parent)
    a=ap.parse_args(); d=a.snapshot_dir
    rows=[]
    for i in range(6):
        t=(d/f'TLBG-{i}.bin').read_bytes(); s=(d/f'STATS3A-{i}.bin').read_bytes()
        if len(t)!=TLBG_TOTAL or len(s)!=S3_TOTAL: raise SystemExit(f'size mismatch frame {i}')
        tm,tv,th=struct.unpack_from('<IHH',t,0); tg=struct.unpack_from('<Q',t,8)[0]
        ts,tslot,traw,tflags=struct.unpack_from('<IIII',t,16)
        if (tm,tv,th,traw,tflags)!=(TLBG_MAGIC,1,TLBG_HEADER,TLBG_RAW,1): raise SystemExit(f'TLBG ABI frame {i}')
        sm,sv,sh=struct.unpack_from('<IHH',s,0); sg=struct.unpack_from('<Q',s,8)[0]
        ss,sslot,aoff,asz,boff,bsz,woff,wsz,sflags,r0,r1,r2=struct.unpack_from('<IIIIIIIIIIII',s,16)
        if (sm,sv,sh)!=(S3_MAGIC,1,S3_HEADER): raise SystemExit(f'3A ABI frame {i}')
        if (aoff,asz,boff,bsz,woff,wsz,sflags,r0,r1,r2)!=(0,S3_AEC,S3_AEC,S3_BHIST,S3_AEC+S3_BHIST,S3_AWB,1,0,0,0): raise SystemExit(f'3A layout frame {i}')
        if (tg,ts,tslot)!=(i+1,i+1,EXPECTED_SLOT[i]): raise SystemExit(f'TLBG identity frame {i}')
        if (sg,ss,sslot)!=(tg,ts,tslot): raise SystemExit(f'paired identity frame {i}')
        p=s[S3_HEADER:]
        parts={'aec_be':p[aoff:aoff+asz], 'bhist':p[boff:boff+bsz], 'awb_bg':p[woff:woff+wsz]}
        if any(nz(v)==0 for v in parts.values()): raise SystemExit(f'zero 3A payload frame {i}')
        rows.append({
            'frame':i,'generation':sg,'source_seq':ss,'slot':sslot,
            'tlbg_snapshot_sha256':sha(t),'tlbg_raw_sha256':sha(t[TLBG_HEADER:]),
            'stats3a_snapshot_sha256':sha(s),
            **{f'{n}_bytes':len(v) for n,v in parts.items()},
            **{f'{n}_nonzero_bytes':nz(v) for n,v in parts.items()},
            **{f'{n}_sha256':sha(v) for n,v in parts.items()},
        })
    for n in ('aec_be','bhist','awb_bg'):
        if len({r[f'{n}_sha256'] for r in rows}) != 6: raise SystemExit(f'{n} not generation-unique')
    if len({r['tlbg_raw_sha256'] for r in rows}) != 6: raise SystemExit('TLBG not generation-unique')
    out={
        'schema':'sp11-e003i-z-paired-live-stats-analysis-v1',
        'status':'PASS',
        'frames':rows,
        'paired_identity_exact':True,
        'generation_sequence':[r['generation'] for r in rows],
        'source_seq_sequence':[r['source_seq'] for r in rows],
        'slot_sequence':[r['slot'] for r in rows],
        'aec_be_all_nonzero':True,'bhist_all_nonzero':True,'awb_bg_all_nonzero':True,
        'aec_be_all_generation_unique':True,'bhist_all_generation_unique':True,'awb_bg_all_generation_unique':True,
        'tlbg_all_generation_unique':True,
        'request_id_inference_authorized':False,
    }
    print(json.dumps(out, indent=2, sort_keys=True))
if __name__=='__main__': main()
