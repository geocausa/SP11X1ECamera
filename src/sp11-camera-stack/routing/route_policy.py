# SPDX-License-Identifier: MIT
"""Fail-closed SP11 RGB route policy; no OS/device backend is provided.

The caller owns the exclusive device session and supplies fresh graph reads,
link writes and proof that every camera is stopped. Never use cached link flags.
Any failure poisons the controller: no retry, automatic rollback or further write.
"""
from dataclasses import dataclass
import re
from typing import Protocol
from graph_contract import complete_graph

Edge = tuple[str, int, str, int]
FRONT = (("msm_csiphy2", 1, "msm_csid1", 0),
         ("msm_csid1", 1, "msm_vfe1_rdi0", 0))
REAR = (("msm_csiphy1", 1, "msm_csid0", 0),
        ("msm_csid0", 1, "msm_vfe0_rdi0", 0))
ROUTES = {"neutral": (), "front": FRONT, "rear": REAR}
PATHS = {
    "front": ("imx681", "msm_csiphy2", "msm_csid1",
              "msm_vfe1_rdi0", "msm_vfe1_video0"),
    "rear": ("ov13858", "msm_csiphy1", "msm_csid0",
             "msm_vfe0_rdi0", "msm_vfe0_video0"),
}

class Rejected(RuntimeError):
    pass

def canonical(name: str) -> str:
    for sensor, address in (("imx681", "0010"), ("ov13858", "0010"),
                            ("sp11-vd55g0", "0060")):
        if re.fullmatch(rf"{sensor} [0-9]+-{address}", name):
            return sensor
    return name

def camera_for_sensor(name: str) -> str:
    name = canonical(name)
    for camera, path in PATHS.items():
        if name == path[0]:
            return camera
    raise Rejected("SENSOR_NOT_ADMITTED")

def admit_path(sensor: str, path: tuple[Edge, ...]) -> str:
    camera = camera_for_sensor(sensor)
    names = PATHS[camera]
    expected = ((names[0], 0, names[1], 0), *ROUTES[camera],
                (names[3], 1, names[4], 0))
    normalized = tuple((canonical(a), ap, canonical(b), bp)
                       for a, ap, b, bp in path)
    if normalized != expected:
        raise Rejected("PATH_NOT_ADMITTED")
    return camera

def snapshot(text: str) -> frozenset[Edge]:
    """Validate all original structure/immutable flags plus enabled symmetry.

    Clearing ONLY exact mutable ENABLED flags permits validation of transaction
    intermediate states without weakening the existing 119-edge contract.
    Incoming/outgoing enabled sets are separately compared before returning.
    """
    neutral = re.sub(r'(?m)^(\s*(?:->|<-) "[^"]+":\d+) \[ENABLED\]$',
                     r'\1 []', text)
    try:
        if complete_graph(neutral):
            raise Rejected("NON_NEUTRAL_NORMALIZATION")
    except ValueError as error:
        raise Rejected(str(error)) from error
    source = None
    pad = None
    enabled = {"->": set(), "<-": set()}
    for line in text.splitlines():
        match = re.match(r"- entity \d+: (.*?) \(", line)
        if match:
            source = canonical(match[1])
        match = re.match(r"\s*pad(\d+):", line)
        if match:
            pad = int(match[1])
        match = re.fullmatch(r'\s*(->|<-) "([^"]+)":(\d+) \[ENABLED\]', line)
        if match:
            arrow, target, tp = match.groups()
            edge = ((source, pad, canonical(target), int(tp))
                    if arrow == "->"
                    else (canonical(target), int(tp), source, pad))
            enabled[arrow].add(edge)
    if enabled["->"] != enabled["<-"]:
        raise Rejected("ASYMMETRIC_ENABLED_FLAGS")
    return frozenset(enabled["->"])

def phase(state: frozenset[Edge]) -> str:
    for camera, route in ROUTES.items():
        if state == frozenset(route):
            return camera
    raise Rejected("UNADMITTED_OR_PARTIAL_INITIAL_STATE")

@dataclass(frozen=True)
class Change:
    edge: Edge
    enable: bool
    before: frozenset[Edge]
    after: frozenset[Edge]

def plan(text: str, target: str) -> tuple[Change, ...]:
    if target not in ROUTES:
        raise Rejected("TARGET_NOT_ADMITTED")
    state = snapshot(text)
    current = phase(state)
    if current == target:
        return ()
    steps = []
    # Drain downstream first; connect upstream first. Always pass through neutral.
    operations = [(edge, False) for edge in reversed(ROUTES[current])]
    operations += [(edge, True) for edge in ROUTES[target]]
    for edge, enable in operations:
        after = state | {edge} if enable else state - {edge}
        steps.append(Change(edge, enable, state, frozenset(after)))
        state = frozenset(after)
    return tuple(steps)

class Backend(Protocol):
    def read_graph(self) -> str: ...
    def all_cameras_stopped(self) -> bool: ...
    def exclusive_session_held(self) -> bool: ...
    def set_link(self, edge: Edge, enable: bool) -> None: ...

class Controller:
    """One session owner; backend exceptions are fatal, including uncertain writes."""
    def __init__(self, backend: Backend):
        self.backend = backend
        self.poisoned = False

    def _idle(self):
        if (self.backend.exclusive_session_held() is not True or
                self.backend.all_cameras_stopped() is not True):
            raise Rejected("EXCLUSIVE_QUIESCENT_SESSION_REQUIRED")

    def transition(self, target: str) -> tuple[Change, ...]:
        if self.poisoned:
            raise Rejected("SESSION_POISONED")
        try:
            self._idle()
            initial = self.backend.read_graph()
            steps = plan(initial, target)
            for step in steps:
                self._idle()
                if snapshot(self.backend.read_graph()) != step.before:
                    raise Rejected("GRAPH_CHANGED_BEFORE_WRITE")
                self.backend.set_link(step.edge, step.enable)
                if snapshot(self.backend.read_graph()) != step.after:
                    raise Rejected("GRAPH_WRITE_NOT_CONFIRMED")
            self._idle()
            if snapshot(self.backend.read_graph()) != frozenset(ROUTES[target]):
                raise Rejected("FINAL_GRAPH_MISMATCH")
            return steps
        except BaseException:
            self.poisoned = True
            raise
