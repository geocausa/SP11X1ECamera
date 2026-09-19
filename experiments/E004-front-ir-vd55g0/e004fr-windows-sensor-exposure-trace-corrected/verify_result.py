#!/usr/bin/env python3
"""Verify the single E004fr bounded Windows IR exposure observation offline.

Read archived raw records only. Do not access camera devices or change boot state.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from pathlib import Path
from zipfile import ZipFile
import json
import re

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
KD_SHA = "e51fe8ac39c4dcada637bf914c18c891ab81d27e974bffc0bd330f4201223722"
CAP_SHA = "079dd61665adbfe21c5f5316078e9cebb91d5462ddb05e4be79dda5233cebb78"
ARCHIVE = EVIDENCE / "ORIGINAL-WINDOWS-LOGS.zip"


def need(test: bool, reason: str) -> None:
    if not test:
        raise SystemExit("E004FR_RESULT=FAIL " + reason)


need(ARCHIVE.is_file(), "original Windows logs archive missing")
with ZipFile(ARCHIVE) as zipped:
    need(set(zipped.namelist()) == {"WINDOWS-KD.log", "WINDOWS-CAPTURE.txt"},
         "unexpected original logs archive entries")
    kd_bytes = zipped.read("WINDOWS-KD.log")
    cap_bytes = zipped.read("WINDOWS-CAPTURE.txt")
need(sha256(kd_bytes).hexdigest() == KD_SHA, "original KD log drift")
need(sha256(cap_bytes).hexdigest() == CAP_SHA, "original capture log drift")
kd = kd_bytes.decode("utf-8").replace("\r\n", "\n")
cap = cap_bytes.decode("utf-16").replace("\r\n", "\n")
for mark in ("E004FR_DRY_END_STAY_BROKEN", "E004FR_ARMED_STAY_BROKEN",
             "E004FR_BREAKPOINTS_CLEARED", "Shutdown occurred"):
    need(mark in kd, "KD lifecycle missing: " + mark)
need("Malformed string" not in kd and "Syntax error" not in kd,
     "KD parser error")
need("surfacecamauxsensor8380" in kd, "sensor driver module not observed")
need("fffff801`3c08a350" in kd, "live write-helper breakpoint not at recorded module base")
need("E004FR_SOURCE subtype=NV12 width=644 height=604 fps=60/1" in cap,
     "unexpected capture format")
need("E004FR_START=Success" in cap and "E004FR_STOP_PASS" in cap
     and "E004FR_ACQUIRED=12" in cap and "E004FR_END " in cap,
     "capture start/stop/bounds incomplete")
frames = [int(x) for x in re.findall(r"^E004FR_FRAME n=(\d+) ", cap, re.M)]
need(frames == list(range(1, 13)), "capture frame sequence")
readbacks = re.findall(r"^E004FR_EXPOSURE phase=(?:initialized|frame-\d+) auto=(\w+) .*?value_ticks=(\d+)$", cap, re.M)
need(len(readbacks) == 13 and set(readbacks) == {("True", "5000")},
     "Windows API exposure readback changed")
hits = [(int(i), int(reg, 16), int(value, 16))
        for i, reg, value in re.findall(
            r"E004FR_SENSOR_WRITE hit=(\d+) reg=([0-9a-f]+) data=([0-9a-f]+)", kd)]
need(len(hits) == 114 and [i for i, _, _ in hits] == list(range(1, 115)),
     "expected 114 contiguous observed sensor writes")
by_reg: dict[int, list[int]] = {}
for _, reg, data in hits:
    by_reg.setdefault(reg, []).append(data)
need({f"{reg:04x}": len(values) for reg, values in by_reg.items()} ==
     {"0201": 1, "0202": 1, "044d": 16, "044e": 16, "044f": 16,
      "0450": 16, "0451": 16, "0458": 16, "0459": 16},
     "unexpected register or write count")
for reg, value in ((0x0201, 1), (0x0202, 1), (0x0450, 0), (0x0451, 1)):
    need(set(by_reg[reg]) == {value}, "unexpected write data at " + hex(reg))
# These two adjacent addresses carry a coarse exposure 16-bit value in the
# pinned VD55G0 package/driver; frame length occupies the other two bytes.
exposures = [low | high << 8 for low, high in zip(by_reg[0x044e], by_reg[0x044f])]
frame_lengths = [low | high << 8 for low, high in zip(by_reg[0x0458], by_reg[0x0459])]
need(exposures == [32, 47, 71, 154, 243, 357, 853, 1234, 1866,
                   1955, 1955, 1955, 1955, 1955, 1955, 1955],
     "unexpected 16-bit coarse exposure sequence")
need(frame_lengths == [1955]*9 + [2000]*7,
     "unexpected frame length sequence")
need(all(e <= f for e, f in zip(exposures, frame_lengths)),
     "exposure exceeds programmed frame length")
need(len(by_reg[0x044d]) == len(exposures), "gain sequence incomplete")
result = {
    "experiment": "E004fr",
    "status": "PASS_BOUNDED_WINDOWS_SENSOR_REGISTER_WRITE_OBSERVATION",
    "date": "2026-09-19",
    "scope": "single fresh Windows one-shot, normal IR preview, 12 acquired frames",
    "kd_log_sha256": KD_SHA,
    "capture_log_sha256": CAP_SHA,
    "driver": "surfacecamauxsensor8380.sys",
    "fresh_module_base": "fffff8013c080000",
    "write_helper_hook": "fffff8013c08a350",
    "kd_arm_validation": "PASS; exactly one breakpoint, target left broken before manual resume",
    "kd_breakpoint_cleanup": "PASS; empty breakpoint list, target resumed",
    "windows_capture": {"format": "NV12", "width": 644, "height": 604,
                        "reported_fps": "60/1", "frames_acquired": 12,
                        "stop": "PASS", "image_files_saved": False,
                        "exposure_api_auto": True,
                        "exposure_api_value_ticks": 5000},
    "observed_writes": len(hits),
    "observed_register_write_counts": {f"{reg:04x}": len(v) for reg, v in sorted(by_reg.items())},
    "observed_coarse_exposure_lines": exposures,
    "observed_frame_length_lines": frame_lengths,
    "observed_analogue_gain_codes": by_reg[0x044d],
    "observed_gpio_strobe_register_writes": 0,
    "caveats": [
        "These are driver write-call arguments, not electrical pulse or optical measurements.",
        "Sixteen register programming groups were observed during twelve acquired frames; no 1:1 frame/group pairing was established.",
        "The standard Windows exposure API reported Auto=True and 5000 ticks even while sensor coarse exposure writes changed.",
        "No 0x0467..0x046e write occurred during this bounded session; prior static initial configuration is separate evidence.",
        "This sensor-only trace does not close PMIC timer/current/timeout requirements, emitter safety, useful optical image quality or face authentication."
    ],
    "golden_return": "verified separately after Windows reboot; see project checkpoint",
    "native_linux_emitter_enabled": False
}
(EVIDENCE / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
print("E004FR_RESULT=PASS WINDOWS_FRAMES=12 SENSOR_WRITES=114 OBSERVED_GROUPS=16")
print("COARSE_EXPOSURE_LINES=" + ",".join(map(str, exposures)))
print("FRAME_LENGTH_LINES=" + ",".join(map(str, frame_lengths)))
print("AUTHORIZATION_FOR_LINUX_EMITTER=NO")
