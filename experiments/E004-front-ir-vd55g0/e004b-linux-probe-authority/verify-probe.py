#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, shutil, subprocess, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SRC = REPO / "src/front-ir-vd55g0/sp11-vd55g0-idprobe"
C = SRC / "sp11-vd55g0-idprobe.c"
MAKEFILE = SRC / "Makefile"
KERNEL = REPO.parents[1] / "02-kernel/build-runtime-v4-headers-20260826"
DT_VERIFY = HERE / "verify-e004b-dtb.py"

SOURCE_SHA = "609eae6acd085719f36bc7923b8ca2f3500c49c8cc7f052502f162d01058f7aa"
MAKEFILE_SHA = "9f213c1d062c4bef95ba2b3f93d5d77100f8ec75a5dec22d07601a327a9754f6"
MODULE_SHA = "d749fb549ff7c03e0ebcd1690b78b795d985d6d37083ab938a2a2663c397daed"
VERMAGIC = "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64"

ALLOWED_UNDEFINED = {
    "clk_disable", "clk_enable", "clk_get_rate", "clk_prepare", "clk_set_rate", "clk_unprepare",
    "_dev_err", "dev_err_probe", "_dev_info", "devm_clk_get", "devm_gpiod_get", "devm_kmalloc",
    "devm_regulator_get", "gpiod_set_value_cansleep", "i2c_del_driver", "i2c_register_driver",
    "i2c_transfer", "regulator_disable", "regulator_enable", "regulator_get_voltage",
    "__stack_chk_fail", "__ubsan_handle_load_invalid_value", "usleep_range_state",
}


