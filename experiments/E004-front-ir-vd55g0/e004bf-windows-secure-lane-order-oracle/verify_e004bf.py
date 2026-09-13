#!/usr/bin/env python3
from pathlib import Path
import json,sys

d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004bf VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_WINDOWS_PROTECT_START_STOP_UNPROTECT_ORDER","status")
need(r["dynamic_start"]==[
    "op_0x804","lane_enable_0x2e_mask_0x8",
    "config_secure_camera_protect_1","task_2"],"dynamic start order")
need(r["dynamic_stop"]==[
    "op_0x805","task_3","lane_disable_0x2f_mask_0x8",
    "config_secure_camera_protect_0","op_0x80e"],"dynamic stop order")
need(r["static_labels"]["op_0x804"]=="DeviceStart","DeviceStart label")
need(r["static_labels"]["task_2"]=="ISPTRUSTLET_START","start task label")
need(r["static_labels"]["op_0x805"]=="DeviceStop","DeviceStop label")
need(r["static_labels"]["task_3"]=="ISPTRUSTLET_STOP","stop task label")
need(r["parity_order"]["start"]=="protect_before_protected_worker_start","start rule")
need(r["parity_order"]["stop"]=="protected_worker_stop_before_unprotect","stop rule")
need(r["physical_csiphy_state_at_protect"]=="unobserved","physical timing overclaim")
need(r["new_windows_boot"] is False,"unexpected Windows boot")
need(r["linux_runtime_executed"] is False,"Linux runtime")
need(r["secure_csi_state_changed_linux"] is False,"Linux secure CSI")
need(r["camera_memory_reassigned"] is False,"memory reassignment")
need(r["qcomtee_loaded"] is False,"QCOMTEE")

dyn=(d/"evidence/WINDOWS-DYNAMIC-ORDER.txt").read_text(errors="replace")
for s in (
    "1638 SecureISP_OpDispatcher command=0x804",
    "1639 SecureISP_LaneDispatch command=0x2e mask=0x8",
    "1640 SecureISP_ConfigSecureCamera mask=0x8 protect=1",
    "1641 SecureISP_TaskSend task=2 selector=0",
    "1543 SecureISP_OpDispatcher command=0x805",
    "1544 SecureISP_TaskSend task=3 selector=0",
    "1546 SecureISP_LaneDispatch command=0x2f mask=0x8",
    "1547 SecureISP_ConfigSecureCamera mask=0x8 protect=0",
    "physical_csiphy_programming_state_at_transition=unobserved",
):
    need(s in dyn,"dynamic evidence missing "+s)

st=(d/"evidence/KMD-START-STOP-SEMANTICS.txt").read_text(errors="replace")
for s in (
    '"SecureISPDriver_DeviceStart"',
    "FUN_140004b88(param_1,1",
    "FUN_140004a90(2,0",
    '"SendTask - ISPTRUSTLET_START Succeeded',
    '"SecureISPDriver_DeviceStop"',
    "FUN_140004a90(3,0",
    "FUN_140004b88(param_1,0",
):
    need(s in st,"static label evidence missing "+s)

print("E004bf VERIFY: PASS")
print(" - Windows dynamic start order is protect -> task 2")
print(" - static Windows labels task 2 as protected worker START")
print(" - Windows dynamic stop order is task 3 -> unprotect")
print(" - static Windows labels task 3 as protected worker STOP")
print(" - exact physical CSIPHY state at the transition remains intentionally unresolved")
print(" - no new Windows boot or Linux secure runtime occurred")
