#!/usr/bin/env python3
"""E004ns rear CSID1 IPP source-only ARM64 build acceptance / negative tests.

No camera access, no kernel install, no Golden reboot, no frame/pixel data.
"""
from __future__ import annotations
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
BASE=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss")
BUILD=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e004ns-rear-csid-ipp-build/camss")
PRIOR=REPO/"experiments/E004-front-ir-vd55g0/e004nr-rear-pix-kernel-source-profile"
ORACLE=REPO/"experiments/E004-front-ir-vd55g0/e004nq-rear-physical-mmio-5phase"
CSID_SHA="9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90"
FRONT_SHA="788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91"
INC_SHA="f145ec03045bf4e8a177011d52a44d6f56f9aff9fbd90fd4a6fc89200cf3f40f"
MODULE_SHA="8f500bc15226cec583272c5b202b38ff1f9fb2d7a56a7d9b7de6370711ccfc90"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def verify(oracle,csid,macros,source):
    assert oracle["schema"]=="sp11-e004nq-rear-windows-physical-dd-slash-p-5phase-scalar-v1"
    assert oracle["phases"]==["IDLE","LIVE1","POST","LIVE2","POST2"]
    assert len(oracle["region_stats"])==6
    assert all(b["idle_all_sentinel"] and b["POST_vs_IDLE_dword_differences"]==0
               and b["POST2_vs_IDLE_dword_differences"]==0 for b in oracle["region_stats"])
    assert oracle["Linux_rear_native_4k_ISP_optical_frame_proven"] is False
    assert csid["schema"]=="sp11-e004ns-windows-rear-csid1-ipp-whitelisted-config-scalar-v1"
    assert len(csid["phases"])==2
    a,b=csid["phases"]
    assert [a["phase"],b["phase"]]==["LIVE1","LIVE2"]
    assert a["csid1"]==b["csid1"]
    assert (a["csid0_wrapper_config"],a["csid1_wrapper_config"],
            a["csid0_ipp_cfg0"])==("0x00000001","0x00000101","0x00000000")
    assert (b["csid0_wrapper_config"],b["csid1_wrapper_config"],
            b["csid0_ipp_cfg0"])==("0x00000001","0x00000101","0x00000000")
    m=macros
    expect={
        "RX_CFG0":0x10232103,"RX_CFG1":1,"IPP_CFG0":0x802b2000,
        "IPP_CFG1":0x7241,"IPP_HCROP":0x0fdf0000,"IPP_VCROP":0x08ed0000,
        "IPP_FORMAT_CFG0":0x1f,"IPP_FORMAT_CFG1":0x08ee0fe0,
        "PARITY_ZERO0":0,"PARITY_ZERO1":0x02000000,
        "EPOCH_IRQ_CFG":0x00130013,"EPOCH_PATTERN":0xffffffff,
        "FRAME_DROP_PATTERN":0,"FRAME_DROP_PERIOD":1,
        "PIX_DROP_PATTERN":0,"PIX_DROP_PERIOD":1,
        "LINE_DROP_PATTERN":0,"LINE_DROP_PERIOD":1,
        "IRQ_SUBSAMPLE_PATTERN":1,"IRQ_SUBSAMPLE_PERIOD":0,
        "RX_IRQ_MASK":0x019fb800,"BUF_DONE_IRQ_MASK":0x1ffff,
        "IPP_IRQ_MASK":0x3cbc601c,"TOP_IRQ_MASK":1,
        "WRAPPER_CFG0":0x101,"LANE_ASSIGN":0x3210,
    }
    assert m==expect
    fields={
        "top_irq_mask":"TOP_IRQ_MASK",
        "buffer_done_irq_mask":"BUF_DONE_IRQ_MASK",
        "rx_irq_mask":"RX_IRQ_MASK",
        "ipp_irq_mask":"IPP_IRQ_MASK",
        "rx_cfg0":"RX_CFG0",
        "rx_cfg1":"RX_CFG1",
        "ipp_cfg0":"IPP_CFG0",
        "ipp_ctrl":None,
        "ipp_cfg1":"IPP_CFG1",
        "ipp_parity_zero0":"PARITY_ZERO0",
        "ipp_parity_zero1":"PARITY_ZERO1",
        "ipp_epoch_irq_cfg":"EPOCH_IRQ_CFG",
        "ipp_epoch0_subsample":"EPOCH_PATTERN",
        "ipp_epoch1_subsample":"EPOCH_PATTERN",
        "ipp_hcrop":"IPP_HCROP",
        "ipp_vcrop":"IPP_VCROP",
        "ipp_pix_drop_pattern":"PIX_DROP_PATTERN",
        "ipp_pix_drop_period":"PIX_DROP_PERIOD",
        "ipp_line_drop_pattern":"LINE_DROP_PATTERN",
        "ipp_line_drop_period":"LINE_DROP_PERIOD",
        "ipp_frame_drop_pattern":"FRAME_DROP_PATTERN",
        "ipp_frame_drop_period":"FRAME_DROP_PERIOD",
        "ipp_irq_subsample_pattern":"IRQ_SUBSAMPLE_PATTERN",
        "ipp_irq_subsample_period":"IRQ_SUBSAMPLE_PERIOD",
        "ipp_format_measure_cfg0":"IPP_FORMAT_CFG0",
        "ipp_format_measure_cfg1":"IPP_FORMAT_CFG1",
    }
    assert set(a["csid1"])==set(fields)
    for phase,real in zip(oracle["live_physical_config"],(a,b)):
        assert phase["phase"]==real["phase"]
        assert phase["csid"][0]["ipp_path_enabled"] is False
        assert phase["csid"][1]["ipp_path_enabled"] is True
        for name,const in fields.items():
            target=1 if const is None else m[const]
            assert int(real["csid1"][name],16)==target, (phase["phase"],name)
        assert phase["wrapper"][1]["config"]==real["csid1_wrapper_config"]
        assert phase["csid"][1]["rx_cfg0"]==real["csid1"]["rx_cfg0"]
        assert phase["csid"][1]["ipp_cfg0"]==real["csid1"]["ipp_cfg0"]
        assert (phase["csid"][1]["x_start"],phase["csid"][1]["x_end"],
                phase["csid"][1]["y_start"],phase["csid"][1]["y_end"]) == (0,4063,0,2285)
        assert phase["vfe"][0]["enabled_clients"]==[]
    assert ((m["RX_CFG0"] & 0xf)+1)==4
    assert (m["RX_CFG0"]>>4)&0xffff==m["LANE_ASSIGN"]
    assert (m["RX_CFG0"]>>20)&0xf==2   # OEM PHY_NUM_SEL1+1
    assert (m["RX_CFG0"]>>24)&1==0      # D-PHY
    assert (m["RX_CFG0"]>>28)&1==1      # rear TPG selector also 1, not just front C-PHY
    assert ((m["IPP_CFG0"]>>16)&0x3f)==0x2b
    assert ((m["IPP_CFG0"]>>12)&0xf)==2
    assert m["IPP_CFG0"]>>31==1
    assert m["IPP_HCROP"]>>16==4063 and m["IPP_HCROP"]&0xffff==0
    assert m["IPP_VCROP"]>>16==2285 and m["IPP_VCROP"]&0xffff==0
    assert m["IPP_FORMAT_CFG1"]==(2286<<16 | 4064)
    # Distinct rear E004nq value: existing front packet0 writes 0 at +0x330.
    assert m["PARITY_ZERO1"]==0x02000000
    assert "val |= 1U << CSI2_RX_CFG0_TPG_NUM_SEL;" in source
    assert "format->data_type != 0x2b" in source
    assert "rx_cfg0 != CSID_E004NS_REAR_RX_CFG0" in source
    assert "format->data_type << IPP_CFG0_DATA_TYPE" in source
    assert "csid->phy.phy_sel != CSID_PHY_SEL_DPHY" in source
    assert "csid->phy.lane_cnt != 4" in source
    assert "csid->phy.lane_assign != CSID_E004NS_REAR_LANE_ASSIGN" in source
    assert "MEDIA_BUS_FMT_SGRBG10_1X10" in source
    assert "fmt->width == 4076 && fmt->height == 2806" in source
    for symbol in ("CSID_IPP_HCROP","CSID_IPP_VCROP",
                   "CSID_IPP_FORMAT_MEASURE_CFG0",
                   "CSID_IPP_FORMAT_MEASURE_CFG1",
                   "CSID_IPP_SP11_PARITY_ZERO1",
                   "CSID_TOP_IO_PATH_CFG0(csid->id)"):
        assert symbol in source
    assert source.count("return -EOPNOTSUPP;")==1
    assert "static int __used\ncsid_e004ns_rear_ipp_runtime_authorization(" in source


