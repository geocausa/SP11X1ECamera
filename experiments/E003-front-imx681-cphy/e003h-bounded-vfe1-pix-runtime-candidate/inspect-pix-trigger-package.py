#!/usr/bin/env python3
import argparse, hashlib, json, subprocess
from pathlib import Path

EXP = Path(__file__).resolve().parent
EXPECTED = {
    'camss': '7d8c8953f8c14e34d36e3d2352b3ea2581d66a5af777f061f6cd0951fcee1680',
    'sensor': '389c4a8c8ba991e7bd4575e06cfac64090077898ef9d88949631d4f669457388',
    'dtb': '019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
    'capsule': '6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20',
    'helper': 'd13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09',
    'golden_kernel': 'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a',
    'golden_initrd': 'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d',
}
EXPECTED_IOMMUS = ['3d','800','60','3d','820','60','3d','840','60','3d','860','60','3d','18a0','0']

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def die(msg):
    raise SystemExit('FAIL: ' + msg)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('-o','--output',type=Path,required=True)
    a = ap.parse_args()
    root = Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
    camss = Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/qcom-camss.ko')
    sensor = root/'experiments/E003-front-imx681-cphy/e003h-bounded-front-first-frame-runtime/imx681.ko'
    dtb = EXP/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'
    cap = EXP/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin'
    helper = EXP/'e003h-pix-one-shot'
    for key,path in [('camss',camss),('sensor',sensor),('dtb',dtb),('capsule',cap),('helper',helper)]:
        if sha(path) != EXPECTED[key]:
            die(key + ' hash drift')

    c = (EXP/'e003h-pix-one-shot.c').read_text()
    if 'xioctl(vfd, VIDIOC_QBUF' in c or 'xioctl(vfd, VIDIOC_STREAMON' in c:
        die('helper invokes normal streaming')
    for name in ('preflight-pix-one-shot.sh','install-pix-candidate-boot.sh','load-pix-candidate.sh','setup-pix-media.sh','watch-rtcdm-stage.py'):
        if not (EXP/name).is_file():
            die('missing ' + name)

    install = (EXP/'install-pix-candidate-boot.sh').read_text()
    if any('grub-reboot ' in line and not line.lstrip().startswith('#') for line in install.splitlines()):
        die('installer arms next boot')
    load = (EXP/'load-pix-candidate.sh').read_text()
    if 'e003h_pix_rtcdm_diag' not in load:
        die('load script does not require persistent RT-CDM observer')

    ports = subprocess.check_output(['fdtget','-l',str(dtb),'/soc@0/isp@acb7000/ports'],text=True).split()
    if ports != ['port@2']:
        die('DT not front-only')
    reg = subprocess.check_output(['fdtget','-t','x',str(dtb),'/soc@0/isp@acb7000','reg'],text=True)
    if 'ac71000 0 f000' not in reg or 'ac26000 0 1000' not in reg:
        die('DT resource drift')
    iom = subprocess.check_output(['fdtget','-t','x',str(dtb),'/soc@0/isp@acb7000','iommus'],text=True).split()
    if iom != EXPECTED_IOMMUS:
        die('DT IOMMU set drift: ' + repr(iom))

    env = subprocess.check_output(['grub-editenv','list'],text=True,stderr=subprocess.DEVNULL)
    if 'saved_entry=sp11-audio-fullio-v19c\n' not in env or any(x.startswith('next_entry=') and x!='next_entry=' for x in env.splitlines()):
        die('Golden boot env not safe')
    if Path('/sys/module/qcom_camss').exists() or Path('/sys/module/imx681').exists():
        die('candidate camera module loaded')

    boot = Path('/boot/sp11-7.1.5-camera-e003h-pix-one-shot')
    installed = {
        'kernel': sha(boot/'vmlinuz-7.1.5-sp11-render-parity-v4+'),
        'initrd': sha(boot/'initrd.img-7.1.5-sp11-camera-e003h-pix-one-shot'),
        'dtb': sha(boot/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'),
    }
    if installed != {'kernel':EXPECTED['golden_kernel'],'initrd':EXPECTED['golden_initrd'],'dtb':EXPECTED['dtb']}:
        die('installed candidate boot drift')

    out = {
        'accepted': True,
        'schema': 'sp11-e003h-pix-trigger-package-v3-requester-sid-proven',
        'hashes': EXPECTED,
        'installed_boot': installed,
        'front_only_ports': ports,
        'iommu_set': ['0x800/0x60','0x820/0x60','0x840/0x60','0x860/0x60','0x18a0/0'],
        'windows_requester_sid': '0x18a0',
        'windows_requester_context': 'CB16/S1_IFE_HLOS',
        'normal_vb2_qbuf_used': False,
        'normal_vb2_streamon_used': False,
        'candidate_boot_installed': True,
        'candidate_boot_armed': False,
        'golden_saved_default': True,
        'camera_modules_loaded': False,
        'runtime_authorized': False,
        'rtcdm_stage_telemetry': True,
        'rtcdm_persistent_observer': True,
        'rtcdm_multififo_irq_parity': True,
        'rtcdm_irq_context_gate': False,
        'bounded_provenance_expected_green': True,
        'next': 'fresh post-provenance one-shot authorization review',
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: post-provenance PIX package is hash-pinned, front-only, 0x18a0-domain-corrected and unarmed')

if __name__ == '__main__':
    main()
