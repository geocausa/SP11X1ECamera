#!/usr/bin/env python3
"""SP11 camera architecture contract: enforce honest Windows->Linux port boundaries.

Read-only static docs/OEM-INF/scalar checks. No camera/driver, binary export,
image data or live hardware access. Run before future port-slice changes.
"""
from pathlib import Path
import json
import re
import yaml

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/"docs/CAMERA-STACK-PORT-MAP.md"
STATE=ROOT/"state/project.yaml"
INF=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/"
         "surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/surfacecamavs8380.inf")
E=ROOT/"experiments/E004-front-ir-vd55g0"
NX=E/"e004nx-rear4k-no-kd-baseline/RESULT.json"
NY=E/"e004ny-rear4k-live-control/RESULT.json"
NV=E/"e004nv-rear-six-group-bf-static/BF-RESULT.json"

def check():
    doc=DOC.read_text()
    state=yaml.safe_load(STATE.read_text())
    inf=INF.read_text(encoding="utf-16")
    nx=json.loads(NX.read_text())
    ny=json.loads(NY.read_text())
    nv=json.loads(NV.read_text())

    # Architecture is not a promise to load Windows code on Linux or copy AI.
    must={
      "# SP11 camera stack — Windows behaviour to clean native Linux port map",
      "Windows services, proprietary driver code, Studio Effects and AI image enhancements are not parity requirements",
      "**P — physically observed/proven",
      "**S — same-SP11 OEM static evidence",
      "**H — working hypothesis / unverified link",
      "**D — chosen Linux design",
      "~~~mermaid\nflowchart TB",
      "~~~mermaid\nstateDiagram-v2",
      "**“Integrated into the driver” means integrating deterministic, safety-critical hardware behaviour",
      "**hard CSID1/VFE1 lease and stop safety remain kernel-owned**",
      "per-frame stats→decision→sensor/ISP update",
      "Do not promote S or H to P",
      "A **registered DLL** is not proof",
      "WM16 CFG0 at VFE+0x1E00",
      "WM16 ADDR_STATUS0 at VFE+0x1E70",
      "**source-only compiled, runtime DENIED",
      "**NOT a live rear BF event**",
      "**NOT proof of live BF or Linux native ISP**",
      "Do not bypass blocked debugger safety checks",
      "What remains unproven",
      "No Windows-specific runtime service is intrinsically required",
    }
    for phrase in must:
        assert phrase in doc, f"Missing critical boundary: {phrase}"
    assert doc.count("~~~mermaid")==2
    assert doc.count("~~~")==4
    for section in ("Windows components and decisions", "Linux port ownership",
                    "native camera/session state machine", "Permanent evidence pointers"):
        assert section in doc, f"Missing architecture section {section}"
    for n in range(7):
        assert re.search(rf"\*\*L{n}:",doc), f"Missing owner L{n}"
    for component in ("surfacecamavs8380.sys","QcDeviceMFT8380.dll",
                      "qccamplatform8380.sys","qccamisp8380.sys",
                      "IMX681","OV13858","VD55G0","libcamera","V4L2",
                      "RT-CDM","IOMMU","WM16","CSID1","VFE1","CSID0","VFE0"):
        assert component in doc, f"Unmapped camera component: {component}"

    # Verify OEM AVStream pins and separately registered Device MFT, but NEVER
    # claim an installed CLSID proves the DLL loaded in a particular session.
    for directive in ('AddService=QCCamAvs', 'Pin0','Pin1','Pin2',
                      'BackSensor.RefGuid','FrontSensor.RefGuid',
                      'QcDeviceMFT8380.dll', 'DMFTRegistration'):
        assert directive.lower() in inf.lower(), f"OEM INF evidence changed: {directive}"
    assert "Registration alone" not in doc or "does **not** imply" in doc
    assert "Registration does **not** imply" in doc
    assert "actual session role UNKNOWN" in doc

    # Two physical rear Windows live snapshots have enabled WM16, but a live
    # BF event is not an established observation and cannot be promoted.
    assert nv["BF_static_dispatch"]["driver_event_id"]=="0x0f"
    assert nv["BF_static_dispatch"]["queue_group_index"]==8
    assert nv["BF_event_live_during_OEM_rear_recording_observed"] is False
    assert state["latest_windows_rear_BF_verified_static_callchain"]["Windows_live_rear_BF_event_observed"] is False
    assert state["latest_windows_rear_BF_verified_static_callchain"]["per_device_selected_mode_during_rear_live_4k_confirmed"] is False
    assert state["latest_windows_rear_BF_group_and_linux_six_group_source"]["new_rear_six_group_runtime_authorization_unconditionally_denied"] is True
    assert state["latest_windows_rear_BF_group_and_linux_six_group_source"]["Linux_rear_native_4k_ISP_optical_frame_proven"] is False
    assert nx["kd_attached_during_session"] is False
    assert ny["KD_breakpoint_attached_during_this_session"] is False
    assert nx["total_valid_4k_frame_handles"]==731
    assert ny["total_valid_4k_frame_handles"]==2306
    assert nx["BF_event_0x0f_live_during_rear_capture_observed"] is False
    assert ny["BF_event_0x0f_live_recording_observed"] is False

    # All *relative* Markdown file links in the pinned map must resolve.
    links=re.findall(r"\]\(([^)]+)\)",doc)
    assert len(links)>=10
    for link in links:
        if link.startswith(("http:","https:","#")):
            continue
        assert (DOC.parent/link).resolve().is_file(), f"Dead architecture evidence link: {link}"

    # Machine-readable handoff points at the SAME map and doesn't silently
    # classify runtime-denied rear source as a completed Linux 4K ISP stream.
    route=state["camera_stack_architecture_port_map"]
    assert route["document"]=="docs/CAMERA-STACK-PORT-MAP.md"
    assert route["status"]=="PINNED_WINDOWS_TO_NATIVE_LINUX_FUNCTIONAL_SLICES"
    assert route["native_rear_4k_isp_optical_frame_proven"] is False
    assert route["windows_live_BF_event_observed"] is False
    assert route["native_linux_windows_services_or_AI_required"] is False
    assert route["hardware_critical_session_safety_in_kernel"] is True
    assert route["optional_AE_AWB_AF_policy_can_live_in_open_userspace"] is True
    assert route["linux_slices"]==[f"L{n}" for n in range(7)]
    print(f"PASS_SP11_CAMERA_WINDOWS_LINUX_ARCHITECTURE_{len(links)}_LINKS_"
          "AVSTREAM_PROFILE_INVENTORY_L0_TO_L6_STATIC_VS_LIVE_"
          "BF_NOT_PROMOTED_RUNTIME_REAR_DENIED_GOLDEN_UNTOUCHED")

if __name__=="__main__":
    check()
