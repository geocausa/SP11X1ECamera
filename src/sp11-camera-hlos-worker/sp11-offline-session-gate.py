#!/usr/bin/env python3
"""E004go: OFFLINE aggregate-telemetry session guard, never a biometric authenticator.

No device interface, LED, GPIO, kernel module, facial image, enrollment, PAM,
password or unlock API. Caller injects monotonic ticks; this has no physical
watchdog or host-crash guarantees. Every new session needs a new object.
"""
import json
from enum import Enum

MAX_FRAMES = 16
MAX_TELEMETRY_BYTES = 8192
METRIC_KEYS = frozenset((
    "frame", "mean_milli", "p10", "p90", "dark_0_15_permille",
    "bright_240_255_permille", "neighbor_abs_diff_milli",
))
ROOT_KEYS = frozenset(("kind", "face_authentication_proven", "frames"))
KIND = "unprotected-offline-signal-telemetry"

class State(str, Enum):
    IDLE = "idle"
    COLLECTING = "collecting"
    COMPLETE = "complete"
    FAULT = "fault"
    CANCELLED = "cancelled"

class SessionFault(Exception):
    """Never includes an input frame or its contents."""

def _pairs_unique(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate json field")
        out[key] = value
    return out

def _no_constant(text):
    raise ValueError("nonfinite json constant")

def _parse(payload):
    if type(payload) is not bytes or not (1 <= len(payload) <= MAX_TELEMETRY_BYTES):
        raise ValueError("invalid aggregate telemetry size")
    try:
        root = json.loads(payload.decode("utf-8", errors="strict"),
                          object_pairs_hook=_pairs_unique,parse_constant=_no_constant)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("invalid aggregate telemetry encoding") from exc
    if type(root) is not dict or set(root) != ROOT_KEYS:
        raise ValueError("unknown aggregate telemetry fields")
    if root["kind"] != KIND or root["face_authentication_proven"] is not False:
        raise ValueError("not unprotected diagnostic telemetry")
    frames = root["frames"]
    if type(frames) is not list or not (1 <= len(frames) <= MAX_FRAMES):
        raise ValueError("invalid telemetry frame count")
    for idx, frame in enumerate(frames, 1):
        if type(frame) is not dict or set(frame) != METRIC_KEYS:
            raise ValueError("unexpected per-frame telemetry fields")
        for key, value in frame.items():
            if type(value) is not int:
                raise ValueError("non-integer signal diagnostic")
            maximum = {
                "frame": MAX_FRAMES,
                "mean_milli": 255000,
                "p10": 255, "p90": 255,
                "dark_0_15_permille": 1000,
                "bright_240_255_permille": 1000,
                "neighbor_abs_diff_milli": 255000,
            }[key]
            if not (0 <= value <= maximum):
                raise ValueError("out-of-range signal diagnostic")
        if frame["frame"] != idx or frame["p10"] > frame["p90"]:
            raise ValueError("invalid aggregate frame order or percentiles")
    return len(frames)

class OfflineSession:
    """One-shot, no rearm, metadata-only; no hardware or authentication methods."""

    __slots__ = ("state", "max_ticks", "start_tick", "last_tick", "count")

    def __init__(self, max_ticks=50):
        if type(max_ticks) is not int or not (1 <= max_ticks <= 1000):
            raise ValueError("invalid injected monotonic deadline")
        self.state = State.IDLE
        self.max_ticks = max_ticks
        self.start_tick = None
        self.last_tick = None
        self.count = 0

    def _fault(self):
        self.state = State.FAULT
        self.count = 0
        raise SessionFault("offline session rejected")

    def _clock(self, tick):
        if type(tick) is not int or tick < 0:
            self._fault()
        if self.last_tick is not None and tick < self.last_tick:
            self._fault()
        self.last_tick = tick
        if self.start_tick is not None and tick - self.start_tick > self.max_ticks:
            self._fault()

    def start(self, tick):
        if self.state != State.IDLE:
            self._fault()
        self._clock(tick)
        self.start_tick = tick
        self.state = State.COLLECTING

    def accept(self, tick, telemetry):
        if self.state != State.COLLECTING:
            self._fault()
        self._clock(tick)
        try:
            self.count = _parse(telemetry)
        except (ValueError, TypeError, RecursionError):
            self._fault()
        self.state = State.COMPLETE

    def deadline_check(self, tick):
        if self.state != State.COLLECTING:
            self._fault()
        self._clock(tick)

    def cancel(self):
        if self.state != State.COLLECTING:
            self._fault()
        self.state = State.CANCELLED
        self.count = 0

    def diagnostic_result(self):
        if self.state != State.COMPLETE:
            self._fault()
        return {
            "kind": "offline-session-diagnostic-only",
            "status": "complete",
            "frames_checked": self.count,
            "native_ir_emitter_activated": False,
            "face_authentication_proven": False,
            "login_or_unlock_authorized": False,
            "autonomous_hardware_cutoff_proven": False,
        }
