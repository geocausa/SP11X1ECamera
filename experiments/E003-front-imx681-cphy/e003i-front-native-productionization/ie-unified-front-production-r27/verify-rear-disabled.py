#!/usr/bin/env python3
import argparse,re,subprocess
def need(v,m):
    if not v: raise AssertionError(m)
def block(text,name):
    m=re.search(rf'^- entity \d+: {re.escape(name)} \(.*?\)(.*?)(?=^- entity |\Z)',text,re.M|re.S)
    need(m,'missing '+name); return m.group(1)
def flags(b,direction,peer,pad):
    m=re.search(rf'^\s*{re.escape(direction)} "{re.escape(peer)}":{pad} \[([^\]]*)\]\s*$',b,re.M)
    need(m,f'missing link {direction} {peer}:{pad}')
    return {x.strip() for x in m.group(1).split(',') if x.strip()}
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--media',default='/dev/media0'); a=ap.parse_args()
    text=subprocess.check_output(['media-ctl','-d',a.media,'-p'],text=True)
    b1=block(text,'msm_csiphy1'); b0=block(text,'msm_csid0')
    need(flags(b1,'->','msm_csid0',0)==set(),'rear csiphy1->csid0 enabled')
    need(flags(b0,'->','msm_vfe0_rdi0',0)==set(),'rear csid0->rdi0 enabled')
    print('IE_REAR_ROUTE_DISABLED=PASS')
if __name__=='__main__': main()
