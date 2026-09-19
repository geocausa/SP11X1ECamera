#!/usr/bin/env python3
"""Offline negative checks for sensor stop package and native reset contract."""
from pathlib import Path
import importlib.util
from tempfile import TemporaryDirectory
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004gj", HERE/"verify_sensor_stop.py")
v=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)
native=v.NATIVE.read_text()
st=v.ST.read_text()
v.check(v.PKG,native,st)
count=0
for old,repl in (
    ("sp11_write8(sensor, 0x0202, 0x01)",
     "sp11_write8(sensor, 0x0202, 0x00)"),
    ('sp11_poll8(sensor, 0x0202, 0, 2000, "STOP_COMPLETE")',
     'sp11_poll8(sensor, 0x0202, 0, 0, "STOP_COMPLETE")'),
    ("gpiod_set_value_cansleep(sensor->reset, 1)",
     "gpiod_set_value_cansleep(sensor->reset, 0)"),
    ("static const u8 sp11_gpio_disabled[] = { 1, 1, 1, 1 };",
     "static const u8 sp11_gpio_disabled[] = { 1, 2, 1, 1 };"),
    ("sp11_write8(sensor, 0x0201, 0x01)",
     "sp11_write8(sensor, 0x0201, 0x02)"),
    ('VD55G0_FSM_SW_STBY, 100, "STOP_STANDBY"',
     'VD55G0_FSM_SW_STBY, 100, "STREAMING"'),
):
    assert old in native,old
    try:v.check(v.PKG,native.replace(old,repl),st)
    except AssertionError: count+=1
    else:raise AssertionError("native sensor source mutation was accepted "+old)
for old,repl in (
    ("VD55G0_REG_8BIT(0x0202)","VD55G0_REG_8BIT(0x0201)"),
    ("VD55G0_STREAMING_STOP_STREAM","VD55G0_STREAMING_START_STREAM"),
):
    assert old in st
    try:v.check(v.PKG,native,st.replace(old,repl))
    except AssertionError: count+=1
    else:raise AssertionError("ST naming reference mutation accepted "+old)
with TemporaryDirectory(prefix="e004gj-sensor-negative-") as tmp:
    p=Path(tmp)/"tampered-oem-package.bin"
    p.write_bytes(v.PKG.read_bytes()+b"0")
    try:v.check(p,native,st)
    except AssertionError:count+=1
    else:raise AssertionError("modified OEM package accepted")
assert count==9
print("E004GJ_OEM_SOURCE_AND_STOP_RESET_NEGATIVES=PASS CASES=9")
print("SENSOR_RESET_NOT_HARDWARE_EMITTER_CUTOFF=YES")