def need(v, message):
    if not v:
        raise AssertionError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_once(log_path: Path):
    subprocess.run(["make", "-C", str(KERNEL), f"M={SRC}", "clean"], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    with log_path.open("w") as log:
        subprocess.run(["make", "-C", str(KERNEL), f"M={SRC}", "modules", "V=0"],
                       check=True, stdout=log, stderr=subprocess.STDOUT)
    ko = SRC / "sp11-vd55g0-idprobe.ko"
    need(ko.is_file(), "module output")
    return ko


def main():
    subprocess.run(["python3", str(DT_VERIFY)], check=True, stdout=subprocess.DEVNULL)

    need(sha(C) == SOURCE_SHA, "probe source identity")
    need(sha(MAKEFILE) == MAKEFILE_SHA, "probe Makefile identity")
    source = C.read_text()

    # Exact bounded behavior: only two 16-bit register reads and no sensor-data write API.
    need(source.count("i2c_transfer(") == 1, "exactly one I2C transfer helper")
    need("sp11_read16(client, 0x0000, model)" in source, "model read")
    need("sp11_read16(client, 0x0004, revision)" in source, "revision read")
    need(source.count("sp11_read16(client,") == 2, "only model/revision reads")
    for forbidden in (
        "i2c_master_send(", "i2c_smbus_write", "regmap_write(", "request_firmware(",
        "v4l2_async_register", "video_register", "media_entity", "st,leds",
    ):
        need(forbidden not in source, "forbidden probe API " + forbidden)

    need('"microsoft,sp11-vd55g0-idprobe"' in source, "private compatible")
    need("#define SP11_XCLK_HZ        19200000UL" in source, "MCLK target")
    need("#define SP11_VCORE_UV        1152000" in source, "quantized VCORE")
    need("#define SP11_VDDIO_UV        1800000" in source, "VDDIO")
    need("#define SP11_VANA_UV         2800000" in source, "VANA")
    need("#define SP11_SAFE_DELAY_US       5000" in source, "bounded safety delay")
    need('devm_regulator_get(dev, "VDDIO")' in source and
         'devm_regulator_get(dev, "VCORE")' in source and
         'devm_regulator_get(dev, "VANA")' in source, "three named rails")
    need(source.index("regulator_enable(p->vddio)") <
         source.index("regulator_enable(p->vcore)") <
         source.index("regulator_enable(p->vana)"), "Windows D0 rail ordering")
    need(source.index("regulator_disable(p->vana)") <
         source.index("regulator_disable(p->vcore)") <
         source.index("regulator_disable(p->vddio)") <
         source.index("clk_disable_unprepare(p->xclk)"), "Windows D3 resource ordering")

    # Golden must still have no matching live device/module before the candidate is ever installed.
    need(not Path("/sys/module/sp11_vd55g0_idprobe").exists(), "probe module must not be loaded")
    live_compat = Path("/proc/device-tree")
    if live_compat.exists():
        cp = subprocess.run(["grep", "-Rals", "microsoft,sp11-vd55g0-idprobe", str(live_compat)],
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        need(not cp.stdout.strip(), "probe compatible must not exist in Golden live DT")

    with tempfile.TemporaryDirectory(prefix="e004b-probe-build-") as td:
        td = Path(td)
        ko_a = build_once(td / "build-a.log")
        a_copy = td / "A.ko"
        shutil.copyfile(ko_a, a_copy)
        sha_a = sha(a_copy)

        ko_b = build_once(td / "build-b.log")
        b_copy = td / "B.ko"
        shutil.copyfile(ko_b, b_copy)
        sha_b = sha(b_copy)

        need(sha_a == sha_b == MODULE_SHA, "two-build byte reproducibility")
        need(a_copy.read_bytes() == b_copy.read_bytes(), "two-build exact bytes")

        modinfo = subprocess.check_output(["modinfo", str(ko_b)], text=True)
        need("description:    Surface Pro 11 VD55G0 bounded identity/revision probe only" in modinfo,
             "module description")
        vermagic_line = next(line for line in modinfo.splitlines() if line.startswith("vermagic:"))
        vermagic = vermagic_line.split(":", 1)[1].strip()
        need(vermagic == VERMAGIC, "Golden vermagic")

        nm = subprocess.check_output(["nm", "-u", str(ko_b)], text=True)
        undefined = {line.split()[-1] for line in nm.splitlines() if line.strip()}
        need(undefined == ALLOWED_UNDEFINED,
             "unexpected undefined symbols " + repr(sorted(undefined ^ ALLOWED_UNDEFINED)))
        for forbidden_symbol in ("request_firmware", "regmap_write", "i2c_master_send",
                                 "v4l2_async_register_subdev", "media_entity_pads_init"):
            need(forbidden_symbol not in undefined, "forbidden module symbol " + forbidden_symbol)

        strings = subprocess.check_output(["strings", str(ko_b)], text=True, errors="replace")
        need("microsoft,sp11-vd55g0-idprobe" in strings, "compatible in module")
        need("SP11_VD55G0_IDPROBE_READS_COMPLETE" in strings, "bounded completion marker")
        need("sensor_data_writes=0 patch=0 boot=0 configure=0 stream=0 illumination=0" in strings,
             "safety marker")

    result = {
        "schema": "sp11-camera-e004b-idprobe-build-v1",
        "status": "PASS_OFFLINE_E004B_WRITE_FREE_IDPROBE_BUILD",
        "source_sha256": SOURCE_SHA,
        "makefile_sha256": MAKEFILE_SHA,
        "module_sha256_build_a": MODULE_SHA,
        "module_sha256_build_b": MODULE_SHA,
        "byte_reproducible_two_builds": True,
        "module_vermagic": VERMAGIC,
        "compatible": "microsoft,sp11-vd55g0-idprobe",
        "register_reads": ["0x0000 model (2 bytes)", "0x0004 revision (2 bytes)"],
        "sensor_data_register_writes": 0,
        "patch_upload": False,
        "sensor_boot": False,
        "sensor_configure": False,
        "v4l2_registration": False,
        "stream": False,
        "illumination": False,
        "power_off_before_probe_return": True,
        "safe_interstep_delay_us": 5000,
        "safe_delay_is_windows_parity_claim": False,
        "windows_aeob_delay_unit": "UNRESOLVED",
        "module_loaded": False,
        "linux_sensor_probe_performed": False,
        "next_gate": "Package a one-shot IB+IR DTB candidate with manual one-shot module load and mandatory Golden return; no stream or patch.",
    }
    (HERE / "PROBE-BUILD-RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("E004B_PROBE_VERIFY=PASS MODULE_SHA256=" + MODULE_SHA)
    print("E004B_PROBE_REPRODUCIBLE=YES VERMAGIC=" + VERMAGIC)
    print("E004B_PROBE_I2C=READ_ONLY MODEL=0x0000 REVISION=0x0004 SENSOR_DATA_WRITES=0")
    print("E004B_PROBE_SAFETY=PASS PATCH=NO BOOT=NO CONFIGURE=NO V4L2=NO STREAM=NO ILLUMINATION=NO")
    print("E004B_PROBE_RUNTIME=NO")


if __name__ == "__main__":
    main()
