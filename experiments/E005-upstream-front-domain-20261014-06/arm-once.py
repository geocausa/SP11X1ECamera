#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
# One-use worker; consumed identity must never be rearmed.
from pathlib import Path
import hashlib,json,os,subprocess,time
R=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-upstream')
Q=R/'experiments/E005-upstream-front-domain-20261014-06'
D=Path('/var/lib/sp11-camera-upstream-front-20261014-06')
ID=D.name
HEAD=(D/'EXPECTED-HEAD').read_text().strip()
os.environ.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(R))
def run(a):
 return subprocess.check_output(a,text=True)
def sha(p):
 return hashlib.sha256(p.read_bytes()).hexdigest()
assert os.geteuid()==0
assert json.loads(Path('/var/lib/sp11-camera-upstream-front-20261014-05/RETIRED.json').read_text())['status']=='RETIRED_CONSUMED_DO_NOT_RETRY'
subprocess.run(['bash',str(R/'tools/camera-overlap-guard.sh'),'--require-clean-tracked','--require-golden','--require-no-camera-process','--expect-head',HEAD,'--expect-origin',HEAD],check=True)
assert not run(['git','-C',str(R),'status','--porcelain']).strip()
assert Path('/proc/sys/kernel/random/boot_id').read_text().strip()=='680034da-fa16-4599-a374-c0486b7b2f5d'
assert json.loads((D/'INSTALL.json').read_text())['status']=='PASS_INSTALLED_UNARMED'
assert not (D/'ATTEMPT-CONSUMED').exists() and not (D/'ARM.json').exists()
assert sha(Q/'run-once.py')==sha(D/'run-once.py')
assert sha(Q/'return-golden.sh')==sha(D/'return-golden.sh')
extra=[Path('/etc/grub.d/99zzzzzz_sp11_camera_upstream_front_20261014_06')]
for suffix in ['.service','-watchdog.timer','-return.service']:
 p=Path('/etc/systemd/system')/(ID+suffix)
 assert sha(p)==sha(Q/p.name)
 extra.append(p)
for n in [ID+'.service',ID+'-watchdog.timer']:
 assert run(['systemctl','is-enabled',n]).strip()=='enabled'
for p,h in json.loads((D/'GOLDEN-HASHES.json').read_text()).items(): assert sha(Path(p))==h
with (D/'ASSETS.sha256').open('a') as f:
 for p in extra:f.write(sha(p)+'  '+str(p)+'\n')
subprocess.run(['sha256sum','--quiet','-c',str(D/'ASSETS.sha256')],check=True)
(D/'EXPECTED-HEAD').write_text(HEAD+'\n')
assert ID in Path('/boot/grub/grub.cfg').read_text()
subprocess.run(['grub-script-check','/boot/grub/grub.cfg'],check=True)
record={'status':'ARMING','source_head':HEAD,'baseline_boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'entry':ID,'kernel_release':'7.2.0-sp11-upstream-front26','system_sleep':False,'streaming':False,'capture':False,'mmap_allocation_only':False,'sensor_domain_teardown':True,'time_epoch':time.time()}
with (D/'ARM.json').open('x') as f:f.write(json.dumps(record,indent=2)+'\n')
subprocess.run(['grub-reboot',ID],check=True)
env=run(['grub-editenv','/boot/grub/grubenv','list'])
assert 'next_entry='+ID in env and 'saved_entry=sp11-audio-fullio-v19c' in env
record['status']='ARMED_ONE_USE_REBOOT_REQUESTED'
(D/'ARM.json').write_text(json.dumps(record,indent=2)+'\n')
os.sync()
print(json.dumps(record),flush=True)
subprocess.run(['systemctl','reboot','--no-block'],check=True)
