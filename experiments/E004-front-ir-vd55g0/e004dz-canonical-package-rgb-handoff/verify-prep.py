#!/usr/bin/env python3
from pathlib import Path
import json,subprocess
D=Path(__file__).resolve().parent;R=D.parents[2]
def need(v,m):
    if not v:raise AssertionError(m)
for p in D.glob('*.sh'):subprocess.run(['bash','-n',str(p)],check=True)
for p in D.glob('*.py'):
    if p.name!='verify-prep.py':compile(p.read_text(),str(p),'exec')
r=json.loads((D/'RESULT.json').read_text());need(r['attempt_limit']==1 and r['retry_authorized'] is False,'attempt')
for rel,status in (('e004dv-canonical-unified-camera-hardware-product','PASS_CANONICAL_UNIFIED_THREE_CAMERA_HARDWARE_AUTHORITY_EXACT'),('e004dw-canonical-full-stack-package','PASS_OFFLINE_FULL_STACK_PACKAGE_STAGED_NOT_ACTIVATED'),('e004dy-live-unactivated-package-lifecycle','PASS_LIVE_FILESYSTEM_INSTALL_UPDATE_UNINSTALL_WITH_ZERO_ACTIVATION_SIDE_EFFECTS')):
    j=json.loads((R/'experiments/E004-front-ir-vd55g0'/rel/'RESULT.json').read_text());need(j['status']==status,rel)
run=(D/'run-once.sh').read_text();
for tok in ('/usr/lib/sp11-camera-stack/hardware','/usr/lib/sp11-front-imx681','rear-colorbar.raw','BETWEEN-NEUTRAL','front-imx681-launcher.py','--post-g3-write-policy shadow'):need(tok in run,'run '+tok)
need('e004t_csiphy_readback_test' not in run,'receiver harness')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
for p in ('/usr/lib/sp11-front-imx681','/usr/lib/sp11-camera-stack','/var/lib/sp11-camera-stack'):need(not Path(p).exists(),'package should be absent during prep '+p)
need(not Path('/boot/sp11-7.1.5-camera-e004dz-canonical-package-rgb-handoff').exists(),'candidate boot')
print('E004dz PREP VERIFY: PASS (canonical package rear->front one-shot, currently uninstalled/unarmed)')
