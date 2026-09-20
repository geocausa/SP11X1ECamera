#!/usr/bin/env python3
"""E004jy source-locked, non-image, complete-or-partial camera pipeline audit."""
from __future__ import annotations
import argparse
from pathlib import Path
import re
import sys


def check(source_text: str, reader_text: str, app_text: str,
          publisher_rc: int, reader_rc: int, events_text: str) -> tuple[dict, bool]:
    source = [int(x) for x in re.findall(
        r"cap dqbuf:\s*\d+ seq:\s*(\d+) bytesused:\s*14321824", source_text)]
    ts = [float(x) for x in re.findall(r"ts:\s*([0-9]+\.[0-9]+)", source_text)]
    virt = [int(x) for x in re.findall(
        r"cap dqbuf:\s*\d+ seq:\s*(\d+) bytesused:\s*12441600", reader_text)]
    match = re.search(
        r"E004JX_NV12_APPSRC_CONSUMER=(PASS|PARTIAL) FRAMES=(\d+)"
        r" REQUESTED_FRAMES=90 INPUT_SHORTFALL_REASON=([A-Z0-9_]+)"
        r".*?\bSINK_OBSERVED_FPS=([0-9]+(?:\.[0-9]+)?)"
        r"\s+SINK_P95_INTERARRIVAL_MS=([0-9]+(?:\.[0-9]+)?)"
        r"\s+SINK_MAX_INTERARRIVAL_MS=([0-9]+(?:\.[0-9]+)?)"
        r"\s+INTERARRIVAL_SAMPLES=(\d+)", app_text)
    events = dict(re.findall(r"(?m)^([A-Z_]+)=(\d+)$", events_text))
    for required in ("PUBLISHER_START_NS", "VIRTUAL_FORMAT_READY_NS",
                     "READER_START_NS", "READER_END_NS", "PUBLISHER_END_NS"):
        if required not in events:
            raise ValueError(f"MISSING_EVENT_{required}")
    times = {k: int(v) for k, v in events.items()}
    if not (times["PUBLISHER_START_NS"] <= times["VIRTUAL_FORMAT_READY_NS"]
            <= times["READER_START_NS"] <= times["READER_END_NS"]):
        raise ValueError("INVALID_SUBSCRIBER_TIMELINE")
    if times["PUBLISHER_END_NS"] < times["PUBLISHER_START_NS"]:
        raise ValueError("INVALID_PUBLISHER_TIMELINE")
    if not source or not virt or len(source) != len(ts):
        raise ValueError("MISSING_SOURCE_OR_COMPLETE_READER_FRAMES")
    if not all(a < b for a, b in zip(source, source[1:])):
        raise ValueError("NONMONOTONIC_SENSOR_SEQUENCE")
    if not all(a < b for a, b in zip(ts, ts[1:])):
        raise ValueError("NONMONOTONIC_SENSOR_TIMESTAMP")
    if not all(a < b for a, b in zip(virt, virt[1:])):
        raise ValueError("NONMONOTONIC_VIRTUAL_SEQUENCE")
    if match is None:
        raise ValueError("NO_FINAL_COMPLETED_OR_PARTIAL_APPSINK_TIMING")
    verdict, num, reason, fps, p95, maximum, intervals = match.groups()
    app_frames = int(num)
    if (app_frames < 1 or app_frames > 90 or app_frames > len(virt)
            or int(intervals) != app_frames - 1):
        raise ValueError("INCONSISTENT_APP_SINK_FRAME_COUNT")
    if verdict == "PASS" and (app_frames != 90 or reason != "NONE"):
        raise ValueError("FALSE_APPLICATION_SUCCESS")
    if verdict == "PARTIAL" and (app_frames >= 90 or reason == "NONE"):
        raise ValueError("FALSE_APPLICATION_PARTIAL")
    if publisher_rc == 0 and len(source) != 180:
        raise ValueError("PUBLISHER_SUCCESS_WITH_INCOMPLETE_SOURCE")
    source_seconds = ts[-1] - ts[0] if len(ts) > 1 else 0
    source_fps = (len(ts) - 1) / source_seconds if source_seconds > 0 else 0.0
    missing_source = sum(max(0, b-a-1) for a, b in zip(source, source[1:]))
    missing_virtual = sum(max(0, b-a-1) for a, b in zip(virt, virt[1:]))
    result = {
        "sensor_frames": len(source), "sensor_first_seq": source[0],
        "sensor_last_seq": source[-1], "sensor_missing_seq": missing_source,
        "source_delivered_fps": round(source_fps, 4),
        "virtual_full_frames": len(virt), "virtual_first_seq": virt[0],
        "virtual_last_seq": virt[-1], "virtual_missing_seq": missing_virtual,
        "app_verdict": verdict, "app_frames": app_frames,
        "app_shortfall": reason, "app_observed_fps": fps,
        "app_p95_gap_ms": p95, "app_max_gap_ms": maximum,
        "publisher_rc": publisher_rc, "reader_rc": reader_rc,
        "format_ready_to_reader_ms": round((times["READER_START_NS"] -
            times["VIRTUAL_FORMAT_READY_NS"]) / 1e6, 3),
        "publisher_to_reader_start_ms": round((times["READER_START_NS"] -
            times["PUBLISHER_START_NS"]) / 1e6, 3),
        "publisher_lifetime_ms": round((times["PUBLISHER_END_NS"] -
            times["PUBLISHER_START_NS"]) / 1e6, 3),
        "subscriber_lifetime_ms": round((times["READER_END_NS"] -
            times["READER_START_NS"]) / 1e6, 3),
    }
    success = (publisher_rc == 0 and reader_rc == 0 and len(source) == 180
               and len(virt) == 90 and app_frames == 90 and verdict == "PASS")
    return result, success


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("reader")
    parser.add_argument("app")
    parser.add_argument("events")
    parser.add_argument("--publisher-rc", type=int, required=True)
    parser.add_argument("--reader-rc", type=int, required=True)
    args = parser.parse_args()
    try:
        data, success = check(
            Path(args.source).read_text(), Path(args.reader).read_text(),
            Path(args.app).read_text(), args.publisher_rc, args.reader_rc,
            Path(args.events).read_text())
    except Exception as err:
        print(f"E004JY_TEXT_ONLY_TELEMETRY=INVALID {type(err).__name__}: {err}",
              file=sys.stderr)
        return 2
    print("E004JY_TEXT_ONLY_TELEMETRY=" + ("COMPLETE_PASS" if success else "PARTIAL_FAIL_CLOSED")
          + " " + " ".join(f"{k}={v}" for k, v in data.items())
          + " CAMERA_FPS_INDEPENDENT_OF_SYNTHETIC_PTS=YES WINDOWS_QUALITY_PARITY=NO")
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
