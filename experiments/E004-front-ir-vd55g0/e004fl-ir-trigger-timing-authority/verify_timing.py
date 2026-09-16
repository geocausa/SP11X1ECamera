#!/usr/bin/env python3
"""Verify local binary constants and prior Windows sensor timing evidence.

No hardware I/O. Handler semantics are manually reviewed at README RVAs;
constant checks do not independently prove arbitrary control flow.
"""
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import pefile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
ARCHIVE = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
EXPECTED = {
    "qccamflash8380.sys": "6bc1d698bc3b6da16974cd6f3ea89dc1ba6a8ea102eebe1a5d41129b4eb9ba2b",
    "qcpmic8380.sys": "756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e",
}

def main():
    images, hashes = {}, {}
    for name, expected in EXPECTED.items():
        matches = list(ARCHIVE.glob("*/" + name))
        assert len(matches) == 1
        data = matches[0].read_bytes()
        assert hashlib.sha256(data).hexdigest() == expected
        images[name] = pefile.PE(data=data)
        hashes[name] = expected
    flash, pmic = images.values()

    def u32(image, rva):
        return struct.unpack("<I", image.get_data(rva, 4))[0]

    def u64(image, rva):
        return struct.unpack("<Q", image.get_data(rva, 8))[0]

    commands = []
    for label, frva, prva, code, offset, target in [
        ("trigger input selector", 0x6238, 0x7c14, 0x802f0fcc, 0x70, 0x27f20),
        ("trigger mode", 0x623c, 0x7c18, 0x802f0fd0, 0x80, 0x281e0),
        ("safety timer", 0x4e80, 0x7bf8, 0x802f0fac, 0x28, 0x26d50),
    ]:
        assert u32(flash, frva) == u32(pmic, prva) == code
        assert u64(pmic, 0x39470 + offset) == 0x140000000 + target
        commands.append({"name": label, "command": hex(code),
                         "active_table_callback_rva": hex(target)})
    timer_regs = [u32(pmic, 0x36d48 + i * 4) for i in range(4)]
    assert timer_regs == [0xee3e, 0xee3f, 0xee40, 0xee41]
    assert [u32(flash, 0x4e78 + i * 4) for i in range(2)] == [1270, 1270]
    reciprocal = u32(pmic, 0x26f28)
    assert reciprocal == 0xcccccccd
    # Check recovered divide-by-ten arithmetic for the complete accepted range.
    for ms in range(10, 1281):
        encoded = ((ms - 10) * reciprocal >> 35) & 255
        assert encoded == (ms - 10) // 10

    decoder = REPO / "experiments/E004-front-ir-vd55g0/e004d-windows-initialconfig-sequence/decode_windows_initialconfig.py"
    decoded = json.loads(subprocess.check_output(["python3", str(decoder)], text=True))
    saved = json.loads((decoder.parent / "WINDOWS-INITIALCONFIG-DECODE.json").read_text())
    assert decoded == saved
    writes = {int(row["address"], 16): int(row["data"], 16)
              for row in decoded["post_boot_config"]["raw_writes"]}
    assert [writes[x] for x in (0x0468, 0x046d, 0x046e)] == [2, 0, 0]
    assert writes[0x044e] | writes[0x044f] << 8 == 100
    timing = decoded["post_boot_config"]["decoded_windows_values"]
    assert timing["line_length"] == 1200 and timing["frame_length"] == 1955
    # Type-0 caller supplies uint32 words [1,1,0,1,0]:
    # three LED-select bytes at +0, HW/SW +4, level/edge +8,
    # polarity +12, common register bit at +16.
    payload = struct.pack("<5I", 1, 1, 0, 1, 0)
    assert list(payload[:3]) == [1, 0, 0]
    config = (struct.unpack_from("<I", payload, 4)[0] << 2 |
              struct.unpack_from("<I", payload, 8)[0] << 1 |
              struct.unpack_from("<I", payload, 12)[0])
    assert config == 5
    result = {
        "status": "PASS_STATIC_TRIGGER_AND_INITIAL_TIMING",
        "source_sha256": hashes,
        "commands": commands,
        "sensor_initialization": {
            "live_packet_sha256": decoded["live_initialconfig_packet"]["sha256"],
            "gpio1": 2, "strobe_start_delay_lines": 0, "strobe_end_delay_lines": 0,
            "initial_exposure_lines": 100, "line_length": 1200, "frame_length": 1955,
        },
        "type0_trigger_configuration": {
            "payload_u32": [1, 1, 0, 1, 0],
            "selected_logical_led": 1,
            "paired_registers": ["0xee4a", "0xee4d"],
            "mask": 7, "value": config,
            "linux_bit_interpretation": "hardware, level, active high",
            "common_register": "0xee67", "common_mask": 1, "common_value": 0,
            "common_bit_semantics": "unresolved",
            "input_selector": "platform-dependent; runtime value not yet observed",
        },
        "timer_handler": {
            "registers": [hex(x) for x in timer_regs],
            "accepted_ms": [10, 1280], "step_ms": 10,
            "enabled_value": "0x80 | floor((requested_ms - 10) / 10)",
            "disabled_value": 0,
            "flash_helper_enabled_request_ms": 1270,
            "flash_helper_enabled_register_value": 254,
            "used_by_type0_stream_proven": False,
        },
        "calculation_only_at_linux_measured_pixel_clock": {
            "pixel_clock_hz": 137600000,
            "line_time_us": 1200 / 137600000 * 1e6,
            "initial_100_line_pulse_us": 100 * 1200 / 137600000 * 1e6,
            "initial_100_line_duty_percent": 100 / 1955 * 100,
            "windows_stream_clock_measured": False,
        },
        "camera_opened": False, "hardware_activated": False,
        "physical_pulse_limits_proven": False,
        "remaining": [
            "Observe Windows type-0 input selector and common-bit behavior.",
            "Observe streaming exposure and actual timer configuration.",
            "Establish bounded native pulse policy before illumination.",
        ],
    }
    output = HERE / "evidence/RESULT.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
