#!/usr/bin/env python3
"""Same-SP11 native arithmetic fragments; originals and numeric results stay private."""
from pathlib import Path
import hashlib, importlib.util, itertools, json, random, struct, subprocess, tempfile
import pefile, capstone
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm64_const import *
HERE = Path(__file__).resolve().parent
DLL = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll")
DLL_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
TUNE = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin")
def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module); return module
P = load("request_trigger_ae", HERE / "producer.py")
A = load("authority_ae", HERE.parent / "e011ac-rear-bpcabf411-tuning-selection" / "authority.py")
def bits(value): return struct.pack("<f", value)
def neighbor(value, up):
    word = struct.unpack("<I", bits(value))[0] + (1 if up else -1)
    return struct.unpack("<f", struct.pack("<I", word))[0]

def native():
    blob = DLL.read_bytes()
    assert hashlib.sha256(blob).hexdigest() == DLL_SHA
    pe = pefile.PE(data=blob); base = pe.OPTIONAL_HEADER.ImageBase
    cs = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    anchors = {
        0x88a598: ("ldr", "s17, [x10, #0xc]"),
        0x88a5a4: ("fcvt", "d16, s16"),
        0x88a5b4: ("fdiv", "s16, s16, s17"),
        0x88a5c0: ("str", "s16, [x22, #0x20ac]"),
        0x88a7b4: ("ldr", "w8, [x19, #0xf4]"),
        0x88a8b0: ("ldr", "s16, [x8, #0x38]"),
        0x88a8bc: ("ldr", "s16, [x8, #0x20]"),
        0x88a8c8: ("ldr", "s16, [x8, #8]"),
        0x88a8cc: ("str", "s16, [x19, #0x20b0]"),
        0x88ab08: ("ldr", "s16, [x8, #0x78]"),
        0x88ab10: ("fcsel", "s16, s16, s8, gt"),
        0x88ab14: ("str", "s16, [x27, #0x20f4]"),
        0x897ba0: ("ldr", "x9, [x8, #0x190]"),
        0x897bb0: ("str", "s16, [x9, #4]"),
        0x897bb8: ("str", "s16, [x9, #8]"),
        0x897bc8: ("str", "s16, [x9, #0x14]"),
    }
    for rva, expected in anchors.items():
        ins = next(cs.disasm(pe.get_data(rva, 4), rva))
        assert (ins.mnemonic, ins.op_str) == expected, {"source_anchor_rva": hex(rva)}
    ins = next(cs.disasm(pe.get_data(0x746f4c, 4), base + 0x746f4c))
    assert ins.mnemonic == "bl" and int(ins.op_str[1:], 16) == base + 0x897b78
    assert struct.unpack("<d", pe.get_data(0x88af40, 8))[0] == 1e-6
    u = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    u.mem_map(base, (pe.OPTIONAL_HEADER.SizeOfImage + 4095) & ~4095)
    u.mem_write(base, pe.get_memory_mapped_image())
    heap = 0x70000000; isp = heap; aec = heap + 0x20000; node = heap + 0x22000
    vector = heap + 0x30000
    u.mem_map(heap, 0x40000); u.mem_map(heap + 0x50000, 0x10000)
    snapshot = [0]; calls = [0]
    def hook(uc, addr, size, data):
        if addr == base + 0x5d4158:
            # External metadata lookup return is a declared test input, not emulated policy.
            calls[0] += 1; uc.reg_write(UC_ARM64_REG_X0, snapshot[0])
            uc.reg_write(UC_ARM64_REG_PC, uc.reg_read(UC_ARM64_REG_LR))
    u.hook_add(UC_HOOK_CODE, hook)
    def run(case):
        u.mem_write(heap, bytes(0x40000))
        u.mem_write(isp, struct.pack("<Q", aec))
        u.mem_write(isp + 0x17190, struct.pack("<3Q", vector, vector + 42*4, vector + 42*4))
        for offset, name in ((8, "short"), (0x20, "mid"), (0x38, "long")):
            u.mem_write(aec + offset, bits(P.f32(case["gains"][name])))
        for offset, name in ((0xc, "short"), (0x24, "mid")):
            u.mem_write(aec + offset, bits(P.f32(case["sensitivities"][name])))
        u.mem_write(aec + 0x78, bits(P.f32(case["drc_gain"])))
        u.mem_write(isp + 0xf4, struct.pack("<I", int(case["sensor_mid_override"])))
        u.mem_write(isp + 0x1712c, bytes([case["input_context"]]))
        u.mem_write(node + 0x33ec, bytes([case["node_context"]]))
        snapshot[0] = case["snapshot_context"]
        for reg, value in ((UC_ARM64_REG_X10, aec), (UC_ARM64_REG_X9, aec), (UC_ARM64_REG_X22, isp),
                           (UC_ARM64_REG_X19, isp), (UC_ARM64_REG_X20, node),
                           (UC_ARM64_REG_X27, isp), (UC_ARM64_REG_SP, heap + 0x5f000),
                           (UC_ARM64_REG_S8, struct.unpack("<I", bits(1.0))[0]),
                           (UC_ARM64_REG_S19, 0),
                           (UC_ARM64_REG_D18, struct.unpack("<Q", struct.pack("<d", 1e-6))[0])):
            u.reg_write(reg, value)
        for start, stop in ((0x88a598, 0x88a5c4), (0x88a7b4, 0x88a8d0),
                            (0x88ab04, 0x88ab18), (0x897b98, 0x897bcc)):
            u.emu_start(base + start, base + stop, count=1000)
            assert u.reg_read(UC_ARM64_REG_PC) == base + stop
        return tuple(bytes(u.mem_read(vector + index*4, 4)) for index in (2, 5, 1))
    return run, len(anchors) + 2, calls

