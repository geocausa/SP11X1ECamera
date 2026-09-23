# SPDX-License-Identifier: MIT
"""One guarded opt-in front/rear selector hardware acceptance run.

Candidate-only isolated finite root-private service: authentic UNIX socket
commands activate the maintained RGBSession controller, then independent
ordinary uid1000 applications open front/rear named V4L2 loopback nodes.
On any error the outer one-shot candidate automatically returns Golden;
this script NEVER guesses an unsafe graph rollback or reboots itself.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import time

from rgbctl import command as rgb_command
from sensor_gain_trial import perform as perform_gain_trial


def checked_status(candidate: str, expected: str) -> dict:
    reply = rgb_command(candidate, "status")
    if reply.get("status") != "OK" or reply.get("selected") != expected:
        raise RuntimeError("UNEXPECTED_LIVE_RGB_SELECTOR_STATUS")
    return reply


def wait_output(camera: str, *, deadline_seconds: float = 12.) -> None:
    node, dimensions = (("/dev/video91","1920/1080") if camera=="front"
                        else ("/dev/video90","3840/2160"))
    deadline = time.monotonic() + deadline_seconds
    while time.monotonic() < deadline:
        try:
            info = subprocess.run(("v4l2-ctl","-d",node,"--get-fmt-video"),
                        stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                        text=True,check=True,timeout=2.).stdout
        except (OSError,subprocess.SubprocessError):
            info = ""
        if dimensions in info and "NV12" in info and "Width/Height" in info:
            return
        time.sleep(.08)
    raise RuntimeError("NAMED_RGB_NV12_OUTPUT_FORMAT_NOT_READY")


def service_invocation(candidate: str, camera: str) -> str:
    unit=f"sp11-camera-{candidate}-session@{camera}.service"
    text=subprocess.run(("systemctl","show",unit,"-p","InvocationID","--value"),
               stdout=subprocess.PIPE,stderr=subprocess.PIPE,
               check=True,text=True,timeout=5.).stdout.strip()
    if len(text)!=32 or not all(c in "0123456789abcdef" for c in text):
        raise RuntimeError("INVALID_CAMERA_PUBLISHER_INVOCATION")
    return text


def sensor_control_readback(root:Path,camera:str)->dict:
    """Bounded READ-ONLY sensor V4L2 query. Does not write registers."""
    meta=json.loads((root/"output/UNIFIED.json").read_text())
    node=meta["front_sensor_device" if camera=="front" else "rear_sensor_device"]
    if not node.startswith("/dev/v4l-subdev") or not node[15:].isdigit():
        raise RuntimeError("UNEXPECTED_SENSOR_DEVICE_NODE")
    names=("exposure","analogue_gain","digital_gain")
    result={"device_kind":"native_v4l2_sensor_subdevice","read_only":True,
            "controls":{},"hardware_registers_written":False}
    for name in names:
        try:
            cmd=subprocess.run(("v4l2-ctl","-d",node,"--get-ctrl",name),
                 stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,
                 timeout=3.,check=False)
            result["controls"][name]={"exit_code":cmd.returncode,
                        "text":cmd.stdout.strip()[:120] if cmd.returncode==0
                               else "QUERY_UNAVAILABLE"}
        except (OSError,subprocess.SubprocessError):
            result["controls"][name]={"exit_code":None,"text":"QUERY_UNAVAILABLE"}
    return result


def scene_probe(root:Path,camera:str,*,stage:str="DAYLIGHT")->dict:
    """Independent UID1000 app reads virtual RGB only; no control writes."""
    if stage not in ("DAYLIGHT","GAIN"):
        raise RuntimeError("UNEXPECTED_RGB_SCENE_PROBE_PHASE")
    output=root/"output"/(camera.upper()+"-"+stage+"-PROBE.json")
    err=root/"output"/(camera.upper()+"-"+stage+"-PROBE-STDERR.txt")
    argv=("runuser","-u","geoca","--","python3",
          "/usr/local/lib/sp11-camera-e004me/scene_probe.py",
          "--camera",camera,"--frames","90")
    with output.open("x") as out,err.open("x") as errors:
        subprocess.run(argv,stdout=out,stderr=errors,
                       timeout=45.,check=True,close_fds=True)
    report=json.loads(output.read_text().splitlines()[-1])
    if report.get("status")!="PASS" or report.get("camera")!=camera or (
        report.get("frames")!=90 or report.get("effective_uid")!=1000 or
        report.get("pixel_files_saved") is not False or
        report.get("camera_route_or_controls_changed") is not False):
        raise RuntimeError("INDEPENDENT_REAL_SCENE_PROBE_CONTRACT_FAILED")
    return report


def run_trial(candidate: str) -> dict:
    root=Path("/var/lib/sp11-camera-"+candidate)
    if os.geteuid()!=0 or not root.is_dir():
        raise RuntimeError("ROOT_PRIVATE_CANDIDATE_MISSING")
    O=root/"output"
    server_argv=("python3",str(root/"rgb/service/selector.py"),
                 "--candidate",candidate,"--max-seconds","180")
    result={"status":"INCOMPLETE_FAIL_CLOSED","camera_order":[],
            "client_results":{},"selector_control":"ROOT_PRIVATE_UNIX_SOCKET",
            "system_sleep_tested":False,"ir_illumination_enabled":False}
    p=None
    done=False
    stdout=O/"RGB-SELECTOR-SERVER-STDOUT.txt"
    stderr=O/"RGB-SELECTOR-SERVER-STDERR.txt"
    with stdout.open("x") as out,stderr.open("x") as errors:
        try:
            p=subprocess.Popen(server_argv,stdout=out,stderr=errors,
                               start_new_session=True,close_fds=True)
            deadline=time.monotonic()+12.
            sock=root/"rgb-control.sock"
            while not sock.is_socket() and time.monotonic()<deadline:
                if p.poll() is not None:
                    raise RuntimeError("RGB_SELECTOR_SERVER_EXITED_EARLY")
                time.sleep(.05)
            if not sock.is_socket():
                raise RuntimeError("RGB_SELECTOR_CONTROL_SOCKET_NOT_READY")
            checked_status(candidate,"off")
            for camera in ("front","rear"):
                choice=rgb_command(candidate,camera)
                if choice.get("status")!="OK" or choice.get("selected")!=camera:
                    raise RuntimeError("RGB_CONTROL_CAMERA_SELECTION_FAILED")
                checked_status(candidate,camera)
                wait_output(camera)
                before=service_invocation(candidate,camera)
                ctrl_before=sensor_control_readback(root,camera)
                U=camera.upper()
                app_record=O/(U+"-CLIENT-CYCLE.json")
                app_error=O/(U+"-CLIENT-CYCLE-ERROR.txt")
                cmd=("python3",str(root/"client_lifecycle.py"),"--camera",camera,
                     "--client",str(Path("/usr/local/lib/sp11-camera-"+candidate)/"client.py"),
                     "--output",str(O))
                with app_record.open("x") as report,app_error.open("x") as errors:
                    subprocess.run(cmd,stdout=report,stderr=errors,
                                   timeout=105.,check=True,close_fds=True)
                app=json.loads(app_record.read_text())
                if (app.get("status")!="PASS" or
                    app.get("normal_open_count")!=3 or
                    app.get("forced_app_crash_count")!=1 or
                    len(app.get("phases",()))!=4 or
                    not all(x.get("process_group_gone") for x in app["phases"])):
                    raise RuntimeError("INDEPENDENT_UID1000_APP_CYCLE_NOT_VALID")
                normal=[x["app"] for x in app["phases"] if "app" in x]
                if (len(normal)!=3 or
                    any(x.get("effective_uid")!=1000 or x.get("complete_frames")!=120 or
                        x.get("requested_frames")!=120 or x.get("distinct_payloads")!=120 or
                        x.get("app_format")!=("I420_1920x1080" if camera=="front" else "I420_3840x2160")
                        for x in normal)):
                    raise RuntimeError("REAL_APP_FRAME_LENGTH_COUNT_OR_UID_INVALID")
                if service_invocation(candidate,camera)!=before:
                    raise RuntimeError("PUBLISHER_RESTARTED_DURING_CLIENT_RECOVERY")
                checked_status(candidate,camera)
                probe=scene_probe(root,camera)
                if service_invocation(candidate,camera)!=before:
                    raise RuntimeError("PUBLISHER_RESTARTED_DURING_SCENE_PROBE")
                ctrl_after=sensor_control_readback(root,camera)
                if ctrl_after["controls"]!=ctrl_before["controls"]:
                    raise RuntimeError("UNEXPECTED_SENSOR_AUTO_CONTROL_CHANGED_BEFORE_GAIN_TRIAL")
                checked_status(candidate,camera)
                gain_trial=perform_gain_trial(root,camera,probe,
                    lambda:scene_probe(root,camera,stage="GAIN"))
                if service_invocation(candidate,camera)!=before:
                    raise RuntimeError("PUBLISHER_RESTARTED_DURING_SENSOR_GAIN_TRIAL")
                ctrl_restored=sensor_control_readback(root,camera)
                if ctrl_restored["controls"]!=ctrl_before["controls"]:
                    raise RuntimeError("RGB_SENSOR_CONTROL_NOT_RESTORED_BEFORE_SESSION_STOP")
                checked_status(candidate,camera)
                result.setdefault("gain_trials",{})[camera]=gain_trial
                result.setdefault("scene_probe",{})[camera]={
                    "app":probe,"sensor_controls_before":ctrl_before,
                    "sensor_controls_after":ctrl_after,
                    "auto_exposure_or_windows_quality_parity_proven":False}
                result["camera_order"].append(camera)
                result["client_results"][camera]={
                    "publisher_invocation_id":before,
                    "normal_unprivileged_opens_with_120_complete_frames_each":3,
                    "intentional_client_kill_and_same_publisher_recovery":True,
                    "independent_app_observed_fps":[x["observed_fps"] for x in normal],
                    "application_format":normal[0]["app_format"],
                    "sampled_scene_luma_y_range":[
                        min(x["quality_stats"]["y_mean_range"][0] for x in normal),
                        max(x["quality_stats"]["y_mean_range"][1] for x in normal)]}
            reply=rgb_command(candidate,"off")
            if reply.get("selected")!="off" or reply.get("status")!="OK":
                raise RuntimeError("FINAL_RGB_OFF_COMMAND_NOT_ACKNOWLEDGED")
            checked_status(candidate,"off")
            reply=rgb_command(candidate,"quit")
            if reply.get("status")!="OK" or reply.get("finished") is not True:
                raise RuntimeError("ROOT_CAMERA_SELECTOR_QUIT_NOT_ACKNOWLEDGED")
            if p.wait(timeout=10)!=0:
                raise RuntimeError("RGB_SELECTOR_SERVER_NONZERO_EXIT")
            summary=json.loads((O/"RGB-SELECTOR-RESULT.json").read_text())
            if (summary.get("status")!="PASS_ROOT_OPT_IN_FRONT_REAR_SOFTWARE_RGB_SELECTOR"
                    or summary.get("accepted_commands")!=["front","rear","off","quit"]):
                raise RuntimeError("RGB_SELECTOR_DURABLE_COMMAND_LEDGER_UNEXPECTED")
            result["status"]="PASS_REAL_OPT_IN_RGB_SELECTOR_UID1000_FRONT1080_REAR4K"
            result["verified_reversible_command_sequence"]=summary["accepted_commands"]
            done=True
            return result
        finally:
            if p is not None and p.poll() is None:
                # Do not issue speculative graph or camera stop commands
                # after any unexpected condition. Terminate the candidate
                # owner and let the outer one-shot reboot to protected Golden.
                os.killpg(p.pid,signal.SIGTERM)
                p.wait(timeout=7)
            if not done:
                result["status"]="FAIL_CLOSED_REBOOT_GOLDEN_NO_GRAPH_GUESS"
            (O/"RGB-SELECTOR-ACCEPTANCE.json").write_text(
                json.dumps(result,indent=2,sort_keys=True)+"\n")


if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--candidate",required=True)
    args=parser.parse_args()
    result=run_trial(args.candidate)
    print(json.dumps(result,sort_keys=True),flush=True)
