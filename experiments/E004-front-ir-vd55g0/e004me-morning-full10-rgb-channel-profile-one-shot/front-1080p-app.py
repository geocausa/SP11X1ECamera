#!/usr/bin/python3
"""E004kh: bounded STDIN NV12 -> real GStreamer appsrc application consumer.

This is an FRONT RDI CANDIDATE 1080p in-process application receiver for NV12 buffers,
NOT a v4l2loopback/PipeWire camera device, IR/Hello provider, or proof
of real camera video without a separately validated V4L2 producer.
No raw pixels are written to disk or printed.
"""
from __future__ import annotations
import argparse
import hashlib
import os
import selectors
import sys
import time

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst

WIDTH = 1920
HEIGHT = 1080
FRAME_BYTES = WIDTH * HEIGHT * 3 // 2
FPS_NUM = 30
FPS_DEN = 1
FRAME_NS = 1_000_000_000 // FPS_NUM
MAX_FRAMES = 60
TIMEOUT_SECONDS = 90


class InputShortfall(Exception):
    """No optical or decoded payload bytes are exported in diagnostics."""
    pass


def read_exact_bounded(fd: int, size: int, idle_seconds: float) -> bytes:
    result = bytearray()
    with selectors.DefaultSelector() as selector:
        selector.register(fd, selectors.EVENT_READ)
        while len(result) < size:
            if not selector.select(idle_seconds):
                raise InputShortfall(f"INPUT_IDLE_TIMEOUT_OFFSET_{len(result)}")
            data = os.read(fd, min(1 << 20, size - len(result)))
            if not data:
                raise InputShortfall(f"INPUT_EOF_OFFSET_{len(result)}")
            result.extend(data)
    return bytes(result)


