#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
D=Path(__file__).resolve().parent;R=D.parents[2];Q=D.parent/'e004dq-unified-rgb-ir-rear-regression'
def need(v,m):
    if not v:raise AssertionError(m)
for p in D.glob('*.sh'):subprocess.run(['bash','-n',str(p)],check=True)
for p in D.glob('*.py'):
    if p.name!='verify-prep.py':compile(p.read_text(),str(p),'exec')
r=json.loads((D/'RESULT.json').read_text());need(r['attempt_limit']==1 and r['retry_authorized'] is False,'attempt')
need(r['only_runtime_code_delta_from_e004dq'].startswith('verify-live reads root-only CAMSS parameter via sudo -n cat'),'delta declaration')
# Camera runtime script must be unchanged after normalizing experiment identity.
q=(Q/'run-once.sh').read_text().replace('e004dq-unified-rgb-ir-rear-regression','e004dr-unified-rgb-ir-rear-regression-r2').replace('E004DQ','E004DR').replace('e004dq','e004dr')
need(q==(D/'run-once.sh').read_text(),'run-once drift beyond identity')
v=(D/'verify-live.py').read_text();need("subprocess.check_output(['sudo','-n','cat','/sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity']" in v,'sudo verifier read');need("Path('/sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity').read_text" not in v,'old verifier read remains')
run=(D/'run-once.sh').read_text();need(run.count('--stream-mmap=4')==2,'stream count')
for line in [x for x in run.splitlines() if '--stream-mmap=4' in x]:need('"$REARVIDEO"' in line,'nonrear stream')
need('insmod "$HARNESS"' not in run,'receiver harness')
# Failed parent must remain closed and retired.
subprocess.run(['python3',str(Q/'verify-failure-close.py')],check=True,stdout=subprocess.DEVNULL)
# Current machine must be Golden and fresh candidate absent.
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'not Golden');env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
need(not Path('/boot/sp11-7.1.5-camera-e004dr-unified-rgb-ir-rear-r2').exists(),'candidate boot');need(not Path('/etc/grub.d/99zzzzzz_sp11_camera_e004dr_unified_rgb_ir_rear_r2').exists(),'candidate entry')
g=(D/'99zzzzzz_sp11_camera_e004dr_unified_rgb_ir_rear_r2').read_text();need('sp11-camera-e004dr-unified-rgb-ir-rear-r2-one-shot' in g and 'sp11_camera_e004dr_unified_rgb_ir_rear_r2=1' in g,'GRUB candidate')
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0','e004t_csiphy_readback_test'):need(not Path('/sys/module',m).exists(),'module '+m)
# If prearm build exists, pin exact hashes.
expected={'qcom-camss-ir-gated.ko':'862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7','sp11-vd55g0.ko':'4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72','imx681.ko':'ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6','ov13858-production.ko':'13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309'}
if (D/'build').exists():
    for n,h in expected.items():need(hashlib.sha256((D/'build'/n).read_bytes()).hexdigest()==h,'build '+n)
if (D/'PREARM.txt').exists():need('status=PASS_READY_TO_INSTALL' in (D/'PREARM.txt').read_text(),'prearm status')
print('E004dr PREP VERIFY: PASS (fresh candidate / camera runtime identical / verifier-only sudo fix)')
