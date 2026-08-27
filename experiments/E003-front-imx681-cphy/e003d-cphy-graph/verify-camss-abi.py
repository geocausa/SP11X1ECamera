#!/usr/bin/env python3
import argparse, hashlib, os, subprocess
from pathlib import Path

def run(*a):
    p=subprocess.run(a,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if p.returncode: raise SystemExit(f"FAIL {' '.join(a)}: {p.stderr.strip()}")
    return p.stdout.strip()
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def symvers(p):
    d={}
    for l in Path(p).read_text().splitlines():
        c=l.split('\t')
        if len(c)>=4: d[c[1]]=c[0].lower()
    return d
def modvers(p):
    d={}
    for l in run('modprobe','--dump-modversions',str(p)).splitlines():
        if l.strip():
            crc,s=l.split(None,1); d[s]=crc.lower()
    return d
def req(x,m):
    if not x: raise SystemExit('FAIL '+m)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--module',required=True); ap.add_argument('--golden-symvers',default=None); a=ap.parse_args()
    m=Path(a.module); rel=os.uname().release; gs=Path(a.golden_symvers or f'/lib/modules/{rel}/build/Module.symvers')
    gp=Path(run('modinfo','-n','qcom_camss'))
    cv=run('modinfo','-F','vermagic',str(m)); gv=run('modinfo','-F','vermagic',str(gp))
    cs=run('modinfo','-F','srcversion',str(m)); gsrc=run('modinfo','-F','srcversion',str(gp))
    req(cv==gv, 'candidate vermagic differs from Golden qcom_camss')
    gm=symvers(gs); mv=modvers(m); bad=[s for s,c in mv.items() if gm.get(s)!=c]
    print('running_release='+rel); print('candidate_vermagic='+cv); print('golden_vermagic='+gv)
    print('candidate_srcversion='+cs); print('golden_srcversion='+gsrc)
    print('candidate_sha256='+sha(m)); print('required_imports='+str(len(mv))); print('golden_crc_mismatches='+str(len(bad)))
    if bad:
        for s in bad: print(f'BAD {s} candidate={mv[s]} golden={gm.get(s)}')
    req(not bad,'candidate has missing/mismatched Golden symbol CRCs')
    req(cs!=gsrc,'candidate srcversion unexpectedly equals Golden despite CAMSS source changes')
    print('E003D_CAMSS_ABI=PASS')
if __name__=='__main__': main()
