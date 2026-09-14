#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess
D=Path(__file__).resolve().parent; R=D.parents[2]
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
# Syntax / contract checks. GRUB menuentry is data, not Bash.
for p in sorted(D.glob('*.sh')):
    subprocess.run(['bash','-n',str(p)],check=True)
for p in sorted(D.glob('*.py')):
    if p.name=='verify-prep.py': continue
    compile(p.read_text(),str(p),'exec')
g=(D/'99zzzzzz_sp11_camera_e004dp_unified_rgb_ir_receiver').read_text()
for t in ("sp11-camera-e004dp-unified-rgb-ir-receiver-one-shot",'sp11_camera_e004dp_unified_rgb_ir_receiver=1','x1e80100-microsoft-denali-sp11-e004do-unified-rgb-ir.dtb','modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0'):
    need(t in g,'GRUB '+t)
r=json.loads((D/'RESULT.json').read_text())
need(r['status']=='PASS_PREP_READY_UNINSTALLED_UNARMED','status')
need(r['attempt_limit']==1 and r['retry_authorized'] is False,'one attempt')
need(r['accepted_rgb_camss_baseline_byte_reproduced'] is True,'baseline provenance')
need(r['kernel_wrapper_restored_after_artifact_build'] is True,'wrapper restore')
need(r['dtb_sha256']=='3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb','dtb')
expected={
 'qcom-camss-ir-gated.ko':'862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7',
 'sp11-vd55g0.ko':'4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72',
 'e004t_csiphy_readback_test.ko':'6475d453d9e9661ce2979afdd7ad57da8badeba65b2e17ac0f47a54ca890193e',
 'imx681.ko':'ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6',
 'ov13858-production.ko':'13a8ad956075c518687149f8473764d85979f38a7666244b132ad992a9bc1309'}
for n,h in expected.items(): need((D/'build'/n).is_file() and sha(D/'build'/n)==h,'build '+n)
pre=(D/'PREARM.txt').read_text()
need('PREARM-LIVE.txt' in (D/'prearm-check.sh').read_text(),'live prearm target')
need('> "$D/PREARM.txt"' not in (D/'prearm-check.sh').read_text(),'tracked prearm rewrite')
for t in ('status=PASS_READY_TO_INSTALL','dtb_sha256=3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb','action=three_sensor_bind_plus_csiphy0_receiver_readback_only','sensor_stream=NO','capture=NO','illumination=NO','secureisp=NO','retry=NO'):
    need(t in pre,'PREARM '+t)
# Candidate script cannot contain a userspace stream or link-mutation command.
run=(D/'run-once.sh').read_text()
for bad in ('--stream-mmap','--stream-user','--stream-dmabuf','--stream-count','media-ctl -l','media-ctl --links'):
    need(bad not in run,'forbidden command '+bad)
for dep in ('videobuf2_memops','v4l2_cci'): need(dep in run,'accepted dependency '+dep)
for t in ('insmod "$CAMSS" e004j_ir_dphy_windows_parity=1','insmod "$REARMOD"','insmod "$FRONTMOD"','insmod "$IRMOD"','--expect neutral','insmod "$HARNESS"','same_boot_retry_performed'):
    need(t in run,'runtime contract '+t)
# Build-authority must require exact accepted baseline before allowing patched CAMSS.
ba=(D/'build-authority.sh').read_text()
for t in ('7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95','862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7','baseline_not_accepted','wrapper_restore','source_link_restore'):
    need(t in ba,'build authority '+t)
# Current state must remain protected Golden and uninstalled/unarmed.
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'not Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB current state')
need(not Path('/boot/sp11-7.1.5-camera-e004dp-unified-rgb-ir-receiver').exists(),'candidate boot exists')
need(not Path('/etc/grub.d/99zzzzzz_sp11_camera_e004dp_unified_rgb_ir_receiver').exists(),'candidate entry exists')
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0','e004t_csiphy_readback_test'):
    need(not Path('/sys/module',m).exists(),'camera module active '+m)
# Historical wrapper must have been restored.
K=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
new='/home/geoca/Documents/SP11-PROJECT/02-kernel/.golden-v33-delta-replay/src'
need(new+'/Makefile' in (K/'Makefile').read_text(),'kernel wrapper')
need((K/'source').resolve()==Path(new),'kernel source symlink')
print('E004dp PREP VERIFY: PASS (exact lineage + three-sensor bind/receiver-only + one-shot/no-retry)')
