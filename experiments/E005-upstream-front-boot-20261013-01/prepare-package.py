#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Stage isolated modules, versioned WiFi firmware and initrd; never arm or boot."""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys

R = Path(__file__).resolve().parents[2]
Q = Path(__file__).resolve().parent
B = R.parents[1] / '02-kernel'
C = B / 'upstream-ife-base-build-20261011-01/candidate-26/final-qual02'
S = C.parent / 'source'
O = C / 'build'
STAGE = B / 'upstream-front-boot-20261013-01'
KREL = '7.2.0-sp11-upstream-front26'
FW = Path('/lib/firmware') / KREL
MODULES = Path('/lib/modules') / KREL
GOLDEN = Path('/boot/sp11-7.1.5-audio-fullio-v19c')
PINS = {
    'x1e80100-microsoft-denali-sp11-fullio-v19c.dtb': '2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00',
    'initrd.img-7.1.5-sp11-fullio-v19c': 'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d',
    'vmlinuz-7.1.5-sp11-render-parity-v4+': 'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a',
}

def need(v, why):
    if not v:
        raise RuntimeError(why)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def run(label, args, env=None):
    p = subprocess.run([str(a) for a in args], text=True, capture_output=True, env=env)
    (STAGE / (label + '.log')).write_text(p.stdout + p.stderr)
    need(p.returncode == 0, label + ': ' + p.stderr[-1200:])
    return p.stdout

