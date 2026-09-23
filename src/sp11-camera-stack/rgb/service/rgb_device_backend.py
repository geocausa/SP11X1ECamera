# SPDX-License-Identifier: MIT
"""Linux RGB device/service adapter to the maintained fail-closed RGBSession.

This is source-only until exercised in a NEW guarded SP11 camera candidate.
The owning root-private boot harness must initialize devices and both named
loopbacks, pin binaries/manifests, acquire the controller's process-backed
exclusive lease, independently audit all camera+reader FDs, keep IR off and
provide independently verified systemd stop/STREAMOFF evidence. No module
load, boot change, default install, system sleep or IR action lives here.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from typing import Callable, Protocol

from media_backend import PhysicalMediaBackend, validated_transition, bounded_command
from session import SessionRejected

CAMERAS = frozenset(("front", "rear"))
# Hardcoded expected capture outputs; never dynamically infer a different
# format from a stale, user-writable discovery cache.
SPECS = {
    "front": {
        "sensor": r"imx681 [0-9]+-0010",
        "node_key": "front_rdi_video_device",
        "sensor_key": "front_sensor_entity",
        "entity_pads": (("msm_csiphy2", 0), ("msm_csiphy2", 1),
                        ("msm_csid1", 0), ("msm_csid1", 1),
                        ("msm_vfe1_rdi0", 0), ("msm_vfe1_rdi0", 1)),
        "mbus": "SRGGB10_1X10/3840x2160",
        "fmt": "width=3840,height=2160,pixelformat=pRAA",
        "width_height": "3840/2160", "fourcc": "pRAA",
        "bytesperline": "4800", "sizeimage": "10368000",
        "virtual": "/dev/video91", "virt_width_height": "1920/1080",
        "card": "SP11-Front-Preview",
    },
    "rear": {
        "sensor": r"ov13858 [0-9]+-0010",
        "node_key": "rear_video_device",
        "sensor_key": "rear_sensor_entity",
        "entity_pads": (("msm_csiphy1", 0), ("msm_csiphy1", 1),
                        ("msm_csid0", 0), ("msm_csid0", 1),
                        ("msm_vfe0_rdi0", 0), ("msm_vfe0_rdi0", 1)),
        "mbus": "SGRBG10_1X10/4076x2806",
        "fmt": "width=4076,height=2806,pixelformat=pgAA",
        "width_height": "4076/2806", "fourcc": "pgAA",
        "bytesperline": "5104", "sizeimage": "14321824",
        "virtual": "/dev/video90", "virt_width_height": "3840/2160",
        "card": "SP11-Rear-Preview",
    },
}


class ExternalOwner(Protocol):
    def authorized(self) -> bool:
        """Exact fresh root-sealed candidate boot/manifest/current-boot gate."""
    def lease_held(self) -> bool:
        """Live process-backed, root-exclusive controller lease."""
    def no_camera_users(self) -> bool:
        """Independent source AND virtual-reader FD/publisher audit."""
    def ir_off(self) -> bool:
        """IR standby and illumination-off verified without writing to IR."""
    def run(self, argv: tuple[str, ...], *, timeout: float) -> str:
        """Bounded exact argv command, nonzero/timeout/signal raises."""
    def unit(self, camera: str) -> str:
        """Candidate-specific pinned systemd unit; only front or rear admitted."""
    def service_state(self, camera: str) -> dict:
        """Fresh unit status with active, pid, invocation ID, result."""
    def stop_proof(self, camera: str, invocation_id: str) -> bool:
        """Actual matching STOPPED=143 and successful STREAMOFF and reaped pid."""


class RGBDeviceBackend:
    def __init__(self, discovery: dict, owner: ExternalOwner):
        if not isinstance(discovery, dict):
            raise SessionRejected("UNTRUSTED_DEVICE_DISCOVERY")
        media = discovery.get("media")
        if not isinstance(media, str) or not re.fullmatch(r"/dev/media(?:0|[1-9][0-9]*)", media):
            raise SessionRejected("INVALID_DISCOVERED_MEDIA")
        self.device = {}
        self.sensor = {}
        for camera, spec in SPECS.items():
            source = discovery.get(spec["node_key"])
            sensor = discovery.get(spec["sensor_key"])
            if (not isinstance(source, str) or
                    not re.fullmatch(r"/dev/video(?:0|[1-9][0-9]*)", source) or
                    source in ("/dev/video90", "/dev/video91") or
                    not isinstance(sensor, str) or
                    not re.fullmatch(spec["sensor"], sensor)):
                raise SessionRejected("INVALID_DISCOVERED_"+camera.upper())
            self.device[camera] = source
            self.sensor[camera] = sensor
        if self.device["front"] == self.device["rear"]:
            raise SessionRejected("FRONT_REAR_DEVICE_ALIAS")
        self.owner = owner
        self.media = media
        self.graph = PhysicalMediaBackend(
            media, authorized=owner.authorized,
            exclusive=owner.lease_held, no_camera_users=owner.no_camera_users,
            run=owner.run)
        self.invocation: dict[str, str] = {}

    def _require(self, ok: bool, reason: str):
        if ok is not True:
            raise SessionRejected(reason)

    def _guard(self):
        self._require(self.owner.authorized(), "CANDIDATE_BOOT_ASSETS_NOT_AUTHORIZED")
        self._require(self.owner.lease_held(), "CONTROLLER_LEASE_NOT_HELD")
        self._require(self.owner.ir_off(), "IR_NOT_STANDBY_OR_ILLUMINATION_NOT_OFF")

    def authorized(self):
        return self.owner.authorized() is True

    def holds_exclusive_lease(self):
        return self.owner.lease_held() is True

    def camera_users_closed(self):
        return self.owner.no_camera_users() is True

    def ir_off(self):
        return self.owner.ir_off() is True

    def route_phase(self):
        self._guard()
        return validated_phase(self.graph.read_graph())

    def activate_route(self, camera):
        self._guard()
        self._require(camera in CAMERAS, "INVALID_RGB_CAMERA")
        self._require(self.owner.no_camera_users(), "CAMERA_USERS_REMAIN_BEFORE_ROUTE")
        validated_transition(self.graph, camera)
        self._require(self.route_phase() == camera, "CAMERA_GRAPH_DRIFT_AFTER_ROUTE")

    def configure(self, camera):
        self._guard()
        if camera not in CAMERAS:
            raise SessionRejected("INVALID_RGB_CAMERA")
        self._require(self.route_phase() == camera, "CONFIGURE_WRONG_GRAPH")
        self._require(self.owner.no_camera_users(), "CAMERA_USERS_REMAIN_BEFORE_CONFIG")
        spec=SPECS[camera]
        fmt=spec["mbus"]
        self.owner.run(("media-ctl", "-d", self.media, "-V",
                        f'"{self.sensor[camera]}":0 [fmt:{fmt}]'), timeout=7.0)
        for entity, pad in spec["entity_pads"]:
            self.owner.run(("media-ctl", "-d", self.media, "-V",
                            f'"{entity}":{pad} [fmt:{fmt}]'), timeout=7.0)
        self.owner.run(("v4l2-ctl", "-d", self.device[camera],
                        "--set-fmt-video="+spec["fmt"]), timeout=7.0)
        text=self.owner.run(("v4l2-ctl", "-d", self.device[camera],
                             "--get-fmt-video"), timeout=7.0)
        for pattern in (rf"Width/Height\s*:\s*{re.escape(spec['width_height'])}\b",
                        rf"Pixel Format\s*:\s*'{spec['fourcc']}'",
                        rf"Bytes per Line\s*:\s*{spec['bytesperline']}\b",
                        rf"Size Image\s*:\s*{spec['sizeimage']}\b"):
            if not re.search(pattern, text):
                raise SessionRejected("UNVERIFIED_SOURCE_FORMAT_"+camera.upper())
        self._require(self.route_phase() == camera, "GRAPH_DRIFT_AFTER_CONFIG")

    def start_publisher(self, camera):
        self._guard()
        if camera not in CAMERAS or camera in self.invocation:
            raise SessionRejected("PUBLISHER_START_ALREADY_ACTIVE_OR_INVALID")
        self._require(self.route_phase() == camera, "START_WRONG_GRAPH")
        unit=self.owner.unit(camera)
        self.owner.run(("systemctl", "start", unit), timeout=12.0)
        state=self.owner.service_state(camera)
        self._require(state.get("active") is True and
                      isinstance(state.get("pid"), int) and state["pid"]>1,
                      "PUBLISHER_NOT_RUNNING_AFTER_START")
        invocation=state.get("invocation_id")
        self._require(isinstance(invocation,str) and
                      re.fullmatch(r"[0-9a-f]{32}",invocation) is not None,
                      "PUBLISHER_INVOCATION_UNVERIFIED")
        self.invocation[camera]=invocation

    def publisher_running(self, camera):
        self._guard()
        state=self.owner.service_state(camera)
        return (camera in self.invocation and state.get("active") is True
                and isinstance(state.get("pid"),int) and state["pid"]>1
                and state.get("invocation_id")==self.invocation[camera])

    def stop_publisher(self, camera):
        self._guard()
        if camera not in self.invocation:
            raise SessionRejected("PUBLISHER_INVOCATION_MISSING")
        original=self.invocation[camera]
        self.owner.run(("systemctl", "stop", self.owner.unit(camera)), timeout=12.0)
        self._guard()
        state=self.owner.service_state(camera)
        self._require(state.get("active") is False and state.get("pid")==0,
                      "PUBLISHER_STILL_RUNNING_AFTER_STOP")
        self._require(self.owner.stop_proof(camera, original),
                      "ACTUAL_STREAMOFF_SERVICE_EXIT_NOT_VERIFIED")
        # A generic service 'inactive' state is insufficient: the
        # candidate-specific proof must bind the exact invocation.
        del self.invocation[camera]
        return True

    def neutralize_route(self, camera):
        self._guard()
        if camera not in CAMERAS:
            raise SessionRejected("INVALID_RGB_CAMERA")
        self._require(camera not in self.invocation, "PUBLISHER_NOT_VERIFIABLY_STOPPED")
        self._require(self.owner.no_camera_users(), "CLIENT_READER_OR_CAMERA_FD_OPEN")
        self._require(self.route_phase() == camera, "WRONG_GRAPH_BEFORE_NEUTRAL")
        validated_transition(self.graph, "neutral")
        self._require(self.route_phase() == "neutral", "POST_STOP_GRAPH_NOT_NEUTRAL")


def validated_phase(graph: str) -> str:
    """Require full source/link integrity before admitting named RGB routes."""
    from media_backend import route_policy
    return route_policy.phase(route_policy.snapshot(graph))
