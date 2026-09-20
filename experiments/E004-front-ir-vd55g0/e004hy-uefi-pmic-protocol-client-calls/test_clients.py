#!/usr/bin/env python3
"""In-memory mutations of six SHA-pinned original UEFI client code images."""
import importlib.util
from pathlib import Path
import pefile
HERE=Path(__file__).resolve().parent
S=importlib.util.spec_from_file_location("hy",HERE/"verify_clients.py")
assert S and S.loader
hy=importlib.util.module_from_spec(S)
S.loader.exec_module(hy)

def main():
    tested=0
    for name, spec in hy.CLIENTS.items():
        orig=hy.original_client(name)
        raw=bytes(orig.__data__)
        hy.check_client_image(orig,name)
        for addr in spec["code"]:
            changed=bytearray(raw)
            offset=orig.get_offset_from_rva(addr)
            changed[offset:offset+4]=bytes(4)
            try:hy.check_client_image(pefile.PE(data=bytes(changed)),name)
            except AssertionError as exc:
                assert str(exc).startswith("E004HY_FAIL_CLOSED"),(name,hex(addr))
            else:raise AssertionError("E004HY_FAIL_OPEN "+name+" "+hex(addr))
            tested+=1
        addr=spec["guid_rva"]
        changed=bytearray(raw)
        changed[orig.get_offset_from_rva(addr)]^=1
        try:hy.check_client_image(pefile.PE(data=bytes(changed)),name)
        except AssertionError as exc:
            assert str(exc).startswith("E004HY_FAIL_CLOSED"),name
        else:raise AssertionError("E004HY_GUID_FAIL_OPEN "+name)
        tested+=1
    print("E004HY_ORIGINAL_CLIENT_MUTATION_NEGATIVES_PASS",tested)
    print("E004HY_NO_OEM_ARCHIVE_OR_DEVICE_MUTATION")
if __name__=="__main__":main()
