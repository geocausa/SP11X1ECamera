#!/usr/bin/env python3
"""In-memory mutation negatives for E004hw. Never modifies archived firmware."""
import importlib.util
import struct
from pathlib import Path

import pefile

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("e004hw", HERE / "verify_protocol.py")
assert SPEC and SPEC.loader
hw = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(hw)

def main():
    original = hw.hv.original_image()
    baseline = bytes(original.__data__)
    hw.check_original(original)
    tests = []
    for rva in hw.INSTRUCTIONS:
        tests.append((f"original_instruction_{rva:x}", rva, bytes(4)))
    for rva in (hw.GUID_INTERFACE_RVA, hw.GUID_INTERFACE_RVA + 15,
                hw.GUID_OTHER_RVA, hw.GUID_OTHER_RVA + 15,
                0x38b50, 0x38d98, 0x39ef0, 0x39ef0 + 13 * 8):
        tests.append((f"original_data_{rva:x}", rva, bytes([baseline[original.get_offset_from_rva(rva)] ^ 1])))
    for label, address, corrupt in tests:
        altered = bytearray(baseline)
        offset = original.get_offset_from_rva(address)
        altered[offset: offset + len(corrupt)] = corrupt
        try:
            hw.check_original(pefile.PE(data=bytes(altered)))
        except AssertionError as err:
            assert str(err).startswith("E004HW_FAIL_CLOSED"), (label, err)
        else:
            raise AssertionError("E004HW_NEGATIVE_FAIL_OPEN " + label)
    print("E004HW_IN_MEMORY_NEGATIVE_TESTS_PASS", len(tests))
    print("E004HW_NO_ARCHIVE_OR_DEVICE_MUTATION")
if __name__ == "__main__":
    main()
