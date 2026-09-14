#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess
D=Path(__file__).resolve().parent; R=D.parents[2]
def need(v,m):
    if not v:raise AssertionError(m)
for p in D.glob('*.sh'):subprocess.run(['bash','-n',str(p)],check=True)
for p in D.glob('*.py'):
    if p.name!='verify-prep.py':compile(p.read_text(),str(p),'exec')
r=json.loads((D/'RESULT.json').read_text());need(r['attempt_limit']==1 and r['retry_authorized'] is False,'attempt')
need(r['status']=='PASS_PREP_READY_UNINSTALLED_UNARMED','status')
pre=(D/'PREARM.txt').read_text();need('status=PASS_READY_TO_INSTALL' in pre and 'rear_colorbar_sha256=6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346' in pre,'prearm evidence')
expected={'qcom-camss-ir-gated.ko':'862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7','sp11-vd55g0.ko':'4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72','imx681.ko':'ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6','ov13858-production.ko':'13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309'}
import hashlib
for n,h in expected.items(): need((D/'build'/n).is_file() and hashlib.sha256((D/'build'/n).read_bytes()).hexdigest()==h,'build '+n)
g=(D/'99zzzzzz_sp11_camera_e004dq_unified_rgb_ir_rear').read_text();need('sp11-camera-e004dq-unified-rgb-ir-rear-one-shot' in g and 'sp11_camera_e004dq_unified_rgb_ir_rear=1' in g,'GRUB contract')
need(r['dtb_sha256']=='3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb','dtb')
run=(D/'run-once.sh').read_text()
need(run.count('--stream-mmap=4')==2,'stream command count')
for line in [x for x in run.splitlines() if '--stream-mmap=4' in x]:need('"$REARVIDEO"' in line,'non-rear stream '+line)
need('insmod "$HARNESS"' not in run and 'e004t_csiphy_readback_test' not in run,'receiver harness use')
for t in ('rear_on; route_snapshot ROUTE-REAR-ON rear-only','6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346','--stream-count=8','rear_off; route_snapshot FINAL-NEUTRAL neutral'):
    need(t in run,'rear contract '+t)
v=(D/'verify-live.py').read_text();need("'E004J_CSIPHY0_DPHY_WINDOWS_PARITY'" in v,'IR gate nonselection check');need("'MODE_SELECT=1 front transmission started'" in v,'front nonstream check');need("'SP11_VD55G0_NATIVE_STREAM_BLOCK'" in v,'IR nonstream check')
# Golden and uninstalled.
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'not Golden');env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
need(not Path('/boot/sp11-7.1.5-camera-e004dq-unified-rgb-ir-rear').exists(),'boot exists');need(not Path('/etc/grub.d/99zzzzzz_sp11_camera_e004dq_unified_rgb_ir_rear').exists(),'entry exists')
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0','e004t_csiphy_readback_test'):need(not Path('/sys/module',m).exists(),'module '+m)
print('E004dq PREP VERIFY: PASS (rear-only stream under three-camera authority / front+IR nonstream / one-shot)')
