#!/usr/bin/env python3
"""Fail-closed original binary in-memory mutations; no firmware/device writes."""
import importlib.util
from pathlib import Path
import pefile

HERE=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location("e004hx",HERE/"verify_descriptor.py")
assert S and S.loader
stage=importlib.util.module_from_spec(S)
S.loader.exec_module(stage)

def main():
    original=stage.HV.original_image()
    raw=bytes(original.__data__)
    stage.inspect(original)
    tests=[]
    for a in stage.INSTRUCTIONS:
        tests.append(("instruction_"+hex(a),a,bytes(4)))
    for a in (0x2fed8,0x2fed9,0x2feda,0x2fedb,0x39ee8,
              0x39ef0,0x39ef0+8*13):
        old=raw[original.get_offset_from_rva(a)]
        tests.append(("data_"+hex(a),a,bytes([old^1])))
    for name,a,corrupt in tests:
        mutant=bytearray(raw)
        i=original.get_offset_from_rva(a)
        mutant[i:i+len(corrupt)]=corrupt
        try:stage.inspect(pefile.PE(data=bytes(mutant)))
        except AssertionError as exc:
            assert str(exc).startswith("E004HX_FAIL_CLOSED"),(name,str(exc))
        else:raise AssertionError("E004HX_NEGATIVE_FAIL_OPEN "+name)
    print("E004HX_ORIGINAL_IN_MEMORY_MUTATION_NEGATIVES_PASS",len(tests))
    print("E004HX_NO_FIRMWARE_IMAGE_OR_DEVICE_MUTATION")
if __name__=="__main__":main()
