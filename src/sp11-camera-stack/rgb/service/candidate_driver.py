# SPDX-License-Identifier: MIT
"""Guarded front/rear RGBSession hardware adapter acceptance CLI.

Must only run in a fresh source-pinned disposable SP11 camera candidate,
AFTER its separate boot/driver/manifest/root-only/virtual-device preflight.
The single-use owner policy refuses Golden or a missing armed boot token.
This does not install, reboot, illuminate IR or invoke Linux system sleep.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import time

from candidate_owner import CandidateOwner
from rgb_device_backend import RGBDeviceBackend, SPECS
from session import RGBSession, SessionRejected


def run_trial(candidate: str) -> dict:
    if not re.fullmatch(r"e004[a-z]{2}",candidate):
        raise SessionRejected("FRESH_EXPERIMENT_IDENTITY_REQUIRED")
    root=Path("/var/lib/sp11-camera-"+candidate)
    output=root/"output"
    discovery=json.loads((output/"UNIFIED.json").read_text())
    owner=CandidateOwner(candidate,staged=root,discovery=discovery)
    session=RGBSession(RGBDeviceBackend(discovery,owner))
    evidence={"status":"INCOMPLETE_FAIL_CLOSED","camera_order":[],
              "candidate_boot_id":owner.boot,"run_kind":"GUARDED_EXCLUSIVE_RGB_SESSION",
              "linux_os_system_sleep":False,"ir_illumination_enabled":False,
              "session_policy_live_integrated":True,"camera_results":{}}
    try:
        for camera in ("front","rear"):
            spec=SPECS[camera]
            before=(output/(camera.upper()+"-BEFORE-MEDIA.txt"))
            before.write_text(owner.run(("media-ctl","-d",owner.media,"-p"),timeout=7.0))
            session.open(camera)
            if session.active!=camera:
                raise SessionRejected("ACTIVE_CAMERA_NOT_CONFIGURED")
            # The physical source publisher owns the source FD and both
            # named virtual nodes persist; the unprivileged client opens only
            # the named endpoint corresponding to the selected real camera.
            virtual=spec["virtual"]
            if not Path(virtual).exists():
                raise SessionRejected("NAMED_VIRTUAL_CAMERA_MISSING")
            ready=False
            deadline=time.monotonic()+12.
            while time.monotonic()<deadline:
                if not session.backend.publisher_running(camera):
                    raise SessionRejected("PUBLISHER_DIED_DURING_VIRTUAL_READINESS")
                try:
                    text=subprocess.run(("v4l2-ctl","-d",virtual,"--get-fmt-video"),
                        check=True,text=True,stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,timeout=2.).stdout
                except (subprocess.SubprocessError,OSError):
                    text=""
                if ("Width/Height" in text and spec["virt_width_height"] in text
                        and "NV12" in text):
                    ready=True
                    break
                time.sleep(0.08)
            if not ready:
                raise SessionRejected("LIVE_RGB_VIRTUAL_FORMAT_NOT_READY")
            first_inv=session.backend.invocation[camera]
            client=root/"client_lifecycle.py"
            app=Path("/usr/local/lib/sp11-camera-"+candidate+"/client.py")
            if not client.is_file() or not app.is_file():
                raise SessionRejected("PINNED_UID1000_APP_OR_LIFECYCLE_MISSING")
            stdout=output/(camera.upper()+"-CLIENT-CYCLE.json")
            stderr=output/(camera.upper()+"-CLIENT-CYCLE-ERROR.txt")
            # Client lifecycle tool is itself a pinned, root-private
            # candidate asset, verified by the external boot preflight.
            with stdout.open("x") as fp,stderr.open("x") as err:
                subprocess.run(("python3",str(client),"--camera",camera,
                    "--client",str(app),"--output",str(output)),
                    check=True,stdout=fp,stderr=err,timeout=105.,
                    close_fds=True)
            client_record=json.loads(stdout.read_text())
            if (client_record["status"]!="PASS" or
                    client_record["normal_open_count"]!=3 or
                    client_record["forced_app_crash_count"]!=1 or
                    len(client_record["phases"])!=4 or
                    not all(p["process_group_gone"] for p in client_record["phases"])):
                raise SessionRejected("REAL_UID1000_APP_REOPEN_CRASH_RECOVERY_FAILED")
            if session.backend.invocation[camera]!=first_inv or not session.backend.publisher_running(camera):
                raise SessionRejected("PUBLISHER_RESTARTED_DURING_APP_RECOVERY")
            session.stop()
            after=(output/(camera.upper()+"-AFTER-NEUTRAL-MEDIA.txt"))
            after.write_text(owner.run(("media-ctl","-d",owner.media,"-p"),timeout=7.0))
            if session.active is not None or session.backend.route_phase()!="neutral":
                raise SessionRejected("POST_CAMERA_SWITCH_GRAPH_NOT_NEUTRAL")
            evidence["camera_order"].append(camera)
            evidence["camera_results"][camera]={
                "publisher_invocation":first_inv,
                "normal_uid1000_app_opens":3,
                "independent_120_complete_frames_per_normal_app":True,
                "intentional_client_kill_and_recovery":True,
                "same_publisher_invocation":True,
                "owner_verified_streamoff_143_and_clean_exit":True,
                "neutral_after_reader_and_publisher_stop":True,
                "source_output":("front1080p_NV12" if camera=="front" else "rear4k_NV12"),
            }
        session.close()
        if session.completed_stops!=2 or session.poisoned:
            raise SessionRejected("SESSION_STOPS_OR_CONTROLLER_STATE_INVALID")
        evidence["full_native_graph_neutral_after_both"]=True
        evidence["status"]="PASS_GUARDED_LIVE_RGB_SESSION_CONTROLLER_WITH_UID1000_REOPEN_RECOVERY"
        return evidence
    finally:
        # Never guess rollback after an ambiguous publisher or link write.
        # The outer one-shot's watchdog/automatic Golden fallback owns
        # power/boot recovery on error; do not perform another graph write.
        (output/"RGB-SESSION-CONTROLLER-RESULT.json").write_text(
            json.dumps(evidence,indent=2,sort_keys=True)+"\n")
        owner.close()


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--candidate",required=True,
                        help="single-use root-private camera candidate identity")
    args=parser.parse_args()
    if os.geteuid()!=0:
        raise SystemExit("GUARDED_ROOT_ONLY_SESSION_REQUIRED")
    print(json.dumps(run_trial(args.candidate),sort_keys=True),flush=True)
