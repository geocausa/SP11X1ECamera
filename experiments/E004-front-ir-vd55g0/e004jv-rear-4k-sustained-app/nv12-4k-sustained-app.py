#!/usr/bin/python3
"""E004jv: bounded STDIN NV12 -> real GStreamer appsrc application consumer.

This is an OFFLINE 4K in-process application receiver for NV12 buffers,
NOT a v4l2loopback/PipeWire camera device, IR/Hello provider, or proof
of real camera video without a separately validated V4L2 producer.
No raw pixels are written to disk or printed.
"""
from __future__ import annotations
import argparse
import hashlib
import sys
import time

import gi
gi.require_version("Gst", "1.0")
from gi.repository import Gst

WIDTH = 3840
HEIGHT = 2160
FRAME_BYTES = WIDTH * HEIGHT * 3 // 2
FPS_NUM = 30
FPS_DEN = 1
FRAME_NS = 1_000_000_000 // FPS_NUM
MAX_FRAMES = 120
TIMEOUT_SECONDS = 90


def read_exact(stream, size: int) -> bytes:
    result = bytearray()
    while len(result) != size:
        block = stream.read(size - len(result))
        if not block:
            raise EOFError(f"truncated NV12 payload: {len(result)} of {size} bytes")
        result.extend(block)
    return bytes(result)


def consume(stream, frames: int, require_distinct: bool = False) -> tuple[int, int, list[int], bool]:
    if type(frames) is not int or not 1 <= frames <= MAX_FRAMES:
        raise ValueError("E004JV_FRAME_BOUND_MUST_BE_1_TO_120")
    if stream.isatty():
        raise ValueError("E004JV_REFUSE_TTY_NV12_INPUT")
    Gst.init(None)
    pipeline = Gst.parse_launch(
        "appsrc name=nv12source is-live=false format=time do-timestamp=false "
        "block=true max-bytes=24883200 "
        "caps=video/x-raw,format=NV12,width=3840,height=2160,framerate=30/1 "
        "! queue max-size-buffers=3 max-size-bytes=49766400 max-size-time=0 "
        "! videoconvert ! video/x-raw,format=I420,width=3840,height=2160 "
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
        return Gst.FlowReturn.OK
    sink.connect("new-sample", on_sample)
    started = time.monotonic()
    try:
        state = pipeline.set_state(Gst.State.PLAYING)
        if state == Gst.StateChangeReturn.FAILURE:
            raise RuntimeError("GStreamer pipeline refused PLAYING")
        for i in range(frames):
            payload = read_exact(stream, FRAME_BYTES)
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
        if stream.read(1):
            raise ValueError("E004JV_EXTRA_NV12_BYTES_AFTER_FRAME_BOUND")
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
        if len(seen) != frames:
            raise RuntimeError(f"app frame count {len(seen)} != {frames}")
        if require_distinct and len(set(hashes)) != frames:
            raise RuntimeError("E004JV_OUTPUT_FRAMES_NOT_DISTINCT")
        return (len(seen), int((time.monotonic() - started) * 1000), sink_arrival_ns,
                len(set(hashes if require_distinct else sampled_payload_hashes)) > 1)
    finally:
        pipeline.set_state(Gst.State.NULL)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bounded private NV12 -> GStreamer appsrc consumer")
    parser.add_argument("--frames", type=int, required=True)
    parser.add_argument("--require-distinct", action="store_true",
                        help="Fail unless every consumed I420 frame has different bytes")
    args = parser.parse_args()
    try:
        count, ms, arrivals, payload_variation = consume(sys.stdin.buffer, args.frames, args.require_distinct)
    except Exception as exc:
        print(f"E004JV_NV12_APPSRC_CONSUMER=FAIL {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1
    gaps_ms = [(b-a)/1e6 for a,b in zip(arrivals, arrivals[1:])]
    cadence_ms = (arrivals[-1]-arrivals[0])/1e6 if len(arrivals)>1 else 0.0
    observed_fps = (count-1)/(cadence_ms/1000) if cadence_ms>0 else 0.0
    ordered = sorted(gaps_ms)
    p95_ms = ordered[max(0, (95*len(ordered)+99)//100-1)] if ordered else 0.0
    print(
        f"E004JV_NV12_APPSRC_CONSUMER=PASS FRAMES={count} "
        f"SIZE={FRAME_BYTES} VIDEO=NV12_3840x2160_30 "
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
