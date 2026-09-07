#!/usr/bin/env python3
"""Bounded offline model of the ordinary SP11 front AEC request state.

This state layer intentionally keeps the still-unresolved semantic name of the
Algorithm001 F-3 history scalar abstract.  Its byte identity and timing are
closed; its producer semantic is not guessed here.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
import struct
from typing import Dict, Iterable, Optional, Tuple

EPS_BITS = 0x33D6BF95
LUX_K_BITS = 0x429BCC0C
LUX_TARGET_BITS = 0x42480000  # 50.0f, pinned Algorithm001 path


def f32(x: float) -> float:
    return struct.unpack('<f', struct.pack('<f', float(x)))[0]


def from_bits(bits: int) -> float:
    return struct.unpack('<f', struct.pack('<I', int(bits) & 0xFFFFFFFF))[0]


def bits(x: float) -> int:
    return struct.unpack('<I', struct.pack('<f', f32(x)))[0]


EPS = from_bits(EPS_BITS)
LUX_K = from_bits(LUX_K_BITS)
LUX_TARGET = from_bits(LUX_TARGET_BITS)

# FrameSA_Target tuning regions from pinned entry 3603.
# (start, end, targetLow=targetHigh)
FRAME_SA_TARGET_REGIONS = (
    (0.0, 140.0, 55.0),
    (160.0, 270.0, 50.0),
    (300.0, 360.0, 46.0),
    (370.0, 410.0, 40.0),
    (420.0, 460.0, 40.0),
    (500.0, 1000.0, 30.0),
)


def framesa_target_low(lux_trigger: float) -> float:
    """Pinned FrameSA targetLow with Windows-style gap interpolation."""
    x = f32(lux_trigger)
    regs = FRAME_SA_TARGET_REGIONS
    if x < regs[0][0]:
        return f32(regs[0][2])
    prev = regs[0]
    for i, cur in enumerate(regs):
        start, end, value = cur
        if x < start:
            # Interpolate from previous region's end/value to current start/value.
            p_end, p_value = prev[1], prev[2]
            den = f32(start - p_end)
            t = f32(f32(x - p_end) / den)
            return f32(f32(f32(1.0 - t) * f32(p_value)) + f32(t * f32(value)))
        if x <= end:
            return f32(value)
        prev = cur
    return f32(regs[-1][2])


def target_si(source_exposure_s1: int, measured_luma: float, target_low: float) -> int:
    """BD normal positive-finite scalar: Safe <- S1 for FrameSA."""
    if source_exposure_s1 < 0:
        raise ValueError('source exposure must be non-negative')
    measured = f32(measured_luma)
    target = f32(target_low)
    den = measured if measured > EPS else EPS
    ratio = f32(target / den)
    product = float(source_exposure_s1) * float(ratio)
    if not math.isfinite(product) or product < 0.0:
        raise ValueError('non-finite/negative SI product')
    return int(product)  # positive FCVTZU semantics


def algorithm001_lux(measured_luma: float, history_reference: float,
                     previous_lux: float = 0.0, alpha: float = 0.0) -> float:
    """AB bit-exact normal Algorithm001 arithmetic.

    The pinned front runs have alpha == 0.0, but the optional blend is retained
    so the state transition matches the disassembled branch.
    """
    measured = f32(measured_luma)
    baseline = f32(history_reference)
    previous = f32(previous_lux)
    alpha = f32(alpha)
    den = measured if measured > EPS else EPS
    num = LUX_TARGET if LUX_TARGET > EPS else EPS
    ratio = f32(num / den)
    delta = f32(0.0)
    if ratio > 0.0:
        delta = f32(math.log10(float(ratio)) * float(LUX_K))
    candidate = f32(baseline + delta)
    if candidate < 0.0:
        candidate = f32(0.0)
    if abs(previous) >= 0.5:
        candidate = f32(f32(f32(1.0 - alpha) * candidate) + f32(alpha * previous))
    return candidate


@dataclass(frozen=True)
class RequestResult:
    frame_id: int
    lux_trigger_in: float
    target_low: float
    measured_luma: float
    frame_sa_safe_si: int
    history_reference_frame: int
    history_reference: float
    next_lux_trigger: float
    external_lux_publication: Optional[float]
    previous_exposure_frame: Optional[int]
    previous_exposure_lanes: Optional[Tuple[int, ...]]


class AECRequestState:
    """Offline request-state coordinator for the proven ordinary front path.

    Temporal boundaries are kept distinct:
      * FrameSA target reads the trigger value present at request entry.
      * Algorithm001 reads an explicitly committed history reference at F-3.
      * Algorithm001 writes the internal (9,8) Lux trigger in request F.
      * the same Algorithm001 result is externally observable at F+2.
      * downstream convergence may consume separately committed exposure F-1.

    `commit_history_reference()` is deliberately explicit: BH proves where
    Algorithm001 reads the scalar but does not guess its semantic producer.
    """
    def __init__(self, initial_lux_trigger: float, *, algorithm001_alpha: float = 0.0):
        self.lux_trigger = f32(initial_lux_trigger)
        self.algorithm001_alpha = f32(algorithm001_alpha)
        self.history_reference: Dict[int, float] = {}
        self.exposure_history: Dict[int, Tuple[int, ...]] = {}
        self.pending_external_lux: Dict[int, float] = {}

    def commit_history_reference(self, frame_id: int, value: float) -> None:
        self.history_reference[int(frame_id)] = f32(value)

    def commit_exposure_history(self, frame_id: int, lanes: Iterable[int]) -> None:
        v = tuple(int(x) for x in lanes)
        if len(v) != 7 or any(x < 0 for x in v):
            raise ValueError('exposure history must contain seven non-negative lanes')
        self.exposure_history[int(frame_id)] = v

    def process_request(self, frame_id: int, measured_luma: float,
                        source_exposure_s1: int) -> RequestResult:
        f = int(frame_id)
        href_frame = f - 3
        if href_frame not in self.history_reference:
            raise KeyError(f'missing Algorithm001 F-3 history reference for frame {href_frame}')

        # Ordering is intentional: target uses the trigger state visible on entry.
        lux_in = self.lux_trigger
        target = framesa_target_low(lux_in)
        measured = f32(measured_luma)
        si = target_si(int(source_exposure_s1), measured, target)

        href = self.history_reference[href_frame]
        next_lux = algorithm001_lux(measured, href, lux_in, self.algorithm001_alpha)

        publication = self.pending_external_lux.pop(f, None)
        self.pending_external_lux[f + 2] = next_lux
        self.lux_trigger = next_lux

        prev_frame = f - 1
        prev = self.exposure_history.get(prev_frame)
        return RequestResult(
            frame_id=f,
            lux_trigger_in=lux_in,
            target_low=target,
            measured_luma=measured,
            frame_sa_safe_si=si,
            history_reference_frame=href_frame,
            history_reference=href,
            next_lux_trigger=next_lux,
            external_lux_publication=publication,
            previous_exposure_frame=prev_frame if prev is not None else None,
            previous_exposure_lanes=prev,
        )
