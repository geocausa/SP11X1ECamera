#!/usr/bin/env python3
from pathlib import Path
import json,subprocess
D=Path(__file__).resolve().parent;E=D/'evidence'
def need(v,m):
    if not v: raise AssertionError(m)
r=json.loads((D/'RESULT.json').read_text());o=json.loads((E/'ATTEMPT1-OBSERVATION.json').read_text())
need(r['status']=='PASS_SIDE_LIGHTS_NO_APPLY_ONE_NATIVE_GOLDEN_RETURN_RETIRED_UNINSTALLED','status')
need(o['status']=='PASS_SIDE_LIGHTS_NO_APPLY_ONE_NATIVE','observation')
need(o['apply_one_native_sources']==[] and o['policy_disabled_shadow_count']==0 and o['cap_active_shadow_count']==21 and o['later_native_writes']==0,'decision counts')
need(o['front_sequences']==list(range(27)),'frames')
need('status=PASS_GOLDEN_RETURN' in (E/'GOLDEN-RETURN.txt').read_text(),'golden');need('status=PASS_CANDIDATE_RETIRED' in (E/'RETIRE.txt').read_text(),'retire');need('SP11_CAMERA_STACK_LIVE_UNINSTALL=PASS ACTIVATED=NO' in (E/'PACKAGE-UNINSTALL.txt').read_text(),'uninstall')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'current golden');env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'grub')
for p in ('/usr/lib/sp11-front-imx681','/usr/lib/sp11-camera-stack','/var/lib/sp11-camera-stack'): need(not Path(p).exists(),'package path '+p)
print('E004ec CLOSE VERIFY: PASS (side lights insufficient; clean Golden return)')
