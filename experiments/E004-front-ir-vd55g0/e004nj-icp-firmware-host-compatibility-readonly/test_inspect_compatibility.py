#!/usr/bin/env python3
import struct
import tempfile
import unittest
from pathlib import Path
from inspect_compatibility import read_elf_metadata

def fake_elf(path:Path,machine:int,phnum:int=1):
    header=bytearray(52)
    header[:6]=b"\x7fELF\x01\x01"
    struct.pack_into("<H",header,16,2)
    struct.pack_into("<H",header,18,machine)
    struct.pack_into("<I",header,28,52)
    struct.pack_into("<H",header,42,32)
    struct.pack_into("<H",header,44,phnum)
    path.write_bytes(header+b"\x00"*64)
class ELFCompatibilityTests(unittest.TestCase):
    def test_synthetic_xtensa_accepted_for_metadata_only(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"synthetic.elf";fake_elf(p,94)
            x=read_elf_metadata(p)
            self.assertEqual(x["cpu_architecture"],"XTENSA")
            self.assertFalse(x["has_section_header"])
    def test_synthetic_aarch64_not_xtensa(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"synthetic.elf";fake_elf(p,183)
            self.assertEqual(read_elf_metadata(p)["cpu_architecture"],"AARCH64")
    def test_synthetic_hexagon_not_xtensa(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"synthetic.elf";fake_elf(p,164)
            self.assertEqual(read_elf_metadata(p)["cpu_architecture"],"HEXAGON")
    def test_bad_header_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"synthetic.elf";p.write_bytes(b"not_elf")
            with self.assertRaises(ValueError):read_elf_metadata(p)
    def test_unrecognized_architecture_fail_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"synthetic.elf";fake_elf(p,0xffff)
            with self.assertRaises(ValueError):read_elf_metadata(p)
    def test_corrupt_header_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"synthetic.elf";fake_elf(p,94,0)
            with self.assertRaises(ValueError):read_elf_metadata(p)

if __name__=="__main__":unittest.main()
