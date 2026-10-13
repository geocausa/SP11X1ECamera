#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Test the real collector parser with synthetic traces; no hardware access."""
from pathlib import Path
import runpy
import json
m = runpy.run_path(str(Path(__file__).with_name('run-once.py')))
parse = m['parse_mode_trace']
addresses = {'ldob7': 0x41800, 'ldom3': 0x40b00}
def event(addr, data=7, state='active', msgid=0x10108):
    return f"synthetic [000] 0.8: rpmh_send_msg: apps_rsc: tcs(m): 0 [{state}] cmd(n): 0 msgid: {msgid:#x} addr: {addr:#x} data: {data:#x} complete: 0"
good = [event(0x41808), event(0x40b08), event(0x50000, data=0)]
messages, votes = parse('\n'.join(good), addresses)
assert len(messages) == 3 and all(v['counts'] == {'voltage': 0, 'enable': 0, 'mode': 1} for v in votes.values())
controls = {
    'wrong-HPM-value': [event(0x41808, 6), *good[1:]],
    'missing-response-request': [event(0x41808, msgid=0x10008), *good[1:]],
    'wrong-state': [event(0x41808, state='wake'), *good[1:]],
    'unexpected-voltage': [*good, event(0x41800, data=2800)],
    'unexpected-enable': [*good, event(0x40b04, data=1)],
    'duplicate-mode': [*good, good[0]],
    'missing-mode': good[1:],
    'unparsed-event': [*good, 'rpmh_send_msg: malformed'],
}
results = []
for name, lines in controls.items():
    try:
        parse('\n'.join(lines), addresses)
    except RuntimeError as exc:
        results.append({'name': name, 'rejected': True, 'reason': str(exc)})
    else:
        raise AssertionError('control admitted: ' + name)
try:
    parse('\n'.join(good), {'ldob7': 0x41800, 'ldom3': 0x41800})
except RuntimeError:
    results.append({'name': 'resource-address-alias', 'rejected': True})
else:
    raise AssertionError('aliased addresses admitted')
print(json.dumps({'status': 'PASS_HPM_TRACE_PARSER_NO_DEVICE_ACCESS', 'nominal_events': len(messages), 'cmd_wait_zero_with_response_bit_admitted': True, 'rejections': results}, sort_keys=True))
