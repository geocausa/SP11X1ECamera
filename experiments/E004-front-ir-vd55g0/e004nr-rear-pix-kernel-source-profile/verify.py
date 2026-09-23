#!/usr/bin/env python3
"""E004nr Linux-rear native ISP SOURCE-ONLY profile acceptance, no hardware.

Checks real E004nq two Windows physical captures, strict WM nonpointer
whitelist, separately compiled Qualcomm CAMSS module, original front source
preservation, and an unconditional rear hardware-runtime denial.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
KERNEL = Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src")
ORIGINAL = KERNEL / "drivers/media/platform/qcom/camss/camss.c"
BUILD = Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e004nr-rear-pix-profile-build-v2/camss")
ORACLE = ROOT / "experiments/E004-front-ir-vd55g0/e004nq-rear-physical-mmio-5phase"
EXPECT_BASE = "788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91"
EXPECT_HEADER = "4c3e38cd2da75d758fcf595ae58cbc49122c96ca6f9b12e70d2692da9c06198d"
EXPECT_MODULE = "5bbb584e6ce01b20cc7fb24b0ee5201409c493be3d9ef5e72420ba91d0e7e9fc"
EXPECT_STAGE = "03e3138e6ac10725e0a5bdfda4128344d0d3c75e904268fb1fbf0aacb8514c01"


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def macros(text: str) -> dict[str, int]:
    return {
        name: int(val, 0)
        for name, val in re.findall(
            r"^#define\s+CAMSS_E004NR_REAR_([A-Z0-9_]+)\s+(0x[0-9a-fA-F]+|\d+)U\s*$",
            text, re.M
        )
    }


def verified_profile(phys: dict, windows: dict, wm: dict, constants: dict) -> None:
    assert phys["schema"] == "sp11-e004nq-rear-windows-physical-dd-slash-p-5phase-scalar-v1"
    assert phys["phases"] == ["IDLE", "LIVE1", "POST", "LIVE2", "POST2"]
    assert len(phys["region_stats"]) == 6
    assert all(
        block["idle_all_sentinel"] is True
        and block["POST_vs_IDLE_dword_differences"] == 0
        and block["POST2_vs_IDLE_dword_differences"] == 0
        for block in phys["region_stats"]
    )
    assert phys["Linux_rear_native_4k_ISP_optical_frame_proven"] is False
    assert windows["Windows_rear_two_distinct_successful_StartAsync_and_StopAsync_phases"] is True
    assert windows["Windows_rear_first_live_3840x2160_frame_handles"] == 861
    assert windows["Windows_rear_second_live_3840x2160_frame_handles"] == 338
    assert windows["Linux_rear_native_4k_ISP_hardware_frame_proven"] is False
    assert wm["schema"] == "sp11-e004nr-rear-oem-Windows-VFE1-output-WM-safe-scalar-v1"
    assert len(wm["phases"]) == 2
    expected_wm_ids = (0, 1, 2, 3, 11, 12, 13, 14, 16, 18)
    allowed = frozenset(
        ("wm", "wm_config", "frame_increment", "image_geometry", "image_cfg1",
         "wm_stride", "packer_config", "bandwidth_limit",
         "irq_subsample_period", "irq_subsample_pattern", "frame_drop_period",
         "frame_drop_pattern", "metadata_config", "output_mode_config",
         "statistics_ctrl", "secondary_ctrl", "lossy_threshold0",
         "lossy_threshold1")
    )
    p1, p2 = wm["phases"]
    assert p1["phase"] == "LIVE1" and p2["phase"] == "LIVE2"
    assert [entry["wm"] for entry in p1["write_masters"]] == list(expected_wm_ids)
    assert p1["write_masters"] == p2["write_masters"]
    assert all(set(entry) == allowed for entry in p1["write_masters"])
    c = constants
    expected_constants = {
        "SENSOR_WIDTH": 4076,
        "SENSOR_HEIGHT": 2806,
        "IPP_CROP_WIDTH": 4064,
        "IPP_CROP_HEIGHT": 2286,
        "FULL_WIDTH": 3840,
        "FULL_Y_HEIGHT": 2160,
        "FULL_C_HEIGHT": 1080,
        "FULL_WM_STRIDE": 5120,
        "FULL_PACKER_CFG": 0x0b,
        "FULL_Y_FRAME_INCR": 0x00a9d000,
        "FULL_C_FRAME_INCR": 0x00559000,
        "FULL_META_CFG": 0x800,
        "FULL_Y_MODE": 0x23,
        "FULL_C_MODE": 0x33,
        "DS4_FRAME_INCR": 0x0010e000,
        "DS16_FRAME_INCR": 0x00018000,
        "RX_CFG0": 0x10232103,
        "IPP_CFG0": 0x802b2000,
        "IPP_CFG1": 0x00007241,
        "IPP_HCROP": 0x0fdf0000,
        "IPP_VCROP": 0x08ed0000,
        "IPP_FORMAT_MEASURE": 0x08ee0fe0,
    }
    assert c == expected_constants
    for phase in phys["live_physical_config"]:
        assert phase["phase"] in ("LIVE1", "LIVE2")
        assert [wrapper["config"] for wrapper in phase["wrapper"]] == [
            "0x00000001", "0x00000101", "0x00000001"]
        assert [wrapper["output_ife_enable"] for wrapper in phase["wrapper"]] == [
            False, True, False]
        csid0, csid1 = phase["csid"]
        assert csid0["ipp_path_enabled"] is False
        assert csid1["instance"] == 1 and csid1["ipp_path_enabled"] is True
        assert int(csid1["rx_cfg0"], 16) == c["RX_CFG0"]
        assert (c["RX_CFG0"] & 0xF) + 1 == 4
        assert ((c["RX_CFG0"] >> 24) & 1) == 0  # DPHY
        assert ((c["RX_CFG0"] >> 20) & 0xF) == 2  # CSIPHY1 OEM encoding
        assert int(csid1["ipp_cfg0"], 16) == c["IPP_CFG0"]
        assert int(csid1["ipp_cfg1"], 16) == c["IPP_CFG1"]
        assert int(csid1["hcrop"], 16) == c["IPP_HCROP"]
        assert int(csid1["vcrop"], 16) == c["IPP_VCROP"]
        assert int(csid1["format_measure"], 16) == c["IPP_FORMAT_MEASURE"]
        assert (csid1["x_start"], csid1["y_start"]) == (0, 0)
        assert (csid1["measured_width"], csid1["measured_height"]) == (
            c["IPP_CROP_WIDTH"], c["IPP_CROP_HEIGHT"])
        vfe0, vfe1 = phase["vfe"]
        assert vfe0["instance"] == 0 and vfe0["enabled_clients"] == []
        assert vfe1["instance"] == 1
        assert [client["wm"] for client in vfe1["enabled_clients"]] == list(expected_wm_ids)
        all_clients = p1["write_masters"]
        for i, name, height, frame_incr in (
            (0, "FULL_Y", c["FULL_Y_HEIGHT"], c["FULL_Y_FRAME_INCR"]),
            (1, "FULL_C", c["FULL_C_HEIGHT"], c["FULL_C_FRAME_INCR"]),
        ):
            r = vfe1["enabled_clients"][i]
            w = all_clients[i]
            assert (r["name"], r["width"], r["height"]) == (
                name, c["FULL_WIDTH"], height)
            assert r["stride"] == c["FULL_WM_STRIDE"]
            assert int(r["packer_config"], 16) == c["FULL_PACKER_CFG"]
            assert int(w["frame_increment"], 16) == frame_incr
            assert int(w["wm_stride"], 16) == c["FULL_WM_STRIDE"]
            assert int(w["metadata_config"], 16) == c["FULL_META_CFG"]
            assert int(w["output_mode_config"], 16) == c["FULL_Y_MODE" if i == 0 else "FULL_C_MODE"]
        for i, inc in ((2, c["DS4_FRAME_INCR"]), (3, c["DS16_FRAME_INCR"])):
            assert int(all_clients[i]["frame_increment"], 16) == inc


def source_and_build_integrity():
    original = ORIGINAL.read_text()
    hdr = (HERE / "camss-e004nr-rear-profile.inc").read_text()
    staged = (BUILD / "camss.c").read_text()
    assert sha(ORIGINAL) == EXPECT_BASE
    assert sha(HERE / "camss-e004nr-rear-profile.inc") == EXPECT_HEADER
    assert sha(BUILD / "camss.c") == EXPECT_STAGE
    assert staged.count('#include "camss-e004nr-rear-profile.inc"\n\n') == 1
    assert staged.replace('#include "camss-e004nr-rear-profile.inc"\n\n', "") == original
    assert (BUILD / "camss-e004nr-rear-profile.inc").read_bytes() == (
        HERE / "camss-e004nr-rear-profile.inc").read_bytes()
    assert sha(BUILD / "qcom-camss.ko") == EXPECT_MODULE
    manifest=json.loads((HERE / "BUILD-RESULT.json").read_text())
    assert manifest["schema"]=="sp11-e004nr-isolated-aarch64-camss-rear-profile-build-scalar-v1"
    assert manifest["isolated_compiled_aarch64_qcom_camss_module_sha256"]==EXPECT_MODULE
    assert manifest["unmodified_front_camss_c_byte_identity_after_removing_one_include"] is True
    assert manifest["compiler_warnings_or_errors"]==0
    assert manifest["module_installed_or_loaded"] is False
    assert manifest["rear_runtime_authorization_returns_EOPNOTSUPP"] is True
    assert manifest["linux_rear_native_4k_isp_optical_frame_proven"] is False
    assert "static int __used\ncamss_e004nr_rear_pix_graph_preflight(" in hdr
    assert "static int __used\ncamss_e004nr_rear_pix_runtime_authorization(" in hdr
    assert "return -EOPNOTSUPP;" in hdr
    assert ".linux_rear_4k_hardware_authorized = false," in hdr
    assert "MEDIA_BUS_FMT_SGRBG10_1X10" in hdr
    assert "CSID_PHY_SEL_DPHY" in hdr
    assert "camss_x1e_pix_link(&csid->pads[MSM_CSID_PAD_SINK]" in hdr
    assert "camss_x1e_pix_link(&vfe->line[VFE_LINE_PIX].pads[MSM_VFE_PAD_SINK]" in hdr
    assert "camss_e004nr_rear_pix_runtime_authorization(" not in staged
    assert "camss_e004nr_rear_pix_graph_preflight(" not in staged
    assert "module_param_named(e004nr" not in staged
    assert "camss_x1e_pix_runtime_arm" in staged
    assert (BUILD / "E004NR-CAMSS-BUILD.log").exists()
    out = subprocess.check_output(
        ["aarch64-linux-gnu-nm", "-a", str(BUILD / "qcom-camss.ko")], text=True)
    for symbol in (
        "camss_e004nr_rear_pix_graph_preflight",
        "camss_e004nr_rear_pix_runtime_authorization",
        "camss_e004nr_rear_oem_profile",
    ):
        assert symbol in out
    vermagic = subprocess.check_output(
        ["modinfo", "-F", "vermagic", str(BUILD / "qcom-camss.ko")], text=True).strip()
    assert vermagic == (
        "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64")
    return True


if __name__ == "__main__":
    phys=json.loads((ORACLE / "RESULT.json").read_text())
    win=json.loads((ORACLE / "WINDOWS-RESULT.json").read_text())
    wm=json.loads((HERE / "WM-RESULT.json").read_text())
    hdr=(HERE / "camss-e004nr-rear-profile.inc").read_text()
    const=macros(hdr)
    verified_profile(phys, win, wm, const)
    source_and_build_integrity()
    mutations=(
        ("route_wrong_instance", lambda p,w,m,c:
         p["live_physical_config"][0]["wrapper"][1].__setitem__("output_ife_enable",False)),
        ("bad_rear_phy", lambda p,w,m,c:
         p["live_physical_config"][0]["csid"][1].__setitem__("rx_cfg0","0x11300000")),
        ("front_sensor_crop",lambda p,w,m,c:c.__setitem__("IPP_CROP_WIDTH",3840)),
        ("wrong_wm_stride",lambda p,w,m,c:c.__setitem__("FULL_WM_STRIDE",3840)),
        ("wrong_wm_increment",lambda p,w,m,c:c.__setitem__("FULL_Y_FRAME_INCR",0x004f2000)),
        ("live_2_wm_conflict",lambda p,w,m,c:
         m["phases"][1]["write_masters"][1].__setitem__("frame_increment","0x00558000")),
        ("pointer_leak",lambda p,w,m,c:
         [phase["write_masters"][0].__setitem__("image_addr","0xDEADBEEF")
          for phase in m["phases"]]),
        ("wrong_wm_meta",lambda p,w,m,c:
         m["phases"][0]["write_masters"][0].__setitem__("metadata_config","0x00000400")),
        ("wrong_wm_mode",lambda p,w,m,c:
         m["phases"][0]["write_masters"][1].__setitem__("output_mode_config","0x00000023")),
        ("false_vfe0_active",lambda p,w,m,c:
         p["live_physical_config"][0]["vfe"][0].__setitem__("enabled_clients",[{"wm":0}])),
        ("false_sustained_second_capture",lambda p,w,m,c:
         w.__setitem__("Windows_rear_second_live_3840x2160_frame_handles",0)),
        ("post_not_idle",lambda p,w,m,c:
         p["region_stats"][0].__setitem__("POST2_vs_IDLE_dword_differences",1)),
        ("false_native_linux_hw_proof",lambda p,w,m,c:
         p.__setitem__("Linux_rear_native_4k_ISP_optical_frame_proven",True)),
        ("bogus_pack_config",lambda p,w,m,c:
         c.__setitem__("FULL_PACKER_CFG",0x0a)),
        ("wrong_aux_frame_increment",lambda p,w,m,c:
         m["phases"][0]["write_masters"][2].__setitem__("frame_increment","0x00084000")),
    )
    for name,mut in mutations:
        p,w,m,c=copy.deepcopy(phys),copy.deepcopy(win),copy.deepcopy(wm),copy.deepcopy(const)
        mut(p,w,m,c)
        try:
            verified_profile(p,w,m,c)
        except (AssertionError,KeyError):
            continue
        raise SystemExit("E004NR_MUTATION_INCORRECTLY_ACCEPTED: "+name)
    print(
        "PASS_E004NR_E004nq_REAR_CSI1_VFE1_4K_WM0_1_CFG_GEOMETRY_STRIDE_FRAMEINCR_"
        "TWO_WINDOWS_PHASES_15_NEGATIVE_TESTS_"
        "ACTUAL_COMPILED_CAMSS_SOURCE_FRONT_UNMODIFIED_REAR_RUNTIME_DENIED")
