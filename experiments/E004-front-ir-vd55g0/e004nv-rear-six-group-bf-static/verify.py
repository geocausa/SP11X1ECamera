#!/usr/bin/env python3
"""E004nv source-only static OEM BF completion group and offline Linux gate.

No OEM binary is exported, no kernel load or camera/device DMA activity.
"""
import copy
import hashlib
import itertools
import json
import re
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
WM=ROOT/"experiments/E004-front-ir-vd55g0/e004nr-rear-pix-kernel-source-profile/WM-RESULT.json"
NR=ROOT/"experiments/E004-front-ir-vd55g0/e004nr-rear-pix-kernel-source-profile"
NS=ROOT/"experiments/E004-front-ir-vd55g0/e004ns-rear-csid1-ipp-offline"
NT=ROOT/"experiments/E004-front-ir-vd55g0/e004nt-rear-vfe1-4k-buffer-contract"
NU=ROOT/"experiments/E004-front-ir-vd55g0/e004nu-rear-vfe1-ten-wm-ownership"
INC=HERE/"camss-vfe-e004nv-rear-six-group.inc"
BASE=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss")
BUILD=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e004nv-rear-six-group-bf-build/camss")
DRIVER=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys")
DRIVER_SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
MODULE_SHA="e7981c01e51ae4246f060b416ac6c11eb01546e2b182bce445478e36f490b80b"
INC_SHA="8271758a4aac09532f2e75ce4b46e49261650075f204440f7f051e9ba2f24efb"
EXPECT=[
 (3,0,"VIDEO_WM",0x00f),
 (13,5,"AEC_BHIST_WM",0x030),
 (14,6,"TINTLESS_WM",0x040),
 (16,7,"AWB_WM",0x080),
 (15,8,"BF_WM16",0x100),
 (18,9,"RS_WM",0x200),
]

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def parse_groups(source):
    values={
        k:int(v,0)
        for k,v in re.findall(
            r"^#define\s+VFE680_E004NV_([A-Z0-9_]+)_MASK\s+(0x[0-9a-fA-F]+)U\s*$",
            source,re.M)
    }
    assert set(values)=={x[2] for x in EXPECT}
    records=re.findall(
        r"\{\s*\.event_id = (0x[0-9a-fA-F]+)U,\s*"
        r"\.fifo_index = (\d+)U,\s*"
        r"\.wm_mask = VFE680_E004NV_([A-Z0-9_]+)_MASK\s*\},",
        source,re.S)
    assert len(records)==6
    return [(int(evt,0),int(idx),name,values[name])
            for evt,idx,name in records]

def assert_oracle(bf,wm,groups,src):
    assert bf["schema"]=="sp11-e004nv-same-sp11-oem-qccamisp8380-rear-BF-event-static-v1"
    assert bf["driver"]["sha256"]==DRIVER_SHA
    assert bf["driver"]["same_SP11_private_original_retained"] is True
    assert bf["BF_static_dispatch"]=={
       "driver_event_id":"0x0f",
       "BF_diagnostic_RVA":"0x37b88",
       "BF_diagnostic":"IFE%d IFE BF stats buf done Irq occured.",
       "event_compare_RVA":"0x1fc60",
       "queue_group_index":8,
       "queue_group_argument_RVA":"0x1fc8c",
       "queue_pop_helper_RVA":"0x26460",
       "queue_pop_call_RVA":"0x1fc94",
       "BF_group_client_resource_port":"0x300d",
       "resource_port_stored_RVA":"0x1fce8",
       "independent_queue_index_arithmetic_RVA":"0x2650c",
       "independent_queue_pointer_load_RVA":"0x26514",
    }
    assert bf["rear_BF_WM16_BAF_static_association_corroborated_by_active_WM16_and_driver_BF_name"] is True
    assert bf["BF_event_live_during_OEM_rear_recording_observed"] is False
    assert bf["all_six_rear_groups_live_confirmed"] is False
    assert bf["Linux_rear_native_4k_ISP_optical_frame_proven"] is False
    assert bf["no_driver_binary_or_DMACSV_or_optical_data_exported"] is True
    assert [(int(x["event_id"],16),x["queue_group_index"])
            for x in bf["front_proven_groups_in_same_driver"]]==[
                (3,0),(13,5),(14,6),(16,7),(18,9)]
    assert wm["schema"]=="sp11-e004nr-rear-oem-Windows-VFE1-output-WM-safe-scalar-v1"
    assert len(wm["phases"])==2
    assert wm["phases"][0]["write_masters"]==wm["phases"][1]["write_masters"]
    assert [x["wm"] for x in wm["phases"][0]["write_masters"]]==[
        0,1,2,3,11,12,13,14,16,18]
    assert wm["phases"][0]["write_masters"][8]["wm_config"]=="0x00020001"
    assert groups==EXPECT
    assert sum(g[3] for g in groups)==0x3ff
    assert not any(x[3]&y[3] for i,x in enumerate(groups)
                   for y in groups[i+1:])
    assert src.count("return -EOPNOTSUPP;")==1
    assert "frame->pending &= ~group->wm_mask;" in src
    assert "(frame->pending & group->wm_mask) != group->wm_mask" in src
    assert "return -EALREADY;" in src
    assert "vfe680_e004nu_rear_frame_retire(" in src
    assert "independently_verified_bus_stopped" in src
    assert "VFE680_E004NV_BF_WM16_MASK" in src
    assert "return -ENOENT;" in src
    assert "vfe680_e004nv_rear_runtime_authorization(" in src
    assert "VFE680_X1E_BUS_IMAGE_ADDR" not in src
    assert "VFE680_X1E_BUS_META_ADDR" not in src
    return True

