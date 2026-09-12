#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re,subprocess
from dataclasses import dataclass
from pathlib import Path

ENTITY_RE=re.compile(r'^- entity \d+: (.+?) \(')
NODE_RE=re.compile(r'^\s*device node name (\S+)\s*$')
LINK_RE=re.compile(r'^\s*-> "([^"]+)":(\d+) \[([^]]*)\]\s*$')
SENSOR_RE=re.compile(r'^imx681(?:\s|$)')
PIPELINE=('msm_csiphy2','msm_csid1','msm_vfe1_pix','msm_vfe1_video3')

@dataclass
class Entity:
    name:str
    node:str|None=None
    outgoing:list[tuple[str,int,str]]=None
    def __post_init__(self):
        if self.outgoing is None:self.outgoing=[]

def parse_topology(text:str)->dict[str,Entity]:
    entities={};cur=None
    for raw in text.splitlines():
        m=ENTITY_RE.match(raw)
        if m:
            cur=Entity(m.group(1));entities[cur.name]=cur;continue
        if cur is None:continue
        m=NODE_RE.match(raw)
        if m:cur.node=m.group(1);continue
        m=LINK_RE.match(raw)
        if m:cur.outgoing.append((m.group(1),int(m.group(2)),m.group(3)))
    return entities

def enabled_to(e:Entity,target:str)->bool:
    return any(t==target and 'ENABLED' in flags for t,_pad,flags in e.outgoing)

def resolve(text:str,media:str)->dict:
    e=parse_topology(text)
    sensors=[x for x in e.values() if SENSOR_RE.match(x.name) and x.node and x.node.startswith('/dev/v4l-subdev')]
    if len(sensors)!=1:raise RuntimeError(f'expected exactly one IMX681 sensor entity, found {[x.name for x in sensors]}')
    sensor=sensors[0]
    missing=[x for x in PIPELINE if x not in e]
    if missing:raise RuntimeError(f'missing proven pipeline entities: {missing}')
    phy,csid,pix,video=(e[x] for x in PIPELINE)
    if not enabled_to(sensor,phy.name):raise RuntimeError(f'{sensor.name}: immutable/enabled link to {phy.name} not found')
    if not video.node or not video.node.startswith('/dev/video'):raise RuntimeError(f'{video.name}: video node not found')
    # Configurable CSIPHY->CSID and CSID->PIX links may be inactive before setup; entity identity is pinned,
    # while /dev numbering and the sensor I2C bus are deliberately discovered at runtime.
    return {
      'schema':'sp11-front-imx681-media-discovery-v1','media':media,
      'sensor_entity':sensor.name,'sensor_subdev':sensor.node,
      'csiphy_entity':phy.name,'csid_entity':csid.name,'pix_entity':pix.name,
      'video_entity':video.name,'video_node':video.node,
      'format':'SRGGB10_1X10/3840x2160','proven_capture_fourcc':'QC10C',
    }

def live_candidates()->list[tuple[str,str]]:
    out=[]
    for p in sorted(Path('/dev').glob('media*')):
        if not re.fullmatch(r'media\d+',p.name):continue
        cp=subprocess.run(['media-ctl','-d',str(p),'-p'],text=True,capture_output=True)
        if cp.returncode==0:out.append((str(p),cp.stdout))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--topology-file',type=Path)
    ap.add_argument('--media',default='/dev/media0')
    ap.add_argument('--json',action='store_true')
    a=ap.parse_args()
    if a.topology_file:
        result=resolve(a.topology_file.read_text(errors='replace'),a.media)
    else:
        matches=[];errors=[]
        for media,text in live_candidates():
            try:matches.append(resolve(text,media))
            except Exception as exc:errors.append(f'{media}: {exc}')
        if len(matches)!=1:
            raise SystemExit('front IMX681 media discovery failed: matches='+str(len(matches))+'; '+'; '.join(errors))
        result=matches[0]
    if a.json:print(json.dumps(result,sort_keys=True))
    else:
        for k,v in result.items():print(f'{k.upper()}={v}')
if __name__=='__main__':main()
