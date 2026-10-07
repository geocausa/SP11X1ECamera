#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Hosted actual statistics geometry/binder/packers; optional same-SP11 oracle.
Oracle controls are decoded semantic inputs, not an independent control producer.
Geometry candidates come from the source-closed cold/normal presets. No hardware.
"""
import argparse
from collections import Counter
import ctypes
import importlib.util
import itertools
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIVATE = ROOT.parent / "private/E011X-source-recovered"
DECODER = ROOT / "experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py"
REGISTERS = [0xb258, 0xb25c, 0xb26c, 0xbe60, 0xbe68, 0xbe6c, 0xbe70]
REGISTERS += [base + 4 * i for base in [0xb060, 0xb660, 0xb860] for i in range(18)]
BRIDGE = r"""
#include "rear-statistics-host-fixture.h"
int sp11_rear_statistics_pack(const u32 *controls, const u32 *policy,
			     const u32 *rs_controls, u32 *output)
{
	struct e008o_rear_packet_semantics base[4];
	struct native_rear_startup_stats_input input;
	const u16 registers[61] = {
		0xb258,0xb25c,0xb26c,0xbe60,0xbe68,0xbe6c,0xbe70,
		0xb060,0xb064,0xb068,0xb06c,0xb070,0xb074,0xb078,0xb07c,0xb080,0xb084,0xb088,0xb08c,0xb090,0xb094,0xb098,0xb09c,0xb0a0,0xb0a4,
		0xb660,0xb664,0xb668,0xb66c,0xb670,0xb674,0xb678,0xb67c,0xb680,0xb684,0xb688,0xb68c,0xb690,0xb694,0xb698,0xb69c,0xb6a0,0xb6a4,
		0xb860,0xb864,0xb868,0xb86c,0xb870,0xb874,0xb878,0xb87c,0xb880,0xb884,0xb888,0xb88c,0xb890,0xb894,0xb898,0xb89c,0xb8a0,0xb8a4,
	};
	unsigned p, f, r;
	int ret = native_rear_stats_test_initialize(base, &input);
	if (ret) return ret;
	for (p = 0; p < 4; p++) {
		struct native_rear_packet_stats_input *i = &input.packet[p];
		struct native_rear_bg_input *bg[3] = {&i->aec, &i->tintless, &i->awb};
		struct native_rear_packet_stats_input cold = *i;
		ret = native_rear_stats_geometry_preset(i, NATIVE_REAR_STATS_NORMAL);
		if (ret) return ret;
		ret = native_rear_stats_geometry_preset(&cold, NATIVE_REAR_STATS_COLD);
		if (ret) return ret;
		if (policy[p*3]) i->bhist = cold.bhist;
		if (policy[p*3+1]) {
			i->aec.roi = cold.aec.roi;
			i->aec.h_num = cold.aec.h_num;
			i->aec.v_num = cold.aec.v_num;
		}
		if (policy[p*3+2]) i->awb.roi = cold.awb.roi;
		i->rs.color_conversion = !!rs_controls[p*3];
		i->rs.h_num = rs_controls[p*3+1];
		i->rs.v_num = rs_controls[p*3+2];
		for (f = 0; f < 3; f++) {
			const u32 *c = &controls[(p*3+f)*10];
			bg[f]->threshold_r = c[0]; bg[f]->threshold_b = c[1];
			bg[f]->threshold_gr = c[2]; bg[f]->threshold_gb = c[3];
			bg[f]->black_level_offset = c[4];
			for (r = 0; r < 3; r++) {
				if (c[5+r] > 127) return -ERANGE;
				bg[f]->y_weight_q4[r] = c[5+r];
			}
			bg[f]->quad_sync_enable = !!c[8];
			bg[f]->enabled = !!c[9];
			bg[f]->controls_valid = true;
		}
	}
	ret = native_rear_bind_startup_statistics(base, &input);
	if (ret) return ret;
	for (p = 0; p < 4; p++)
		for (r = 0; r < 61; r++) {
			ret = native_rear_stats_test_lookup(&base[p], registers[r], &output[p*61+r]);
			if (ret) return ret;
		}
	return 0;
}
"""
def checked(command, env=None):
    p = subprocess.run(command, capture_output=True, text=True, env=env)
    if p.returncode:
        raise RuntimeError(p.stdout + p.stderr)
    return p

def private_oracle(staged, temporary):
    if not str(ROOT).startswith("/home/geoca/Documents/SP11-PROJECT/"):
        raise RuntimeError("retained oracle requires authorized SP11 workspace")
    code = temporary / "private-statistics.c"
    code.write_text(BRIDGE)
    library = temporary / "private-statistics.so"
    checked(["gcc", "-std=gnu11", "-Wall", "-Wextra", "-Werror", "-shared", "-fPIC",
             "-I" + str(HERE), "-I" + str(staged), "-I" + str(temporary),
             str(code), "-o", str(library)])
    lib = ctypes.CDLL(str(library))
    pack = lib.sp11_rear_statistics_pack
    u32 = ctypes.c_uint32
    pack.argtypes = [ctypes.POINTER(u32)] * 4
    pack.restype = ctypes.c_int
    spec = importlib.util.spec_from_file_location("rear_stats_decode", DECODER)
    decoder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(decoder)
    corpus = json.loads((PRIVATE / "E006A-PRIVATE-RECORDS-v2.json").read_text(
        encoding="utf-8-sig"))["records"]
    writes = [decoder.decode(bytes.fromhex(next(r for r in corpus
              if r["n"] == phase and r["idx"] == 1)["hex"]))["writes"] for phase in range(4)]
    values = [{reg: value for reg, value, _, _ in w} for w in writes]
    controls = (u32 * 120)()
    policies = (u32 * 12)()
    rs_controls = (u32 * 12)()
    packed = (u32 * 244)()
    # Decode only semantic scalar controls. This is intentionally a binding/
    # geometry test, not proof that an independent IPA produced these controls.
    for phase in range(4):
        rs_controls[phase*3] = bool(values[phase].get(0xbe60, 0) & 0x10)
        if 0xbe6c in values[phase]:
            counts = values[phase][0xbe6c]
            rs_controls[phase*3+1] = (counts & 0xf) + 1
            rs_controls[phase*3+2] = ((counts >> 16) & 0x3ff) + 1
        else:
            rs_controls[phase*3+1:phase*3+3] = [16, 1024]
        for family, base in enumerate([0xb060, 0xb660, 0xb860]):
            v = values[phase]
            if base in v:
                data = [v[base+0x24] >> 14, v[base+0x2c] >> 14,
                        v[base+0x20] >> 14, v[base+0x28] >> 14, v[base+4] >> 14]
                data += [(v[base+8] >> shift) & 0x7f for shift in [9, 17, 25]]
                data += [bool(v[base] & 0x200), bool(v[base] & 1)]
            else:
                # Omitted blocks have no original control oracle. Explicit
                # synthetic valid controls keep their unused state well formed.
                data = [0x3ffff] * 4 + [0, 4, 8, 4, 0, 1]
            start = (phase * 3 + family) * 10
            controls[start:start+10] = data
    selected = []
    for phase in range(4):
        present = {reg: val for reg, val in values[phase].items() if reg in REGISTERS}
        candidates = []
        closest = None
        for policy in itertools.product([0, 1], repeat=3):
            policies[phase*3:phase*3+3] = policy
            if pack(controls, policies, rs_controls, packed):
                raise RuntimeError("actual statistics composer rejected private semantic fixture")
            mismatches = [reg for reg, val in present.items()
                          if packed[phase*61+REGISTERS.index(reg)] != val]
            if closest is None or len(mismatches) < len(closest):
                closest = mismatches
            if not mismatches:
                candidates.append(policy)
        if not candidates:
            groups = {"BHist": sum(reg in [0xb258, 0xb25c, 0xb26c] for reg in closest),
                      "RS": sum(reg in [0xbe60, 0xbe68, 0xbe6c, 0xbe70] for reg in closest),
                      "AEC": sum(0xb060 <= reg <= 0xb0a4 for reg in closest),
                      "Tintless": sum(0xb660 <= reg <= 0xb6a4 for reg in closest),
                      "AWB": sum(0xb860 <= reg <= 0xb8a4 for reg in closest)}
            raise RuntimeError("geometry candidates fail retained phase " + str(phase) +
                               "; aggregate mismatch counts=" + str(groups))
        # Omitted families may be indistinguishable; choose explicit normal
        # input there. Do not report uniqueness for absent packet blocks.
        policies[phase*3:phase*3+3] = candidates[0]
        selected.append({"phase": phase, "matching_geometry_candidates": len(candidates)})
    if pack(controls, policies, rs_controls, packed):
        raise RuntimeError("final statistics binding failed")
    source = (staged / "camss-e007y-rear-startup.inc").read_text()
    results = []
    for phase in range(4):
        pattern = r"static const u8 e007y_startup_skeleton_" + str(phase) + r"\[\] = \{(.*?)\};"
        arrays = re.findall(pattern, source, re.S)
        if len(arrays) != 1:
            raise RuntimeError("E007Y skeleton extraction drift")
        skeleton = bytes(int(v, 16) for v in re.findall(r"0x([0-9a-fA-F]{2})", arrays[0]))
        required = Counter(reg for reg, _, _, _ in decoder.decode(skeleton)["writes"]
                           if reg in REGISTERS)
        actual = Counter(reg for reg, _, _, _ in writes[phase] if reg in REGISTERS)
        if required != actual:
            raise RuntimeError("source/retained statistics coverage mismatch")
        present = exact = 0
        for reg, val, _, _ in writes[phase]:
            if reg in REGISTERS:
                present += 1
                exact += packed[phase*61+REGISTERS.index(reg)] == val
        if present != exact:
            raise RuntimeError("retained statistics binding mismatch")
        results.append({"phase": phase, "register_instances_present": present,
                        "register_instances_exact": exact})
    if [p["register_instances_present"] for p in results] != [61, 59, 5, 1]:
        raise RuntimeError("unexpected aggregate statistics coverage " + str(results))
    return {"status": "PASS_RETAINED_STATISTICS_GEOMETRY_BINDING_AND_PACKER",
            "phase_results": results, "register_instances_present": 126,
            "register_instances_exact": 126,
            "source_closed_cold_normal_geometry_candidates": selected,
            "scalar_controls_decoded_from_retained_private_words": True,
            "RS_counts_decoded_as_caller_owned_request_override": True,
            "independent_IPA_scalar_control_producer_proven": False,
            "omitted_family_controls_explicitly_synthetic": True,
            "source_skeleton_and_retained_address_multisets_match": True,
            "private_words_controls_payloads_or_images_exported": False,
            "new_camera_capture": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--private-retained-oracle", action="store_true")
    args = parser.parse_args()
    if args.report.exists():
        raise SystemExit("report identity already exists")
    staged = args.staged.resolve()
    with tempfile.TemporaryDirectory(prefix="sp11-rear-statistics-") as temporary:
        temporary = Path(temporary)
        period = (staged / "camss-e007c-period-cfg.inc").read_text()
        anchor = "static int\ne007c_rear_fill_startup_packet("
        if period.count(anchor) != 1:
            raise RuntimeError("period extraction anchor drift")
        (temporary / "e007c-period-types.h").write_text(period[:period.index(anchor)])
        results = []
        for compiler in ["gcc", "clang"]:
            executable = shutil.which(compiler)
            if not executable:
                raise RuntimeError("compiler missing: " + compiler)
            binary = temporary / (compiler + "-statistics")
            checked([executable, "-std=gnu11", "-Wall", "-Wextra", "-Werror",
                     "-O1", "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
                     "-I" + str(temporary), "-I" + str(staged),
                     str(HERE / "test-rear-startup-statistics.c"), "-o", str(binary)])
            run = checked([str(binary)], env=dict(os.environ,
                          ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",
                          UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1"))
            if "NATIVE_REAR_STATISTICS_PASS" not in run.stdout:
                raise RuntimeError("statistics test result missing")
            results.append({"compiler": compiler, "compile_Werror": True,
                            "sanitizers": ["ASAN", "UBSAN"], "stdout": run.stdout.strip(),
                            "stderr": run.stderr})
        report = {"status": "PASS_HOSTED_REAR_STATISTICS_COMPOSER",
                  "actual_statistics_geometry_binder_and_packers": True,
                  "unrelated_full_packet_fields_omitted_in_host_fixture": True,
                  "results": results, "hardware_access": False,
                  "ready_or_sealed_state_granted": False,
                  "independent_IPA_controls_or_full_rear_bootstrap_proven": False}
        if args.private_retained_oracle:
            report["retained_oracle"] = private_oracle(staged, temporary)
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))
if __name__ == "__main__":
    main()
