#!/usr/bin/env python3
"""Read-only verification of exact SP11 CAMSS front guards/rear RAW evidence.
Never call camera, load firmware/modules, inspect photos or write outside RESULT.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
KERNEL = Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src")
CAMSS = KERNEL / "drivers/media/platform/qcom/camss"
SENSOR = KERNEL / "drivers/media/i2c/ov13858.c"
FILES = {
    "csid": CAMSS / "camss-csid-680.c",
    "vfe": CAMSS / "camss-vfe-680.c",
    "orchestrator": CAMSS / "camss.c",
    "sensor": SENSOR,
}
ORACLE = ROOT / "oracle/windows-rear-kd-2026-08-27.md"
REAR_RAW = ROOT / "experiments/E004-front-ir-vd55g0/e004lr-guarded-rgb-raw-frames-one-shot/RESULT.json"
IG = ROOT / "experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ig-unified-rear-to-front-r16-r27/UNIFIED-DISCOVERY.json"

def assert_source(name, expr):
    if not expr:
        raise ValueError("SOURCE_BOUNDARY_FAIL: " + name)

def function_prefix(source, name, n=1700):
    found = re.search(r"\b" + re.escape(name) + r"\s*\(", source)
    assert_source(name + " function exists", found is not None)
    begin = source.find("{", found.end())
    assert_source(name + " function body", begin >= 0)
    return source[begin:begin + n]

def inspect():
    text = {name: p.read_text() for name, p in FILES.items()}
    csid = function_prefix(text["csid"], "__csid_sp11_front_ipp_mode0", 620)
    vfe = function_prefix(text["vfe"], "vfe680_x1e_bus_target", 360)
    camss = function_prefix(text["orchestrator"], "camss_x1e_pix_runner_validate", 3400)
    for pattern in (
        r"csid->id\s*==\s*1",
        r"csid->phy.csiphy_id\s*==\s*2",
        r"CSID_PHY_SEL_CPHY",
        r"csid->phy.lane_cnt\s*==\s*1",
        r"MEDIA_BUS_FMT_SRGGB10_1X10",
        r"fmt->width\s*==\s*3840",
        r"fmt->height\s*==\s*2160",
    ):
        assert_source("CSID front-only " + pattern, re.search(pattern, csid) is not None)
    assert_source("VFE front-only id", re.search(r"vfe->id\s*==\s*1", vfe) is not None)
    for pattern in (r"vfe\[1\]", r"csid\[1\]", r"csiphy\[2\]",
                    r"CSID_PHY_SEL_CPHY", r"MEDIA_BUS_FMT_SRGGB10_1X10",
                    r"camss_x1e_pix_link"):
        assert_source("CAMSS front runner " + pattern, re.search(pattern, camss) is not None)
    for macro, val in (
        ("VFE680_X1E_QC10C_WIDTH", "2560"),
        ("VFE680_X1E_QC10C_HEIGHT", "1440"),
        ("VFE680_X1E_QC10C_STRIDE", "3584"),
        ("VFE680_X1E_QC10C_SIZE", "0x0076b000"),
    ):
        match = re.search(r"^#define\s+" + macro + r"\s+" + val + r"\b",
                          text["vfe"], flags=re.MULTILINE)
        assert_source("front QC10C-only " + macro, match is not None)
    assert_source("rear sensor mode 4076x2806",
                  re.search(r"surface_pro11_modes\[\].*?\.width\s*=\s*4076,\s*\.height\s*=\s*2806",
                            text["sensor"], flags=re.DOTALL) is not None)
    assert_source("rear driver SGRBG10", "MEDIA_BUS_FMT_SGRBG10_1X10" in text["sensor"])
    oracle = ORACLE.read_text()
    assert_source("Windows OEM rear board", "MSHW0491" in oracle)
    assert_source("Windows OEM rear sensor id", "0xd855" in oracle)
    raw = json.loads(REAR_RAW.read_text())
    route = json.loads(IG.read_text())
    assert_source("real rear RAW mode", raw["rear_ov13858"]["raw_format"] == "4076x2806-SGRBG10_CSI2P")
    assert_source("accepted rear source route",
                  route["rear_route"] == ["msm_csiphy1", "msm_csid0", "msm_vfe0_rdi0", "msm_vfe0_video0"])
    return {
        "status": "PASS_SOURCE_ONLY_FRONT_GUARDS_LOCKED_REAR_RAW_PINNED",
        "kernel_source": str(KERNEL),
        "checked_functions": ["__csid_sp11_front_ipp_mode0", "vfe680_x1e_bus_target",
                              "camss_x1e_pix_runner_validate"],
        "local_source_sha256": {name: hashlib.sha256(path.read_bytes()).hexdigest()
                                for name, path in FILES.items()},
        "front_qc10c_output": {"width": 2560, "height": 1440, "stride": 3584, "surface_bytes": 0x76b000},
        "front_pix_input": {"width": 3840, "height": 2160, "bayer": "SRGGB10"},
        "rear_proven_raw_input": {"width": 4076, "height": 2806, "bayer": "SGRBG10"},
        "rear_requested_output": {"width": 3840, "height": 2160, "hardware_proven": False},
        "windows_rear_board": "MSHW0491",
        "windows_rear_sensor_probe_id": "0xd855",
        "rear_isp_configuration_derived": False,
        "camera_or_firmware_or_boot_accessed": False,
    }

if __name__ == "__main__":
    print(json.dumps(inspect(), sort_keys=True, indent=2))