def build_verification():
    original_c=(BASE/"camss.c").read_text()
    original_s=(BASE/"camss-csid-680.c").read_text()
    staged_c=(BUILD/"camss.c").read_text()
    staged_s=(BUILD/"camss-csid-680.c").read_text()
    cinclude='#include "camss-e004nr-rear-profile.inc"\n\n'
    sinclude='#include "camss-csid-e004ns-rear-ipp.inc"\n\n'
    assert sha(BASE/"camss.c")==FRONT_SHA
    assert sha(BASE/"camss-csid-680.c")==CSID_SHA
    assert sha(HERE/"camss-csid-e004ns-rear-ipp.inc")==INC_SHA
    assert staged_c.count(cinclude)==1 and staged_c.replace(cinclude,"")==original_c
    assert staged_s.count(sinclude)==1 and staged_s.replace(sinclude,"")==original_s
    assert (BUILD/"camss-e004nr-rear-profile.inc").read_bytes()==(
        PRIOR/"camss-e004nr-rear-profile.inc").read_bytes()
    assert (BUILD/"camss-csid-e004ns-rear-ipp.inc").read_bytes()==(
        HERE/"camss-csid-e004ns-rear-ipp.inc").read_bytes()
    assert sha(BUILD/"qcom-camss.ko")==MODULE_SHA
    meta=json.loads((HERE/"BUILD-RESULT.json").read_text())
    assert meta["schema"]=="sp11-e004ns-rear-only-csid1-ipp-offline-kernel-build-scalar-v1"
    assert meta["isolated_arm64_module_sha256"]==MODULE_SHA
    assert meta["original_integrated_front_CAMSS_source_byte_preserved"] is True
    assert meta["original_integrated_front_CSID680_source_byte_preserved"] is True
    assert meta["new_rear_csid_runtime_authorization_unconditionally_denied"] is True
    assert meta["new_rear_runtime_call_sites_added"] is False
    assert meta["new_module_installed_or_loaded"] is False
    assert meta["linux_native_rear_4k_hardware_isp_optical_frame_proven"] is False
    assert not any(x in (BUILD/"E004NS-CAMSS-BUILD.log").read_text()
                   for x in ("warning:","error:"))
    sym=subprocess.check_output(["aarch64-linux-gnu-nm","-a",
                                 str(BUILD/"qcom-camss.ko")],text=True)
    for name in meta["isolated_arm64_module_new_rear_symbols"]:
        assert name in sym
    for name in ("csid_e004ns_rear_ipp_prepare",
                 "csid_e004ns_rear_ipp_enable",
                 "csid_e004ns_rear_ipp_runtime_authorization"):
        # Isolated body retains intended entry points but NO active call sites.
        assert name+"(" not in original_s
        assert name+"(" not in staged_s
    vm=subprocess.check_output(["modinfo","-F","vermagic",
                                str(BUILD/"qcom-camss.ko")],text=True).strip()
    assert vm=="7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64"
    return True


