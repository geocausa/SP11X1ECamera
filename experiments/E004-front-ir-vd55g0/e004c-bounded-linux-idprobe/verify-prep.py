#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, subprocess

D=Path(__file__).resolve().parent
R=D.parents[2]
B=R/'experiments/E004-front-ir-vd55g0/e004b-linux-probe-authority'
BOOT=Path('/boot/sp11-7.1.5-camera-e004c-ir-idprobe')
ENTRY=Path('/etc/grub.d/99zzzzzz_sp11_camera_e004c_ir_idprobe')


def need(v,m):
    if not v: raise AssertionError(m)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

scripts=['prearm-check.sh','install-candidate.sh','verify-installed.sh','arm-once.sh',
         'runtime-preflight.sh','run-once.sh','golden-return-check.sh','retire-candidate.sh']
for name in scripts:
    subprocess.run(['bash','-n',str(D/name)],check=True)

o=json.load(open(D/'RESULT.json'))
need(o['status']=='READY_UNINSTALLED_UNARMED','prep status')
need(o['attempt_limit']==1 and o['retry_authorized'] is False,'one attempt')
need(o['dtb_sha256']=='2b9ff2265606aa95006e3c952597c496367106e00aa1e2d1ec1e75b8f9e485e6','DT hash')
need(o['module_sha256']=='d749fb549ff7c03e0ebcd1690b78b795d985d6d37083ab938a2a2663c397daed','module hash')
need(sha(B/'x1e80100-microsoft-denali-sp11-e004b-ir-probe.dtb')==o['dtb_sha256'],'DT identity')

g=(D/'99zzzzzz_sp11_camera_e004c_ir_idprobe').read_text()
for token in ('sp11-camera-e004c-ir-idprobe-one-shot',
              'sp11_camera_e004c_ir_idprobe=1',
              'modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0_idprobe',
              '/boot/sp11-7.1.5-camera-e004c-ir-idprobe/'):
    need(token in g,'grub token '+token)
need('saved_entry' not in g,'grub entry must not alter persistent default')

run=(D/'run-once.sh').read_text()
need(run.count('insmod "$KO"')==1,'exact one probe insmod')
need(run.index('ATTEMPT1-CONSUMED.marker') < run.index('insmod "$KO"'),'consume before probe')
need("'be=0x3047 windows_qti_expected_be=0x3047'" in run,'Windows ID acceptance')
for forbidden in ('v4l2-ctl','media-ctl','gst-launch','ffmpeg','request_firmware','st,vd55g0'):
    need(forbidden not in run,'runtime forbidden token '+forbidden)
for token in ('patch=0 boot=0 configure=0 stream=0 illumination=0',
              'retry_authorized', 'reboot to Golden immediately'):
    need(token in run,'runtime safety token '+token)

install=(D/'install-candidate.sh').read_text()
need('cp /boot/sp11-7.1.5-audio-fullio-v19c/' in install,'copy Golden artifacts')
need('sp11-7.1.5-camera-e004c-ir-idprobe' in install,'separate candidate boot dir')
need('rm -rf /boot/sp11-7.1.5-audio-fullio-v19c' not in install,'must not remove Golden')

retire=(D/'retire-candidate.sh').read_text()
need('golden-return-check.sh' in retire,'Golden check before retire')
need('rm -rf "$BOOT"' in retire and 'rm -f "$ENTRY"' in retire,'candidate-only retire')

need(not BOOT.exists(),'candidate boot absent before install')
need(not ENTRY.exists(),'candidate entry absent before install')
need('sp11_camera_e004c_ir_idprobe=1' not in Path('/proc/cmdline').read_text(),'currently not candidate')
need(subprocess.check_output(['uname','-r'],text=True).strip()=='7.1.5-sp11-render-parity-v4+','Golden kernel')

print('E004C_PREP_VERIFY=PASS INSTALLED=NO ARMED=NO ATTEMPT=NO')
print('E004C_CONTRACT=ONE_SHOT MANUAL_INSMOD=1 RETRY=NO PATCH=NO STREAM=NO ILLUMINATION=NO')
