#!/usr/bin/env python3
from pathlib import Path
import json,sys

d=Path(__file__).resolve().parent
def need(x,m):
    if not x:
        print("E004bc VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_WINDOWS_TRUSTLET_IS_IUM_NOT_QTEE_TA","status")
w=r["windows_worker"]
need(w["service_type"]=="SecureCompanion","service type")
need(w["trustlet_identity"]==4096,"trustlet identity")
need(w["qsee_qtee_ta_image"] is False,"TA-image overclaim")
need(w["trustlet_identity_is_qtee_uid"] is False,"UID overclaim")
need(r["linux_qcomtee"]["golden_config_enabled"] is False,"Golden qcomtee")
need(r["linux_qcomtee"]["platform_device_present"] is True,"qcomtee platform device")
need(r["linux_qcomtee"]["arbitrary_windows_pe_loader"] is False,"PE loader")
need(r["linux_qseecom"]["upstream_base_apps"]==["qcom.tz.uefisecapp"],"QSEE base app")
need(r["linux_qseecom"]["arbitrary_ta_loader"] is False,"QSEE loader")
need(r["microsoft_linux_firmware"]["camera_ta_filename_found"] is False,"firmware inventory")
need(r["linux_primitives"]["qcom_scm_assign_mem"] is True,"assign_mem")
need(r["runtime_executed"] is False and r["qcomtee_loaded"] is False,"runtime boundary")

wn=(d/"evidence/WINDOWS-SECURECOMPANION-NATURE.txt").read_text(errors="replace")
for s in ("PE32+ executable for MS Windows", "Name: IumSdk.dll", "Symbol: MapSecureIo",
          "Symbol: AssignMemoryToSocDomain", "ServiceType = SecureCompanion", "TrustletIdentity = 4096"):
    need(s in wn,"Windows evidence missing "+s)

qt=(d/"evidence/LINUX-QCOMTEE-MODEL.txt").read_text(errors="replace")
for s in ("its loaded Trusted Applications", "qcomtee_object_get_client_env",
          "qcomtee_object_get_service", "QCOMTEE_CLIENT_ENV_OPEN"):
    need(s in qt,"QCOMTEE evidence missing "+s)

qs=(d/"evidence/LINUX-QSEECOM-MODEL.txt").read_text(errors="replace")
for s in ("assuming the app has already been loaded", '"qcom.tz.uefisecapp"', "qcom_scm_qseecom_app_get_id"):
    need(s in qs,"QSEECOM evidence missing "+s)

g=(d/"evidence/GOLDEN-TEE-STATE.txt").read_text(errors="replace")
for s in ("# CONFIG_QCOMTEE is not set","/sys/bus/platform/devices/qcomtee present","qcom_qseecom.uefisecapp.0"):
    need(s in g,"Golden evidence missing "+s)

p=(d/"evidence/LINUX-CAMERA-DOMAIN-PRIMITIVES.txt").read_text(errors="replace")
for s in ("QCOM_SCM_VMID_CP_CAMERA","QCOM_SCM_VMID_CP_CAMERA_PREVIEW","qcom_scm_assign_mem"):
    need(s in p,"camera primitive evidence missing "+s)

print("E004bc VERIFY: PASS")
print(" - Windows SecureISP worker is a SecureCompanion/IUM PE, not a QSEE/QTEE TA image")
print(" - Linux QCOMTEE and upstream QSEECOM target already-loaded trusted services")
print(" - Golden QSEECOM is active; QCOMTEE is present as an unbound platform device")
print(" - Microsoft Linux firmware tree has no obvious camera TA file")
print(" - Linux already exposes generic camera-domain memory assignment primitives")
print(" - no Linux secure-camera runtime occurred")
