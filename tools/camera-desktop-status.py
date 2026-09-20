#!/usr/bin/env python3
"""Inspect desktop camera prerequisites without opening a camera or starting services."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

PACKAGES = ("libcamera-tools", "libcamera-ipa", "libspa-0.2-libcamera",
            "gstreamer1.0-libcamera", "pipewire", "wireplumber",
            "xdg-desktop-portal", "xdg-desktop-portal-gnome")
SERVICES = ("pipewire.service", "wireplumber.service", "xdg-desktop-portal.service")
ROOT = Path(__file__).resolve().parents[1]
DUAL_RGB_CONTRACT = ROOT / "src/sp11-camera-stack/rgb-desktop-output-contract.json"
FRONT_HARDWARE_CONTRACT = ROOT / "src/front-imx681/desktop-output-contract.json"
REAR_BRIDGE_EVIDENCE = ROOT / "experiments/E004-front-ir-vd55g0/e004is-rear-bayer-to-nv12-offline/RESULT.json"


def load_rgb_contract():
    """Validate BOTH camera source semantics before reporting desktop readiness."""
    c = json.loads(DUAL_RGB_CONTRACT.read_text())
    front = json.loads(FRONT_HARDWARE_CONTRACT.read_text())
    rear = json.loads(REAR_BRIDGE_EVIDENCE.read_text())
    if c.get("schema") != "sp11-dual-rgb-desktop-output-contract-v1":
        raise ValueError("unknown dual-camera desktop contract")
    r, f = c["rear"], c["front"]
    if not (r["sensor"] == "OV13858" and r["accepted_v4l2_fourcc"] == "pgAA"
            and r["raw_bayer"] == "GRBG" and r["capture_width"] == 4076
            and r["capture_height"] == 2806 and r["capture_stride_bytes"] == 5104
            and r["capture_frame_bytes"] == 14321824
            and rear["source_sha256"] == "6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346"
            and rear["rear_source_geometry"]["frame_bytes"] == 14321824
            and rear["output_geometry"]["frame_bytes"] == 3110400
            and rear["real_rear_colourbar_gstreamer_nv12_rawvideoparse_and_videoconvert"] == "PASS"
            and rear["offline_positive_negative_tests"] == 9
            and r["offline_previous_real_colorbar_to_nv12"] is True
            and r["offline_gstreamer_nv12_processing_verified"] is True):
        raise ValueError("rear source geometry/provenance changed")
    if not (f["sensor"] == "IMX681" and f["accepted_v4l2_fourcc"] == "Q10C"
            and f["capture_frame_bytes"] == 7778304
            and front["v4l2_symbol"] == "V4L2_PIX_FMT_QC10C"
            and front["allocation_bytes"] == f["capture_frame_bytes"]
            and front["linear_nv12"] is False
            and front["raw_bayer"] is False
            and f["offline_synthetic_already_linear_nv12_scaler_verified"] is True
            and f["may_treat_qc10c_as_bayer"] is False
            and f["may_treat_qc10c_as_linear_nv12"] is False):
        raise ValueError("front QC10C semantic contract changed")
    if not (c["common_desktop_target"]["fourcc"] == "NV12"
            and c["common_desktop_target"]["width"] == 1920
            and c["common_desktop_target"]["height"] == 1080
            and c["common_desktop_target"]["frame_bytes"] == 3110400):
        raise ValueError("desktop NV12 output contract changed")
    if any((c["default_install_authorized"],
            c["common_desktop_target"]["verified_physical_live_desktop_capture"],
            c["common_desktop_target"]["selectable_front_rear_live_devices"],
            r["device_advertisable_to_applications"],
            r["live_desktop_nv12_device_verified"],
            f["device_advertisable_to_applications"],
            f["live_desktop_nv12_device_verified"],
            f["genuine_live_front_linear_nv12_verified"],
            f["compressed_qc10c_decompression_verified"],
            f["may_treat_qc10c_as_bayer"], f["may_treat_qc10c_as_linear_nv12"],
            c["protected_ir_and_hello"]["illumination_authorized"],
            c["protected_ir_and_hello"]["secure_production_worker_signed"] )):
        raise ValueError("unproven front/rear desktop capability must not be advertised")
    return c

def query(argv, env=None):
    try:
        cp = subprocess.run(argv, capture_output=True, text=True, timeout=8, env=env)
        return cp.returncode, cp.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None, ""

def collect():
    rgb_contract = load_rgb_contract()
    packages = {}
    for name in PACKAGES:
        rc, value = query(["dpkg-query", "-W", "-f=${db:Status-Abbrev}|${Version}", name])
        installed = rc == 0 and value.startswith("ii ")
        packages[name] = {"installed": installed, "version": value.split("|", 1)[1] if installed else None}
    runtime = Path("/run/user") / str(os.getuid())
    env = dict(os.environ, XDG_RUNTIME_DIR=str(runtime),
               DBUS_SESSION_BUS_ADDRESS="unix:path=" + str(runtime / "bus"))
    services = {}
    for name in SERVICES:
        rc, value = query(["systemctl", "--user", "is-active", name], env)
        services[name] = value if rc is not None and value else "unavailable"
    nodes = {kind: sorted(str(p) for p in Path("/dev").glob(kind + "*")
                          if p.name[len(kind):].isdigit()) for kind in ("video", "media")}
    missing = [name for name, value in packages.items() if not value["installed"]]
    blockers = []
    if not nodes["video"] or not nodes["media"]:
        blockers.append("Camera media/video devices are not exposed on this boot; expected on protected Golden.")
    if missing:
        blockers.append("Missing desktop prerequisites: " + ", ".join(missing))
    inactive = [name for name, value in services.items() if value != "active"]
    if inactive:
        blockers.append("Desktop services inactive or unavailable: " + ", ".join(inactive))
    return {"schema": "sp11-camera-desktop-status-v1", "camera_opened": False,
            "activation_performed": False, "packages": packages, "services": services,
            "tools": {name: shutil.which(name) for name in ("cam", "gst-launch-1.0", "gst-inspect-1.0", "wpctl")},
            "device_nodes": nodes, "prerequisite_gaps": blockers,
            "rgb_cameras": {
                "rear": {"sensor": rgb_contract["rear"]["sensor"],
                    "capture_fourcc": rgb_contract["rear"]["accepted_v4l2_fourcc"],
                    "offline_real_colorbar_to_nv12": "PASS_UNCALIBRATED_PROTOTYPE",
                    "live_desktop_device": "NOT_VERIFIED",
                    "required_next": rgb_contract["rear"]["required_next"]},
                "front": {"sensor": rgb_contract["front"]["sensor"],
                    "capture_fourcc": rgb_contract["front"]["accepted_v4l2_fourcc"],
                    "offline_synthetic_linear_nv12_scaler": "PASS_SYNTHETIC_ONLY",
                    "real_linear_nv12_or_qc10c_decode": "NOT_VERIFIED",
                    "live_desktop_device": "NOT_VERIFIED",
                    "required_next": rgb_contract["front"]["required_next"]}},
            "rear_front_live_app_switching": "NOT_VERIFIED",
            "application_capture": "NOT_TESTED",
            "assessment": "PREREQUISITES_INCOMPLETE" if blockers else "PREREQUISITES_PRESENT_CAPTURE_UNPROVEN",
            "next_validation": "Rear: calibrated continuous Bayer-to-NV12 and its app endpoint. Front: proven QC10C decode or safe true linear ISP output and its app endpoint. Then validate selectable switching between BOTH; see src/sp11-camera-stack/rgb-desktop-output-contract.json.",
            "ir_illumination": "NOT_AUTHORIZED_BY_THIS_DIAGNOSTIC",
            "authentication": "NOT_IMPLEMENTED_BY_THIS_DIAGNOSTIC"}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = collect()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Desktop camera: " + result["assessment"])
        for gap in result["prerequisite_gaps"]:
            print("- " + gap)
        for position in ("rear", "front"):
            profile = result["rgb_cameras"][position]
            print(f"{position.title()} RGB ({profile['sensor']}): capture {profile['capture_fourcc']}; live app endpoint {profile['live_desktop_device']}.")
        print("Front/rear app switching: NOT_VERIFIED; no camera opened or service started.")
        print("Next: " + result["next_validation"])

if __name__ == "__main__":
    main()
