#!/usr/bin/env python3
"""E004nk: read-only rear PIX feasibility gate. NEVER arms, loads or captures."""
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DTB = ROOT / "src/sp11-camera-stack/authority/ib-unified-rear-front.dtb"
IG = ROOT / "experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ig-unified-rear-to-front-r16-r27/UNIFIED-DISCOVERY.json"
HY = ROOT / "experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hy-production-one-stream-r27"
Z = ROOT / "experiments/E003-front-imx681-cphy/e003i-front-native-productionization/z-live-3a-runtime/RESULT.json"
LR = ROOT / "experiments/E004-front-ir-vd55g0/e004lr-guarded-rgb-raw-frames-one-shot/RESULT.json"
REAR = "/soc@0/cci@ac15000/i2c-bus@1/camera@10"
FRONT = "/soc@0/cci@ac16000/i2c-bus@1/camera@10"
CAMSS = "/soc@0/isp@acb7000"
ENDPOINTS = {
    "rear_sensor": REAR + "/port/endpoint",
    "rear_camss": CAMSS + "/ports/port@1/endpoint",
    "front_sensor": FRONT + "/port/endpoint",
    "front_camss": CAMSS + "/ports/port@2/endpoint",
}

class GateError(ValueError):
    pass

def require(value, reason):
    if not value:
        raise GateError(reason)

def read_json(path):
    return json.loads(path.read_text())

def dt_get(path, prop, kind="x"):
    result = subprocess.run(
        ["fdtget", "-t", kind, str(DTB), path, prop],
        text=True, capture_output=True, check=False, timeout=10)
    require(result.returncode == 0,
            "DT property unavailable: " + path + " " + prop)
    return result.stdout.strip()

def check(unified, front_discovery, front_result, stats_result, raw_result, get=dt_get):
    """Pure gate with injected DT reader for fail-closed synthetic tests."""
    require(unified["front_route"] ==
            ["msm_csiphy2", "msm_csid1", "msm_vfe1_pix", "msm_vfe1_video3"],
            "accepted front PIX route changed")
    require(unified["rear_route"] ==
            ["msm_csiphy1", "msm_csid0", "msm_vfe0_rdi0", "msm_vfe0_video0"],
            "accepted rear RAW route changed: do not claim PIX")
    require(front_discovery["format"] == "SRGGB10_1X10/3840x2160"
            and front_discovery["proven_capture_fourcc"] == "QC10C",
            "front proof format changed")
    require(front_result["frames"] == 27 and
            front_result["golden_return"] == "PASS" and
            front_result["candidate_retired"] is True,
            "front bounded PIX proof / retirement missing")
    require(stats_result["status"] == "PASS" and
            stats_result["paired_tlbg_stats3a_identity_exact"] is True
            and stats_result["aec_be_all_nonzero"] is True
            and stats_result["bhist_all_nonzero"] is True
            and stats_result["awb_bg_all_nonzero"] is True,
            "front paired hardware 3A proof missing")
    rear = raw_result["rear_ov13858"]
    require(rear["frames"] == 6 and
            rear["raw_format"] == "4076x2806-SGRBG10_CSI2P" and
            rear["whole_kernel_media_graph_after_session"] == "neutral"
            and raw_result["automatic_golden_return"] is True,
            "rear RAW transport proof missing or format changed")

    require(get(REAR, "compatible", "s") == "ovti,ov13858", "wrong rear sensor")
    require(get(FRONT, "compatible", "s") == "sony,imx681", "wrong front sensor")
    require(get(CAMSS, "compatible", "s") == "qcom,x1e80100-camss",
            "unexpected CAMSS compatibility")
    for name in ("rear_sensor", "rear_camss", "front_sensor", "front_camss"):
        require(get(ENDPOINTS[name], "phandle"), "missing endpoint: " + name)
    for a, b in (("rear_sensor", "rear_camss"), ("front_sensor", "front_camss")):
        require(get(ENDPOINTS[a], "remote-endpoint") ==
                get(ENDPOINTS[b], "phandle") and
                get(ENDPOINTS[b], "remote-endpoint") ==
                get(ENDPOINTS[a], "phandle"),
                "nonreciprocal DT endpoint pair: " + a)
    require(get(ENDPOINTS["rear_sensor"], "bus-type") == "4" and
            get(ENDPOINTS["rear_camss"], "bus-type") == "4" and
            get(ENDPOINTS["front_sensor"], "bus-type") == "1" and
            get(ENDPOINTS["front_camss"], "bus-type") == "1",
            "D-PHY/C-PHY cross-camera bus mismatch")
    require(get(ENDPOINTS["rear_sensor"], "data-lanes").split() ==
            ["1", "2", "3", "4"] and
            get(ENDPOINTS["rear_camss"], "data-lanes").split() ==
            ["0", "1", "2", "3"],
            "rear physical vs CAMSS lane numbering changed")
    require(get(ENDPOINTS["front_sensor"], "data-lanes").split() ==
            ["0"] and get(ENDPOINTS["front_camss"], "data-lanes").split() == ["0"],
            "front C-PHY lanes changed")
    return {
        "gate": "PASS_SOURCE_ONLY_REAR_PIX_BOUNDARY_NOT_HARDWARE_PROVEN",
        "rear_sensor": "OV13858 MSHW0491",
        "rear_proven_route": unified["rear_route"],
        "rear_source_format": rear["raw_format"],
        "rear_dphy_sensor_lanes": [1, 2, 3, 4],
        "rear_dphy_camss_lane_indices": [0, 1, 2, 3],
        "front_proven_route": unified["front_route"],
        "front_bounded_native_PIX_frames": front_result["frames"],
        "front_paired_stats_frames": len(stats_result["observed_sequences"]),
        "rear_native_PIX_frames_proven": 0,
        "rear_PIX_target": ["msm_csiphy1", "msm_csid0",
                            "msm_vfe0_pix", "msm_vfe0_video3"],
        "rear_PIX_target_status": "ARCHIVED_MEDIA_ENTITIES_ONLY_NO_REAR_PIX_HARDWARE_FRAME",
        "no_front_IQ_or_bayer_lsc_gain_reused_for_rear": True,
        "next_required_source_gates": [
            "Validate archived CSID0 pad4 to VFE0 PIX link under rear D-PHY mode; rediscover video node at runtime.",
            "Derive rear OV13858 4076x2806-to-3840x2160 input crop and RAW Bayer GRBG mapping.",
            "Validate rear-specific VFE0 PIX RT-CDM/IQ producer and QC10C or true-linear output contract.",
            "Validate rear VFE0 write-master/SMMU SID, output stride/size, clocks and buffer retirement.",
            "Use MSHW0491 Windows rear mode/tuning metadata as oracle, never front IMX681 tables.",
            "Only then prepare a distinct source-pinned Golden-protected single-use physical candidate."
        ],
        "hardware_or_windows_firmware_loaded_by_this_gate": False,
        "golden_or_boot_modified_by_this_gate": False,
        "optical_pixels_or_photo_hashes_accessed_by_this_gate": False,
    }

def main():
    result = check(read_json(IG), read_json(HY / "DISCOVERY.json"),
                   read_json(HY / "RESULT.json"), read_json(Z), read_json(LR))
    print(json.dumps(result, sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
