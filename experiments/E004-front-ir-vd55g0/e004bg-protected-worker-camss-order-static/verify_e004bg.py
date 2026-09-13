#!/usr/bin/env python3
from pathlib import Path
import json,sys

d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004bg VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_WINDOWS_WORKER_ORDER_EXPOSES_CAMSS_SECURE_STOP_GAP","status")
need(r["windows_outer"]["start"]=="protect -> protected_worker_START","outer start")
need(r["windows_outer"]["stop"]=="protected_worker_STOP -> unprotect","outer stop")
need(r["windows_worker_static"]["start"]==[
    "IFE_START","initial_packet_replay_IFE_optional_SFE_CSID","CSID_START"],"worker start")
need(r["windows_worker_static"]["stop"]==["CSID_STOP","IFE_STOP"],"worker stop")
need(r["linux_x1e_graph"]==["sensor","CSIPHY","CSID","VFE","video"],"Linux graph")
need(r["linux_normal_stream_walk"]["start"]==["VFE","CSID","CSIPHY","sensor"],"Linux start")
need(r["linux_normal_stream_walk"]["stop"]==["VFE","CSID","CSIPHY","sensor"],"Linux stop")
p=r["parity"]
need(p["protected_block_start_direction_compatible"] is True,"start compatibility")
need(p["protected_block_stop_direction_compatible"] is False,"stop mismatch")
need(p["csiphy_local_protect_is_too_late_for_windows_outer_invariant"] is True,"hook consequence")
need(r["physical_csiphy_state_at_protect"]=="unobserved","CSIPHY overclaim")
need(r["production_hook_selected"] is False,"hook overclaim")
need(r["linux_secure_runtime_executed"] is False,"runtime")
need(r["qcomtee_loaded"] is False,"QCOMTEE")
need(r["camera_memory_reassigned"] is False,"memory")

w=(d/"evidence/WINDOWS-PROTECTED-WORKER.txt").read_text(errors="replace")
for s in (
    "CAMERA_DEVICE_IOCTL_DEVICE_START",
    "ife%d Start_cmd",
    "Initial packet %d to ife%d",
    "Initial packet %d to csid%d",
    "CSID%d Start_cmd",
    "CAMERA_DEVICE_IOCTL_DEVICE_STOP",
    "CSID Core0 stop cmd",
    "IFE Core%x  stop cmd",
):
    need(s in w,"Windows worker evidence missing "+s)

l=(d/"evidence/LINUX-CAMSS-STREAM-WALK.txt").read_text(errors="replace")
for s in (
    "media_create_pad_link(&camss->csiphy[i].subdev.entity",
    "&camss->csid[j].subdev.entity",
    "MSM_CSID_PAD_FIRST_SRC + j",
    "struct v4l2_subdev *vfe = &camss->vfe[k].line[j].subdev;",
    "v4l2_subdev_call(subdev, video, s_stream, 1)",
    "v4l2_subdev_call(subdev, video, s_stream, 0)",
):
    need(s in l,"Linux stream evidence missing "+s)

o=(d/"evidence/ORDER-DERIVATION.txt").read_text(errors="replace")
for s in (
    "normal start call order=VFE -> CSID -> CSIPHY -> sensor",
    "normal stop call order=VFE -> CSID -> CSIPHY -> sensor",
    "worker_start=IFE start -> replay initial config packets to IFE/CSID -> CSID start",
    "worker_stop=CSID stop -> IFE stop",
    "csiphy-local protect is too late",
    "physical-CSIPHY register state at protect instant remains unobserved",
):
    need(s in o,"derivation missing "+s)

print("E004bg VERIFY: PASS")
print(" - Windows protected worker starts IFE before CSID")
print(" - Windows protected worker stops CSID before IFE")
print(" - Linux CAMSS normal walk starts and stops VFE before CSID")
print(" - CSIPHY-local protection would occur after protected VFE/CSID start")
print(" - secure parity therefore needs a pipeline-level bracket and Windows-order stop path")
print(" - physical CSIPHY timing remains intentionally unresolved")
