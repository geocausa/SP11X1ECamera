# SPDX-License-Identifier: MIT
"""Root-only finite, opt-in software RGB camera selector CLI.

No camera hardware commands or boot writes. Requires a running
authorized unique-candidate root-owned selector socket; the server is
the single owner and independently verifies all sensor/route actions.
Ordinary apps only open the named front/rear V4L2 endpoints.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import socket
import stat
import sys


def command(candidate: str, action: str) -> dict:
    if action not in ("front", "rear", "off", "status", "quit"):
        raise ValueError("INVALID_RGB_ACTION")
    if not re.fullmatch(r"e004[a-z]{2}", candidate):
        raise ValueError("INVALID_ONE_SHOT_CANDIDATE")
    if os.geteuid() != 0:
        raise PermissionError("ROOT_CONTROL_ONLY")
    root = Path("/var/lib/sp11-camera-" + candidate)
    s = root.stat(follow_symlinks=False)
    if not stat.S_ISDIR(s.st_mode) or s.st_uid != 0 or stat.S_IMODE(s.st_mode) != 0o700:
        raise PermissionError("ROOT_PRIVATE_CANDIDATE_DIRECTORY_REQUIRED")
    socket_path = root / "rgb-control.sock"
    s = socket_path.stat(follow_symlinks=False)
    if not stat.S_ISSOCK(s.st_mode) or s.st_uid != 0 or stat.S_IMODE(s.st_mode) != 0o600:
        raise PermissionError("ROOT_PRIVATE_RGB_CONTROL_SOCKET_REQUIRED")
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as client:
        client.settimeout(16.0)
        client.connect(str(socket_path))
        client.sendall((action + "\n").encode("ascii"))
        data = bytearray()
        while not data.endswith(b"\n"):
            chunk = client.recv(512)
            if not chunk:
                raise OSError("RGB_SELECTOR_DID_NOT_REPLY")
            data.extend(chunk)
            if len(data) > 2048:
                raise OSError("OVERSIZED_RGB_SELECTOR_RESPONSE")
    response = json.loads(data.decode("ascii"))
    if not isinstance(response, dict) or response.get("status") not in ("OK", "REJECTED"):
        raise OSError("UNTRUSTED_RGB_SELECTOR_RESPONSE")
    return response


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", required=True)
    parser.add_argument("action", choices=("front", "rear", "off", "status", "quit"))
    args = parser.parse_args()
    result = command(args.candidate, args.action)
    print(json.dumps(result, sort_keys=True), flush=True)
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    sys.exit(main())
