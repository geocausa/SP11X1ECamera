#!/usr/bin/env python3
from pathlib import Path
import json,subprocess
D=Path(__file__).resolve().parent;R=D.parents[2]
def need(v,m):
    if not v: raise AssertionError(m)
for p in D.glob('*.sh'): subprocess.run(['bash','-n',str(p)],check=True)
for p in D.glob('*.py'):
    if p.name!='verify-prep.py': compile(p.read_text(),str(p),'exec')
r=json.loads((D/'RESULT.json').read_text());need(r['attempt_limit']==1 and r['retry_authorized'] is False and r['native_write_authorized'] is False,'policy')
run=(D/'run-once.sh').read_text();need('--post-g3-write-policy shadow' in run,'not shadow');need('--allow-one-native-write' not in run,'native write flag present');need('rear-colorbar' not in run and '--stream-mmap' not in run,'unexpected direct rear stream')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
for p in ('/usr/lib/sp11-front-imx681','/usr/lib/sp11-camera-stack','/var/lib/sp11-camera-stack'): need(not Path(p).exists(),'package present '+p)
print('E004ec PREP VERIFY: PASS (side-light front shadow observation, no native write)')
