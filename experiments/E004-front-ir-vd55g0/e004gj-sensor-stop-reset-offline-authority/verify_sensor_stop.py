#!/usr/bin/env python3
"""Reconcile package STOP_STREAM candidate with Linux sensor stop/reset source.

Only static package/code evidence. No sensor/PMIC I/O or emitter testing.
"""
from pathlib import Path
from hashlib import sha256
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/"tools"))
import qti_parameter_bin as qti
import qti_sensor_summary as summary

PKG=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamauxsensor_extension8380.inf_arm64_84ddd55dc933cac9/com.surface.sensormodule.aux_vd55g0_MSHW0492.bin")
PKG_HASH="e574db7eb28231d3fa4f5eee5c1861919125d8ec7a753fc7a0708606e1f1a794"
NATIVE=ROOT/"src/front-ir-vd55g0/native/sp11-vd55g0-native.c"
ST=ROOT/"src/front-ir-vd55g0/st-vd55g0/vd55g0.c"

def need(ok,msg):
    if not ok: raise AssertionError("E004GJ_SENSOR_STOP_FAIL_CLOSED "+msg)

def validate_row(rows, name, target):
    need(rows==target, name+" sensor package register list mismatch")

def check(package, native, st):
    need(sha256(package.read_bytes()).hexdigest()==PKG_HASH,"pinned original Windows OEM sensor package hash")
    obj=qti.parse(package)
    ids={e["id"]:e for e in obj["entries"]}
    for n,expected in ((1880,[(0x0202,0x01)]),
                       (1884,[(0x0448,0x01)]),
                       (1888,[(0x0448,0x00)])):
        e=ids[n]
        need(e["name"]=="regSetting" and e["payload_size"]==40,
             f"package register entry {n} schema")
        rows=[(r["address"],r["data"]) for r in summary.reg_list(e,ids)]
        validate_row(rows,str(n),expected)
    # ST source is a naming reference; this does not show which OEM stream
    # path runs or what the actual sensor output GPIO does electrically.
    for token in ("VD55G0_REG_STREAMING", "VD55G0_REG_8BIT(0x0202)",
                  "VD55G0_STREAMING_STOP_STREAM", "VD55G0_REG_SW_STBY",
                  "VD55G0_SYSTEM_FSM_SW_STBY"):
        need(token in st,"ST register semantics drift "+token)
    need("VD55G0_STREAMING_STOP_STREAM\t\t\t1" in st or
         "#define VD55G0_STREAMING_STOP_STREAM" in st,
         "STOP_STREAM command value missing")
    need("static const u8 sp11_gpio_disabled[] = { 1, 1, 1, 1 };" in native,
         "native GPIO disabled state changed")
    start=native.index("static int sp11_vd55g0_enable_streams(")
    stop=native.index("static const struct v4l2_subdev_video_ops",start)
    text=native[start:stop]
    require_order=["memcmp(gpio, sp11_gpio_disabled", "sp11_write8(sensor, 0x0201, 0x01)",
                   "static int sp11_vd55g0_disable_streams(",
                   "sp11_write8(sensor, 0x0202, 0x01)",
                   "sp11_poll8(sensor, 0x0202, 0, 2000, \"STOP_COMPLETE\")",
                   "VD55G0_FSM_SW_STBY, 100, \"STOP_STANDBY\"",
                   "if (ret) {", "gpiod_set_value_cansleep(sensor->reset, 1)"]
    pos=-1
    for item in require_order:
        new=text.find(item,pos+1)
        need(new>pos,"stream/stop/fallback source order changed "+item)
        pos=new
    need("pm_runtime_put_sync_suspend(sensor->dev)" in text,
         "native stream-stop error suspend path missing")
    # The emitted GPIO is disabled during the previous ambient optical
    # candidate; none of this proves the PMIC output fault case.
    return {
        "package_stop_candidate_entry_id":1880,
        "package_stop_candidate_register":"0x0202",
        "package_stop_candidate_value":"0x01",
        "st_reference_semantic":"VD55G0_STREAMING_STOP_STREAM",
        "linux_native_start_reg":"0x0201",
        "linux_native_stop_reg":"0x0202",
        "linux_native_failed_stop_asserts_sensor_reset":True,
        "windows_oem_stop_packet_executed_live_proven":False,
        "reset_or_standby_proves_actual_emitter_led_off":False,
    }

def main():
    output=check(PKG,NATIVE.read_text(),ST.read_text())
    output.update({
        "experiment":"E004gj",
        "status":"PASS_PINNED_SENSOR_STOP_PACKAGE_AND_LINUX_SOURCE_RECONCILIATION_OFFLINE",
        "windows_oem_package_sha256":PKG_HASH,
        "linux_native_source_sha256":sha256(NATIVE.read_bytes()).hexdigest(),
        "st_source_reference_sha256":sha256(ST.read_bytes()).hexdigest(),
        "verifier_sha256":sha256((HERE/"verify_sensor_stop.py").read_bytes()).hexdigest(),
        "negative_test_sha256":sha256((HERE/"test_sensor_stop.py").read_bytes()).hexdigest(),
        "windows_oem_sensor_driver_stop_callback_dynamically_traced":False,
        "independent_pmic_emitter_cutoff_proven":False,
        "native_emitter_authorized":False,
        "camera_windows_kd_pmic_or_emitter_accessed":False,
        "golden_modified":False,
    })
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(output,indent=2)+"\n")
    print("E004GJ_OEM_PACKAGE_SENSOR_STOP_CANDIDATE=PASS 0202_01")
    print("E004GJ_LINUX_NATIVE_STOP_STANDBY_RESET_SOURCE=PASS")
    print("OEM_STOP_RUNTIME=UNOBSERVED PHYSICAL_LED_OFF=UNPROVEN EMITTER=OFF")

if __name__=="__main__":main()