def consume(stream, frames: int, require_distinct: bool = False,
            idle_seconds: float = 5.0) -> tuple[int, int, list[int], bool, str]:
    if type(frames) is not int or not 1 <= frames <= MAX_FRAMES:
        raise ValueError("E004KH_FRAME_BOUND_MUST_BE_1_TO_60")
    if stream.isatty():
        raise ValueError("E004KH_REFUSE_TTY_NV12_INPUT")
    Gst.init(None)
    pipeline = Gst.parse_launch(
        "appsrc name=nv12source is-live=false format=time do-timestamp=false "
        "block=true max-bytes=6220800 "
        "caps=video/x-raw,format=NV12,width=1920,height=1080,framerate=30/1 "
        "! queue max-size-buffers=3 max-size-bytes=12441600 max-size-time=0 "
        "! videoconvert ! video/x-raw,format=I420,width=1920,height=1080 "
        "! appsink name=application emit-signals=true sync=false "
        "max-buffers=3 drop=false"
    )
    source = pipeline.get_by_name("nv12source")
    sink = pipeline.get_by_name("application")
    seen = []
    hashes = []
    sampled_payload_hashes = []
    sink_arrival_ns = []
    error = []
    def on_sample(application):
        sample = application.emit("pull-sample")
        if sample is None:
            error.append("missing GStreamer app sample")
            return Gst.FlowReturn.ERROR
        buf = sample.get_buffer()
        expected = len(seen)
        if buf.get_size() != FRAME_BYTES or buf.pts != expected * FRAME_NS:
            error.append(
                f"app payload/PTS mismatch frame={expected} size={buf.get_size()} pts={buf.pts}"
            )
            return Gst.FlowReturn.ERROR
        if require_distinct:
            hashes.append(hashlib.sha256(buf.extract_dup(0, buf.get_size())).digest())
        elif expected in (0, frames // 2, frames - 1):
            sampled_payload_hashes.append(hashlib.sha256(buf.extract_dup(0, buf.get_size())).digest())
        sink_arrival_ns.append(time.monotonic_ns())
        seen.append(buf.pts)
        if len(seen) % 10 == 0:
            seconds = (sink_arrival_ns[-1] - sink_arrival_ns[0]) / 1e9
            rate = (len(seen) - 1) / seconds if seconds > 0 else 0.0
            print(f"E004KH_APP_PROGRESS SINK_FRAMES={len(seen)} WALL_FPS={rate:.4f} "
                  "SYNTHETIC_PTS_ONLY=YES", file=sys.stderr, flush=True)
        return Gst.FlowReturn.OK
    sink.connect("new-sample", on_sample)
    started = time.monotonic()
    try:
        state = pipeline.set_state(Gst.State.PLAYING)
        if state == Gst.StateChangeReturn.FAILURE:
            raise RuntimeError("GStreamer pipeline refused PLAYING")
        pushed = 0
        shortfall = ""
        for i in range(frames):
            try:
                payload = read_exact_bounded(stream.fileno(), FRAME_BYTES, idle_seconds)
            except InputShortfall as exc:
                shortfall = str(exc)
                break
            buf = Gst.Buffer.new_allocate(None, FRAME_BYTES, None)
            if buf is None:
                raise MemoryError("GStreamer frame allocation failed")
            if buf.fill(0, payload) != FRAME_BYTES:
                raise RuntimeError("GStreamer frame buffer short fill")
            buf.pts = i * FRAME_NS
            buf.dts = Gst.CLOCK_TIME_NONE
            buf.duration = FRAME_NS
            status = source.emit("push-buffer", buf)
            if status != Gst.FlowReturn.OK:
                raise RuntimeError(f"GStreamer appsrc push frame {i} failed: {status}")
            pushed += 1
        if not shortfall:
            try:
                read_exact_bounded(stream.fileno(), 1, idle_seconds)
            except InputShortfall as exc:
                if str(exc) != "INPUT_EOF_OFFSET_0":
                    shortfall = "POSTBOUND_" + str(exc)
            else:
                raise ValueError("E004KH_EXTRA_NV12_BYTES_AFTER_FRAME_BOUND")
        status = source.emit("end-of-stream")
        if status != Gst.FlowReturn.OK:
            raise RuntimeError(f"GStreamer appsrc EOS failed: {status}")
        bus = pipeline.get_bus()
        message = bus.timed_pop_filtered(
            TIMEOUT_SECONDS * Gst.SECOND, Gst.MessageType.EOS | Gst.MessageType.ERROR
        )
        if message is None:
            raise TimeoutError("GStreamer app consumer timed out")
        if message.type == Gst.MessageType.ERROR:
            exception, debug = message.parse_error()
            raise RuntimeError(f"GStreamer app consumer error: {exception}, {debug}")
        if error:
            raise RuntimeError("; ".join(error))
        if len(seen) != pushed:
            raise RuntimeError(f"app frame count {len(seen)} != pushed {pushed}")
        if require_distinct and not shortfall and len(set(hashes)) != frames:
            raise RuntimeError("E004KH_OUTPUT_FRAMES_NOT_DISTINCT")
        return (len(seen), int((time.monotonic() - started) * 1000), sink_arrival_ns,
                len(set(hashes if require_distinct else sampled_payload_hashes)) > 1,
                shortfall)
    finally:
        pipeline.set_state(Gst.State.NULL)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded private NV12 -> GStreamer appsrc consumer")
    parser.add_argument("--frames", type=int, required=True)
    parser.add_argument("--idle-seconds", type=float, default=5.0,
                        help="Bound for waiting on each next raw frame fragment (0.1..15 s)")
    parser.add_argument("--require-distinct", action="store_true",
                        help="Fail unless every consumed I420 frame has different bytes")
    args = parser.parse_args()
    try:
        if not 0.1 <= args.idle_seconds <= 15.0:
            raise ValueError("E004KH_IDLE_BOUND_MUST_BE_0P1_TO_15")
        count, ms, arrivals, payload_variation, shortfall = consume(
            sys.stdin.buffer, args.frames, args.require_distinct, args.idle_seconds)
    except Exception as exc:
        print(f"E004KH_NV12_APPSRC_CONSUMER=FAIL {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    gaps_ms = [(b-a)/1e6 for a,b in zip(arrivals, arrivals[1:])]
    cadence_ms = (arrivals[-1]-arrivals[0])/1e6 if len(arrivals)>1 else 0.0
    observed_fps = (count-1)/(cadence_ms/1000) if cadence_ms>0 else 0.0
    ordered = sorted(gaps_ms)
    p95_ms = ordered[max(0, (95*len(ordered)+99)//100-1)] if ordered else 0.0
    print(
        f"E004KH_NV12_APPSRC_CONSUMER={'PARTIAL' if shortfall else 'PASS'} "
        f"FRAMES={count} REQUESTED_FRAMES={args.frames} "
        f"INPUT_SHORTFALL_REASON={shortfall or 'NONE'} "
        f"SIZE={FRAME_BYTES} VIDEO=NV12_1920x1080_30 "
        f"APP_CONSUMER=GSTREAMER_APPSINK_I420 "
        f"PIPELINE_MS={ms} SINK_OBSERVED_FPS={observed_fps:.4f} "
        f"SINK_P95_INTERARRIVAL_MS={p95_ms:.3f} "
        f"SINK_MAX_INTERARRIVAL_MS={max(gaps_ms,default=0):.3f} "
        f"INTERARRIVAL_SAMPLES={len(gaps_ms)} "
        f"SAMPLED_FRAME_PAYLOAD_VARIATION={'YES' if payload_variation else 'NO'} "
        f"SYNTHETIC_PTS_ONLY=YES "
        f"DISTINCT_PAYLOADS_VERIFIED={'YES' if args.require_distinct else 'NO'} "
        f"LIVE_CAMERA_PROVEN=NO "
        f"VIRTUAL_WEBCAM_CREATED=NO",
        file=sys.stderr,
    )
    return 1 if shortfall else 0


if __name__ == "__main__":
    raise SystemExit(main())
