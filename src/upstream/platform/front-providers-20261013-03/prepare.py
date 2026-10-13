#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build and validate isolated HPM-only front RPMh providers."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import struct
import subprocess

GOLDEN = Path('/boot/sp11-7.1.5-audio-fullio-v19c')
HASHES = {
    'x1e80100-microsoft-denali-sp11-fullio-v19c.dtb': '2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00',
    'initrd.img-7.1.5-sp11-fullio-v19c': 'ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d',
    'vmlinuz-7.1.5-sp11-render-parity-v4+': 'bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a',
}
RSC = '/soc@0/rsc@17500000'
PARENTS = {'bob2': RSC + '/regulators-0/bob2', 'smps4': RSC + '/regulators-1/smps4'}

def need(value, reason):
    if not value:
        raise ValueError(reason)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def cell(value):
    return struct.pack('>I', value)

def text(value):
    return value.encode() + b'\0'

def parse(path):
    b = path.read_bytes()
    need(len(b) >= 40, 'short header')
    magic, total, so, stro, ro, ver, compat, cpu, strsz, structsz = struct.unpack('>10I', b[:40])
    need(magic == 0xd00dfeed and total <= len(b) and ver == 17 and compat <= 17, 'header')
    need(40 <= so <= total and so + structsz <= total and 40 <= stro <= total and stro + strsz <= total, 'bounds')
    need(40 <= ro < total, 'reservation offset')
    end = ro
    while True:
        need(end + 16 <= total, 'reservation bounds')
        pair = struct.unpack('>QQ', b[end:end + 16])
        end += 16
        if pair == (0, 0):
            break
    reservations = b[ro:end]
    st, strings = b[so:so + structsz], b[stro:stro + strsz]
    tree, stack, i, finished = {}, [], 0, False
    def cstring(block, offset):
        need(0 <= offset < len(block), 'string offset')
        z = block.index(b'\0', offset)
        return block[offset:z].decode(), z + 1
    while i < len(st):
        need(i + 4 <= len(st), 'token bounds')
        token = struct.unpack('>I', st[i:i + 4])[0]
        i += 4
        if token == 1:
            name, i = cstring(st, i)
            i = (i + 3) & ~3
            need('/' not in name and (stack or name == ''), 'node name')
            p = stack[-1].rstrip('/') + '/' + name if stack else '/'
            need(p not in tree, 'duplicate node')
            tree[p] = {}
            stack.append(p)
        elif token == 2:
            need(stack, 'unbalanced end node')
            stack.pop()
        elif token == 3:
            need(stack and i + 8 <= len(st), 'property header')
            size, off = struct.unpack('>II', st[i:i + 8])
            i += 8
            need(i + size <= len(st), 'property bounds')
            name, _ = cstring(strings, off)
            need(name not in tree[stack[-1]], 'duplicate property')
            tree[stack[-1]][name] = st[i:i + size]
            i = (i + size + 3) & ~3
        elif token == 4:
            pass
        elif token == 9:
            need(not stack and '/' in tree, 'unbalanced final tree')
            finished = True
            break
        else:
            raise ValueError('unknown FDT token')
    need(finished, 'missing final token')
    return tree, reservations, cpu

def expected(base):
    ph = {}
    seen = set()
    for p, props in base.items():
        if 'phandle' in props:
            need(len(props['phandle']) == 4, 'phandle width')
            value = struct.unpack('>I', props['phandle'])[0]
            need(value not in seen and value not in (0, 0xffffffff), 'phandle collision')
            seen.add(value)
            ph[p] = value
    for name, path in PARENTS.items():
        need(path in ph and base[path]['regulator-name'].startswith(b'vreg_' + name[0:1].encode()), 'parent identity')
    need(base[PARENTS['bob2']]['regulator-name'] == text('vreg_bob2'), 'BOB2 name')
    need(base[PARENTS['smps4']]['regulator-name'] == text('vreg_s4c_1p8'), 'SMPS4 name')
    # Reject duplicate resource ownership anywhere in the Golden tree.
    for p, props in base.items():
        if props.get('qcom,pmic-id') in (text('b'), text('m')):
            child = 'ldo7' if props['qcom,pmic-id'] == text('b') else 'ldo3'
            need(p + '/' + child not in base, 'resource already owned')
    a, d = RSC + '/regulators-10', RSC + '/regulators-11'
    return {
        a: {'compatible': text('qcom,pm8550-rpmh-regulators'), 'qcom,pmic-id': text('b'), 'vdd-l6-l7-supply': cell(ph[PARENTS['bob2']])},
        a + '/ldo7': {'regulator-name': text('vreg_l7b_2p8'), 'regulator-min-microvolt': cell(2800000), 'regulator-max-microvolt': cell(2800000), 'regulator-initial-mode': cell(3)},
        d: {'compatible': text('qcom,pm8010-rpmh-regulators'), 'qcom,pmic-id': text('m'), 'vdd-l3-l4-supply': cell(ph[PARENTS['smps4']])},
        d + '/ldo3': {'regulator-name': text('vreg_l3m_1p8'), 'regulator-min-microvolt': cell(1800000), 'regulator-max-microvolt': cell(1800000), 'regulator-initial-mode': cell(3)},
    }

def validate(golden, candidate):
    base, reservations, cpu = parse(golden)
    actual, res2, cpu2 = parse(candidate)
    added = expected(base)
    need(not set(added) & set(base), 'provider identity exists')
    need(set(actual) == set(base) | set(added), 'node delta')
    need(reservations == res2 and cpu == cpu2, 'reservation or boot CPU changed')
    for p, props in base.items():
        need(actual[p] == props, 'Golden property changed: ' + p)
    for p, props in added.items():
        need(actual[p] == props, 'provider property changed: ' + p)
    return {'golden_nodes': len(base), 'candidate_nodes': len(actual), 'added_nodes': sorted(added), 'original_properties_byte_identical': True, 'reservation_map_byte_identical': True, 'parent_paths': PARENTS, 'initial_mode_hpm_on_both_children': True, 'enable_properties': False}

def build(output):
    need(not output.exists(), 'output stage exists')
    for name, pin in HASHES.items():
        need(sha(GOLDEN / name) == pin, 'Golden hash drift: ' + name)
    output.mkdir(parents=True)
    g = GOLDEN / 'x1e80100-microsoft-denali-sp11-fullio-v19c.dtb'
    c = output / 'front-providers.dtb'
    shutil.copyfile(g, c)
    base, _, _ = parse(g)
    for path, props in expected(base).items():
        subprocess.run(['fdtput', '-p', '-c', str(c), path], check=True)
        for name, value in props.items():
            subprocess.run(['fdtput', '-t', 'bx', str(c), path, name, *[f'{x:x}' for x in value]], check=True)
    result = validate(g, c)
    result.update(status='PASS_ISOLATED_FRONT_PROVIDER_HPM_DTB_PREPARED_NOT_INSTALLED', golden_hashes=HASHES, candidate_sha256=sha(c), kernel_release='7.1.5-sp11-render-parity-v4+', sensor_or_mode_runtime_qualified=False)
    (output / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path)
    ap.add_argument('--validate', type=Path)
    args = ap.parse_args()
    need(bool(args.out) != bool(args.validate), 'select build or validate')
    if args.out:
        build(args.out)
    else:
        print(json.dumps(validate(GOLDEN / 'x1e80100-microsoft-denali-sp11-fullio-v19c.dtb', args.validate), sort_keys=True))
