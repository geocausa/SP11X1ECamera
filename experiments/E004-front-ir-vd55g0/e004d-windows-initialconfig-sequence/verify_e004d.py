#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, subprocess, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
E004A = REPO / "experiments/E004-front-ir-vd55g0/e004a-windows-authority"
E004C = REPO / "experiments/E004-front-ir-vd55g0/e004c-bounded-linux-idprobe"
PACKAGE = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamauxsensor_extension8380.inf_arm64_84ddd55dc933cac9/com.surface.sensormodule.aux_vd55g0_MSHW0492.bin")
PACKET = E004A / "E004_IR_4C74_PACKET_20260912.bin"
AUX = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamauxsensor8380.inf_arm64_7d23cd8fdfa9b39f/surfacecamauxsensor8380.sys")
DECODE = HERE / "WINDOWS-INITIALCONFIG-DECODE.json"
DECODER = HERE / "decode_windows_initialconfig.py"

PACKAGE_SHA = "e574db7eb28231d3fa4f5eee5c1861919125d8ec7a753fc7a0708606e1f1a794"
PACKET_SHA = "81e96e0470cbfa58065eba12ea1a998349b306111f2edee296d7044a69146cdd"
AUX_SHA = "e5b6b064f39cf239ab07e22ca2434e3c08c93b691dc7d27cebb90861226efa75"
PATCH_SHA = "5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321"


def need(v, m):
    if not v:
        raise AssertionError(m)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def norm(s):
    return re.sub(r"\s+", " ", s)


def disasm(start, stop):
    return subprocess.check_output([
        "llvm-objdump", "-d", "--no-show-raw-insn",
        f"--start-address=0x{start:x}", f"--stop-address=0x{stop:x}", str(AUX)
    ], text=True)


def assert_all(text, tokens, label):
    n = norm(text)
    for token in tokens:
        need(norm(token) in n, f"{label}: missing {token}")


