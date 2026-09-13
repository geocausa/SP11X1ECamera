#!/usr/bin/env python3
from pathlib import Path
import json,sys,re

d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004bd VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_WINDOWS_DYNAMIC_SECURE_LANE_MASK_MATCHES_QUALCOMM_LINUX","status")
w=r["windows_dynamic"]
need(w["enable"]=={"lane_dispatch_command":"0x2e","lane_mask":"0x8","protect":1},"Windows enable")
need(w["disable"]=={"lane_dispatch_command":"0x2f","lane_mask":"0x8","protect":0},"Windows disable")
need(w["exact_mask_same_both_sides"] is True,"same mask")
t=r["windows_topology"]
need(t["csiphy_index"]==0 and t["phy"]=="DPHY","topology")
need(t["num_data_lanes"]==1 and t["data_lane_position"]==0,"lane topology")
q=r["qualcomm_linux_crosscheck"]
need(q["active_data_lane_bitmask"]=="0x1","active lane bit")
need(q["dphy_secure_shift"]==3,"DPHY shift")
need(q["computed_secure_lane_mask"]=="0x8","computed mask")
need(q["calls_symbol"]=="qcom_scm_camera_protect_phy_lanes","SCM symbol")
need(q["exact_windows_mask_match"] is True,"exact match")
need(r["local_linux_7_1_5"]["camera_protect_phy_lanes_wrapper"] is False,"upstream gap")
need(r["local_linux_7_1_5"]["runtime_call_executed"] is False,"runtime")
need(r["secure_csi_state_changed_linux"] is False,"Linux secure CSI state")

dyn=(d/"evidence/WINDOWS-DYNAMIC-LANE-PROTECTION.txt").read_text(errors="replace")
for s in (
    "command=0x2e lane_mask=0x8",
    "lane_mask=0x8 protect=1",
    "command=0x2f lane_mask=0x8",
    "lane_mask=0x8 protect=0",
):
    need(s in dyn,"dynamic evidence missing "+s)

top=(d/"evidence/WINDOWS-IR-TOPOLOGY.txt").read_text(errors="replace")
for s in ("csiphy_index=0","num_data_lanes=1","data_lane_position_linux=0","raw_receiver_lane_mask=0x81"):
    need(s in top,"topology evidence missing "+s)

src=(d/"evidence/QUALCOMM-LINUX-SECURE-CSIPHY.txt").read_text(errors="replace")
for s in (
    "#define CAM_CSIPHY_MAX_CPHY_LANES            3",
    "lane_assign_bitmask |= (1 << (lane_assign & 0xF));",
    "csiphy_dev->soc_info.index * bit_offset_bet_phys_in_cp_ctrl",
    "(!csiphy_dev->csiphy_info[index].csiphy_3phase)",
    "qcom_scm_camera_protect_phy_lanes(protect,",
):
    need(s in src,"Qualcomm source missing "+s)

# Mechanical parity math for SP11 Windows-proven topology.
lane_assign_bitmask=1 << t["data_lane_position"]
mask=lane_assign_bitmask << 3
need(mask==8,"mechanical mask math")
need(f"0x{mask:x}"==w["enable"]["lane_mask"],"mechanical Windows match")

gap=(d/"evidence/CURRENT-LINUX-SCM-GAP.txt").read_text(errors="replace")
need("generic SCM implementation is present" in gap,"generic SCM evidence")
need("qcom_scm_camera_protect_phy_lanes" not in "\n".join(
    line for line in gap.splitlines()
    if not line.startswith("camera_protect_phy_lanes symbol search:")
), "unexpected local wrapper")

print("E004bd VERIFY: PASS")
print(" - Windows dynamically protects Surface IR with lane mask 0x8 and unprotects the same 0x8")
print(" - Windows-proven topology is CSIPHY0 D-PHY, one data lane at receiver position 0")
print(" - Qualcomm Linux secure-CSIPHY math independently computes 0x8")
print(" - public camera stack calls qcom_scm_camera_protect_phy_lanes(protect, mask)")
print(" - local 7.1.5 still lacks that camera-specific wrapper; no Linux secure call executed")
