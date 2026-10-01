#!/usr/bin/env python3
"""Same-SP11 bounded source audit. Original bytes never leave this host."""
from pathlib import Path
import hashlib, importlib.util, json, struct
import capstone, pefile
from unicorn import UC_HOOK_MEM_WRITE
from unicorn.arm64_const import UC_ARM64_REG_X0, UC_ARM64_REG_SP, UC_ARM64_REG_LR, UC_ARM64_REG_PC
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DLL = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll")
ARCHIVE = DLL.parents[1]
DLL_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
FILES = [
 ("qccamplatform8380.inf_arm64_16d44e9aca3becfb/com.qti.tuned.default.bin", "aa685fb55e528e717eaf115112dd08bffb5d15c7cd00c4570282163667008150"),
 ("surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.qti.tuned.default.bin", "ca620fbcfd9bde3c25157289ac7172244fb39744b36d293ea53ab94422eea634"),
 ("surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin", "4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"),
]
def load(path):
 spec = importlib.util.spec_from_file_location("e011bc_native", path)
 module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
 return module
def main():
 blob = DLL.read_bytes()
 assert hashlib.sha256(blob).hexdigest() == DLL_SHA
 pe = pefile.PE(data=blob); base = pe.OPTIONAL_HEADER.ImageBase
 assert pe.get_data(0x1419fc8, 20).rstrip(b"\0") == b"QTI Chromatix Header"
 md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM); md.detail = True
 i = next(md.disasm(pe.get_data(0x6f0258, 4), base + 0x6f0258))
 assert i.mnemonic == "ldrh"
 assert i.operands[-1].type == capstone.arm64.ARM64_OP_MEM
 assert i.operands[-1].mem.disp == 0x26
 sources = []
 for path, sha in FILES:
  data = (ARCHIVE / path).read_bytes()
  assert hashlib.sha256(data).hexdigest() == sha
  assert data[:20].rstrip(b"\0") == b"QTI Chromatix Header"
  value = struct.unpack_from("<H", data, 0x26)[0]
  assert value == 0, "SHA-pinned field26 source fact changed"
  sources.append(dict(source=path, sha256=sha, header_field26_is_zero=True,
      header_field26_is_fixture_alignment_one=False))
 native = load(ROOT / "experiments/E004-front-ir-vd55g0/e011ai-rear-neutral-scalar-full-integration/native-private.py")
 expected = {
  0: (8, base + 0x133b740), 8: (8, base + 0x1419fc8),
  0x450: (8, 0), 0x10: (8, 0), 0x18: (4, 0), 0x1c: (1, 0),
  0x420: (8, 0), 0x428: (8, 0), 0x430: (8, 0),
  0x438: (4, 0), 0x440: (8, 0), 0x448: (8, 0),
 }
 cases = []
 for bias in (0x100, 0x230, 0x1010, 0x8010):
  n = native.Native(); u = n.u; object_address = n.heap + bias
  before = bytes([0xa5]) * 0x30000
  u.mem_write(n.heap, before); desired = bytearray(before); writes = []
  for offset, (size, value) in expected.items():
   desired[bias+offset:bias+offset+size] = value.to_bytes(size, "little")
  def on_write(uc, access, address, size, value, user):
   if n.heap <= address < n.heap + 0x30000:
    assert object_address <= address and address + size <= object_address + 0x458
    offset = address - object_address
    assert offset in expected and expected[offset] == (size, value)
    writes.append(offset)
  u.hook_add(UC_HOOK_MEM_WRITE, on_write)
  for register, value in ((UC_ARM64_REG_X0, object_address),
       (UC_ARM64_REG_SP, n.stack + 0xf000), (UC_ARM64_REG_LR, n.end)):
   u.reg_write(register, value)
  u.emu_start(base + 0x6f3d08, n.end, count=1000)
  assert u.reg_read(UC_ARM64_REG_PC) == n.end
  assert sorted(writes) == sorted(expected)
  assert bytes(u.mem_read(n.heap, 0x30000)) == bytes(desired)
  cases.append(dict(placement_bias=hex(bias), returned=True,
      exact_member_writes=len(writes), all_other_heap_bytes_preserved=True,
      helper_calls_stubbed=False))
 safe = dict(experiment="E011BC", status="PASS_BOUNDED_SOURCE_AUDIT_ALIGNMENT_OPEN",
   original_DLL_sha256=DLL_SHA, original_constructor_rva="0x6f3d08",
   manager_vtable_rva="0x133b740", header_identifier_rva="0x1419fc8",
   manager_constructor_cases=cases, SHA_pinned_sources=sources,
   candidate_halfword_reader=dict(function_rva="0x6f01e8", read_rva="0x6f0258",
      source_offset="0x26", width_bytes=2,
      association_with_AEC_deserializer_caller_proven=False),
   simple_header26_equals_alignment1_hypothesis_rejected=True,
   zero_to_nonzero_conversion_ruled_out=False,
   actual_caller_alignment_policy_closed=False, exact_loaded_tuning_filename_closed=False,
   full_profile_materialization_closed=False, original_grid_proof_repeated=False,
   raw_original_bytes_exported=False, production_C_changed=False,
   observer_armed=False, new_camera_starts=0, new_reboots=0,
   native_rear_runtime_allowed=False)
 (HERE / "SOURCE-SAFE.json").write_text(json.dumps(safe, indent=2, sort_keys=True) + "\n")
 print(json.dumps(safe, indent=2, sort_keys=True))
if __name__ == "__main__":
 main()