def main():
    subprocess.run(["python3", str(E004A / "verify.py")], check=True, stdout=subprocess.DEVNULL)
    subprocess.run(["python3", str(E004C / "verify-runtime.py")], check=True, stdout=subprocess.DEVNULL)

    need(sha(PACKAGE) == PACKAGE_SHA, "Surface package hash")
    need(sha(PACKET) == PACKET_SHA, "live InitialConfig packet hash")
    need(sha(AUX) == AUX_SHA, "exact aux driver hash")

    # Re-run decoder from raw authority and require exact saved JSON.
    fresh = json.loads(subprocess.check_output(["python3", str(DECODER)], text=True))
    saved = json.load(open(DECODE))
    need(fresh == saved, "saved decode differs from fresh mechanical replay")

    p = saved["live_initialconfig_packet"]
    need(p == {
        "path": str(PACKET),
        "sha256": PACKET_SHA,
        "bytes": 4880,
        "commands": 7,
        "poll_commands": 4,
        "write_commands": 3,
        "write_entries": 597,
    }, "packet summary")
    replay = saved["package_replay"]
    need(replay["rows_matched_exactly"] == 601, "601 package rows")
    need(replay["rows_unmatched"] == 0 and replay["packet_extra_operations"] == 0, "no replay mismatch")
    need([(x["kind"], x["package_row_start"], x["package_row_end"]) for x in replay["partition"]] == [
        ("poll", 0, 0),
        ("write", 1, 553),
        ("poll", 554, 554),
        ("write", 555, 555),
        ("poll", 556, 556),
        ("poll", 557, 557),
        ("write", 558, 600),
    ], "command partition")

    need(saved["surface_patch"]["bytes"] == 552, "patch size")
    need(saved["surface_patch"]["sha256"] == PATCH_SHA, "Surface patch hash")
    need(saved["surface_patch"]["followed_immediately_by"] ==
         "write 0x0200=0x02 in same 553-write Windows command", "patch setup adjacency")

    timeline = saved["timeline"]
    expected = [
        ("poll 0x002c == 0x01", 6),
        ("write 0x2000..0x2227 (552 bytes), then write 0x0200=0x02", None),
        ("poll 0x0200 == 0x00", 28),
        ("write 0x0200=0x01", None),
        ("poll 0x0200 == 0x00", 6),
        ("poll 0x002c == 0x02", 4),
        ("write 43 post-boot timing/config registers", None),
    ]
    need([(x["windows_fact"], x.get("timeout_ms")) for x in timeline] == expected, "timeline")

    post = saved["post_boot_config"]["decoded_windows_values"]
    need(post["ext_clock_hz"] == 19_200_000, "ext clock")
    need(post["mipi_data_rate_bps"] == 840_000_000, "MIPI data rate")
    need(post["line_length"] == 1200 and post["frame_length"] == 1955, "frame timing")
    need(post["roi_x_start"] == 0 and post["roi_x_end"] == 643, "full-width ROI")
    need(post["roi_y_start"] == 0 and post["roi_y_end"] == 603, "full-height ROI")
    need(post["y_start"] == 0 and post["y_end"] == 603, "vertical output")
    need(post["gpio_ctrl"] == [1, 2, 1, 1], "Windows GPIO control bytes")
    need(saved["post_boot_config"]["reference_only_interpretation"]["source"].startswith("public ST driver naming only"), "reference role")

    c = json.load(open(E004C / "RESULT.json"))
    need(c["status"] == "PASS_BOUNDED_LINUX_IDENTITY_REVISION_GOLDEN_RETURN_RETIRED", "E004c pass")
    need(c["revision"]["hex"] == "0x1111" and c["revision"]["classification"] == "CUT1", "actual silicon CUT1")
    need(c["model"]["big_endian_hex"] == "0x3047" and c["model"]["windows_qti_match"] is True, "actual model identity")

    # Exact driver command parser proof:
    # +0x70f8 recognizes the 20-byte poll record, takes timeout from +4,
    # register from +8 and expected value from +0xc.
    wait = disasm(0x1400070f8, 0x1400072c0)
    assert_all(wait, [
        "ldrb w10, [x19, #0x2]",
        "cmp w10, #0x1",
        "ldrb w8, [x19, #0x3]",
        "cmp w8, #0x9",
        "ldrh w5, [x19, #0x4]",
        "ldrh w3, [x19, #0x8]",
        "ldr w9, [x19, #0xc]",
        "mov w8, #0x14",
        "strh w8, [x1]",
        "mov w0, #0x1",
        "bl 0x140003840",
    ], "wait parser")

    # The delay helper multiplies its integer argument by -10000 and sends
    # the resulting relative interval to KeDelayExecutionThread. NT intervals
    # are 100 ns, therefore one parser loop unit is 1 ms.
    delay = disasm(0x140003840, 0x140003880)
    assert_all(delay, [
        "ubfx x9, x0, #0, #32",
        "mov x8, #-0x2710",
        "mul x8, x9, x8",
        "str x8, [sp, #0x10]",
    ], "delay helper")
    imports = subprocess.check_output(["llvm-readobj", "--coff-imports", str(AUX)], text=True)
    need("Symbol: KeDelayExecutionThread" in imports, "KeDelayExecutionThread import")

    # SubmitSeqCmd obtains total byte length from descriptor +8, advances by
    # each decoded command length, and interprets write records as count*8+8.
    seq = disasm(0x140009220, 0x140009530)
    assert_all(seq, [
        "ldr w21, [x22, #0x8]",
        "ldr x8, [x22]",
        "add x20, x8, w23, uxtw",
        "bl 0x1400070f8",
        "ldrh w8, [x20]",
        "lsl w1, w8, #3",
        "add w8, w1, #0x8",
        "ldrb w10, [x20, #0x5]",
        "ldrb w9, [x20, #0x4]",
        "ldrh w8, [x22, #0x8]",
        "ldrh w8, [x22, #0xc]",
        "add w23, w19, w23",
    ], "SubmitSeqCmd")

    # Exact write helper branch for address type 2 + data type 1.
    wr = disasm(0x14000a350, 0x14000a4e8)
    assert_all(wr, [
        "cmp w10, #0x2",
        "cmp w9, #0x1",
        "strh w8, [x0, #0x28]",
        "strb w11, [x10]",
    ], "write helper")

    need(saved["linux_authorization"]["sensor_data_write_authorized"] is False, "Linux writes remain closed")

    result = {
        "schema": "sp11-camera-e004d-windows-initialconfig-authority-v1",
        "status": "PASS_OFFLINE_WINDOWS_INITIALCONFIG_SEQUENCE_RECONSTRUCTED",
        "authority": "same-machine Windows exact Surface package + exact live first-start InitialConfig packet + exact installed aux driver",
        "surface_package_sha256": PACKAGE_SHA,
        "live_packet_sha256": PACKET_SHA,
        "aux_driver_sha256": AUX_SHA,
        "packet_bytes": 4880,
        "packet_commands": 7,
        "package_rows_replayed_exactly": 601,
        "polls": [
            {"reg": "0x002c", "expected": "0x01", "timeout_ms": 6},
            {"reg": "0x0200", "expected": "0x00", "timeout_ms": 28},
            {"reg": "0x0200", "expected": "0x00", "timeout_ms": 6},
            {"reg": "0x002c", "expected": "0x02", "timeout_ms": 4},
        ],
        "write_blocks": [553, 1, 43],
        "surface_patch": {"bytes": 552, "sha256": PATCH_SHA},
        "actual_linux_proven_sensor_revision": "0x1111 CUT1",
        "post_boot_windows_config": {
            "ext_clock_hz": 19_200_000,
            "mipi_data_rate_bps": 840_000_000,
            "line_length": 1200,
            "frame_length": 1955,
            "gpio_ctrl_raw": [1, 2, 1, 1],
        },
        "reference_only_interpretation": {
            "0x0200=2": "PATCH_SETUP",
            "0x0200=1": "BOOT",
            "0x002c=1": "READY_TO_BOOT",
            "0x002c=2": "SW_STBY",
            "gpio_ctrl_1_2_1_1": "ST naming maps GPIO1 value 2 to STROBE and values 1 to DISABLED",
        },
        "linux_sensor_data_write_authorized": False,
        "next_gate": "Design and checkpoint a bounded Linux Surface-patch/setup/boot experiment that preserves this exact Windows ordering and polls, while still prohibiting streaming and external illumination.",
    }
    (HERE / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

    print("E004D_VERIFY=PASS WINDOWS_INITIALCONFIG=7_COMMANDS PACKAGE_ROWS=601 EXACT_REPLAY=YES")
    print("E004D_SEQUENCE=POLL_002c_1_6ms -> WRITE_552B_SURFACE_PATCH+0200_2 -> POLL_0200_0_28ms -> WRITE_0200_1 -> POLL_0200_0_6ms -> POLL_002c_2_4ms -> WRITE_43_CONFIG")
    print("E004D_DRIVER_SEMANTICS=PASS POLL_RECORD=20B WRITE_RECORD=count*8+8 POLL_CADENCE=1ms")
    print("E004D_ACTUAL_SENSOR=CUT1_0x1111 SURFACE_PATCH_SHA256=" + PATCH_SHA)
    print("E004D_LINUX_WRITE_AUTHORIZED=NO")


if __name__ == "__main__":
    main()
