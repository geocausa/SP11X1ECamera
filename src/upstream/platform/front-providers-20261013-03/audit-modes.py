#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Execute pinned regulator mode callbacks; transport is a hosted model."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess

SOURCES = {
    'golden-reference': (Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src'), '036a42419906dadc79e5465286923642bc55aa68786448f270e9ed60399634c2'),
    'candidate23': (Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/upstream-ife-base-build-20261011-01/candidate-23/source'), '796f955c42dc7491690a148d5d20711a59af314ba55b3eee51ed49f38f6a63d0'),
}
HEADER_PIN = '9024ec736a8bca4cc31d414ea2978b237ac6c4ff0409988f8434147a29ecd622'

def need(value, reason):
    if not value:
        raise ValueError(reason)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def function(s, name):
    m = re.search(r'^static (?:int|unsigned int) ' + re.escape(name) + r'\([^;]*?\)\n\{', s, re.M)
    need(m, 'function absent: ' + name)
    i, depth = m.end() - 1, 0
    for j in range(i, len(s)):
        if s[j] == '{':
            depth += 1
        elif s[j] == '}':
            depth -= 1
            if depth == 0:
                return s[m.start():j + 1]
    raise ValueError('unbalanced function')

def table(s, name):
    m = re.search(r'^static const int ' + name + r'\[.*?\] = \{.*?^\};', s, re.M | re.S)
    need(m, 'mode table absent: ' + name)
    return m[0]

PREFIX = r'''
// SPDX-License-Identifier: GPL-2.0-only
// Callback excerpts retain their pinned Linux/Qualcomm source provenance.
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <errno.h>
struct device { int unused; };
struct tcs_cmd { uint32_t addr, data; bool wait; };
enum rpmh_state { RPMH_SLEEP_STATE, RPMH_WAKE_ONLY_STATE, RPMH_ACTIVE_ONLY_STATE };
struct rpmh_vreg_hw_data { const int *pmic_mode_map; };
struct rpmh_vreg { struct device *dev; const struct rpmh_vreg_hw_data *hw_data;
    uint32_t addr; unsigned int mode; bool bypassed, always_wait_for_ack; int enabled; };
struct regulator_dev { struct rpmh_vreg *driver_data; };
static struct rpmh_vreg *rdev_get_drvdata(struct regulator_dev *r) { return r->driver_data; }
static unsigned int calls, cases;
static int failure, last_state;
static struct tcs_cmd last_cmd;
static bool synchronous;
static int rpmh_write(struct device *d, enum rpmh_state s, struct tcs_cmd *c, unsigned int n)
{ (void)d; assert(n == 1); ++calls; last_state = s; last_cmd = *c; synchronous = true; return failure; }
static int rpmh_write_async(struct device *d, enum rpmh_state s, struct tcs_cmd *c, unsigned int n)
{ (void)d; assert(n == 1); ++calls; last_state = s; last_cmd = *c; synchronous = false; return failure; }
'''

TEST = r'''
static void reset(void) { calls = 0; failure = 0; synchronous = false; }
int main(void)
{
    assert(RPMH_REGULATOR_MODE_HPM == 3 && PMIC5_LDO_MODE_HPM == 7);
    assert(RPMH_REGULATOR_REG_VRM_MODE == 8);
    assert(rpmh_regulator_pmic4_ldo_of_map_mode(3) == REGULATOR_MODE_NORMAL); ++cases;
    assert(rpmh_regulator_pmic4_ldo_of_map_mode(2) == REGULATOR_MODE_INVALID); ++cases;
    assert(rpmh_regulator_pmic4_ldo_of_map_mode(99) == REGULATOR_MODE_INVALID); ++cases;
    const int *maps[] = { pmic_mode_map_pmic5_ldo, pmic_mode_map_pmic5_ldo_hpm };
    for (unsigned int k = 0; k < 2; ++k) {
        struct rpmh_vreg_hw_data hw = { .pmic_mode_map = maps[k] };
        struct rpmh_vreg v = { .hw_data = &hw, .addr = 0x40000, .enabled = -EINVAL };
        struct regulator_dev r = { .driver_data = &v };
        reset();
        assert(rpmh_regulator_vrm_set_mode(&r, REGULATOR_MODE_NORMAL) == 0);
        assert(calls == 1 && synchronous && last_state == RPMH_ACTIVE_ONLY_STATE);
        assert(last_cmd.addr == v.addr + 8 && last_cmd.data == 7 && last_cmd.wait == false);
        assert(v.enabled == -EINVAL && v.bypassed == false);
        assert(rpmh_regulator_vrm_get_mode(&r) == REGULATOR_MODE_NORMAL); ++cases;
        assert(rpmh_regulator_vrm_set_mode(&r, REGULATOR_MODE_NORMAL) == 0 && calls == 1); ++cases;
        for (unsigned int m = 9; m < 20; ++m) {
            assert(rpmh_regulator_vrm_set_mode(&r, m) == -EINVAL && calls == 1);
            assert(v.mode == REGULATOR_MODE_NORMAL && v.enabled == -EINVAL); ++cases;
        }
        assert(rpmh_regulator_vrm_set_mode(&r, UINT32_MAX) == -EINVAL && calls == 1); ++cases;
        assert(rpmh_regulator_vrm_set_mode(&r, REGULATOR_MODE_FAST) == -EINVAL && calls == 1); ++cases;
        if (k == 1) {
            assert(rpmh_regulator_vrm_set_mode(&r, REGULATOR_MODE_IDLE) == -EINVAL && calls == 1); ++cases;
            assert(rpmh_regulator_vrm_set_mode(&r, REGULATOR_MODE_STANDBY) == -EINVAL && calls == 1); ++cases;
        }
        v.mode = REGULATOR_MODE_INVALID; reset(); failure = -ETIMEDOUT;
        assert(rpmh_regulator_vrm_set_mode(&r, REGULATOR_MODE_NORMAL) == -ETIMEDOUT);
        assert(calls == 1 && v.mode == REGULATOR_MODE_INVALID && v.enabled == -EINVAL); ++cases;
        reset(); failure = -EIO;
        assert(rpmh_regulator_vrm_set_mode(&r, REGULATOR_MODE_NORMAL) == -EIO);
        assert(calls == 1 && v.mode == REGULATOR_MODE_INVALID && v.enabled == -EINVAL); ++cases;
        reset();
        assert(rpmh_regulator_vrm_set_mode(&r, REGULATOR_MODE_NORMAL) == 0);
        assert(calls == 1 && synchronous && v.mode == REGULATOR_MODE_NORMAL && v.enabled == -EINVAL); ++cases;
    }
    printf("PASS_ACTUAL_MODE_CALLBACKS cases=%u\n", cases);
    return 0;
}
'''

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', type=Path, required=True)
    a = ap.parse_args()
    need(not a.out.exists(), 'retain previous output')
    a.out.mkdir()
    result = {'status': 'PASS_PINNED_MODE_CALLBACK_SOURCE', 'transport': 'modeled synchronous/asynchronous request and error return; no device access', 'runs': [], 'source_pins': {}, 'excerpts': {}}
    for label, (root, driver_pin) in SOURCES.items():
        p, h = root / 'drivers/regulator/qcom-rpmh-regulator.c', root / 'include/dt-bindings/regulator/qcom,rpmh-regulator.h'
        need(sha(p) == driver_pin and sha(h) == HEADER_PIN, 'input drift')
        s, header, consumer = p.read_text(), h.read_text(), (root / 'include/linux/regulator/consumer.h').read_text()
        constants = []
        for text, pattern in ((header, r'^#define RPMH_REGULATOR_MODE_.*$'), (consumer, r'^#define REGULATOR_MODE_.*$'), (s, r'^#define (?:RPMH_REGULATOR_REG_VRM_MODE|PMIC5_LDO_MODE_\w+|PMIC4_BOB_MODE_PASS)\s+.*$')):
            constants += re.findall(pattern, text, re.M)
        funcs = [function(s, name) for name in ('rpmh_regulator_send_request', 'rpmh_regulator_vrm_set_mode_bypass', 'rpmh_regulator_vrm_set_mode', 'rpmh_regulator_vrm_get_mode', 'rpmh_regulator_pmic4_ldo_of_map_mode')]
        tables = [table(s, name) for name in ('pmic_mode_map_pmic5_ldo', 'pmic_mode_map_pmic5_ldo_hpm')]
        excerpt = '\n'.join(constants + tables + funcs)
        result['excerpts'][label] = hashlib.sha256(excerpt.encode()).hexdigest()
        for name in ('drivers/regulator/qcom-rpmh-regulator.c', 'include/dt-bindings/regulator/qcom,rpmh-regulator.h', 'include/linux/regulator/consumer.h', 'drivers/regulator/core.c', 'drivers/regulator/of_regulator.c', 'drivers/soc/qcom/rpmh.c', 'drivers/soc/qcom/rpmh-rsc.c', 'drivers/soc/qcom/trace-rpmh.h'):
            result['source_pins'][str(root / name)] = sha(root / name)
        src = a.out / (label + '.c')
        src.write_text(PREFIX + '\n' + excerpt + '\n' + TEST)
        for cc in ('gcc', 'clang'):
            binary = a.out / (label + '-' + cc)
            command = [cc, '-std=c11', '-Wall', '-Wextra', '-Werror', '-g', '-O1', '-fno-omit-frame-pointer', '-fsanitize=address,undefined', str(src), '-o', str(binary)]
            build = subprocess.run(command, text=True, capture_output=True)
            (a.out / (binary.name + '.build-log')).write_text(build.stdout + build.stderr)
            need(build.returncode == 0, 'fixture compile failed')
            run = subprocess.run([str(binary)], text=True, capture_output=True)
            (a.out / (binary.name + '.run-log')).write_text(run.stdout + run.stderr)
            need(run.returncode == 0 and 'PASS_ACTUAL_MODE_CALLBACKS' in run.stdout, 'callback check failed')
            result['runs'].append({'source': label, 'compiler': cc, 'command': command, 'result': run.stdout.strip()})
    need(len(set(result['excerpts'].values())) == 1, 'old/new mode callback delta requires review')
    (a.out / 'RESULT.json').write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(result, indent=2, sort_keys=True))

if __name__ == '__main__':
    main()