def main():
    run, anchors, metadata_calls = native()
    cases = []
    for override in (False, True):
        for contexts in itertools.product(range(4), repeat=3):
            if not override and contexts == (2,2,2): continue
            cases.append(dict(gains={"short": 1.25, "mid": 2.5, "long": 3.75},
                sensitivities={"short": 2.0, "mid": 7.0}, drc_gain=4.0,
                sensor_mid_override=override, node_context=contexts[0],
                snapshot_context=contexts[1], input_context=contexts[2], request_id=1))
    rng = random.Random(0xE011AE)
    for i in range(512):
        cases.append(dict(gains={key: P.f32(2**rng.uniform(-16,16)) for key in ("short","mid","long")},
            sensitivities={key: P.f32(2**rng.uniform(-30,30)) for key in ("short","mid")},
            drc_gain=P.f32(2**rng.uniform(-16,16)), sensor_mid_override=bool(i%2),
            node_context=i%4, snapshot_context=(i//4)%4, input_context=0, request_id=i+1))
    near = P.f32(1e-6)
    for denominator in (0.0, -0.0, 2**-149, neighbor(near,False), near, neighbor(near,True), 1.0):
        for drc in (0.0, neighbor(1.0,False), 1.0, neighbor(1.0,True), 32.0):
            cases.append(dict(gains={"short":0.0,"mid":1.0,"long":4.0},
                sensitivities={"short":denominator,"mid":3.0}, drc_gain=drc,
                sensor_mid_override=False,node_context=0,snapshot_context=0,input_context=0,
                request_id=1))
    for case_index, case in enumerate(cases):
        expected = tuple(bits(value) for _, value in P.produce_triggers(**case)["typed"])
        actual = run(case)
        assert actual == expected, {"case":case_index,"mismatch_type_ids":[t for t,a,b in zip((2,5,1),actual,expected) if a != b],"contexts":[case[k] for k in ("node_context","snapshot_context","input_context")],"override":case["sensor_mid_override"]}
    authority = A.Authority(TUNE); fields = scalars = integrations = decisions = 0
    c_semantics = bytearray(); c_expected = bytearray()
    interval_native = load("interval_native_ae", HERE.parent / "e011ad-rear-bpcabf411-trigger-interval-selector" / "verify-private.py").native()
    blend_native = load("blend_native_ae", HERE.parent / "e011ac-rear-bpcabf411-tuning-selection" / "verify-private.py").native()
    common_native = load("common_native_ae", HERE.parent / "e011aa-rear-bpcabf411-common-producer" / "verify-private.py").source_runner()
    for modes in ([(0,0)], [(0,0),(1,1),(2,2)]):
        for case in cases:
            result = P.produce_bpc(authority, modes, **case)
            actual_triggers = [struct.unpack("<f", b)[0] for b in run(case)]
            rows, leaves, prefix = P.S.source_intervals(authority, result["root"], with_prefix=True)
            for index, mode in enumerate(("outer", "nested")):
                assert interval_native((prefix[index],), actual_triggers[index], mode) == (0, 0, bits(0.0))
                decisions += 1
            lower, upper, ratio_bits = interval_native(rows, actual_triggers[2], "terminal")
            ratio = struct.unpack("<f", ratio_bits)[0]
            assert result["interval"] == {"lower":lower,"upper":upper,"ratio":ratio}
            decisions += 1
            a = authority.region(result["root"], leaves[lower])
            b = a if lower == upper else authority.region(result["root"], leaves[upper])
            good, region_bytes = blend_native(a, b, ratio)
            assert good == 1 and region_bytes == struct.pack("<107f", *result["region"])
            region = list(struct.unpack("<107f", region_bytes))
            state = common_native(*P.S.AC.selected_terms(region), authority.anchors(result["root"]))
            assert result["state"] == state
            values = state["signed10"] + state["unsigned9"] + state["nibble4"]
            for key in ("byte_group0", "byte_group1", "nibble_group"):
                values.extend(state[key][0] + state[key][1])
            c_semantics.extend(struct.pack("<2h2H26B", *values))
            c_expected.extend(struct.pack("<7I", *[result["registers"][reg] for reg in P.S.AC.P.REGS]))
            assert result["request_id"] == case["request_id"]
            integrations += 1; fields += 107; scalars += 30
    cold = P.S.AC.cold_seed(authority)
    source = P.startup_common(authority, [(0,0),(1,1),(2,2)], cases[0], cases[0] | {"request_id":2})
    assert source["source_request_id"] == (0,1,2) and source["common"][0] == cold["state"]
    assert common_native(*P.S.AC.selected_terms(cold["region"]), authority.anchors(cold["root"])) == cold["state"]
    with tempfile.TemporaryDirectory(prefix="e011ae-private-host-") as directory:
        binary = str(Path(directory) / "binder-check")
        subprocess.run(["cc","-std=c11","-Wall","-Wextra","-Werror",str(HERE / "compile-check.c"),"-o",binary], check=True)
        binder = subprocess.run([binary], capture_output=True, check=True)
        assert b"E011AE_BPC_BINDER_HOST_PASS" in binder.stdout
        packed = subprocess.run([binary,"pack"], input=bytes(c_semantics), capture_output=True, check=True)
        assert packed.stdout == bytes(c_expected), "C provider differs from source-produced semantics; values private"
    rejects = 0
    basecase = cases[0]
    invalid = [
        {"request_id":0},{"request_id":True},{"qll_short_override":True},
        {"drc_gain":float("nan")},{"drc_gain":-1.0},{"drc_gain":float("inf")},
        {"sensitivities":{"short":-1.0,"mid":1.0}},
        {"node_context":9},{"sensor_mid_override":1},
        {"node_context":2,"snapshot_context":2,"input_context":2,"sensor_mid_override":False},
        {"gains":{"short":1.0,"mid":1.0}},
        {"sensitivities":{"short":1e-5,"mid":3e38}},
    ]
    for change in invalid:
        try: P.produce_triggers(**(basecase | change))
        except ValueError: rejects += 1
        else: raise AssertionError("unsupported request domain admitted")
    report = {"experiment":"E011AE","status":"OFFLINE_REQUEST_TRIGGER_SOURCE_PASS_LIVE_BINDING_OPEN",
        "original_source_instruction_and_constant_anchors":anchors,
        "native_input_cases":len(cases),"exact_trigger_scalar_comparisons":len(cases)*3,
        "native_execution":"four bounded original arithmetic/mapping fragments in Unicorn only",
        "external_snapshot_context":"declared semantic input; metadata lookup not executed",
        "metadata_return_stubs_exercised":metadata_calls[0],"domain_rejects":rejects,
        "bpc_source_chain_integration_cases":integrations,"region_fields_checked":fields,
        "common_selected_scalars_checked":scalars,"native_interval_decisions_checked":decisions,"integration_is_independent_live_evidence":False,
        "c_e007a_provider_register_word_matches":integrations*7,
        "host_bpc_binder_packets_checked":4,"host_bpc_binder_domain_rejects":20,
        "host_bpc_binder_schedule":[0,1,2,2],"full_e008o_dmi_validation_exercised":False,
        "trigger_ids":[2,5,1],"terminal_trigger_1_semantic":"selected_AEC_sensor_linear_gain",
        "live_upstream_AEC_context_binding_closed":False,"cold_shared_vector_initialization_closed":False,
        "cold_bpc_common_from_source_invariant_default_closed":True,
        "complete_e008o_composition_closed":False,"wm16_retirement_closed":False,
        "native_rear_linux_runtime_allowed":False,"raw_source_or_capture_values_exported":False}
    print(json.dumps(report, indent=2))
if __name__ == "__main__": main()
