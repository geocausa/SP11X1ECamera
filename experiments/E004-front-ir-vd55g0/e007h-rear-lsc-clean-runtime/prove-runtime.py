#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, importlib.util, json, struct, tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
RUNTIME=HERE/'rear-lsc-runtime.py'
PACK=REPO/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/prove-lsc-live-staging-pack.py'

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p)
    m=importlib.util.module_from_spec(s)
    assert s.loader
    s.loader.exec_module(m)
    return m

def sha(b): return hashlib.sha256(bytes(b)).hexdigest()
def need(v,m):
    if not v: raise RuntimeError(m)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('capture_dir',type=Path)
    ap.add_argument('--out',type=Path,default=HERE/'RUNTIME-PROOF-SAFE.json')
    a=ap.parse_args()
    RT=load(RUNTIME,'e007h_runtime')
    P=load(PACK,'e007h_pack')
    with tempfile.TemporaryDirectory(prefix='e007h-') as td:
        so=Path(td)/'libtintless.so'
        RT.compile_native(so)
        prod=RT.RearDynamicLsc(so)
        rows=[]
        for req in range(4,19):
            q=f'{req:02d}'
            stats=(a.capture_dir/f'R{q}_TINTLESS_STATS.bin').read_bytes()
            trig=(a.capture_dir/f'R{q}_TRIGGER.bin').read_bytes()
            staging=(a.capture_dir/f'R{q}_LSC_STAGING.bin').read_bytes()
            need(len(stats)==0x12bec and len(trig)==0x100 and len(staging)==0x18a0,f'R{req} capture sizes')
            lux=struct.unpack_from('<f',trig,0x38)[0]
            cct=struct.unpack_from('<f',trig,0x48)[0]
            got,meta=prod.run_parsed(stats,lux,cct)
            _,w0,w1,w2=P.pack_live_staging(staging)
            want=(w0,w1,w2,(w0+w1)[0x22e:0x42e])
            exact=[got[i]==want[i] for i in range(4)]
            need(all(exact),f'R{req} wire mismatch {exact}')
            rows.append({
                'request':req,'lux':float(lux),'cct':float(cct),
                'selection':meta['selection'],'exact':exact,
                'lsc0_sha256':sha(got[0]),'lsc1_sha256':sha(got[1]),
                'lsc2_sha256':sha(got[2]),'gic_sha256':sha(got[3]),
            })
        result={
            'schema':'E007h-rear-lsc-clean-runtime-proof-v1',
            'status':'PASS',
            'requests':[x['request'] for x in rows],
            'exact_requests':sum(1 for x in rows if all(x['exact'])),
            'total_requests':len(rows),
            'all_wire_exact':all(all(x['exact']) for x in rows),
            'authority_sha256':sha((HERE/'authority.json').read_bytes()),
            'runtime_source_sha256':sha(RUNTIME.read_bytes()),
            'raw_capture_values_emitted':False,
            'rows':rows,
        }
        a.out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print('E007H_RUNTIME_PROOF_PASS requests=15 exact=15')
        print('authority_sha256='+result['authority_sha256'])
        print('runtime_source_sha256='+result['runtime_source_sha256'])
        print('raw_capture_values_emitted=false')
if __name__=='__main__': main()