if __name__=="__main__":
    oracle=json.loads((ORACLE/"RESULT.json").read_text())
    csid=json.loads((HERE/"CSID1-RESULT.json").read_text())
    source=(HERE/"camss-csid-e004ns-rear-ipp.inc").read_text()
    macros={
        name:int(v,0) for name,v in
        re.findall(r"^#define\s+CSID_E004NS_REAR_([A-Z0-9_]+)\s+(0x[0-9a-fA-F]+|\d+)U\s*$",
                   source,re.M)
    }
    verify(oracle,csid,macros,source)
    build_verification()
    # Negative cases reject wrong face/PHY, wrong crop/format, substituted
    # front TPG and +0x330, disagreement between independent OEM rear runs.
    mutants=(
       ("lost_tpg_selector", lambda o,c,m:m.__setitem__("RX_CFG0",0x00232103)),
       ("front_phy_word",lambda o,c,m:m.__setitem__("RX_CFG0",0x11300000)),
       ("wrong_lane_order",lambda o,c,m:m.__setitem__("LANE_ASSIGN",0x0123)),
       ("front_crop_x",lambda o,c,m:m.__setitem__("IPP_HCROP",0x0eff0000)),
       ("front_crop_y",lambda o,c,m:m.__setitem__("IPP_VCROP",0x086f0000)),
       ("front_second_parity",lambda o,c,m:m.__setitem__("PARITY_ZERO1",0)),
       ("front_dimensions",lambda o,c,m:m.__setitem__("IPP_FORMAT_CFG1",0x08700f00)),
       ("wrong_DT",lambda o,c,m:m.__setitem__("IPP_CFG0",0x802a2000)),
       ("bad_irq_mask",lambda o,c,m:m.__setitem__("IPP_IRQ_MASK",0x3c1c7004)),
       ("bad_epoch",lambda o,c,m:m.__setitem__("EPOCH_IRQ_CFG",0x00120013)),
       ("mismatched_second_capture",lambda o,c,m:c["phases"][1]["csid1"].__setitem__("ipp_parity_zero1","0x00000000")),
       ("rear_csid0_assumed",lambda o,c,m:o["live_physical_config"][0]["csid"][0].__setitem__("ipp_path_enabled",True)),
       ("rear_vfe0_assumed",lambda o,c,m:o["live_physical_config"][1]["vfe"][0].__setitem__("enabled_clients",[{"wm":0}])),
       ("wrong_wrapper",lambda o,c,m:c["phases"][0].__setitem__("csid1_wrapper_config","0x00000001")),
       ("wrong_config_mode",lambda o,c,m:c["phases"][0]["csid1"].__setitem__("ipp_ctrl","0x00000000")),
       ("unrestored_post",lambda o,c,m:o["region_stats"][0].__setitem__("POST_vs_IDLE_dword_differences",1)),
       ("false_linux_hw_proof",lambda o,c,m:o.__setitem__("Linux_rear_native_4k_ISP_optical_frame_proven",True)),
    )
    for name,mut in mutants:
        o,c,m=copy.deepcopy(oracle),copy.deepcopy(csid),dict(macros)
        mut(o,c,m)
        try:verify(o,c,m,source)
        except (AssertionError,KeyError):
            continue
        raise SystemExit("E004NS_FAIL_OPEN_MUTANT: "+name)
    print("PASS_E004NS_26_PHYSICAL_CSID1_CONFIG_DWORDS_MATCH_TWO_WINDOWS_REAR_LIVE_"
          "ARM64_COMPILABLE_REAR_ONLY_CSID1_IPP_RECEIVER_TPG_CROP_PARITY_"
          "17_NEGATIVE_TESTS_NO_RUNTIME_CALLER_GOLDEN_UNTOUCHED")
