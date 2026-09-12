#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,importlib.util,json,os,subprocess,sys,time
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
IQ=ROOT/'userspace/iq'
DISCOVER=HERE/'front-imx681-discover.py'
R4=IQ/'authority/r4-bootstrap.bin'
PRODUCER=IQ/'live-iq-producer.py'
R4_SHA='1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa'
DEFAULT_OUTPUT_ROOT=Path('/var/tmp/sp11-front-imx681')

def default_output_dir()->Path:
    stamp=time.strftime('%Y%m%dT%H%M%SZ',time.gmtime())
    return DEFAULT_OUTPUT_ROOT/f'session-{stamp}-{os.getpid()}'

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise RuntimeError(m)
def discover(topology:Path|None,media:str)->dict:
    cmd=[str(DISCOVER),'--json','--media',media]
    if topology:cmd+=['--topology-file',str(topology)]
    cp=subprocess.run(cmd,text=True,capture_output=True,check=True)
    return json.loads(cp.stdout)
def media_commands(d:dict)->list[list[str]]:
    m=d['media'];s=d['sensor_entity'];fmt=d['format']
    return [
      ['media-ctl','-d',m,'-l',f'"{d["csiphy_entity"]}":1 -> "{d["csid_entity"]}":0 [1]'],
      ['media-ctl','-d',m,'-l',f'"{d["csid_entity"]}":4 -> "{d["pix_entity"]}":0 [1]'],
      *[['media-ctl','-d',m,'-V',f'"{name}":{pad} [fmt:{fmt} field:none]'] for name,pad in ((s,0),(d['csiphy_entity'],0),(d['csiphy_entity'],1),(d['csid_entity'],0),(d['csid_entity'],4),(d['pix_entity'],0),(d['pix_entity'],1))],
    ]
def plan(args)->dict:
    d=discover(args.topology_file,args.media)
    build=args.build_dir.resolve();capture=build/'front-imx681-capture';bootstrap=build/'front-imx681-bootstrap-controls'
    need(R4.is_file() and R4.stat().st_size==41088 and sha(R4)==R4_SHA,'R4 bootstrap identity')
    frames=[str(args.output_dir/f'QC10C-{i}.bin') for i in range(27)]
    producer_out=args.output_dir/'producer'
    capture_cmd=[str(capture),d['video_node'],str(R4),str(PRODUCER),str(producer_out),str(producer_out/'RESULT.json'),str(args.output_dir/'TLBG'),str(args.output_dir/'STATS3A'),*frames]
    return {'schema':'sp11-front-imx681-launch-plan-v1','discovery':d,'post_g3_write_policy':args.post_g3_write_policy,
            'output_dir':str(args.output_dir),'media_commands':media_commands(d),'bootstrap_command':[str(bootstrap),d['sensor_subdev']],
            'capture_command':capture_cmd,'environment':{'DB_SUBDEV':d['sensor_subdev'],'SP11_FRONT_POST_G3_WRITE_POLICY':args.post_g3_write_policy},
            'r4_sha256':R4_SHA,'execute':bool(args.execute)}
def run(cmd,env=None):subprocess.run(cmd,check=True,env=env)
def main():
    ap=argparse.ArgumentParser(description='SP11 front IMX681 production launcher; dry-run unless --execute')
    ap.add_argument('--topology-file',type=Path,help='offline topology fixture; implies dry-run only')
    ap.add_argument('--media',default='/dev/media0')
    ap.add_argument('--build-dir',type=Path,default=ROOT/'build')
    ap.add_argument('--output-dir',type=Path,help='fresh session output directory; default is a unique /var/tmp session path')
    ap.add_argument('--post-g3-write-policy',choices=('shadow','cap-release-one-shot'),default='shadow')
    ap.add_argument('--allow-one-native-write',action='store_true')
    ap.add_argument('--execute',action='store_true')
    a=ap.parse_args()
    if a.output_dir is None:a.output_dir=default_output_dir()
    if a.execute and a.topology_file:raise SystemExit('--execute cannot be combined with --topology-file')
    if a.execute and os.geteuid()!=0:raise SystemExit('--execute requires root')
    if a.execute and a.post_g3_write_policy!='shadow' and not a.allow_one_native_write:
        raise SystemExit('cap-release-one-shot requires explicit --allow-one-native-write')
    p=plan(a);print(json.dumps(p,indent=2,sort_keys=True))
    if not a.execute:return
    capture=Path(p['capture_command'][0]);bootstrap=Path(p['bootstrap_command'][0])
    need(capture.is_file() and os.access(capture,os.X_OK),'production capture binary missing')
    need(bootstrap.is_file() and os.access(bootstrap,os.X_OK),'bootstrap binary missing')
    need(not a.output_dir.exists(),'output-dir already exists; choose a fresh session directory')
    a.output_dir.mkdir(parents=True,exist_ok=False);(a.output_dir/'producer').mkdir()
    for cmd in p['media_commands']:run(cmd)
    run(p['bootstrap_command'])
    env=os.environ.copy();env.update(p['environment']);run(p['capture_command'],env=env)
if __name__=='__main__':main()
