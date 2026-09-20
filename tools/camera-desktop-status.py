#!/usr/bin/env python3
"""Inspect desktop camera prerequisites without opening a camera or starting services."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

PACKAGES = ("libcamera-tools", "libcamera-ipa", "libspa-0.2-libcamera",
            "gstreamer1.0-libcamera", "pipewire", "wireplumber",
            "xdg-desktop-portal", "xdg-desktop-portal-gnome")
SERVICES = ("pipewire.service", "wireplumber.service", "xdg-desktop-portal.service")

def query(argv, env=None):
    try:
        cp = subprocess.run(argv, capture_output=True, text=True, timeout=8, env=env)
        return cp.returncode, cp.stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None, ""

def collect():
    packages = {}
    for name in PACKAGES:
        rc, value = query(["dpkg-query", "-W", "-f=${db:Status-Abbrev}|${Version}", name])
        installed = rc == 0 and value.startswith("ii ")
        packages[name] = {"installed": installed, "version": value.split("|", 1)[1] if installed else None}
    runtime = Path("/run/user") / str(os.getuid())
    env = dict(os.environ, XDG_RUNTIME_DIR=str(runtime),
               DBUS_SESSION_BUS_ADDRESS="unix:path=" + str(runtime / "bus"))
    services = {}
    for name in SERVICES:
        rc, value = query(["systemctl", "--user", "is-active", name], env)
        services[name] = value if rc is not None and value else "unavailable"
    nodes = {kind: sorted(str(p) for p in Path("/dev").glob(kind + "*")
                          if p.name[len(kind):].isdigit()) for kind in ("video", "media")}
    missing = [name for name, value in packages.items() if not value["installed"]]
    blockers = []
    if not nodes["video"] or not nodes["media"]:
        blockers.append("Camera media/video devices are not exposed on this boot; expected on protected Golden.")
    if missing:
        blockers.append("Missing desktop prerequisites: " + ", ".join(missing))
    inactive = [name for name, value in services.items() if value != "active"]
    if inactive:
        blockers.append("Desktop services inactive or unavailable: " + ", ".join(inactive))
    return {"schema": "sp11-camera-desktop-status-v1", "camera_opened": False,
            "activation_performed": False, "packages": packages, "services": services,
            "tools": {name: shutil.which(name) for name in ("cam", "gst-launch-1.0", "gst-inspect-1.0", "wpctl")},
            "device_nodes": nodes, "prerequisite_gaps": blockers,
            "application_capture": "NOT_TESTED",
            "assessment": "PREREQUISITES_INCOMPLETE" if blockers else "PREREQUISITES_PRESENT_CAPTURE_UNPROVEN",
            "next_validation": "Fresh separately checkpointed RGB candidate, continuous processed output, then desktop application capture.",
            "ir_illumination": "NOT_AUTHORIZED_BY_THIS_DIAGNOSTIC",
            "authentication": "NOT_IMPLEMENTED_BY_THIS_DIAGNOSTIC"}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    result = collect()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("Desktop camera: " + result["assessment"])
        for gap in result["prerequisite_gaps"]:
            print("- " + gap)
        print("Application capture: NOT_TESTED; no camera opened or service started.")
        print("Next: " + result["next_validation"])

if __name__ == "__main__":
    main()
