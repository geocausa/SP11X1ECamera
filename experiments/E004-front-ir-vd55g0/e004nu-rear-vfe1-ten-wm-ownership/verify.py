#!/usr/bin/env python3
"""E004nu source-only rear ten-WM BUS source and candidate ownership gate.

Do not load/reboot camera or allocate a DMA buffer. No image data included.
"""
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
WM=ROOT/"experiments/E004-front-ir-vd55g0/e004nr-rear-pix-kernel-source-profile/WM-RESULT.json"
SOURCE=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss")
BUILD=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e004nu-rear-ten-wm-ownership-build/camss")
INC=HERE/"camss-vfe-e004nu-rear-ten-wm.inc"
IDS=[0,1,2,3,11,12,13,14,16,18]
FIELDS={
    "wm_config":"cfg",
    "frame_increment":"frame_incr",
    "image_geometry":"image_cfg0",
    "image_cfg1":"image_cfg1",
    "wm_stride":"image_cfg2",
    "packer_config":"packer",
    "bandwidth_limit":"bw_limit",
    "irq_subsample_period":"irq_subsample_period",
    "irq_subsample_pattern":"irq_subsample_pattern",
    "frame_drop_period":"frame_drop_period",
    "frame_drop_pattern":"frame_drop_pattern",
    "metadata_config":"meta_cfg",
    "output_mode_config":"mode_cfg",
    "statistics_ctrl":"stats_ctrl",
    "secondary_ctrl":"ctrl2",
    "lossy_threshold0":"loss0",
    "lossy_threshold1":"loss1",
}
REGS=[
 "VFE680_X1E_BUS_CFG", "VFE680_X1E_BUS_FRAME_INCR",
 "VFE680_X1E_BUS_IMAGE_CFG0", "VFE680_X1E_BUS_IMAGE_CFG1",
 "VFE680_X1E_BUS_IMAGE_CFG2", "VFE680_X1E_BUS_PACKER_CFG",
 "VFE680_X1E_BUS_BW_LIMIT", "VFE680_X1E_BUS_IRQ_SUBSAMPLE_PERIOD",
 "VFE680_X1E_BUS_IRQ_SUBSAMPLE_PATTERN", "VFE680_X1E_BUS_FRAMEDROP_PERIOD",
 "VFE680_X1E_BUS_FRAMEDROP_PATTERN", "VFE680_X1E_BUS_META_CFG",
 "VFE680_X1E_BUS_MODE_CFG", "VFE680_X1E_BUS_STATS_CTRL",
 "VFE680_X1E_BUS_CTRL_2", "VFE680_X1E_BUS_LOSSY_THRESH0",
 "VFE680_X1E_BUS_LOSSY_THRESH1",
]
ORIG={
 "camss.c":"788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91",
 "camss-csid-680.c":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
 "camss-vfe-680.c":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208",
}
INC_SHA="ccbd1415e2e2c94e366b6c3c2ba636f272c868edbc7fef556e2a1b2b5b4c4f23"
MODULE_SHA="dc93bd4093b121e55e5f2f9a1e2fc4d48aaaaa361bc44fdef399d431e4b8a1a0"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def parse_contract(src):
    match=re.search(
      r"vfe680_e004nu_rear_wm_contract\[VFE680_E004NU_REAR_CLIENTS\] __used = \{\n(.*?)\n\};",
      src,re.S)
    assert match,"rear WM contract missing"
    rows=[]
    for line in match.group(1).splitlines():
        m=re.fullmatch(r"\s*\{ \.wm = (\d+), (.*?) \},",line)
        assert m,("malformed row",line)
        w={"wm":int(m.group(1))}
        for item in m.group(2).split(", "):
            field,val=re.fullmatch(r"\.([a-z0-9_]+) = (0x[0-9a-fA-F]+|\d+)U",item).groups()
            assert field not in w
            w[field]=int(val,0)
        rows.append(w)
    return rows

