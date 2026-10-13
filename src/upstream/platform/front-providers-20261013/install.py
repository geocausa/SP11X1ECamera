#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Install a fresh, unarmed, registration-only candidate. Root required."""
import hashlib
import json
import os
from pathlib import Path
import runpy
import shlex
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(__file__).resolve().parent
BUILD = ROOT.parents[1] / '02-kernel/standard-front-providers-20261013-01'
SLUG = 'standard-front-providers-20261013-01'
ID = 'sp11-camera-' + SLUG
TOKEN = 'sp11_camera_standard_front_providers_20261013_01=1'
D = Path('/var/lib') / ID
B = Path('/boot/sp11-7.1.5-camera-' + SLUG)
G = Path('/etc/grub.d/99zzzzzz_sp11_camera_standard_front_providers_20261013_01')
S = Path('/etc/systemd/system') / (ID + '.service')
GOLDEN = Path('/boot/sp11-7.1.5-audio-fullio-v19c')

def need(value, reason):
    if not value:
        raise RuntimeError(reason)

def run(args, timeout=120):
    return subprocess.check_output([str(x) for x in args], text=True, timeout=timeout)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def write(path, content, mode):
    with path.open('x') as f:
        f.write(content)
    path.chmod(mode)

def main():
    need(os.geteuid() == 0, 'root required')
    os.environ.update(GIT_CONFIG_COUNT='1', GIT_CONFIG_KEY_0='safe.directory', GIT_CONFIG_VALUE_0=str(ROOT))
    head = run(['git', '-C', ROOT, 'rev-parse', 'HEAD']).strip()
    run(['bash', ROOT / 'tools/camera-overlap-guard.sh', '--require-clean-tracked', '--require-golden', '--require-no-camera-process', '--expect-head', head, '--expect-origin', head])
    need(not run(['git', '-C', ROOT, 'status', '--porcelain']).strip(), 'source checkpoint must be clean')
    need(all(not p.exists() for p in (D, B, G, S)), 'candidate identity exists')
    need(ID not in run(['cat', '/boot/grub/grub.cfg']), 'GRUB identity exists')
    prep = runpy.run_path(str(SOURCE / 'prepare.py'))
    pins = prep['HASHES']
    for name, pin in pins.items():
        need(sha(GOLDEN / name) == pin, 'Golden hash drift')
    dtb = BUILD / 'front-providers.dtb'
    evidence = json.loads((BUILD / 'RESULT.json').read_text())
    need(evidence['status'] == 'PASS_ISOLATED_FRONT_PROVIDER_DTB_PREPARED_NOT_INSTALLED' and evidence['candidate_sha256'] == sha(dtb), 'candidate evidence')
    prep['validate'](GOLDEN / 'x1e80100-microsoft-denali-sp11-fullio-v19c.dtb', dtb)
    need(sha(dtb) == 'ae9e93ef6f62990b712f884bebdbf9d5f35638cfcee1c363f637c60c9f58553c', 'qualified candidate hash')
    D.mkdir(mode=0o700)
    B.mkdir(mode=0o755)
    assets = []
    for source, dest, mode in (
        (SOURCE / 'run-once.py', D / 'run-once.py', 0o700),
        (dtb, B / 'front-providers.dtb', 0o644),
        (GOLDEN / 'vmlinuz-7.1.5-sp11-render-parity-v4+', B / 'vmlinuz-7.1.5-sp11-render-parity-v4+', 0o644),
        (GOLDEN / 'initrd.img-7.1.5-sp11-fullio-v19c', B / 'initrd.img-7.1.5-sp11-fullio-v19c', 0o644),
    ):
        shutil.copyfile(source, dest)
        dest.chmod(mode)
        need(sha(source) == sha(dest), 'copy mismatch')
        assets.append(sha(dest) + '  ' + str(dest))
    command = shlex.split(Path('/proc/cmdline').read_text())
    need(any(x.startswith('BOOT_IMAGE=/boot/sp11-7.1.5-audio-fullio-v19c/') for x in command), 'Golden command line')
    need(not any(x.startswith(('trace_', 'dyndbg=', 'sp11_camera_standard_front_')) for x in command), 'existing diagnostic args')
    blacklist = []
    for arg in command:
        if arg.startswith('modprobe.blacklist='):
            blacklist += arg.split('=', 1)[1].split(',')
    command = [x for x in command if not x.startswith(('BOOT_IMAGE=', 'sp11_entry=', 'modprobe.blacklist='))]
    command += ['sp11_entry=7.1.5-sp11-camera-' + SLUG, TOKEN,
                'modprobe.blacklist=' + ','.join(dict.fromkeys(blacklist + ['qcom_camss', 'imx681', 'ov13858', 'sp11_vd55g0', 'vd55g0', 'v4l2loopback'])),
                'trace_event=rpmh:rpmh_send_msg', 'trace_buf_size=2M',
                'dyndbg="file drivers/regulator/qcom-rpmh-regulator.c +p"']
    uuid = run(['findmnt', '-n', '-o', 'UUID', '/']).strip()
    need(uuid == '33e842b7-0434-4749-b03a-299bdcdb8b9f', 'root UUID')
    grub = f'''#!/bin/sh
exec tail -n +3 $0
menuentry 'SP11 standard front providers — registration only, one use' --id '{ID}' {{
 load_video
 set gfxpayload=keep
 insmod gzio
 insmod part_gpt
 insmod ext2
 insmod fdt
 search --no-floppy --fs-uuid --set=root {uuid}
 devicetree {B}/front-providers.dtb
 linux {B}/vmlinuz-7.1.5-sp11-render-parity-v4+ {' '.join(shlex.quote(x) for x in command)}
 initrd {B}/initrd.img-7.1.5-sp11-fullio-v19c
}}
'''
    syntax = BUILD / 'grub-syntax.txt'
    syntax.write_text('\n'.join(grub.splitlines()[2:]) + '\n')
    run(['grub-script-check', syntax])
    write(G, grub, 0o755)
    recovery = f'''#!/usr/bin/env bash
set -Eeuo pipefail
if grep -qw '{TOKEN}' /proc/cmdline; then
  printf 'service_result=%s\\nexit_code=%s\\nexit_status=%s\\n' "${{SERVICE_RESULT:-unknown}}" "${{EXIT_CODE:-unknown}}" "${{EXIT_STATUS:-unknown}}" > {D}/SERVICE-RESULT.txt
  dmesg > {D}/PRIVATE-DMESG.txt
  grub-reboot sp11-audio-fullio-v19c
  sync
  systemctl reboot --no-block
fi
'''
    write(D / 'return-golden.sh', recovery, 0o700)
    unit = f'''[Unit]
Description=SP11 standard front provider registration, one use
Wants=grub-initrd-fallback.service grub2-common.service
After=grub-initrd-fallback.service grub2-common.service
Before=display-manager.service
ConditionKernelCommandLine={TOKEN}

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {D}/run-once.py
ExecStopPost={D}/return-golden.sh
TimeoutStartSec=90
TimeoutStopSec=10
KillMode=control-group

[Install]
WantedBy=multi-user.target
'''
    write(S, unit, 0o644)
    for p in (G, S, D / 'return-golden.sh'):
        assets.append(sha(p) + '  ' + str(p))
    write(D / 'ASSETS.sha256', '\n'.join(assets) + '\n', 0o600)
    write(D / 'EXPECTED-HEAD', head + '\n', 0o600)
    write(D / 'GOLDEN-ASSET-HASHES.json', json.dumps({str(GOLDEN / k): v for k, v in pins.items()}, indent=2) + '\n', 0o600)
    run(['systemd-analyze', 'verify', S])
    run(['systemctl', 'daemon-reload'])
    run(['systemctl', 'enable', S.name])
    run(['update-grub'])
    need(ID in run(['cat', '/boot/grub/grub.cfg']), 'missing generated menu')
    run(['bash', ROOT / 'tools/camera-overlap-guard.sh', '--require-clean-tracked', '--require-golden', '--require-no-camera-process', '--expect-head', head, '--expect-origin', head])
    result = {'status': 'PASS_PROVIDER_CANDIDATE_INSTALLED_UNARMED', 'source_head': head, 'candidate_sha256': sha(dtb), 'identity': ID, 'golden_hashes': pins, 'command_line': command, 'mode_or_capture_test': False}
    (D / 'INSTALL.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