def main():
    need(os.geteuid() == 0, 'root required')
    os.environ.update(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='safe.directory', GIT_CONFIG_VALUE_0=str(R))
    head = subprocess.check_output(['git', '-C', str(R), 'rev-parse', 'HEAD'], text=True).strip()
    subprocess.run(['bash', str(R / 'tools/camera-overlap-guard.sh'),
                    '--require-clean-tracked', '--require-golden', '--require-no-camera-process',
                    '--expect-head', head, '--expect-origin', head], check=True)
    need(not subprocess.check_output(['git', '-C', str(R), 'status', '--porcelain'], text=True).strip(), 'checkpoint not clean')
    need(not STAGE.exists() and not MODULES.exists() and not FW.exists(), 'package identity already exists; reconcile')
    evidence = json.loads((R / 'docs/UPSTREAM-FRONT-GRAPH-BUILD-20261013.json').read_text())
    need(evidence['status'] == 'PASS_FULL_FRONT_GRAPH_IMAGE_MODULES_SOURCE_ONLY', 'build not qualified')
    for n, pin in evidence['assets'].items():
        need(sha(O / n) == pin['sha256'], 'compiled asset drift: ' + n)
    for n, pin in PINS.items():
        need(sha(GOLDEN / n) == pin, 'Golden drift')
    need(shutil.disk_usage(B).free > 800 * 2**20, 'package budget')
    STAGE.mkdir(mode=0o700)
    result = dict(status='FAILED_PACKAGE', source_head=head, kernel_release=KREL,
                  armed=False, booted=False, hardware_qualified=False)
    try:
        run('modules-install', ['make', '-C', S, 'O=' + str(O), 'ARCH=arm64',
                              'LOCALVERSION=-sp11-upstream-front26', 'INSTALL_MOD_PATH=' + str(STAGE / 'root'),
                              'modules_install'])
        src = STAGE / 'root/lib/modules' / KREL
        need(src.is_dir(), 'module stage')
        shutil.copytree(src, MODULES, symlinks=True)
        shutil.copyfile(O / '.config', MODULES / ('config-' + KREL))
        run('depmod', ['depmod', '-a', KREL])
        firmware = {}
        dest = FW / 'ath12k/WCN7850/hw2.0'
        dest.mkdir(parents=True)
        for name in ['amss.bin', 'm3.bin', 'board-2.bin']:
            old = Path('/lib/firmware/ath12k/WCN7850/hw2.0') / (name + '.zst')
            p = dest / name
            with p.open('xb') as f:
                subprocess.run(['zstd', '-q', '-d', '-c', str(old)], stdout=f, check=True)
            firmware[name] = dict(installed_compressed_sha256=sha(old), decoded_sha256=sha(p),
                                  decoded_bytes=p.stat().st_size)
        alias = Path('/sys/bus/pci/devices/0004:01:00.0/modalias').read_text().strip()
        wifi = run('wifi-alias', ['modprobe', '--resolve-alias', '--set-version', KREL, alias]).splitlines()
        need(wifi == ['ath12k_wifi7'], 'WiFi alias mismatch')
        run('wifi-dependencies', ['modprobe', '--show-depends', '--set-version', KREL, 'ath12k_wifi7'])
        run('nvme-dependencies', ['modprobe', '--show-depends', '--set-version', KREL, 'nvme'])
        conf = STAGE / 'conf'
        for n in ['hooks', 'scripts', 'conf.d']:
            (conf / n).mkdir(parents=True)
        (conf / 'initramfs.conf').write_text('MODULES=most\nBUSYBOX=auto\nCOMPRESS=zstd\nRUNSIZE=10%\n')
        (conf / 'modules').write_text('nvme\nath12k_wifi7\npci_pwrctrl_pwrseq\npwrseq_qcom_wcn\n')
        hooks = STAGE / 'distribution-hooks'
        shutil.copytree('/usr/share/initramfs-tools/hooks', hooks)
        # This distro sweep copies all Qualcomm firmware. Only our copied
        # hook set is narrowed; system hooks and original firmware stay intact.
        (hooks / 'ubuntu-x1e-settings').unlink()
        firmware_hook = conf / 'hooks/front-boot-wifi'
        firmware_hook.write_text('#!/bin/sh\nset -eu\ncase "$1" in prereqs) exit 0;; esac\n'
                                  '. /usr/share/initramfs-tools/hook-functions\n'
                                  'mkdir -p "$DESTDIR/lib/firmware/' + KREL + '/ath12k/WCN7850/hw2.0"\n'
                                  'cp /lib/firmware/' + KREL + '/ath12k/WCN7850/hw2.0/*.bin "$DESTDIR/lib/firmware/' + KREL + '/ath12k/WCN7850/hw2.0/"\n')
        firmware_hook.chmod(0o700)
        wrapper = STAGE / 'mkinitramfs-isolated'
        original = Path('/usr/sbin/mkinitramfs').read_text()
        needle = 'run_scripts_optional /usr/share/initramfs-tools/hooks'
        need(original.count(needle) == 1, 'initrd hook API drift')
        wrapper.write_text(original.replace(needle, 'run_scripts_optional "' + str(hooks) + '"', 1))
        wrapper.chmod(0o700)
        image = STAGE / ('initrd.img-' + KREL)
        env = os.environ.copy()
        env['TMPDIR'] = str(STAGE)
        run('mkinitramfs', [wrapper, '-d', conf, '-o', image, KREL], env)
        listing = run('initrd-list', ['lsinitramfs', image]).splitlines()
        need(any(x.endswith('/nvme.ko') for x in listing), 'initrd NVMe missing')
        need(any(x.endswith('/ath12k_wifi7.ko') for x in listing), 'initrd WiFi missing')
        for name in firmware:
            need(any(x.endswith('/' + KREL + '/ath12k/WCN7850/hw2.0/' + name) for x in listing), 'decoded WiFi missing')
        need(not any('qcom/sp11/' in x or 'imx681-' in x or 'rear-generation-' in x for x in listing), 'private camera input in initrd')
        need(not any('7.1.5-' in x and '.ko' in x for x in listing), 'mixed module release')
        for n, pin in PINS.items():
            need(sha(GOLDEN / n) == pin, 'Golden drift after packaging')
        result.update(status='PASS_ISOLATED_FRONT_BOOT_PACKAGE_UNARMED',
                      initrd_sha256=sha(image), initrd_bytes=image.stat().st_size,
                      wifi_alias=wifi, wifi_firmware=firmware,
                      module_files=len(list(MODULES.rglob('*.ko'))),
                      module_tree=str(MODULES), versioned_wifi_firmware=str(FW),
                      global_hooks_preserved=True, original_firmware_preserved=True,
                      original_mkinitramfs_sha256=hashlib.sha256(original.encode()).hexdigest(),
                      wrapper_sha256=sha(wrapper), firmware_scope='existing WiFi OS dependency only; no camera firmware',
                      golden_hashes=PINS)
    except Exception as e:
        result['error'] = str(e)
        raise
    finally:
        (STAGE / 'PACKAGE.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
