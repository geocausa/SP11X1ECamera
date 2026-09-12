#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,shutil,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
VENDOR=HERE/'vendor'
MANIFEST=HERE/'AUTHORITY-CACHE-MANIFEST.json'
TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,msg):
    if not v: raise RuntimeError(msg)
def detect_repo()->Path:
    cp=subprocess.run(['git','-C',str(HERE),'rev-parse','--show-toplevel'],text=True,capture_output=True,check=True)
    return Path(cp.stdout.strip()).resolve()
def copy_checked(src:Path,dst:Path,size:int,want:str):
    need(src.is_file(),f'missing authority input {src}')
    need(src.stat().st_size==size,f'authority size drift {src}')
    need(sha(src)==want,f'authority SHA drift {src}')
    dst.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(src,dst)
    need(dst.stat().st_size==size and sha(dst)==want,f'cache copy drift {dst}')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source-repo',type=Path,default=None)
    ap.add_argument('--front-tuning',type=Path,required=True,
                    help='local Windows IMX681 tuning blob; verified by SHA and copied only into ignored runtime cache')
    a=ap.parse_args();source=(a.source_repo or detect_repo()).resolve();tuning=a.front_tuning.resolve()
    m=json.loads(MANIFEST.read_text());need(m['schema']=='sp11-front-imx681-iq-authority-cache-manifest-v1','manifest schema')
    for e in m['repo_entries']:
        copy_checked(source/e['source_rel'],VENDOR/e['vendor_rel'],e['bytes'],e['sha256'])
    need(sha(tuning)==TUNING_SHA,'front tuning SHA drift')
    e=m['external_entries'][0];copy_checked(tuning,VENDOR/e['vendor_rel'],e['bytes'],e['sha256'])
    marker=VENDOR/'local-authority/PREPARED.json'
    marker.parent.mkdir(parents=True,exist_ok=True)
    marker.write_text(json.dumps({'schema':'sp11-front-imx681-iq-authority-cache-prepared-v1','status':'PASS','repo_entries':len(m['repo_entries']),'external_entries':len(m['external_entries']),'manifest_sha256':sha(MANIFEST),'front_tuning_sha256':TUNING_SHA},indent=2,sort_keys=True)+'\n')
    print(f'IQ_AUTHORITY_CACHE=PASS REPO={len(m["repo_entries"])} EXTERNAL={len(m["external_entries"])}')
    print(f'MANIFEST_SHA256={sha(MANIFEST)}')
if __name__=='__main__':main()
