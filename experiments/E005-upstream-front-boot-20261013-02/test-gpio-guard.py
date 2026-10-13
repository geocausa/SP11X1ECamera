#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""The retained 7.2 debug format must admit only the known TLMM reset state."""
import importlib.util, sys
from pathlib import Path
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location('observer', Path(__file__).with_name('run-once.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
fixture = 'gpiochip9: 239 GPIOs, parent: platform/f100000.pinctrl, f100000.pinctrl:\n gpio237 : out low  func0 2mA no pull\n'
assert m.reset237_low(fixture)
broken = [fixture.replace('out low', 'out high'), fixture.replace('gpio237', 'gpio238'),
          fixture.replace('f100000', 'f200000'), fixture.replace('func0', 'func1'),
          fixture + fixture.replace('gpiochip9', 'gpiochip99')]
for text in broken:
    try:
        m.reset237_low(text)
    except RuntimeError:
        pass
    else:
        raise AssertionError('invalid GPIO evidence admitted')
print('PASS: retained GPIO format plus five rejected controls')
