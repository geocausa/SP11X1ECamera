#!/usr/bin/env python3
import argparse,re,subprocess
from pathlib import Path

def need(v,m):
    if not v: raise AssertionError(m)

def block(text,name):
    pat=rf'^- entity \d+: {re.escape(name)} \(.*?\)(.*?)(?=^- entity |\Z)'
    m=re.search(pat,text,re.M|re.S); need(m,'missing entity '+name); return m.group(1)

def status(b,direction,peer,pad):
    m=re.search(rf'^\s*{re.escape(direction)} "{re.escape(peer)}":{pad} \[([^\]]*)\]\s*$',b,re.M)
    need(m,f'missing link {direction} {peer}:{pad}'); return {x.strip() for x in m.group(1).split(',') if x.strip()}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--mode',choices=('pre','enabled'),required=True); ap.add_argument('--from-file',type=Path); ap.add_argument('--media',default='/dev/media0'); a=ap.parse_args()
    if a.from_file: text=a.from_file.read_text(errors='replace')
    else: text=subprocess.check_output(['media-ctl','-d',a.media,'-p'],text=True)
    b1=block(text,'msm_csiphy1'); b0=block(text,'msm_csid0'); br=block(text,'msm_vfe0_rdi0'); bf=block(text,'msm_csiphy2')
    # Physical rear/front sensor links and RDI->video are immutable and enabled.
    need(status(b1,'<-',re.search(r'<- "(ov13858 [^"]+)":0',b1).group(1),0)=={'ENABLED','IMMUTABLE'},'rear sensor immutable link')
    need(status(br,'->','msm_vfe0_video0',0)=={'ENABLED','IMMUTABLE'},'rear video immutable link')
    # Front mutable branch must remain untouched in this rear-only experiment.
    need(status(bf,'->','msm_csid1',0)==set(),'front csiphy2->csid1 changed')
    target1=status(b1,'->','msm_csid0',0); target2=status(b0,'->','msm_vfe0_rdi0',0)
    if a.mode=='pre':
        need(target1==set() and target2==set(),'rear route unexpectedly pre-enabled')
    else:
        need(target1=={'ENABLED'} and target2=={'ENABLED'},'rear route not exactly enabled')
    print(f'ID_REAR_ROUTE_VERIFY=PASS MODE={a.mode} REAR_LINK1={sorted(target1)} REAR_LINK2={sorted(target2)} FRONT_MUTABLE=DISABLED')
if __name__=='__main__': main()