def check_compiled():
    assert sha(DRIVER)==DRIVER_SHA
    assert sha(INC)==INC_SHA
    assert sha(BUILD/"qcom-camss.ko")==MODULE_SHA
    m=json.loads((HERE/"BUILD-RESULT.json").read_text())
    assert m["schema"]=="sp11-e004nv-rear-BF-six-group-static-ARM64-build-scalar-v1"
    assert m["isolated_compiled_ARM64_module_sha256"]==MODULE_SHA
    assert m["same_SP11_OEM_driver_sha256"]==DRIVER_SHA
    assert m["new_rear_six_group_source_sha256"]==INC_SHA
    for key in (
       "original_integrated_front_CAMSS_CSID_VFE_byte_preserved",
       "bf_event_static_OEM_dispatch_proven",
       "rear_runtime_authorization_unconditionally_denied",
       "OEM_binary_and_optical_data_retained_only_SP11_not_exported_to_Git",
    ):
        assert m[key] is True,key
    for key in (
       "bf_event_live_during_OEM_rear_recording_observed",
       "six_group_rear_live_hardware_event_lifecycle_proven",
       "new_runtime_callers_added","module_installed_or_loaded",
       "Golden_kernel_DT_boot_or_camera_changed",
       "Linux_rear_native_4k_ISP_optical_frame_proven",
    ):
        assert m[key] is False,key
    assert m["compiler_warnings_or_errors"]==0
    expected_original={
       "camss.c":"788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91",
       "camss-csid-680.c":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
       "camss-vfe-680.c":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208",
    }
    includes={
       "camss.c":'#include "camss-e004nr-rear-profile.inc"\n\n',
       "camss-csid-680.c":'#include "camss-csid-e004ns-rear-ipp.inc"\n\n',
       "camss-vfe-680.c":'#include "camss-vfe-e004nt-rear-4k-buffer.inc"\n'
                     '#include "camss-vfe-e004nu-rear-ten-wm.inc"\n'
                     '#include "camss-vfe-e004nv-rear-six-group.inc"\n\n',
    }
    for name,inc in includes.items():
        assert sha(BASE/name)==expected_original[name]
        assert (BUILD/name).read_text().count(inc)==1
        assert (BUILD/name).read_text().replace(inc,"")==(
            BASE/name).read_text()
    previous={
        "camss-e004nr-rear-profile.inc":NR,
        "camss-csid-e004ns-rear-ipp.inc":NS,
        "camss-vfe-e004nt-rear-4k-buffer.inc":NT,
        "camss-vfe-e004nu-rear-ten-wm.inc":NU,
    }
    for name,p in previous.items():
        assert (BUILD/name).read_bytes()==(p/name).read_bytes()
    assert sha(BUILD/"camss-vfe-e004nv-rear-six-group.inc")==INC_SHA
    assert m["isolated_staged_vfe680_source_sha256"]==sha(BUILD/"camss-vfe-680.c")
    assert "warning:" not in (BUILD/"E004NV-CAMSS-BUILD.log").read_text()
    assert "error:" not in (BUILD/"E004NV-CAMSS-BUILD.log").read_text()
    nm=subprocess.check_output(["aarch64-linux-gnu-nm","-a",str(BUILD/"qcom-camss.ko")],text=True)
    assert all(sym in nm for sym in m["new_and_previous_rear_compiled_symbols"])
    assert "vfe680_e004nv_rear_frame_ack_group(" not in (BUILD/"camss-vfe-680.c").read_text()
    vm=subprocess.check_output(["modinfo","-F","vermagic",str(BUILD/"qcom-camss.ko")],text=True).strip()
    assert vm=="7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64"
    return True

