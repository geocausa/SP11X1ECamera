#!/usr/bin/env python3
from pathlib import Path
import argparse,hashlib,importlib.util,json

HERE=Path(__file__).resolve().parent
PROD=HERE.parents[1]/'e003h-iq-producer-0073-static'
PACK=PROD/'prove-lsc-live-staging-pack.py'
DLL=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll')

def loadmod(path,name):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
def sha(b):return hashlib.sha256(bytes(b)).hexdigest()
def classify(seq):
    if len(set(seq))==1:return 'stable'
    a=seq[0::2];b=seq[1::2]
    if len(set(a))==1 and len(set(b))==1 and a[0]!=b[0]:return 'two_cycle'
    return 'evolving'

def main():
    ap=argparse.ArgumentParser();ap.add_argument('capture_dir',type=Path);ap.add_argument('--result',type=Path,default=HERE/'RESULT.json');a=ap.parse_args()
    P=loadmod(PACK,'ec_pack')
    code=P.verify_code_bytes(DLL)
    rows=[]
    for r in range(4,13):
        f=a.capture_dir/f'R{r:02d}_LSC_STAGING.bin'
        if not f.is_file():raise RuntimeError(f'missing {f.name}')
        b=f.read_bytes()
        if len(b)!=P.STAGING_BYTES:raise RuntimeError(f'{f.name} size {len(b):#x}')
        geo,l0,l1,l2=P.pack_live_staging(b)
        if any(l2):raise RuntimeError(f'R{r} LSC2 unexpectedly nonzero')
        gic=(l0+l1)[0x22e:0x42e]
        rows.append({'request':r,'staging_sha256':sha(b),'bank':geo['bank'],
                     'lsc0_sha256':sha(l0),'lsc1_sha256':sha(l1),'lsc2_sha256':sha(l2),
                     'gic_alias_sha256':sha(gic)})
    banks=[x['bank'] for x in rows]
    if banks != [1,0,1,0,1,0,1,0,1]:raise RuntimeError(f'bank parity drift {banks!r}')
    post=[x for x in rows if x['request']>=6]
    laws={k:classify([x[k] for x in post]) for k in ('lsc0_sha256','lsc1_sha256','gic_alias_sha256','staging_sha256')}
    res={'schema':'sp11-e003i-ec-windows-r4-r12-lsc-staging-oracle-v1','status':'PASS_WINDOWS_ORACLE',
         'requests':list(range(4,13)),'packer_code_bytes':code,'bank_values':banks,
         'post_r6_laws':laws,'post_r6_distinct':{k:len(set(x[k] for x in post)) for k in laws},
         'rows':rows,'raw_capture_committed':False,'linux_camera_runtime':False,'continuous_aec_claimed':False,
         'next_gate':('post-R6 LSC wire content can be carried forward with deterministic bank parity; continue remaining scalar/AWB and bounded continuous scheduler work'
                      if laws['lsc0_sha256']=='stable' and laws['lsc1_sha256']=='stable' and laws['gic_alias_sha256']=='stable'
                      else 'post-R6 LSC remains dynamic; capture/replay request7+ Tintless/upstream state before continuous Linux producer extension')}
    a.result.write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
    print('EC_PACKER_CODE=PASS')
    print('EC_BANK_PARITY=1,0,1,0,1,0,1,0,1 PASS')
    for k,v in laws.items():print('EC_'+k.upper()+'_LAW='+v)
    print('EC_ANALYZE=PASS')

if __name__=='__main__':main()
