#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Registration-only observer; no regulator writes or camera device access."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

D = Path('/var/lib/sp11-camera-standard-front-providers-20261013-03')
TOKEN = 'sp11_camera_standard_front_providers_20261013_03=1'
ENTRY = 'sp11_entry=7.1.5-sp11-camera-standard-front-providers-20261013-03'
DTROOT = Path('/sys/firmware/devicetree/base')
RSC = '/soc@0/rsc@17500000'

def need(value, reason):
    if not value:
        raise RuntimeError(reason)

def run(args):
    return subprocess.check_output(args, text=True, timeout=10)

def no_camera():
    for name in ('qcom_camss', 'imx681', 'ov13858', 'sp11_vd55g0', 'vd55g0', 'v4l2loopback'):
        need(not (Path('/sys/module') / name).exists(), 'camera module present')
    need(not any(Path('/dev').glob('video*')) and not any(Path('/dev').glob('media*')) and not any(Path('/dev').glob('v4l-subdev*')), 'camera node present')

def regulators():
    found = {}
    for p in Path('/sys/class/regulator').glob('regulator.*'):
        if (p / 'name').exists():
            name = (p / 'name').read_text().strip()
            need(name not in found, 'duplicate regulator name')
            found[name] = p
    return found


def parse_mode_trace(events, addresses):
    need(set(addresses) == {'ldob7', 'ldom3'}, 'resource address set')
    need(len(set(addresses.values())) == 2 and all(0 < value <= 0xfffffff4 and value % 4 == 0 for value in addresses.values()), 'resource address collision/alignment')
    lines = [line for line in events.splitlines() if 'rpmh_send_msg:' in line]
    need(lines, 'empty RPMh trace')
    messages = []
    pattern = r'rpmh_send_msg: (\S+): tcs\(m\): (\d+) \[(sleep|wake|active)\] cmd\(n\): (\d+) msgid: (0x[0-9a-fA-F]+|0) addr: (0x[0-9a-fA-F]+|0) data: (0x[0-9a-fA-F]+|0) complete: ([01])'
    for line in lines:
        match = re.search(pattern, line)
        need(match is not None, 'unparsed RPMh event')
        name, tcs, state, cmd, msgid, addr, data, complete = match.groups()
        messages.append({'controller': name, 'tcs': int(tcs), 'state': state, 'cmd': int(cmd), 'msgid': int(msgid, 0), 'addr': int(addr, 0), 'data': int(data, 0), 'cmd_wait': int(complete)})
    votes = {}
    for resource, base in addresses.items():
        selected = [m for m in messages if m['addr'] in (base, base + 4, base + 8)]
        counts = {kind: sum(m['addr'] == base + offset for m in selected) for kind, offset in (('voltage', 0), ('enable', 4), ('mode', 8))}
        need(counts == {'voltage': 0, 'enable': 0, 'mode': 1}, 'unexpected child request count')
        vote = selected[0]
        need(vote['controller'] == 'apps_rsc' and vote['state'] == 'active' and vote['data'] == 7 and vote['msgid'] & 0x100, 'HPM value/state/response request mismatch')
        votes[resource] = {'counts': counts, 'mode_request': vote}
    return messages, votes

