# SPDX-License-Identifier: MIT
"""Exact Linux Media Controller backend for maintained RGB route policy.

Opt-in test candidate only. Does not load modules, install services, open
a sensor, arm/reboot, enable IR, or change Golden. A root-only owner must
provide fresh live boot/asset admission, an acquired exclusive lease,
and independent full camera/reader process and FD release checks.

The actual media-ctl calls are bounded argv operations, not shell strings.
Every physical write is checked by route_policy.Controller against a
fresh complete 119-edge graph. A syscall timeout, uncertain write, graph
drift or loss of lease makes the Controller poisoned and fail closed.
"""
from __future__ import annotations
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable, Protocol

ROUTING = Path(__file__).resolve().parents[2] / "routing"
if str(ROUTING) not in sys.path:
    sys.path.insert(0, str(ROUTING))
import route_policy  # noqa: E402


class Command(Protocol):
    def __call__(self, argv: tuple[str, ...], *, timeout: float) -> str:
        """Run one bounded exact command; fail on nonzero, timeout or signal."""


def bounded_command(argv: tuple[str, ...], *, timeout: float) -> str:
    result = subprocess.run(argv, check=True, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, timeout=timeout,
                            close_fds=True)
    return result.stdout


class PhysicalMediaBackend:
    """Restricted live adapter, also compatible with deterministic fake runner."""
    def __init__(self, media: str, *, authorized: Callable[[], bool],
                 exclusive: Callable[[], bool], no_camera_users: Callable[[], bool],
                 run: Command = bounded_command):
        if not re.fullmatch(r"/dev/media(?:0|[1-9][0-9]*)", media):
            raise ValueError("INVALID_PHYSICAL_MEDIA_NODE")
        for fn in (authorized, exclusive, no_camera_users):
            if not callable(fn):
                raise TypeError("REQUIRED_REAL_AUTHORIZATION_CALLBACK")
        self.media = media
        self.authorized = authorized
        self.exclusive = exclusive
        self.no_camera_users = no_camera_users
        self.run = run

    def _admit(self) -> None:
        if self.authorized() is not True:
            raise route_policy.Rejected("FRESH_CANDIDATE_BOOT_ASSETS_NOT_AUTHORIZED")
        if self.exclusive() is not True:
            raise route_policy.Rejected("EXCLUSIVE_CAMERA_SESSION_NOT_HELD")

    def exclusive_session_held(self) -> bool:
        self._admit()
        return True

    def all_cameras_stopped(self) -> bool:
        self._admit()
        if self.no_camera_users() is not True:
            raise route_policy.Rejected("CAMERA_PUBLISHER_OR_READERS_STILL_OPEN")
        return True

    def read_graph(self) -> str:
        self._admit()
        # Correct media device must have already passed root-only candidate
        # discovery and st_rdev/mode validation by the owning boot harness.
        return self.run(("media-ctl", "-d", self.media, "-p"), timeout=7.0)

    def set_link(self, edge: route_policy.Edge, enable: bool) -> None:
        self._admit()
        if not isinstance(enable, bool) or edge not in (
                *route_policy.FRONT, *route_policy.REAR):
            raise route_policy.Rejected("NON_RGB_OR_INVALID_MEDIA_LINK_WRITE")
        if self.no_camera_users() is not True:
            raise route_policy.Rejected("CAMERA_USER_PRESENT_AT_LINK_WRITE")
        src, spad, dst, dpad = edge
        link = f'"{src}":{spad} -> "{dst}":{dpad} [{int(enable)}]'
        self.run(("media-ctl", "-d", self.media, "-l", link), timeout=7.0)


def validated_transition(backend: PhysicalMediaBackend, target: str):
    """One guarded transition only; caller holds lease until post-readback."""
    if target not in ("neutral", "front", "rear"):
        raise route_policy.Rejected("INVALID_RGB_SESSION_TARGET")
    controller = route_policy.Controller(backend)
    return controller.transition(target)
