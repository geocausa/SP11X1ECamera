# SPDX-License-Identifier: MIT
"""Explicit opt-in RGB-only front/rear selector over a root-private UNIX socket.

Source-only until a NEW unique guarded single-use SP11 camera candidate
validates it. Ordinary unprivileged camera apps use the named V4L2 nodes;
only root controls which physical source is active. The root-only socket
must reside in the unique root-owned 0700 candidate directory. This module
does not load camera modules, touch GRUB/Golden, stream IR or system-sleep.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import signal
import socket
import stat
import struct
import sys
import time

from candidate_owner import CandidateOwner
from rgb_device_backend import RGBDeviceBackend
from session import RGBSession, SessionRejected


class RGBSelector:
    """One stateful owner of both RGB routes; no unrelated camera writes."""
    def __init__(self, session: RGBSession):
        self.session = session
        self.finished = False
        self.command_count = 0

    def dispatch(self, command: str) -> dict:
        if not isinstance(command, str) or command not in (
                "front", "rear", "off", "status", "quit"):
            return {"status": "REJECTED", "reason": "UNKNOWN_RGB_COMMAND"}
        if self.finished or self.session.poisoned:
            raise SessionRejected("SELECTOR_TERMINAL_OR_POISONED")
        if command == "status":
            active = self.session.active
            if active is None:
                self.session.backend._guard()  # enforce real lease and IR off
                if self.session.backend.route_phase() != "neutral":
                    raise SessionRejected("IDLE_NATIVE_GRAPH_DRIFT")
            elif (not self.session.backend.publisher_running(active)
                  or self.session.backend.route_phase() != active):
                raise SessionRejected("ACTIVE_PUBLISHER_OR_GRAPH_DRIFT")
            return {"status": "OK", "selected": active or "off"}
        if command == "quit":
            self.session.close()
            self.command_count += 1
            self.finished = True
            return {"status": "OK", "selected": "off", "finished": True}
        if command == "off":
            if self.session.active is not None:
                self.session.stop()
            else:
                self.session.close()  # still checks complete neutral+lease
            self.command_count += 1
            return {"status": "OK", "selected": "off"}
        if self.session.active == command:
            if (not self.session.backend.publisher_running(command)
                or self.session.backend.route_phase() != command):
                raise SessionRejected("ALREADY_SELECTED_CAMERA_NOT_HEALTHY")
            return {"status": "OK", "selected": command, "already_active": True}
        if self.session.active is None:
            self.session.open(command)
        else:
            # No unsafe simultaneous sensors; full verified STOP -> NEUTRAL
            # -> selected-camera route before new source is allowed to start.
            self.session.switch(command)
        self.command_count += 1
        return {"status": "OK", "selected": command}


def serve(candidate: str, *, max_seconds: int = 180) -> dict:
    if not re.fullmatch(r"e004[a-z]{2}", candidate):
        raise SessionRejected("UNTRUSTED_CANDIDATE_NAME")
    if not 1 <= max_seconds <= 600:
        raise SessionRejected("UNBOUNDED_OR_INVALID_SELECTOR_LEASE")
    root = Path("/var/lib/sp11-camera-" + candidate)
    discovery = json.loads((root / "output/UNIFIED.json").read_text())
    owner = CandidateOwner(candidate, staged=root, discovery=discovery)
    selector = RGBSelector(RGBSession(RGBDeviceBackend(discovery, owner)))
    path = root / "rgb-control.sock"
    stopped = False
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    summary = {"candidate": candidate, "status": "INCOMPLETE_FAIL_CLOSED",
               "accepted_commands": [], "selected": "off", "linux_os_sleep": False,
               "ir_illumination_enabled": False}
    try:
        if path.exists() or path.is_symlink():
            raise SessionRejected("UNTRUSTED_PREEXISTING_CONTROL_SOCKET")
        sock.bind(str(path))
        os.chmod(path, 0o600)
        stat_result = os.lstat(path)
        if (not stat.S_ISSOCK(stat_result.st_mode)
            or stat_result.st_uid != 0 or stat.S_IMODE(stat_result.st_mode) != 0o600):
            raise SessionRejected("UNTRUSTED_CONTROL_SOCKET_PERMISSIONS")
        sock.listen(2)
        sock.settimeout(1.0)
        deadline = time.monotonic() + max_seconds
        while not selector.finished:
            if time.monotonic() >= deadline:
                raise SessionRejected("EXPLICIT_SELECTOR_SESSION_WATCHDOG_EXPIRED")
            if not owner.authorized() or not owner.lease_held() or not owner.ir_off():
                raise SessionRejected("SELECTOR_LOST_ROOT_BOOT_LEASE_OR_IR_OFF_GUARD")
            try:
                conn, _ = sock.accept()
            except socket.timeout:
                # Proactively detect a source publisher dying without a
                # concurrent control request, and fail closed.
                if selector.session.active is not None:
                    active = selector.session.active
                    if (not selector.session.backend.publisher_running(active)
                        or selector.session.backend.route_phase() != active):
                        raise SessionRejected("UNEXPECTED_ACTIVE_CAMERA_FAILURE")
                continue
            with conn:
                conn.settimeout(6.0)
                creds = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12)
                pid, uid, gid = struct.unpack("3i", creds)
                if pid < 1 or uid != 0:
                    conn.sendall(b'{"status":"REJECTED","reason":"ROOT_CONTROL_ONLY"}\n')
                    continue
                request = conn.recv(129)
                if len(request) > 128 or b"\n" not in request or (
                        request.split(b"\n", 1)[1] not in (b"",)):
                    conn.sendall(b'{"status":"REJECTED","reason":"INVALID_COMMAND_FRAME"}\n')
                    continue
                try:
                    command = request[:-1].decode("ascii", "strict")
                except UnicodeDecodeError:
                    command = ""
                response = selector.dispatch(command)
                conn.sendall((json.dumps(response, sort_keys=True) + "\n").encode("ascii"))
                if response.get("status") == "OK" and command != "status":
                    summary["accepted_commands"].append(command)
                    summary["selected"] = response["selected"]
        if selector.session.active is not None or selector.session.poisoned:
            raise SessionRejected("SELECTOR_TERMINATED_WITH_ACTIVE_OR_POISONED_CAMERA")
        summary["status"] = "PASS_ROOT_OPT_IN_FRONT_REAR_SOFTWARE_RGB_SELECTOR"
        stopped = True
        return summary
    finally:
        # IMPORTANT: an uncertain write/stop must never be followed by a
        # guessed graph rollback or another controller command. The outer
        # root-private single-use candidate automatically returns to Golden.
        sock.close()
        if path.is_socket() and not path.is_symlink():
            path.unlink()
        if not stopped:
            summary["status"] = "FAILED_SELECTOR_CANDIDATE_MUST_AUTO_RETURN_GOLDEN"
        (root / "output/RGB-SELECTOR-RESULT.json").write_text(
            json.dumps(summary, sort_keys=True, indent=2) + "\n")
        owner.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--max-seconds", type=int, default=180)
    args = parser.parse_args()
    if os.geteuid() != 0:
        raise SystemExit("ROOT_ONLY_CAMERA_SELECTOR")
    result = serve(args.candidate, max_seconds=args.max_seconds)
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
