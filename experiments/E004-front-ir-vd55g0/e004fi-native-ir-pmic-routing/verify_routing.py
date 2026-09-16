#!/usr/bin/env python3
"""Verify derived PMIC routing facts against exact local Windows binaries.

Offline only: no device handles, kernel memory access, or hardware writes.
Instruction addresses in README document the manually inspected control flow.
This verifies constants/tables and the conditional arithmetic, not runtime branch
selection, physical wiring or arbitrary-current parity.
"""
import hashlib
import json
from pathlib import Path
import struct
import uuid
import pefile

ROOT = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
FILES = {
    "flash": ("qccamflash8380.sys",
              "6bc1d698bc3b6da16974cd6f3ea89dc1ba6a8ea102eebe1a5d41129b4eb9ba2b"),
    "pmic": ("qcpmic8380.sys",
             "756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e"),
}

def main():
    images, hashes = {}, {}
    for name, (filename, expected) in FILES.items():
        matches = list(ROOT.glob("*/" + filename))
        assert len(matches) == 1
        data = matches[0].read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        assert digest == expected
        hashes[str(matches[0])] = digest
        images[name] = pefile.PE(data=data)

    def u32(image, rva):
        return struct.unpack("<I", images[image].get_data(rva, 4))[0]

    def u64(image, rva):
        return struct.unpack("<Q", images[image].get_data(rva, 8))[0]

    guid = images["flash"].get_data(0xd858, 16)
    assert guid == images["pmic"].get_data(0x36fb8, 16)
    assert str(uuid.UUID(bytes_le=guid)) == "20952871-af3d-4a8a-9e47-cb346507b95b"
    commands = []
    for label, flash_rva, pmic_rva, value, size, table_offset, target in [
        ("target current", 0x4d50, 0x7bfc, 0x802f0fb0, 6, 0x38, 0x270c0),
        ("strobe", 0x4dc8, 0x7c10, 0x802f0fc8, 4, 0x90, 0x285c0),
        ("safety timer", 0x4e80, 0x7bf8, 0x802f0fac, 16, 0x28, 0x26d50),
    ]:
        assert u32("flash", flash_rva) == value == u32("pmic", pmic_rva)
        assert u64("pmic", 0x39470 + table_offset) == 0x140000000 + target
        commands.append({"name": label, "command": hex(value), "payload_bytes": size,
                         "four_channel_callback_rva": hex(target)})

    bits = list(images["pmic"].get_data(0x36d58, 4))
    assert bits == [1, 2, 4, 8]
    regs = [u32("pmic", 0x36d60 + i * 4) for i in range(4)]
    assert regs == [0xee42, 0xee43, 0xee44, 0xee45]
    resolution = [u32("pmic", 0x36d30 + i * 4) for i in range(2)]
    assert resolution == [12500, 5000]
    # Conditional initializer: descriptor +4 == 0x31 or 0x49 selects table
    # 0x39470 and sets paired-channel bytes to [3, 2, 4, 4].
    pair = [3, 2]
    mask = bits[0] | bits[pair[0]]
    assert mask == 9
    # The requested 700000 uA is exact in the first (12500 uA) resolution.
    current_ua = 700000
    encoded_total = current_ua // resolution[0] - 1
    windows_target = encoded_total >> 1
    linux_target = (current_ua // 2 + 1) // resolution[0] - 1
    assert windows_target == linux_target == 27
    assert (windows_target + 1) * resolution[0] == 350000
    result = {
        "status": "PASS_CONDITIONAL_STATIC_PMIC_ROUTING",
        "sources": hashes, "interface_guid": str(uuid.UUID(bytes_le=guid)),
        "commands": commands,
        "conditional_hardware_descriptor_values": ["0x31", "0x49"],
        "conditional_led1_channels_one_based": [1, 4],
        "conditional_led2_channels_one_based": [2, 3],
        "conditional_led1_channel_enable_mask": mask,
        "conditional_700ma_per_channel_ma": 350,
        "conditional_700ma_current_register_value": windows_target,
        "candidate_linux_led_sources": [1, 4],
        "runtime_branch_selection_proven": False,
        "physical_wiring_proven": False,
        "pulse_limits_proven": False,
        "hardware_activated": False,
    }
    output = Path(__file__).resolve().parent / "evidence/RESULT.json"
    output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