def check_sources(wm,rows,src):
    assert wm["schema"]=="sp11-e004nr-rear-oem-Windows-VFE1-output-WM-safe-scalar-v1"
    assert len(wm["phases"])==2
    a,b=wm["phases"]
    assert [a["phase"],b["phase"]]==["LIVE1","LIVE2"]
    assert a["write_masters"]==b["write_masters"]
    assert [x["wm"] for x in a["write_masters"]]==IDS
    assert [x["wm"] for x in rows]==IDS
    assert len(rows)==10
    assert len(FIELDS)==17
    assert len(REGS)==17
    for actual,expected in zip(rows,a["write_masters"]):
        assert set(actual)=={"wm",*FIELDS.values()}
        assert set(expected)=={"wm",*FIELDS.keys()}
        for original,field in FIELDS.items():
            assert actual[field]==int(expected[original],16), (actual["wm"],field)
    assert rows[8]["wm"]==16 and rows[8]["cfg"]==0x20001
    assert rows[8]["frame_incr"]==0x2d00
    assert rows[8]["image_cfg0"]==0x00190004
    assert rows[8]["image_cfg2"]==0x20
    assert rows[0]["frame_incr"]==0xa9d000
    assert rows[1]["frame_incr"]==0x559000
    assert rows[0]["image_cfg2"]==rows[1]["image_cfg2"]==5120
    assert rows[0]["meta_cfg"]==rows[1]["meta_cfg"]==0x800
    assert rows[0]["mode_cfg"]==0x23 and rows[1]["mode_cfg"]==0x33
    for name in REGS:
        assert "cfg + "+name+");" in src,("unprogrammed field",name)
    assert "readl_relaxed(cfg + VFE680_X1E_BUS_CFG)" in src
    assert "return -EBUSY;" in src
    assert "c->cfg & ~VFE_BUS_WRITE_CLIENT_CFG_EN" in src
    assert "writel_relaxed(c->cfg & ~VFE_BUS_WRITE_CLIENT_CFG_EN," in src
    assert "VFE680_X1E_BUS_IMAGE_ADDR" not in src
    assert "VFE680_X1E_BUS_META_ADDR" not in src
    assert "VFE680_E004NU_REAR_CLIENTS_MASK\t0x03ffU" in src
    assert "vfe680_e004nu_rear_wm_contract[8].wm !=" in src
    assert "VFE680_E004NU_REAR_WM16_BAF" in src
    assert "frame->pending &= ~BIT(i);" in src
    assert "if (!(frame->pending & BIT(i)))" in src
    assert "return -EALREADY;" in src
    assert "if (frame->pending || !independently_verified_bus_stopped)" in src
    assert "frame->surface->in_flight = false;" in src
    assert "vfe680_e004nt_rear_surface_addrs(vfe, surface, &candidate)" in src
    assert "surface->in_flight = true;" in src
    assert "return -EOPNOTSUPP;" in src
    assert src.count("return -EOPNOTSUPP;")==1
    return True

def check_build():
    m=json.loads((HERE/"BUILD-RESULT.json").read_text())
    assert m["schema"]=="sp11-e004nu-isolated-ten-WM-rear-VFE1-compile-scalar-v1"
    assert m["source_rear_WM_contract_sha256"]==INC_SHA
    assert m["isolated_compiled_ARM64_module_sha256"]==MODULE_SHA
    assert m["source_rear_WM_contract_10_clients_ids"]==IDS
    for key in (
      "source_rear_WM16_BAF_present",
      "source_previous_front_9WM_contract_unchanged",
      "original_CAMSS_CSID_VFE_integrated_sources_byte_preserved",
      "no_rear_BAF_WM16_IRQ_identity_claimed",
      "runtime_authorization_unconditionally_denied",
      "SP11_isolated_compiled_module_not_exported_to_Git",
    ):
        assert m[key] is True,key
    for key in (
      "all_10_completion_sources_proven","no_new_runtime_callers",
      "module_installed_or_loaded","rear_DMA_buffer_actually_allocated",
      "Linux_rear_native_4k_ISP_optical_frame_proven",
      "Golden_kernel_boot_DT_or_camera_state_changed",
    ):
        assert m[key] is (key=="no_new_runtime_callers"),key
    assert m["compiler_warnings_or_errors"]==0
    assert sha(INC)==INC_SHA and sha(BUILD/"qcom-camss.ko")==MODULE_SHA
    includes={
      "camss.c":'#include "camss-e004nr-rear-profile.inc"\n\n',
      "camss-csid-680.c":'#include "camss-csid-e004ns-rear-ipp.inc"\n\n',
      "camss-vfe-680.c":'#include "camss-vfe-e004nt-rear-4k-buffer.inc"\n#include "camss-vfe-e004nu-rear-ten-wm.inc"\n\n',
    }
    for f,inc in includes.items():
        assert sha(SOURCE/f)==ORIG[f]
        staged=(BUILD/f).read_text()
        assert staged.count(inc)==1
        assert staged.replace(inc,"")==(SOURCE/f).read_text()
    assert sha(BUILD/"camss-vfe-e004nu-rear-ten-wm.inc")==INC_SHA
    assert m["staged_vfe680_source_sha256"]==sha(BUILD/"camss-vfe-680.c")
    assert "warning:" not in (BUILD/"E004NU-CAMSS-BUILD.log").read_text()
    assert "error:" not in (BUILD/"E004NU-CAMSS-BUILD.log").read_text()
    nm=subprocess.check_output(["aarch64-linux-gnu-nm","-a",str(BUILD/"qcom-camss.ko")],text=True)
    assert all(symbol in nm for symbol in m["compiled_rear_symbols"])
    vermagic=subprocess.check_output(
       ["modinfo","-F","vermagic",str(BUILD/"qcom-camss.ko")],text=True).strip()
    assert vermagic=="7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64"
    # Other than definitions inside our include, no new external call site.
    assert "vfe680_e004nu_rear_frame_ack_wm(" not in (BUILD/"camss-vfe-680.c").read_text()
    assert "vfe680_e004nu_rear_wm_prepare_disabled(" not in (BUILD/"camss-vfe-680.c").read_text()
    return True

