# SPDX-License-Identifier: MIT
"""Exclusive, fail-closed front/rear RGB software-publisher session policy.

OFFLINE/UNINSTALLED: deliberately no device backend, service unit, route
mutation, boot action or system sleep. The real backend must implement the
reviewed, source-pinned, root-private candidate's boot/manifest/FD guards and
the maintained routing Controller with fresh complete Media Controller reads.
This class cannot itself authorize or install a physical camera session.
"""
from __future__ import annotations

from typing import Protocol


class SessionRejected(RuntimeError):
    """Unsafe or unverified session; owning one-shot candidate must return Golden."""


class SessionBackend(Protocol):
    def authorized(self) -> bool:
        """Verify exact disposable boot identity, privilege and pinned assets."""
    def holds_exclusive_lease(self) -> bool:
        """True only for a live process-backed exclusive camera ownership lease."""
    def camera_users_closed(self) -> bool:
        """Independently prove no camera sensor/media FD users or client readers."""
    def ir_off(self) -> bool:
        """Read-only proof that VD55G0 is standby and illumination is OFF."""
    def route_phase(self) -> str:
        """Fresh complete native media-v2 graph validation; neutral/front/rear only."""
    def activate_route(self, camera: str) -> None:
        """Guarded complete neutral->camera transaction and fresh readback."""
    def configure(self, camera: str) -> None:
        """Verify accepted RAW source and named target NV12 output formats."""
    def start_publisher(self, camera: str) -> None:
        """Start the root-owned conversion publisher; do not return on uncertain start."""
    def publisher_running(self, camera: str) -> bool:
        """Read process/invocation identity and active status."""
    def stop_publisher(self, camera: str) -> bool:
        """Request bounded TERM; true ONLY after STREAMOFF, reap and exit proof."""
    def neutralize_route(self, camera: str) -> None:
        """After verified stop, guarded camera->neutral transaction and readback."""


class RGBSession:
    """Single owner of the shared SP11 CAMSS RGB media graph.

    No success-path speculative rollback. Any ambiguous stop/write/error poisons
    the session so the outer guarded one-shot runner can perform Golden return
    without another route mutation. The active camera is not cleared unless
    STOP, complete neutral, IR-off and all-FDs-closed proofs pass.
    """
    CAMERAS = frozenset(("front", "rear"))
    def __init__(self, backend: SessionBackend):
        self.backend = backend
        self.active: str | None = None
        self.poisoned = False
        self.completed_stops = 0

    def _require(self, condition: bool, reason: str) -> None:
        if condition is not True:
            raise SessionRejected(reason)

    def _lease(self) -> None:
        self._require(self.backend.authorized(), "EXACT_BOOT_AND_ASSETS_NOT_AUTHORIZED")
        self._require(self.backend.holds_exclusive_lease(), "NO_EXCLUSIVE_CAMERA_LEASE")
        self._require(self.backend.ir_off(), "IR_ILLUMINATION_OR_STREAM_NOT_OFF")

    def _neutral_idle(self) -> None:
        self._lease()
        self._require(self.backend.camera_users_closed(), "CAMERA_FDS_OR_READERS_REMAIN")
        self._require(self.backend.route_phase() == "neutral",
                      "FULL_NATIVE_MEDIA_GRAPH_NOT_NEUTRAL")

    def open(self, camera: str) -> None:
        if self.poisoned:
            raise SessionRejected("SESSION_POISONED")
        if camera not in self.CAMERAS:
            raise SessionRejected("UNSUPPORTED_CAMERA")
        if self.active is not None:
            raise SessionRejected("STOP_CURRENT_CAMERA_BEFORE_SWITCH")
        try:
            self._neutral_idle()
            self.backend.activate_route(camera)
            self._lease()
            self._require(self.backend.route_phase() == camera,
                          "SELECTED_CAMERA_GRAPH_UNCONFIRMED")
            self.backend.configure(camera)
            self.backend.start_publisher(camera)
            self._lease()
            self._require(self.backend.publisher_running(camera),
                          "SELECTED_CAMERA_PUBLISHER_NOT_RUNNING")
            self.active = camera
        except BaseException:
            self.poisoned = True
            raise

    def stop(self) -> None:
        if self.poisoned:
            raise SessionRejected("SESSION_POISONED")
        camera = self.active
        if camera is None:
            raise SessionRejected("NO_ACTIVE_CAMERA")
        try:
            self._lease()
            self._require(self.backend.stop_publisher(camera),
                          "PUBLISHER_STREAMOFF_AND_EXIT_NOT_PROVEN")
            # No graph writes unless independent FD/client-release proof passes.
            self._require(self.backend.camera_users_closed(),
                          "PUBLISHER_OR_APP_CAMERA_FDS_STILL_OPEN")
            self._lease()
            self._require(self.backend.route_phase() == camera,
                          "ACTIVE_GRAPH_CHANGED_BEFORE_NEUTRAL")
            self.backend.neutralize_route(camera)
            self._neutral_idle()
            self.active = None
            self.completed_stops += 1
        except BaseException:
            self.poisoned = True
            raise

    def switch(self, camera: str) -> None:
        if self.poisoned:
            raise SessionRejected("SESSION_POISONED")
        if camera not in self.CAMERAS:
            raise SessionRejected("UNSUPPORTED_CAMERA")
        if camera == self.active:
            raise SessionRejected("DUPLICATE_CAMERA_SWITCH")
        if self.active is not None:
            self.stop()
        self.open(camera)

    def close(self) -> None:
        if self.active is not None:
            self.stop()
        elif not self.poisoned:
            try:
                self._neutral_idle()
            except BaseException:
                self.poisoned = True
                raise
        else:
            raise SessionRejected("SESSION_POISONED")
