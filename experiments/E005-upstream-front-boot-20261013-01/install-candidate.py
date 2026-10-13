#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Install a distinct, unarmed boot entry and conditional recovery units."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess
import importlib.util, sys
sys.dont_write_bytecode = True

Q = Path(__file__).resolve().parent
R = Q.parents[1]
spec = importlib.util.spec_from_file_location('package', Q / 'prepare-package.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)
KREL = package.KREL
STAGE, O = package.STAGE, package.O
ID = 'sp11-camera-upstream-front-20261013-01'
TOKEN = 'sp11_camera_upstream_front_20261013_01=1'
D = Path('/var/lib') / ID
BOOT = Path('/boot/sp11-upstream-front-20261013-01')
GRUB = Path('/etc/grub.d/99zzzzzz_sp11_camera_upstream_front_20261013_01')
UNITS = Path('/etc/systemd/system')
DTB = 'x1e80100-microsoft-denali-oled-front-camera.dtb'

def need(v, why):
    if not v:
        raise RuntimeError(why)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def run(args, timeout=60):
    p = subprocess.run([str(x) for x in args], text=True, capture_output=True, timeout=timeout)
    need(p.returncode == 0, str(args[0]) + ': ' + p.stderr[-1200:])
    return p.stdout

def main():
    need(os.geteuid() == 0, 'root required')
    os.environ.update(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='safe.directory', GIT_CONFIG_VALUE_0=str(R))
    head = run(['git', '-C', R, 'rev-parse', 'HEAD']).strip()
    subprocess.run(['bash', str(R / 'tools/camera-overlap-guard.sh'),
                    '--require-clean-tracked', '--require-golden', '--require-no-camera-process',
                    '--expect-head', head, '--expect-origin', head], check=True)
    need(not run(['git', '-C', R, 'status', '--porcelain']).strip(), 'checkpoint not clean')
    pkg = json.loads((STAGE / 'PACKAGE.json').read_text())
    need(pkg['status'] == 'PASS_ISOLATED_FRONT_BOOT_PACKAGE_UNARMED', 'package not qualified')
    need(pkg['source_head'] == head, 'package/source mismatch')
    files = [D, BOOT, GRUB] + [UNITS / (ID + suffix) for suffix in ['.service', '-watchdog.timer', '-return.service']]
    need(not any(p.exists() for p in files), 'candidate identity exists; reconcile')
    for n, pin in package.PINS.items():
        need(sha(package.GOLDEN / n) == pin, 'Golden drift')
    evidence = json.loads((R / 'docs/UPSTREAM-FRONT-GRAPH-BUILD-20261013.json').read_text())
    for n, pin in evidence['assets'].items():
        need(sha(O / n) == pin['sha256'], 'build asset drift')
    need(sha(STAGE / ('initrd.img-' + KREL)) == pkg['initrd_sha256'], 'initrd drift')
    D.mkdir(mode=0o700)
    BOOT.mkdir(mode=0o755)
    result = dict(status='FAILED_UNARMED_INSTALL', source_head=head, kernel_release=KREL, armed=False)
    try:
        shutil.copyfile(O / 'arch/arm64/boot/Image', BOOT / ('vmlinuz-' + KREL))
        shutil.copyfile(O / 'arch/arm64/boot/dts/qcom' / DTB, BOOT / DTB)
        shutil.copyfile(STAGE / ('initrd.img-' + KREL), BOOT / ('initrd.img-' + KREL))
        shutil.copyfile(Q / 'run-once.py', D / 'run-once.py')
        shutil.copyfile(Q / 'return-golden.sh', D / 'return-golden.sh')
        for n in ['run-once.py', 'return-golden.sh']:
            (D / n).chmod(0o700)
        (D / 'empty-modprobe.conf').write_text('# Explicit candidate module requests only.\n')
        (D / 'EXPECTED-HEAD').write_text(head + '\n')
        (D / 'GOLDEN-HASHES.json').write_text(json.dumps({str(package.GOLDEN / n): h for n,h in package.PINS.items()}, indent=2) + '\n')
        pins = list(BOOT.iterdir()) + [D / 'run-once.py', D / 'return-golden.sh', D / 'empty-modprobe.conf']
        pins += [p for p in package.MODULES.rglob('*') if p.is_file() and not p.is_symlink()]
        pins += [p for p in package.FW.rglob('*') if p.is_file()]
        (D / 'ASSETS.sha256').write_text(''.join(sha(p) + '  ' + str(p) + '\n' for p in sorted(pins)))
        grub = """#!/bin/sh
exec tail -n +3 $0
menuentry 'SP11 upstream front26 one-use headless probe' --id=sp11-camera-upstream-front-20261013-01 {
    insmod part_gpt
    insmod ext2
    search --no-floppy --fs-uuid --set=root 33e842b7-0434-4749-b03a-299bdcdb8b9f
    linux /boot/sp11-upstream-front-20261013-01/vmlinuz-7.2.0-sp11-upstream-front26 root=UUID=33e842b7-0434-4749-b03a-299bdcdb8b9f ro clk_ignore_unused pd_ignore_unused cma=128M efi=noruntime console=tty0 panic=30 systemd.unit=multi-user.target sp11_camera_upstream_front_20261013_01=1 sp11_entry=sp11-camera-upstream-front-20261013-01 modprobe.blacklist=qcom_camss,imx681,phy_qcom_mipi_csi2,i2c_qcom_cci,ov13858,vd55g0,sp11_vd55g0,v4l2loopback
    devicetree /boot/sp11-upstream-front-20261013-01/x1e80100-microsoft-denali-oled-front-camera.dtb
    initrd /boot/sp11-upstream-front-20261013-01/initrd.img-7.2.0-sp11-upstream-front26
}
"""
        # Check the generated GRUB fragment before adding it to /etc.
        (D / 'grub-fragment.cfg').write_text(grub.split('exec tail -n +3 $0\n', 1)[1])
        run(['grub-script-check', D / 'grub-fragment.cfg'])
        GRUB.write_text(grub)
        GRUB.chmod(0o755)
        for suffix in ['.service', '-watchdog.timer', '-return.service']:
            shutil.copyfile(Q / (ID + suffix), UNITS / (ID + suffix))
        unit_paths = [UNITS / (ID + s) for s in ['.service', '-watchdog.timer', '-return.service']]
        run(['systemd-analyze', 'verify'] + unit_paths)
        run(['systemctl', 'daemon-reload'])
        run(['systemctl', 'enable', ID + '.service', ID + '-watchdog.timer'])
        update = run(['update-grub'], 90)
        (D / 'UPDATE-GRUB.log').write_text(update)
        need(('menuentry ' in Path('/boot/grub/grub.cfg').read_text()) and ID in Path('/boot/grub/grub.cfg').read_text(), 'entry missing')
        run(['grub-script-check', '/boot/grub/grub.cfg'])
        grubenv = run(['grub-editenv', '/boot/grub/grubenv', 'list'])
        need('saved_entry=sp11-audio-fullio-v19c' in grubenv, 'default changed')
        need(not any(x.startswith('next_entry=') and x != 'next_entry=' for x in grubenv.splitlines()), 'pending boot')
        run(['sha256sum', '-c', D / 'ASSETS.sha256'])
        for n, pin in package.PINS.items():
            need(sha(package.GOLDEN / n) == pin, 'Golden drift after install')
        result.update(status='PASS_INSTALLED_UNARMED', assets={p.name: {'sha256':sha(p),'bytes':p.stat().st_size} for p in BOOT.iterdir()},
                      module_release=KREL, conditional_units_verified=True, automatic_return_seconds=180,
                      asset_pins=len(pins), golden_unchanged=True)
    except Exception as e:
        result['error'] = str(e)
        raise
    finally:
        (D / 'INSTALL.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