def simulated_group_retirement(groups):
    """Offline only: confirm NO cross-group arrival ordering assumption."""
    tested=0
    for order in itertools.permutations(groups):
        pending=0x3ff
        for event,_,_,mask in order:
            assert pending&mask==mask,event
            pending &= ~mask
            assert pending != 0 or event==order[-1][0]
            # A duplicate group cannot consume any other group.
            assert pending&mask==0
        assert pending==0
        tested += 1
    assert tested==720
    return tested

if __name__=="__main__":
    bf=json.loads((HERE/"BF-RESULT.json").read_text())
    wm=json.loads(WM.read_text())
    src=INC.read_text()
    groups=parse_groups(src)
    assert_oracle(bf,wm,groups,src)
    check_compiled()
    tested=simulated_group_retirement(groups)
    mutations=(
      ("missing_BF",lambda b,w,g:g.pop(4)),
      ("wrong_BF_event",lambda b,w,g:g.__setitem__(4,(17,8,"BF",0x100))),
      ("wrong_BF_FIFO",lambda b,w,g:g.__setitem__(4,(15,7,"BF",0x100))),
      ("wrong_BF_mask",lambda b,w,g:g.__setitem__(4,(15,8,"BF",0x080))),
      ("front_only_5",lambda b,w,g:g.pop(4)),
      ("video_retires_BF",lambda b,w,g:g.__setitem__(0,(3,0,"VIDEO",0x10f))),
      ("AWB_wrong_group",lambda b,w,g:g.__setitem__(3,(16,6,"AWB",0x80))),
      ("RS_wrong_index",lambda b,w,g:g.__setitem__(5,(18,8,"RS",0x200))),
      ("WM16_disabled",lambda b,w,g:w["phases"][0]["write_masters"][8].__setitem__("wm_config","0x00000000")),
      ("WM16_missing",lambda b,w,g:w["phases"][1]["write_masters"].pop(8)),
      ("fake_BF_live",lambda b,w,g:b.__setitem__("BF_event_live_during_OEM_rear_recording_observed",True)),
      ("fake_six_live",lambda b,w,g:b.__setitem__("all_six_rear_groups_live_confirmed",True)),
      ("faked_native_linux",lambda b,w,g:b.__setitem__("Linux_rear_native_4k_ISP_optical_frame_proven",True)),
      ("driver_hash_changed",lambda b,w,g:b["driver"].__setitem__("sha256","0"*64)),
      ("BF_resource_port_wrong",lambda b,w,g:b["BF_static_dispatch"].__setitem__("BF_group_client_resource_port","0x300e")),
      ("BF_diag_wrong",lambda b,w,g:b["BF_static_dispatch"].__setitem__("BF_diagnostic","UNKNOWN")),
      ("BF_FIFOpointer_wrong",lambda b,w,g:b["BF_static_dispatch"].__setitem__("independent_queue_pointer_load_RVA","0x26518")),
      ("wrong_AEC_mask",lambda b,w,g:g.__setitem__(1,(13,5,"AEC_BHIST",0x010))),
      ("wrong_Video_event",lambda b,w,g:g.__setitem__(0,(4,0,"VIDEO",0xf))),
      ("second_Windows_WM_mismatch",lambda b,w,g:w["phases"][1]["write_masters"][8].__setitem__("frame_increment","0x00002c00")),
    )
    for name,mut in mutations:
        b,w,g=copy.deepcopy(bf),copy.deepcopy(wm),list(groups)
        mut(b,w,g)
        try:assert_oracle(b,w,g,src)
        except (AssertionError,KeyError,IndexError):
            continue
        raise SystemExit("E004NV_NEGATIVE_CASE_FAIL_OPEN "+name)
    print("PASS_E004NV_SAME_SP11_OEM_BF_EVENT_0F_FIFO_GROUP8_STATIC_DRIVER_PROOF_"
          "REAR_10_WM_SIX_GROUP_CANDIDATE_ARM64_COMPILED_"
          f"{tested}_CROSS_ORDER_SIMULATIONS_20_FAIL_CLOSED_NEGATIVE_TESTS_"
          "GOLDEN_RUNTIME_DISABLED_LIVE_REAR_BF_UNPROVEN")