def main():
    need(os.geteuid() == 0, 'root required')
    command = Path('/proc/cmdline').read_text().split()
    need(TOKEN in command and ENTRY in command, 'dedicated candidate boot required')
    need(run(['uname', '-r']).strip() == '7.1.5-sp11-render-parity-v4+', 'kernel mismatch')
    with (D / 'ATTEMPT-CONSUMED').open('x') as f:
        f.write(Path('/proc/sys/kernel/random/boot_id').read_text())
    lock = (D / 'provider.lock').open('w')
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    result = {'status': 'FAILED_STANDARD_FRONT_PROVIDER_HPM_ONLY', 'retry': False, 'camera_access': False, 'rail_enable_requests': False, 'mode_qualification': False, 'kernel_release': '7.1.5-sp11-render-parity-v4+'}
    try:
        for unit in ('grub-initrd-fallback.service', 'grub2-common.service'):
            state = {k: run(['systemctl', 'show', unit, '-p', k, '--value']).strip() for k in ('Result', 'ConditionResult', 'ExecMainStatus', 'ExecMainStartTimestampMonotonic', 'ExecMainExitTimestampMonotonic')}
            need(state['Result'] == 'success' and state['ConditionResult'] == 'yes' and state['ExecMainStatus'] == '0' and int(state['ExecMainStartTimestampMonotonic']) > 0 and int(state['ExecMainExitTimestampMonotonic']) >= int(state['ExecMainStartTimestampMonotonic']), 'boot writer did not execute')
            result[unit] = state
        need(int(result['grub-initrd-fallback.service']['ExecMainExitTimestampMonotonic']) <= int(result['grub2-common.service']['ExecMainStartTimestampMonotonic']), 'writer order')
        env = run(['grub-editenv', '/boot/grub/grubenv', 'list']).splitlines()
        need('saved_entry=sp11-audio-fullio-v19c' in env and not any(x.startswith('next_entry=') and x != 'next_entry=' for x in env), 'Golden default protection')
        run(['sha256sum', '-c', str(D / 'ASSETS.sha256')])
        for path, pin in json.loads((D / 'GOLDEN-ASSET-HASHES.json').read_text()).items():
            need(hashlib.sha256(Path(path).read_bytes()).hexdigest() == pin, 'Golden asset drift')
        no_camera()
        found = regulators()
        result['providers'] = {}
        for name, node, voltage, parent in (
            ('vreg_l7b_2p8', RSC + '/regulators-10/ldo7', 2800000, 'vreg_bob2'),
            ('vreg_l3m_1p8', RSC + '/regulators-11/ldo3', 1800000, 'vreg_s4c_1p8'),
        ):
            need(name in found and parent in found, 'expected regulator missing')
            p = found[name]
            need((p / 'of_node').resolve() == DTROOT / node.lstrip('/'), 'regulator node mismatch')
            provider = Path('/sys/bus/platform/devices')
            matches = [x for x in provider.iterdir() if (x / 'of_node').is_symlink() and (x / 'of_node').resolve() == DTROOT / node.rsplit('/', 1)[0].lstrip('/')]
            need(len(matches) == 1 and (matches[0] / 'driver').is_symlink() and (matches[0] / 'driver').resolve().name == 'qcom-rpmh-regulator', 'standard driver binding')
            data = {key: int((p / key).read_text()) for key in ('num_users', 'microvolts', 'min_microvolts', 'max_microvolts')}
            need(data['num_users'] == 0 and all(data[k] == voltage for k in ('microvolts', 'min_microvolts', 'max_microvolts')), 'registration cache or users mismatch')
            # A supply consumer symlink on the actual parent identifies this child.
            links = [x for x in found[parent].iterdir() if x.is_symlink() and x.name == p.name + '-SUPPLY' and x.resolve() == p.resolve()]
            need(len(links) == 1, 'parent supply link missing or ambiguous')
            data['opmode'] = (p / 'opmode').read_text().strip()
            need(data['opmode'] == 'normal', 'HPM logical mode cache mismatch')
            data.update(parent=parent, parent_link=links[0].name, node=node, driver='qcom-rpmh-regulator', voltage_is_driver_cache=True)
            result['providers'][name] = data
        log = run(['dmesg'])
        (D / 'PRIVATE-DMESG.txt').write_text(log)
        trace = Path('/sys/kernel/tracing')
        need((trace / 'events/rpmh/rpmh_send_msg/enable').read_text().strip() == '1' and (trace / 'tracing_on').read_text().strip() == '1', 'early trace inactive')
        (trace / 'tracing_on').write_text('0\n')
        result['trace_frozen_before_snapshot'] = True
        stats = {p.parent.name: p.read_text() for p in (trace / 'per_cpu').glob('cpu*/stats')}
        need(stats, 'trace stats missing')
        for value in stats.values():
            for label in ('overrun', 'commit overrun', 'dropped events'):
                match = re.search(r'^' + label + r':\s*(\d+)', value, re.M)
                need(match and int(match[1]) == 0, 'trace lost events')
        events = (trace / 'trace').read_text()
        (D / 'PRIVATE-RPMH-TRACE.txt').write_text(events)
        (D / 'PRIVATE-TRACE-STATS.json').write_text(json.dumps(stats, indent=2))
        debug = Path('/sys/kernel/debug/dynamic_debug/control').read_text()
        selected = [x for x in debug.splitlines() if 'drivers/regulator/qcom-rpmh-regulator.c:' in x]
        (D / 'PRIVATE-RPMH-DYNAMIC-DEBUG.txt').write_text('\n'.join(selected) + '\n')
        addresses = {}
        for resource in ('ldob7', 'ldom3'):
            matches = re.findall(r'regulator registered for RPMh resource ' + resource + r' @ (0x[0-9a-fA-F]+)', log)
            need(len(matches) == 1, 'resource registration debug address missing or duplicated')
            addresses[resource] = int(matches[0], 16)
        messages, votes = parse_mode_trace(events, addresses)
        entries = sum(int(re.search(r'^entries:\s*(\d+)', value, re.M)[1]) for value in stats.values())
        need(entries == len(messages), 'frozen ring/event count mismatch')
        result.update(rpmh_resource_addresses=addresses, child_rpmh_requests_observed=votes, mode_qualification=True, mode_qualification_scope='logical HPM cache and synchronous response-request path; electrical/current capability not measured', trace_events=len(messages), trace_ring_entries=entries, trace_overruns_or_drops=0, trace_scope='kernel boot through frozen collector snapshot; electrical rail state not measured', network_interfaces=[p.name for p in Path('/sys/class/net').iterdir()], sound_cards=[p.name for p in Path('/proc/asound').glob('card[0-9]*')])
        need(result['sound_cards'] and any(x != 'lo' for x in result['network_interfaces']), 'existing audio/network registration missing')
        no_camera()
        result['status'] = 'PASS_STANDARD_FRONT_PROVIDER_HPM_ONLY'
    except Exception as exc:
        result['error'] = str(exc)
        raise
    finally:
        result['candidate_boot_id'] = Path('/proc/sys/kernel/random/boot_id').read_text().strip()
        (D / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')

if __name__ == '__main__':
    main()
