from pathlib import Path
import hashlib, json, struct
import pefile
from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
from capstone.arm64 import ARM64_OP_IMM

ROOT = Path("/home/geoca/Documents/SP11-PROJECT/06-camera")
REPO = ROOT / "SP11X1ECamera-clean"
CANDS = [
    ROOT.parent / "00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll",
    ROOT.parent / "00-RE-archive/recovered-adata/ubi/Documents/SP11/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll",
]
DLL = next(p for p in CANDS if p.exists())
EXPECTED_DLL_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
OUT = Path(__file__).with_name("SOURCE-SAFE.json")

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

assert sha(DLL) == EXPECTED_DLL_SHA
pe = pefile.PE(str(DLL), fast_load=False)
BASE = pe.OPTIONAL_HEADER.ImageBase
assert pe.OPTIONAL_HEADER.AddressOfEntryPoint == 0xCA2D70

# Bounded source windows are sufficient for this static ordering proof.
# CC06F0 and CB3260 are pinned by the inherited accepted E011CM evidence.
spans = {
    0xCA2D70: 0xE0,
    0xCA2BC0: 0x1B0,
    0xCA2970: 104,
    0xCA29D8: 316,
    0xCA31E0: 92,
    0xCB05A8: 44,
    0xCBAE70: 180,
    0xCB5DD0: 80,
    0xCAEDA0: 80,
}
required = list(spans)

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
md.detail = True

def body(rva):
    n = spans[rva]
    raw = pe.get_data(rva, n)
    assert len(raw) == n
    ins = list(md.disasm(raw, BASE + rva))
    assert ins and ins[0].address == BASE + rva
    return raw, ins

def direct_calls(rva):
    _, ins = body(rva)
    out = []
    for i in ins:
        if i.mnemonic == "bl" and i.operands and i.operands[0].type == ARM64_OP_IMM:
            out.append((i.address - BASE, i.operands[0].imm - BASE))
    return out

def calls_target(rva, target):
    return [site for site, t in direct_calls(rva) if t == target]

# Process-attach source chain.
assert calls_target(0xCA2D70, 0xCA2BC0)
assert calls_target(0xCA2BC0, 0xCA2970)
assert calls_target(0xCA2970, 0xCA29D8)
pre_sites = calls_target(0xCA29D8, 0xCA31E0)
ctor_sites = calls_target(0xCA29D8, 0xCAEDA0)
assert pre_sites and ctor_sites and min(pre_sites) < min(ctor_sites)
assert calls_target(0xCA31E0, 0xCB05A8)
assert calls_target(0xCB05A8, 0xCBAE70)
assert calls_target(0xCB5DD0, 0xCC06F0)

# The pre-constructor subsystem table is a 16-byte pair array.
pair_start, pair_end = 0xF8BA20, 0xF8BB20
pairs = []
for rva in range(pair_start, pair_end, 16):
    a, b = struct.unpack("<QQ", pe.get_data(rva, 16))
    def norm(q):
        return q - BASE if BASE <= q < BASE + pe.OPTIONAL_HEADER.SizeOfImage else q
    pairs.append([norm(a), norm(b)])
assert len(pairs) == 16
assert pairs[4] == [0xCB7280, 0xCB7320]
assert pairs[5] == [0xCBAE10, 0xCBAE50]
assert pairs[8] == [0xCB5DD0, 0xCB5E20]

# Verify CBAE70's structural forward pair walk: indirect callback and +16 stride.
_, walk = body(0xCBAE70)
assert any(i.mnemonic == "blr" for i in walk)
assert any(i.mnemonic == "add" and "#0x10" in i.op_str for i in walk)

# CB5DD0 calls CC06F0 with index zero; success is required for its own success path.
_, low_owner = body(0xCB5DD0)
site_map = {i.address - BASE: i for i in low_owner}
assert 0xCB5DEC in site_map and site_map[0xCB5DEC].mnemonic == "mov"
assert "w0, #0" in site_map[0xCB5DEC].op_str
assert 0xCB5DF0 in site_map and site_map[0xCB5DF0].mnemonic == "bl"
assert 0xCB5DF4 in site_map and site_map[0xCB5DF4].mnemonic == "cbnz"
assert site_map[0xCB5DF4].operands[0].reg != 0
assert 0xCB5E00 in site_map and site_map[0xCB5E00].mnemonic == "mov"

# Later constructor table: ascending 8-byte array, first non-null is CB3260.
ctor_start, ctor_end = 0xF7F440, 0xF7F468
ctors = []
for rva in range(ctor_start, ctor_end, 8):
    q = struct.unpack("<Q", pe.get_data(rva, 8))[0]
    ctors.append(q - BASE if BASE <= q < BASE + pe.OPTIONAL_HEADER.SizeOfImage else q)
assert ctors == [0, 0xCB3260, 0xCC2580, 0xCFBDB0, 0xCFE2C0]

_, ctorwalk = body(0xCAEDA0)
assert any(i.mnemonic == "blr" for i in ctorwalk)
assert any(i.mnemonic == "ldr" and getattr(i, "writeback", False) and "#8" in i.op_str for i in ctorwalk)

