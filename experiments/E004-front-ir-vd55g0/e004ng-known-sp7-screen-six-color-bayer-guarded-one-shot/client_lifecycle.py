#!/usr/bin/python3
"""Bounded camera-client lifecycle acceptance. Never changes devices or routes."""
import argparse,json,os,pwd,signal,subprocess,sys,time
from pathlib import Path

def group_gone(pid):
 try: os.killpg(pid,0)
 except ProcessLookupError: return True
 return False

def validate_report(report,camera,frames):
 w,h=(1920,1080) if camera=='front' else (3840,2160)
 assert report['status']=='PASS' and report['effective_uid']==1000
 assert report['camera']==camera and report['app_format']==f'I420_{w}x{h}'
 assert report['complete_frames']==report['requested_frames']==report['distinct_payloads']==frames
 assert report['complete_bytes']==frames*w*h*3//2
 assert report['normal_eos'] and report['all_payloads_distinct'] and not report['errors']

def attempt(argv,stem,crash=False,deadline=35,identity=None):
 log=stem.with_suffix('.jsonl');err=stem.with_suffix('.stderr')
 opts={}
 if identity is not None:
  account=pwd.getpwnam(identity)
  assert account.pw_uid==1000
  opts=dict(user=account.pw_uid,group=account.pw_gid,extra_groups=os.getgrouplist(identity,account.pw_gid))
 p=None;progress=0;killed=False
 with log.open('x') as out,err.open('x') as errors:
  try:
   p=subprocess.Popen(argv,stdout=out,stderr=errors,start_new_session=True,**opts)
   limit=time.monotonic()+deadline
   while p.poll() is None and time.monotonic()<limit:
    rows=log.read_text().splitlines()
    for row in rows:
     try: progress=max(progress,json.loads(row).get('progress_frames',0))
     except json.JSONDecodeError: pass
    if crash and progress>=30:
     uid=next(x for x in Path(f'/proc/{p.pid}/status').read_text().splitlines() if x.startswith('Uid:')).split()[1:]
     assert all(int(x)==1000 for x in uid)
     os.killpg(p.pid,signal.SIGKILL);killed=True;break
    time.sleep(.02)
   if p.poll() is None and not killed: raise TimeoutError('CLIENT_DEADLINE')
   rc=p.wait(timeout=3)
   assert group_gone(p.pid),'CLIENT_DESCENDANTS_REMAIN'
   if crash:
    assert killed and rc==-signal.SIGKILL and 30<=progress<2400
   else: assert rc==0,f'CLIENT_EXIT_{rc}'
   return dict(pid=p.pid,returncode=rc,progress_before_kill=progress if crash else None,
               intentionally_killed=killed,process_group_gone=True,log=str(log))
  finally:
   if p is not None:
    if not group_gone(p.pid):os.killpg(p.pid,signal.SIGKILL)
    p.wait(timeout=3)

def cycle(client,camera,out,source='device',identity=None,deadline=35):
 phases=[];key=camera.upper()
 for name in ['FIRST','REOPEN','CRASH','RECOVERY']:
  crash=name=='CRASH';frames=2400 if crash else 120
  argv=[sys.executable,str(client),'--camera',camera,'--source',source,'--frames',str(frames),'--require-distinct','--deadline-seconds','30']
  record=attempt(argv,out/f'{key}-{name}-APP',crash,15 if crash else deadline,identity)
  if not crash:
   report=json.loads(Path(record['log']).read_text().splitlines()[-1]);validate_report(report,camera,120)
   record['app']=report
  record['phase']=name;phases.append(record)
  time.sleep(.25)
 assert len({r['pid'] for r in phases})==4
 return dict(status='PASS',camera=camera,phases=phases,normal_open_count=3,forced_app_crash_count=1,
             publisher_restart_requested=False,device_or_graph_mutations=False)

def main():
 def interrupted(signum,frame): raise SystemExit(128+signum)
 signal.signal(signal.SIGTERM,interrupted);signal.signal(signal.SIGINT,interrupted)
 p=argparse.ArgumentParser();p.add_argument('--camera',choices=['front','rear'],required=True)
 p.add_argument('--client',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
 a=p.parse_args()
 assert os.geteuid()==0 and 'sp11_camera_e004ng_rgb_session=1' in Path('/proc/cmdline').read_text().split()
 assert a.client==Path('/usr/local/lib/sp11-camera-e004ng/client.py')
 assert a.output==Path('/var/lib/sp11-camera-e004ng/output')
 print(json.dumps(cycle(a.client,a.camera,a.output,identity='geoca'),indent=2),flush=True)
if __name__=='__main__':main()
