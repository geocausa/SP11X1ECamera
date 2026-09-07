#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, importlib.util, json, statistics, tempfile, time

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DEFAULT_Z=BASE/'z-live-3a-runtime'
DEFAULT_AG=BASE/'ag-bounded-live-r5-r6-runtime'/'runtime-output'
EXPECTED={
    'retained_z': {5:'350fed1aaa4c6c3e9fbed8d3e63f14fcaf7a6cf80be9e8f800536a0ddfa14795',6:'e85dbe7b8b46837e09207586b56e4e648d674ea4663d18ea6b46d1b1f885dd8c'},
    'actual_ag': {5:'b05698889f607d5786a441a7c85ef07b6f61852d20a1894ff8f4919b07051d94',6:'f694734412fe7cf4669fd1bfadb0f7eecc4d8f4b34f94f60a4a9068537dc546e'},
}

def load(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m

def sha(data): return hashlib.sha256(bytes(data)).hexdigest()
def shp(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def fs(values):
    s=sorted(values)
    return {'mean_ms':statistics.mean(values),'p95_ms':s[int(len(s)*.95)-1],'p99_ms':s[int(len(s)*.99)-1],'max_ms':max(values)}

def snapshots(directory):
    return [((directory/f'STATS3A-{i}.bin').read_bytes(),(directory/f'TLBG-{i}.bin').read_bytes()) for i in range(3)]

def source_hashes(directory):
    return {
        'stats3a':[shp(directory/f'STATS3A-{i}.bin') for i in range(3)],
        'tlbg':[shp(directory/f'TLBG-{i}.bin') for i in range(3)],
    }

def run_domain(P,name,directory,iterations,cct_mode):
    snaps=snapshots(directory); expected=EXPECTED[name]
    with tempfile.TemporaryDirectory(prefix=f'e003i-selector-{name}-') as td:
        prod=P.Producer(Path(td)); first=[]; caps={}; per=[[],[],[]]; seq=[]
        for s,t in snaps:
            row,cap,_=prod.process(s,t);first.append(row)
            if cap is not None:caps[row['request_target']]=cap
        assert [r['generation'] for r in first]==[1,2,3]
        assert all(r['lsc']['cct_selector_mode']==cct_mode for r in first),[(r['generation'],r['lsc']['cct_selector_mode']) for r in first]
        assert all(r['lsc']['aec_selector_mode']=='gap_390_490' for r in first)
        for req in (5,6):assert sha(caps[req])==expected[req],f'{name} R{req} drift'
        for _ in range(iterations):
            prod.trigger.prev_x=P.frombits(P.INITIAL_PREV_X_BITS);prod.trigger.prev_y=P.frombits(P.INITIAL_PREV_Y_BITS);prod.lsc.reset();prod.rows=[];t0=time.perf_counter_ns()
            for i,(s,t) in enumerate(snaps):
                row,cap,_=prod.process(s,t);per[i].append(row['total_process_ms'])
                if cap is not None:assert sha(cap)==expected[row['request_target']]
            seq.append((time.perf_counter_ns()-t0)/1e6)
        compact=[]
        for r in first:
            compact.append({
                'generation':r['generation'],'lux':r['lux'],'lux_bits':r['lux_bits'],'published_cct':r['published_cct'],'final_cct_bits':r['final_cct_bits'],
                'cct_selector_mode':r['lsc']['cct_selector_mode'],'cct_ratio':r['lsc']['cct_ratio'],'cct_ratio_bits':r['lsc']['cct_ratio_bits'],
                'aec_selector_mode':r['lsc']['aec_selector_mode'],'aec_ratio':r['lsc']['aec_ratio'],'aec_ratio_bits':r['lsc']['aec_ratio_bits'],
                'x22_sha256':r['lsc']['x22_sha256'],'capsule_sha256':r['capsule_sha256']
            })
        return {
            'source_dir':str(directory),'source_hashes':source_hashes(directory),'first_sequence':compact,
            'expected_capsules':expected,'timing':{'iterations':iterations,'G1':fs(per[0]),'G2_R5':fs(per[1]),'G3_R6':fs(per[2]),'G1_G3_sequence':fs(seq),'frame_budget_ms':1000/30},
        }

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--retained-z-dir',type=Path,default=DEFAULT_Z);ap.add_argument('--actual-ag-dir',type=Path,default=DEFAULT_AG);ap.add_argument('--iterations',type=int,default=100);ap.add_argument('--manifest',type=Path,required=True);a=ap.parse_args();assert a.iterations>=20
    P=load(HERE/'live-iq-producer.py','expanded_selector_prod')
    out={'schema':'sp11-e003i-ae-expanded-lsc-selector-proof-v1','status':'PASS','runtime_performed':False,'selection_law':'R5<-G2, R6<-G3','domains':{}}
    out['domains']['retained_z']=run_domain(P,'retained_z',a.retained_z_dir,a.iterations,'leaf_0x4bf')
    out['domains']['actual_ag']=run_domain(P,'actual_ag',a.actual_ag_dir,a.iterations,'gap_4500_5000')
    out['claims']={'retained_z_unchanged':True,'actual_ag_gap_supported':True,'two_dimensional_selector':'lower CCT tree first, then outer AEC tree','continuous_aec_claimed':False}
    a.manifest.parent.mkdir(parents=True,exist_ok=True);a.manifest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('E003I_AE_EXPANDED_SELECTOR=PASS')
    for n in ('retained_z','actual_ag'):
        d=out['domains'][n]
        print(f"{n} G2_R5_P95_MS={d['timing']['G2_R5']['p95_ms']:.4f} G3_R6_P95_MS={d['timing']['G3_R6']['p95_ms']:.4f} R5={d['expected_capsules'][5]} R6={d['expected_capsules'][6]}")

if __name__=='__main__':main()
