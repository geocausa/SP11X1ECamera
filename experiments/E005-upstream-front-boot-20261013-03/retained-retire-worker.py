#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
# Historical retirement worker; do not replay mutations.
from pathlib import Path
import hashlib,json,os,subprocess
R=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-upstream');D=Path('/var/lib/sp11-camera-upstream-front-20261013-03');ID=D.name
os.environ.update(GIT_CONFIG_COUNT='1',GIT_CONFIG_KEY_0='safe.directory',GIT_CONFIG_VALUE_0=str(R))
subprocess.run(['bash',str(R/'tools/camera-overlap-guard.sh'),'--require-clean-tracked','--require-golden','--require-no-camera-process','--expect-head','22ce02b2361ee759928c0e7b6ca21f4feab38462','--expect-origin','22ce02b2361ee759928c0e7b6ca21f4feab38462'],check=True)
assert not (D/'RETIRED.json').exists()
assert (D/'ATTEMPT-CONSUMED').exists()
subprocess.run(['sha256sum','--quiet','-c',str(D/'ASSETS.sha256')],check=True)
for p,h in json.loads((D/'GOLDEN-HASHES.json').read_text()).items():assert hashlib.sha256(Path(p).read_bytes()).hexdigest()==h
for unit in [ID+'.service',ID+'-watchdog.timer',ID+'-return.service']:
 subprocess.run(['systemctl','stop',unit],check=True)
subprocess.run(['systemctl','disable',ID+'.service',ID+'-watchdog.timer'],check=True)
g=Path('/etc/grub.d/99zzzzzz_sp11_camera_upstream_front_20261013_03')
g.rename(D/('RETIRED-'+g.name))
subprocess.run(['update-grub'],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
subprocess.run(['grub-script-check','/boot/grub/grub.cfg'],check=True)
assert ID not in Path('/boot/grub/grub.cfg').read_text()
env=subprocess.check_output(['grub-editenv','/boot/grub/grubenv','list'],text=True)
assert 'saved_entry=sp11-audio-fullio-v19c' in env and not any(x.startswith('next_entry=') and x!='next_entry=' for x in env.splitlines())
record={'status':'RETIRED_CONSUMED_DO_NOT_RETRY','golden_boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'protected_assets_unchanged':True,'pending_entry':False,'units_disabled':True,'watchdog_fired':(D/'RETURN-SERVICE-RESULT').read_text().strip()=='independent-watchdog'}
(D/'RETIRED.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record))
