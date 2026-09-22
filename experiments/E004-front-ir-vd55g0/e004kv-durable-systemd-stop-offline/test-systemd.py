#!/usr/bin/python3
import json,os,subprocess,tempfile,time
from pathlib import Path
assert os.geteuid()==0
def run(*a): return subprocess.check_output(a,text=True).strip()
results=[]
with tempfile.TemporaryDirectory(prefix='sp11-e004kv-systemd-') as d:
 p=Path(d); recorder=Path(__file__).with_name('record-stop.py').resolve()
 worker=p/'worker.py'
 worker.write_text("import signal,sys,time\nsignal.signal(signal.SIGTERM,lambda a,b:sys.exit(143))\nopen(sys.argv[1],'x').close()\nwhile True: time.sleep(.05)\n")
 for case,expected in [('term',('success','exited','143')),('failure',('exit-code','exited','7')),('kill',('signal','killed','KILL'))]:
  unit='sp11-e004kv-offline-'+case+'-'+str(os.getpid()); output=p/(case+'.json'); ready=p/(case+'.ready')
  argv=['systemd-run','--quiet','--unit='+unit,'--property=Type=exec','--property=SuccessExitStatus=143','--property=TimeoutStopSec=3','--property=ExecStopPost=/usr/bin/python3 '+str(recorder)+' '+str(output)]
  argv+=['/usr/bin/python3',str(worker),str(ready)] if case!='failure' else ['/bin/sh','-c','exit 7']
  try:
   subprocess.run(argv,check=True)
   if case!='failure':
    for _ in range(100):
     if ready.exists(): break
     time.sleep(.05)
    assert ready.exists()
    subprocess.run(['systemctl','stop',unit],check=True) if case=='term' else subprocess.run(['systemctl','kill','--kill-whom=main','--signal=KILL',unit],check=True)
   for _ in range(100):
    if output.exists() and output.stat().st_size: break
    time.sleep(.05)
   record=json.loads(output.read_text()); assert tuple(record[k] for k in ('service_result','exit_code','exit_status'))==expected,record
   assert record['invocation_id'] and record['boot_id']
   results.append({'case':case,'record':record,'post_stop_query':run('systemctl','show',unit,'-p','ExecMainStatus','--value')})
  finally:
   subprocess.run(['systemctl','stop',unit],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
   subprocess.run(['systemctl','reset-failed',unit],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
print(json.dumps({'status':'PASS','camera_access':False,'cases':results},indent=2))
