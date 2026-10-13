#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Check actual compiled front graph, physical references and rejection controls."""
import argparse, copy, hashlib, importlib.util, json, struct
from pathlib import Path

def need(v, why):
    if not v:
        raise ValueError(why)

def u32(b):
    need(len(b) % 4 == 0, 'cell width')
    return list(struct.unpack('>' + 'I' * (len(b) // 4), b))

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--dtb', required=True, type=Path)
    ap.add_argument('--output', required=True, type=Path)
    a = ap.parse_args()
    q = Path(__file__).resolve().parent
    r = q.parents[3]
    m = json.loads((q / 'manifest.json').read_text())
    helper = r / 'src/upstream/platform/front-providers-20261013-03/prepare.py'
    need(hashlib.sha256(helper.read_bytes()).hexdigest() == m['reference_sha256'][str(helper.relative_to(r))], 'parser pin')
    need(not a.output.exists(), 'output occupied')
    spec = importlib.util.spec_from_file_location('fdt', helper)
    fdt = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fdt)
    t, _, _ = fdt.parse(a.dtb)
    soc = '/soc@0'
    rsc = soc + '/rsc@17500000'
    sensor = soc + '/cci@ac16000/i2c-bus@1/camera@10'
    phy = soc + '/phy@ace8000'
    camss = soc + '/isp@acb7000'
    io = rsc + '/regulators-8/ldo3'
    analog = rsc + '/regulators-0/ldo7'
    eps = [sensor + '/port/endpoint', phy + '/ports/port@0/endpoint',
           phy + '/ports/port@1/endpoint', camss + '/ports/port@2/endpoint']
    def validate(tree):
        ph = {u32(v['phandle'])[0]: n for n, v in tree.items() if 'phandle' in v}
        need(len(ph) == sum('phandle' in v for v in tree.values()), 'unique phandles')
        def ref(n, prop):
            cells = u32(tree[n][prop])
            need(len(cells) == 1 and cells[0] in ph, prop)
            return ph[cells[0]]
        for n in [soc + '/cci@ac16000', phy, camss]:
            need(tree[n].get('status') == b'okay\0', 'enabled device')
        need(tree[sensor]['compatible'] == b'sony,imx681\0', 'sensor')
        need(u32(tree[sensor]['reg']) == [0x10], 'sensor address')
        need(u32(tree[sensor]['assigned-clock-rates']) == [19200000], 'MCLK rate')
        need(tree[sensor]['clocks'] == tree[sensor]['assigned-clocks'], 'assigned MCLK')
        clk = u32(tree[sensor]['clocks'])
        need(len(clk) == 2 and ph[clk[0]] == soc + '/clock-controller@ade0000' and clk[1] == m['mclk4_id'], 'MCLK4')
        reset = u32(tree[sensor]['reset-gpios'])
        need(len(reset) == 3 and ph[reset[0]] == soc + '/pinctrl@f100000' and reset[1:] == [237, 1], 'reset237 active low')
        need(u32(tree[soc + '/cci@ac16000/i2c-bus@1']['clock-frequency']) == [400000], 'CCI FAST')
        need(ref(sensor, 'dovdd-supply') == io and ref(sensor, 'avdd-supply') == analog, 'sensor rails')
        for n, volts in [(io, 1800000), (analog, 2800000)]:
            need(u32(tree[n]['regulator-min-microvolt']) == [volts] and u32(tree[n]['regulator-max-microvolt']) == [volts], 'rail constraint')
            need(u32(tree[n]['regulator-initial-mode']) == [3], 'HPM')
        need(tree[rsc + '/regulators-0']['qcom,pmic-id'] == b'b\0', 'analog PMIC B')
        need(tree[rsc + '/regulators-8']['qcom,pmic-id'] == b'm\0', 'IO PMIC M')
        need(tree[rsc + '/regulators-8']['compatible'] == b'qcom,pm8010-rpmh-regulators\0', 'standard IO provider')
        need(ref(rsc + '/regulators-8', 'vdd-l3-l4-supply') == rsc + '/regulators-1/smps4', 'SMPS4 parent')
        need(ref(rsc + '/regulators-0', 'vdd-l6-l7-supply') == rsc + '/regulators-0/bob2', 'BOB2 parent')
        for a, b in [(eps[0], eps[1]), (eps[2], eps[3])]:
            need(ref(a, 'remote-endpoint') == b and ref(b, 'remote-endpoint') == a, 'reciprocal graph')
        for ep in [eps[0], eps[1], eps[3]]:
            need(u32(tree[ep]['bus-type']) == [1] and u32(tree[ep]['data-lanes']) == [0] and u32(tree[ep]['line-orders']) == [0], 'one trio0 ABC')
            need(not any(n in tree[ep] for n in ['clock-lanes', 'lane-polarities', 'clock-noncontinuous']), 'unsupported C-PHY properties')
        need(tree[eps[0]]['link-frequencies'] == struct.pack('>Q', 1203000000), '2.406 profile')
        need(u32(tree[phy]['reg']) == [0, 0xace8000, 0, 0x2000], 'PHY2 aperture')
        need(ref(phy, 'vdda-0p9-supply') == rsc + '/regulators-1/ldo2' and ref(phy, 'vdda-1p2-supply') == rsc + '/regulators-1/ldo1', 'retained PHY rails')
        need([n for n in tree if n.startswith(camss + '/ports/') and 'remote-endpoint' in tree[n]] == [eps[3]], 'only front CAMSS link')
        for n in [soc + '/cci@ac15000', soc + '/phy@ace4000', soc + '/phy@ace6000', soc + '/phy@acec000']:
            need(tree[n].get('status') == b'disabled\0', 'other camera nodes disabled')
        pinctrl = soc + '/pinctrl@f100000'
        for state, function, pins in [('front-cci1-default-state', b'aon_cci\0', b'gpio235\0gpio236\0'),
                                      ('front-cci1-sleep-state', b'aon_cci\0', b'gpio235\0gpio236\0'),
                                      ('front-imx681-default-state/mclk-pins', b'cam_aon\0', b'gpio100\0'),
                                      ('front-imx681-default-state/reset-pins', b'gpio\0', b'gpio237\0')]:
            need(tree[pinctrl + '/' + state]['function'] == function and tree[pinctrl + '/' + state]['pins'] == pins, 'retained pinmux')
        return dict(sensor=sensor, phy=phy, camss=camss, supplies=[io, analog], explicit_symbol_rate=2406000000, only_front_route=True)
    facts = validate(t)
    mutants = [('wrong-profile', eps[0], 'link-frequencies', struct.pack('>Q', 1200000000)),
               ('wrong-trio', eps[1], 'data-lanes', struct.pack('>I', 1)),
               ('wrong-order', eps[3], 'line-orders', struct.pack('>I', 1)),
               ('clock-lane', eps[1], 'clock-lanes', struct.pack('>I', 0)),
               ('short-aperture', phy, 'reg', struct.pack('>4I', 0, 0xace8000, 0, 0x1000)),
               ('wrong-reset', sensor, 'reset-gpios', struct.pack('>3I', u32(t[sensor]['reset-gpios'])[0], 237, 0)),
               ('wrong-analog-volts', analog, 'regulator-min-microvolt', struct.pack('>I', 2900000)),
               ('wrong-CCI-speed', soc + '/cci@ac16000/i2c-bus@1', 'clock-frequency', struct.pack('>I', 1000000)),
               ('broken-link', eps[3], 'remote-endpoint', t[eps[1]]['phandle'])]
    rejected = []
    for label, n, prop, value in mutants:
        bad = copy.deepcopy(t)
        bad[n][prop] = value
        try:
            validate(bad)
        except ValueError:
            rejected.append(label)
        else:
            raise ValueError('negative control accepted: ' + label)
    result = dict(status='PASS_COMPILED_FRONT_GRAPH', facts=facts, negative_controls=rejected,
                  dtb_sha256=hashlib.sha256(a.dtb.read_bytes()).hexdigest(), hardware_qualified=False,
                  sensor_binding_schema_missing=True)
    a.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))

if __name__ == '__main__':
    main()
