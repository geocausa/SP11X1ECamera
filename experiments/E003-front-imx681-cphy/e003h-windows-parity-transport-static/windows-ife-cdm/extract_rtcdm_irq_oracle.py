#!/usr/bin/env python3
"""Fail-closed extractor for the same-machine Windows RT-CDM IRQ resource oracle."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

EXPECTED_SHA256 = "0f4b30273ddd7af23bbad5158b2da57a320c143b43ce5119927bbfbcfa6cbf1b"
EXPECTED_BYTES = 7428
EXPECTED = {
    0: {
        "class": 3,
        "instance": 0,
        "raw_gsi": 0x1E8,
        "raw_vector": 0x1E8,
        "translated_level": 0xA,
        "translated_vector": 0xA52,
    },
    1: {
        "class": 3,
        "instance": 1,
        "raw_gsi": 0x13F,
        "raw_vector": 0x13F,
        "translated_level": 0xB,
        "translated_vector": 0xB53,
    },
}

DESC_RE = re.compile(
    r"^[0-9a-f]{8}`[0-9a-f]{8}\s+"
    r"(?P<header>[0-9a-f]{8})\s+"
    r"(?P<level>[0-9a-f]{8})\s+"
    r"(?P<vector>[0-9a-f]{8})\s+"
    r"(?P<affinity>[0-9a-f]{8})$",
    re.IGNORECASE,
)


def die(msg: str) -> None:
    raise SystemExit(f"FAIL: {msg}")


def parse_descriptor(line: str) -> dict[str, int]:
    match = DESC_RE.match(line.strip())
    if not match:
        die(f"malformed CM_PARTIAL_RESOURCE_DESCRIPTOR line: {line!r}")
    values = {key: int(value, 16) for key, value in match.groupdict().items()}
    header = values["header"]
    values.update(
        {
            "type": header & 0xFF,
            "share_disposition": (header >> 8) & 0xFF,
            "flags": (header >> 16) & 0xFFFF,
        }
    )
    if (values["type"], values["share_disposition"], values["flags"]) != (2, 1, 1):
        die(f"descriptor is not the expected exclusive latched interrupt: {values}")
    return values


def section(lines: list[str], marker: str) -> tuple[int, int]:
    try:
        start = lines.index(marker)
    except ValueError:
        die(f"missing marker {marker}")
    end = len(lines)
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("==="):
            end = i
            break
    return start, end


def parse_instance(lines: list[str], instance: int) -> dict[str, object]:
    marker = f"===RTCDM{instance}_CLASS3_INSTANCE{instance}==="
    start, end = section(lines, marker)
    body = [line.strip() for line in lines[start + 1 : end] if line.strip()]
    if not body:
        die(f"empty section for RT_CDM_{instance}")

    if instance == 0:
        match = re.fullmatch(r"class=(\d+)\s+instance=(\d+)", body[0])
    else:
        match = re.fullmatch(
            r"class=([0-9a-f]+)\s+instance=([0-9a-f]+)\s+raw=([0-9a-f]+)\s+translated=([0-9a-f]+)",
            body[0],
            re.IGNORECASE,
        )
    if not match:
        die(f"malformed class/instance record for RT_CDM_{instance}: {body[0]!r}")

    base = 16 if instance == 1 else 10
    cls = int(match.group(1), base)
    inst = int(match.group(2), base)
    expected = EXPECTED[instance]
    if cls != expected["class"] or inst != expected["instance"]:
        die(f"unexpected class/instance for RT_CDM_{instance}: class={cls} instance={inst}")

    descriptor_lines = [line for line in body[1:] if DESC_RE.match(line)]
    if len(descriptor_lines) != 2:
        die(f"expected exactly two descriptor heads for RT_CDM_{instance}, got {len(descriptor_lines)}")
    raw = parse_descriptor(descriptor_lines[0])
    translated = parse_descriptor(descriptor_lines[1])

    if raw["level"] != expected["raw_gsi"] or raw["vector"] != expected["raw_vector"]:
        die(f"RT_CDM_{instance} raw IRQ mismatch: {raw}")
    if translated["level"] != expected["translated_level"] or translated["vector"] != expected["translated_vector"]:
        die(f"RT_CDM_{instance} translated IRQ mismatch: {translated}")

    return {
        "interrupt_class": cls,
        "instance": inst,
        "raw": {
            "gsi_level": raw["level"],
            "vector": raw["vector"],
            "affinity": raw["affinity"],
            "type": raw["type"],
            "share_disposition": raw["share_disposition"],
            "flags": raw["flags"],
        },
        "translated_windows": {
            "level": translated["level"],
            "vector": translated["vector"],
            "affinity": translated["affinity"],
        },
    }


def main() -> None:
    here = Path(__file__).resolve().parent
    default_input = here.parent / "raw" / "E003H_RTCDM_IRQ_MAP_20260828.log"
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=default_input)
    parser.add_argument("--output", type=Path, default=here / "rtcdm-irq-oracle-summary.json")
    args = parser.parse_args()

    raw_bytes = args.input.read_bytes()
    digest = hashlib.sha256(raw_bytes).hexdigest()
    if len(raw_bytes) != EXPECTED_BYTES:
        die(f"raw byte count changed: {len(raw_bytes)} != {EXPECTED_BYTES}")
    if digest != EXPECTED_SHA256:
        die(f"raw SHA-256 changed: {digest} != {EXPECTED_SHA256}")

    try:
        text = raw_bytes.decode("utf-16")
    except UnicodeError as exc:
        die(f"raw log is not valid UTF-16: {exc}")
    lines = text.splitlines()

    if lines.count("===E003H_RTCDM_IRQ_MAP===") != 1:
        die("capture header missing or duplicated")
    if not any(re.search(r"\bqccamisp8380\b", line, re.IGNORECASE) for line in lines):
        die("qccamisp8380 module identity missing")
    if not any("Wdf01000!FxPnpDevicePrepareHardware::InvokeClient" in line for line in lines):
        die("PrepareHardware call-stack proof missing")

    rtcdm0 = parse_instance(lines, 0)
    rtcdm1 = parse_instance(lines, 1)

    summary = {
        "schema": "sp11-e003h-rtcdm-irq-oracle-v1",
        "source": {
            "path": str(args.input.relative_to(here.parent)),
            "bytes": len(raw_bytes),
            "sha256": digest,
            "encoding": "UTF-16LE with BOM",
            "machine": "same SP11 Windows oracle",
            "driver": "qccamisp8380.sys",
            "capture_context": "WDF PrepareHardware dedicated RT-CDM interrupt registration",
        },
        "rt_cdm_0": rtcdm0,
        "rt_cdm_1": rtcdm1,
        "linux_parity_consequence": {
            "rt_cdm_1_firmware_gsi": rtcdm1["raw"]["gsi_level"],
            "rt_cdm_1_firmware_gsi_hex": f"0x{rtcdm1['raw']['gsi_level']:x}",
            "gic_spi_dt_cell": rtcdm1["raw"]["gsi_level"] - 32,
            "gic_spi_dt_cell_hex": f"0x{rtcdm1['raw']['gsi_level'] - 32:x}",
            "namespace_rule": "ARM GIC DT SPI cell = firmware GSI/INTID - 32",
            "sp11_crosscheck": "existing csid0/vfe0/csid1/vfe1/csid_lite0/vfe_lite0 DT cells 464..469 map to Windows ISP GSIs 496..501",
            "windows_translated_vector_is_not_linux_dt_spi": True,
        },
        "accepted": True,
    }

    args.output.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(
        "PASS: RT_CDM1 class=3 instance=1 raw GSI="
        f"{rtcdm1['raw']['gsi_level']} (0x{rtcdm1['raw']['gsi_level']:x}); "
        f"summary={args.output}"
    )


if __name__ == "__main__":
    main()