# Inherited E011CM producer/consumer semantics are accepted source evidence.
cm = REPO / "experiments/E004-front-ir-vd55g0/e011cm-crt-object-producers"
cm_result = json.loads((cm / "RESULT.json").read_text())
cm_boot = json.loads((cm / "BOOTSTRAP-SAFE.json").read_text())
assert cm_result["status"] == "PASS_BOUNDED_ORIGINAL_CRT_OBJECT_PRODUCERS"
assert cm_result["source_script_sha256"] == sha(cm / "source-private.py")
assert cm_result["CRT_count_pointer_and_indexed_object_producers_qualified"] is True
assert cm_boot["authority"]["indexed_table_global_RVA"].lower() == "0x16a2a90"
assert set(cm_boot["authority"]["original_entries"]) >= {"0xcb7280","0xcbae10","0xcc06f0","0xcb3260"}
default_cases = [x for x in cm_boot["cases"] if x["owned_preset_stream_capacity"] == 0]
assert default_cases and all(x["actual_source_stream_capacity"] == 512 for x in default_cases)
assert all(x["original_entry_returns"][2] == {"entry_RVA":"0xcc06f0","return_W0":0} for x in default_cases)
assert all(x["original_entry_returns"][3] == {"entry_RVA":"0xcb3260","return_W0":0} for x in default_cases)
assert all(x["new_allocations_bytes"] == [4608,4096] for x in default_cases)
assert all(x["independent_complete72byte_records"] == 64 for x in default_cases)
assert all(x["independent_complete88byte_stream_objects"] == 3 for x in default_cases)
assert all(x["independent_entire_pointer_vector"] is True for x in default_cases)

# E011EF remains a separate valid path; it is not the startup handoff producer.
ef = REPO / "experiments/E004-front-ir-vd55g0/e011ef-original-lowio-count-activation-return"
ef_result = json.loads((ef / "RESULT.json").read_text())
assert ef_result["status"] == "PASS_BOUNDED_ORIGINAL_LOWIO_COUNT_ACTIVATION_RETURN"

function_hashes = {}
for r in required:
    raw, _ = body(r)
    function_hashes[hex(r)] = {
        "bytes": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }

safe = {
    "experiment": "E011EG",
    "status": "PASS_SOURCE_QUALIFIED_CRT_STARTUP_ORDER",
    "original_DLL_sha256": EXPECTED_DLL_SHA,
    "pe_entrypoint_RVA": "0xca2d70",
    "process_attach_source_chain": [
        "0xca2d70", "0xca2bc0", "0xca2970", "0xca29d8"
    ],
    "preconstructor_initializer_RVA": "0xca31e0",
    "preconstructor_initializer_call_site_RVA": hex(min(pre_sites)),
    "constructor_iterator_RVA": "0xcaeda0",
    "constructor_iterator_call_site_RVA": hex(min(ctor_sites)),
    "preconstructor_precedes_constructor_iterator": True,
    "subsystem_table": {
        "start_RVA": hex(pair_start),
        "end_RVA": hex(pair_end),
        "pair_stride_bytes": 16,
        "pair_count": len(pairs),
        "global_mutex_pair_index": 4,
        "heap_pair_index": 5,
        "lowIO_owner_pair_index": 8,
        "lowIO_owner_init_RVA": "0xcb5dd0",
        "lowIO_owner_uninit_RVA": "0xcb5e20",
        "forward_first_member_walk": True,
        "success_required_to_advance": True,
    },
    "lowIO_startup_owner": {
        "owner_RVA": "0xcb5dd0",
        "producer_RVA": "0xcc06f0",
        "producer_index": 0,
        "producer_success_return_W0": 0,
        "owner_success_return_W0": 1,
        "producer_required_for_owner_success": True,
    },
    "constructor_table": {
        "start_RVA": hex(ctor_start),
        "end_RVA": hex(ctor_end),
        "entries_RVA": [hex(x) if x else "0x0" for x in ctors],
        "first_nonnull_RVA": "0xcb3260",
        "ascending_eight_byte_walk": True,
    },
    "ordering_theorem": {
        "conditional_on_process_attach_reaching_stream_initializer": True,
        "CB05A8_success_precedes_constructor_iteration": True,
        "CB5DD0_success_precedes_constructor_iteration": True,
        "CC06F0_success_precedes_CB3260": True,
        "startup_lowIO_to_stream_order_source_qualified": True,
        "full_native_CRT_startup_success_qualified": False,
    },
    "inherited_E011CM": {
        "result_sha256": sha(cm / "RESULT.json"),
        "bootstrap_sha256": sha(cm / "BOOTSTRAP-SAFE.json"),
        "source_sha256": sha(cm / "source-private.py"),
        "complete_original_entry_returns": cm_result["complete_original_entry_returns"],
        "default_capacity_cases": cm_result["default_capacity_cases"],
        "producer_consumer_state_model_qualified": True,
        "default_stream_capacity": 512,
        "lowIO_records": 64,
        "lowIO_record_bytes": 72,
        "stream_vector_bytes": 4096,
        "static_stream_objects": 3,
    },
    "state_handoff": {
        "startup_CC06F0_to_CB3260_handoff_qualified": True,
        "original_stream_initializer_return_qualified_under_inherited_owned_OS_contracts": True,
        "runtime_stream_table_pointer_RVA": "0x16a2a58",
        "runtime_lowIO_table_pointer_RVA": "0x16a2a90",
        "E011EF_CC08E8_state_joined": False,
        "camera_state_joined": False,
    },
    "separation": {
        "E011EF_remains_valid_separate_lowIO_path": True,
        "CC08E8_is_not_used_as_startup_handoff_producer": True,
        "native_allocator_qualified": False,
        "native_mutex_bytes_or_concurrency_qualified": False,
        "native_loader_internals_qualified": False,
        "complete_CRT_environment_qualified": False,
        "native_rear_runtime_allowed": False,
    },
    "function_pins": function_hashes,
}
OUT.write_text(json.dumps(safe, indent=2) + "\n")
print(json.dumps({
    "status": safe["status"],
    "source_safe": str(OUT),
    "function_pin_count": len(function_hashes),
    "pair_count": len(pairs),
    "constructor_entries": safe["constructor_table"]["entries_RVA"],
    "ordering": safe["ordering_theorem"],
}, indent=2))
