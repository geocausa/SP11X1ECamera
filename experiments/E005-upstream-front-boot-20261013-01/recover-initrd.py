#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reconcile failed hook stage, verify installed dependencies, build fresh initrd."""
from pathlib import Path
import hashlib, importlib.util, json, os, subprocess, sys
sys.dont_write_bytecode = True
Q = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('package', Q / 'prepare-package.py')
p = importlib.util.module_from_spec(spec)
spec.loader.exec_module(p)

def main():
    p.need(os.geteuid() == 0, 'root required')
    os.environ.update(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='safe.directory', GIT_CONFIG_VALUE_0=str(p.R))
    head = subprocess.check_output(['git', '-C', str(p.R), 'rev-parse', 'HEAD'], text=True).strip()
    subprocess.run(['bash', str(p.R / 'tools/camera-overlap-guard.sh'), '--require-clean-tracked',
                    '--require-golden', '--require-no-camera-process', '--expect-head', head, '--expect-origin', head], check=True)
    p.need(not subprocess.check_output(['git', '-C', str(p.R), 'status', '--porcelain'], text=True).strip(), 'checkpoint not clean')
    old = p.STAGE
    prior = json.loads((old / 'PACKAGE.json').read_text())
    p.need(prior['status'] == 'FAILED_PACKAGE' and 'parameter not set' in prior['error'], 'unexpected failed stage')
    p.need(not prior['armed'] and not prior['booted'], 'runtime already changed')
    p.need(not Path('/var/lib/sp11-camera-upstream-front-20261013-01').exists(), 'runtime identity exists')
    evidence = json.loads((p.R / 'docs/UPSTREAM-FRONT-GRAPH-BUILD-20261013.json').read_text())
    for n, pin in evidence['assets'].items():
        p.need(p.sha(p.O / n) == pin['sha256'], 'build pin drift')
    built = {x.relative_to(p.O): x for x in p.O.rglob('*.ko')}
    installed = {x.relative_to(p.MODULES / 'kernel'): x for x in (p.MODULES / 'kernel').rglob('*.ko')}
    p.need(built.keys() == installed.keys(), 'installed module set drift')
    for n, x in installed.items():
        p.need(p.sha(x) == p.sha(built[n]), 'module pin drift: ' + str(n))
    p.need(p.sha(p.MODULES / ('config-' + p.KREL)) == p.sha(p.O / '.config'), 'config drift')
    firmware = {}
    for name in ['amss.bin', 'm3.bin', 'board-2.bin']:
        compressed = Path('/lib/firmware/ath12k/WCN7850/hw2.0') / (name + '.zst')
        decoded = p.FW / 'ath12k/WCN7850/hw2.0' / name
        data = subprocess.check_output(['zstd', '-q', '-d', '-c', str(compressed)])
        p.need(hashlib.sha256(data).hexdigest() == p.sha(decoded), 'decoded WiFi drift')
        firmware[name] = dict(installed_compressed_sha256=p.sha(compressed),
                              decoded_sha256=p.sha(decoded), decoded_bytes=decoded.stat().st_size)
    for n, pin in p.PINS.items():
        p.need(p.sha(p.GOLDEN / n) == pin, 'Golden drift')
    fresh = old.with_name(old.name + '-initrd02')
    p.need(not fresh.exists(), 'fresh initrd identity exists; reconcile')
    fresh.mkdir(mode=0o700)
    p.STAGE = fresh
    result = dict(status='FAILED_PACKAGE', source_head=head, kernel_release=p.KREL,
                  armed=False, booted=False, hardware_qualified=False,
                  prior_failed_stage=str(old), prior_failed_manifest_sha256=p.sha(old / 'PACKAGE.json'),
                  reconciled_modules=len(installed))
    try:
        alias = Path('/sys/bus/pci/devices/0004:01:00.0/modalias').read_text().strip()
        wifi = p.run('wifi-alias', ['modprobe', '--resolve-alias', '--set-version', p.KREL, alias]).splitlines()
        p.need(wifi == ['ath12k_wifi7'], 'WiFi alias mismatch')
        image, wrapper, original = p.build_initrd(firmware)
        for n, pin in p.PINS.items():
            p.need(p.sha(p.GOLDEN / n) == pin, 'Golden drift after initrd')
        result.update(status='PASS_ISOLATED_FRONT_BOOT_PACKAGE_UNARMED',
                      initrd_sha256=p.sha(image), initrd_bytes=image.stat().st_size,
                      wifi_alias=wifi, wifi_firmware=firmware, module_files=len(installed),
                      module_tree=str(p.MODULES), versioned_wifi_firmware=str(p.FW),
                      global_hooks_preserved=True, original_firmware_preserved=True,
                      original_mkinitramfs_sha256=hashlib.sha256(original.encode()).hexdigest(),
                      wrapper_sha256=p.sha(wrapper), firmware_scope='existing WiFi OS dependency only; no camera firmware',
                      golden_hashes=p.PINS)
    except Exception as e:
        result['error'] = str(e)
        raise
    finally:
        (fresh / 'PACKAGE.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