if __name__=="__main__":
    wm=json.loads(WM.read_text())
    src=INC.read_text()
    rows=parse_contract(src)
    check_sources(wm,rows,src)
    check_build()
    negative_cases=(
      ("missing_BAF_16",lambda w,r:r.pop(8)),
      ("wrong_BAF_id",lambda w,r:r[8].__setitem__("wm",15)),
      ("wrong_BAF_CFG",lambda w,r:r[8].__setitem__("cfg",0x10001)),
      ("wrong_BAF_frame_incr",lambda w,r:r[8].__setitem__("frame_incr",0x1800)),
      ("wrong_BAF_geometry",lambda w,r:r[8].__setitem__("image_cfg0",0)),
      ("omitted_AWB",lambda w,r:r.pop(7)),
      ("front_full_Y_incr",lambda w,r:r[0].__setitem__("frame_incr",0x4f2000)),
      ("front_full_C_incr",lambda w,r:r[1].__setitem__("frame_incr",0x279000)),
      ("front_FULL_stride",lambda w,r:r[0].__setitem__("image_cfg2",3584)),
      ("front_FULL_geometry",lambda w,r:r[0].__setitem__("image_cfg0",0x05a00a00)),
      ("wrong_FULL_meta",lambda w,r:r[1].__setitem__("meta_cfg",0x400)),
      ("wrong_FULL_packer",lambda w,r:r[0].__setitem__("packer",0xa)),
      ("second_capture_different_BAF",lambda w,r:w["phases"][1]["write_masters"][8].__setitem__("frame_increment","0x00002e00")),
      ("wrong_wa_order",lambda w,r:r[4].__setitem__("wm",12)),
      ("wrong_stats_RS",lambda w,r:r[9].__setitem__("packer",0x0a)),
      ("missing_aux_DS4",lambda w,r:r.pop(2)),
      ("wrong_drop_pattern",lambda w,r:r[8].__setitem__("frame_drop_pattern",0)),
      ("wrong_stats_ctrl",lambda w,r:r[0].__setitem__("stats_ctrl",1)),
      ("wrong_y_secondary",lambda w,r:r[0].__setitem__("ctrl2",0)),
      ("incorrect_live1_WM0_stride",lambda w,r:w["phases"][0]["write_masters"][0].__setitem__("wm_stride","0x00000e00")),
    )
    for name,mutation in negative_cases:
        w,r=copy.deepcopy(wm),copy.deepcopy(rows)
        mutation(w,r)
        try:check_sources(w,r,src)
        except (AssertionError,IndexError,KeyError):
            pass
        else:raise SystemExit("E004NU_NEGATIVE_TEST_FAILED_OPEN "+name)
    print("PASS_E004NU_10_REAR_VFE1_WM_FULL_DS_STATS_INCLUDING_BAF16_TWO_WINDOWS_LIVE_"
          "ARM64_COMPILED_UNCALLED_BUS_STATIC_AND_COMPLETE_CLIENT_OWNERSHIP_"
          "20_FAIL_CLOSED_NEGATIVE_TESTS_GOLDEN_SAFE")
