#!/usr/bin/env python3
import argparse,re
from pathlib import Path

LINKS={
 'rear1':('msm_csiphy1','msm_csid0',0),
 'rear2':('msm_csid0','msm_vfe0_rdi0',0),
 'front1':('msm_csiphy2','msm_csid1',0),
 'front2':('msm_csid1','msm_vfe1_pix',0),
}

def block(text,name):
    m=re.search(rf'^- entity \d+: {re.escape(name)} \(.*?\)(.*?)(?=^- entity |\Z)',text,re.M|re.S)
    if not m: raise RuntimeError('missing '+name)
    return m.group(1)

def enabled(text,src,dst,pad):
    b=block(text,src)
    m=re.search(rf'^\s*-> "{re.escape(dst)}":{pad} \[([^\]]*)\]\s*$',b,re.M)
    if not m: raise RuntimeError(f'missing link {src}->{dst}:{pad}')
    return 'ENABLED' in {x.strip() for x in m.group(1).split(',')}

def classify(text):
    v={k:enabled(text,*spec) for k,spec in LINKS.items()}
    rear=v['rear1'] and v['rear2']; front=v['front1'] and v['front2']
    partial=(v['rear1']!=v['rear2']) or (v['front1']!=v['front2'])
    if partial: state='invalid-partial'
    elif rear and front: state='invalid-mixed'
    elif rear: state='rear-only'
    elif front: state='front-only'
    else: state='neutral'
    return state,v

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('topology',type=Path)
    ap.add_argument('--expect',choices=('neutral','rear-only','front-only','invalid-partial','invalid-mixed'))
    a=ap.parse_args()
    state,v=classify(a.topology.read_text(errors='replace'))
    if a.expect and state!=a.expect: raise SystemExit(f'expected {a.expect}, got {state}: {v}')
    print('IF_ROUTE_STATE='+state+' '+ ' '.join(f'{k}={int(x)}' for k,x in v.items()))
if __name__=='__main__': main()
