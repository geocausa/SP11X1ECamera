#!/usr/bin/env python3
import argparse,json,re,subprocess
from pathlib import Path

def need(v,m):
    if not v: raise RuntimeError(m)

def parse_entities(text):
    ents={}
    pat=r'^- entity \d+: (.*?) \(\d+ pads?, \d+ links?(?:, \d+ routes?)?\)(.*?)(?=^- entity |\Z)'
    for mm in re.finditer(pat,text,re.M|re.S):
        name=mm.group(1).strip(); block=mm.group(2)
        dn=re.search(r'device node name (\S+)',block)
        ents[name]={'device':dn.group(1) if dn else None,'block':block}
    return ents

def discover(text,media):
    ents=parse_entities(text)
    sensors=[x for x in ents if x.startswith('ov13858 ')]
    fronts=[x for x in ents if x.startswith('imx681 ')]
    need(len(sensors)==1,'rear sensor count '+repr(sensors)); need(len(fronts)==1,'front sensor count '+repr(fronts))
    for x in ('msm_csiphy1','msm_csid0','msm_vfe0_rdi0','msm_vfe0_video0','msm_csiphy2','msm_csid1','msm_vfe1_pix','msm_vfe1_video3'):
        need(x in ents,'missing entity '+x)
    out={'media':media,'rear_sensor_entity':sensors[0],'rear_sensor_device':ents[sensors[0]]['device'],'front_sensor_entity':fronts[0],'front_sensor_device':ents[fronts[0]]['device'],'rear_video_device':ents['msm_vfe0_video0']['device'],'front_video_device':ents['msm_vfe1_video3']['device'],'rear_route':['msm_csiphy1','msm_csid0','msm_vfe0_rdi0','msm_vfe0_video0'],'front_route':['msm_csiphy2','msm_csid1','msm_vfe1_pix','msm_vfe1_video3']}
    need(out['rear_sensor_device'] and out['rear_video_device'],'rear device nodes'); need(out['front_sensor_device'] and out['front_video_device'],'front device nodes')
    return out

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--from-file',type=Path); ap.add_argument('--media-name',default='/dev/media0'); a=ap.parse_args()
    if a.from_file:
        print(json.dumps(discover(a.from_file.read_text(errors='replace'),a.media_name),indent=2,sort_keys=True)); return
    chosen=None;text=None
    for m in sorted(Path('/dev').glob('media*')):
        cp=subprocess.run(['media-ctl','-d',str(m),'-p'],text=True,capture_output=True)
        if cp.returncode==0 and 'ov13858 ' in cp.stdout and 'imx681 ' in cp.stdout and 'msm_csiphy1' in cp.stdout:
            chosen=str(m); text=cp.stdout; break
    need(chosen,'no unified rear+front CAMSS media graph')
    print(json.dumps(discover(text,chosen),indent=2,sort_keys=True))
if __name__=='__main__': main()
