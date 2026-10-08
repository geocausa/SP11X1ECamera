#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Execute actual staged geometry packers/binder. Optional oracle stays on SP11.
No device access; unrelated full packet fields are omitted in the hosted fixture.
The complete kernel structures are checked separately by the ARM64 module build.
"""
import argparse
from collections import Counter
import ctypes
import importlib.util
import json
import os
import re
from pathlib import Path
import shutil
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIVATE = ROOT.parent / "private/E011X-source-recovered"
DECODER = ROOT / "experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py"

def checked(command, env=None):
    p = subprocess.run(command, capture_output=True, text=True, env=env)
    if p.returncode:
        raise RuntimeError(p.stdout + p.stderr)
    return p

def private_oracle(staged, temporary):
    if not str(ROOT).startswith("/home/geoca/Documents/SP11-PROJECT/"):
        raise RuntimeError("retained oracle requires the authorized SP11 workspace")
    source = temporary / "geometry-private.c"
    source.write_text("""#include "rear-geometry-host-fixture.h"
int sp11_rear_geometry_pack(unsigned phase, u16 reg, u32 *out)
{
 struct e008o_rear_packet_semantics base[4];
 struct native_rear_geometry_mode mode;
 int ret;
 if (phase >= 4 || !out) return -EINVAL;
 native_rear_geometry_test_init(base, &mode);
 ret = native_rear_bind_startup_geometry(base, &mode);
 if (ret) return ret;
 return native_rear_geometry_test_lookup(&base[phase], phase, reg, out);
}
""")
    library = temporary / "geometry-private.so"
    checked(["gcc", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
             "-shared", "-fPIC", "-I" + str(HERE), "-I" + str(staged),
             "-I" + str(temporary), str(source), "-o", str(library)])
    lib = ctypes.CDLL(str(library))
    pack = lib.sp11_rear_geometry_pack
    pack.argtypes = [ctypes.c_uint, ctypes.c_uint16, ctypes.POINTER(ctypes.c_uint32)]
    pack.restype = ctypes.c_int
    spec = importlib.util.spec_from_file_location("rear_geometry_decode", DECODER)
    dec = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(dec)
    corpus = json.loads((PRIVATE / "E006A-PRIVATE-RECORDS-v2.json").read_text(
        encoding="utf-8-sig"))["records"]
    skeleton_source = (staged / "camss-e007y-rear-startup.inc").read_text()
    phases = []
    for phase in range(4):
        main = next(r for r in corpus if r["n"] == phase and r["idx"] == 1)
        writes = dec.decode(bytes.fromhex(main["hex"]))["writes"]
        pattern = r"static const u8 e007y_startup_skeleton_" + str(phase) + r"\[\] = \{(.*?)\};"
        arrays = re.findall(pattern, skeleton_source, re.S)
        if len(arrays) != 1:
            raise RuntimeError("source skeleton extraction drift")
        skeleton = bytes(int(v, 16) for v in re.findall(r"0x([0-9a-fA-F]{2})", arrays[0]))
        source_writes = dec.decode(skeleton)["writes"]
        expected_addresses = Counter(reg for reg, _, _, _ in source_writes
                                     if pack(phase, reg, ctypes.byref(ctypes.c_uint32())) == 0)
        observed_addresses = Counter()
        present = exact = canonical_period = disabled_instances = 0
        for reg, value, _, _ in writes:
            calculated = ctypes.c_uint32()
            ret = pack(phase, reg, ctypes.byref(calculated))
            if ret == -2:  # other families deliberately outside this composer
                continue
            if ret:
                raise RuntimeError("geometry provider failed for retained phase " + str(phase))
            present += 1
            observed_addresses[reg] += 1
            if reg in {0x3f60, 0x3f64, 0x3f68, 0x4d60, 0x5260, 0x5460, 0x6360}:
                disabled_instances += 1
            if reg == 0x008c:
                # OEM preserves undefined stack upper bits; Linux zeroes them.
                matches = (value & 0x1f) == calculated.value
                canonical_period += 1
            else:
                matches = value == calculated.value
            exact += int(matches)
        if observed_addresses != expected_addresses:
            raise RuntimeError("retained composer coverage differs from actual E007Y source phase " + str(phase))
        if exact != present:
            raise RuntimeError("retained geometry/disable/period mismatch at phase " + str(phase))
        phases.append({"phase": phase, "register_instances_present": present,
                       "semantic_instances_exact": exact,
                       "disabled_module_instances": disabled_instances,
                       "period_instances_compared_defined_low_5_bits": canonical_period})
    # Actual E007Y packet0 emits seven disable words; later phases omit them.
    expected = [106, 99, 1, 1]
    if [p["disabled_module_instances"] for p in phases] != [7, 0, 0, 0]:
        raise RuntimeError("retained packet-specific disable coverage differs")
    if [p["register_instances_present"] for p in phases] != expected:
        raise RuntimeError("retained geometry coverage differs: aggregate-only phase counts " + str(phases))
    return {"status": "PASS_RETAINED_GEOMETRY_DISABLE_PERIOD_ORACLE",
            "phase_results": phases,
            "register_instances_present": sum(p["register_instances_present"] for p in phases),
            "semantic_instances_exact": sum(p["semantic_instances_exact"] for p in phases),
            "OEM_undefined_period_upper_bits_canonicalized_to_zero": True,
            "source_skeleton_and_retained_composer_address_multisets_match": True,
            "private_words_payloads_or_images_exported": False,
            "new_camera_capture": False}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--private-retained-oracle", action="store_true")
    parser.add_argument("--linear-full-nv12", action="store_true")
    args = parser.parse_args()
    if args.report.exists():
        raise SystemExit("report identity already exists")
    staged = args.staged.resolve()
    with tempfile.TemporaryDirectory(prefix="sp11-rear-geometry-") as temporary:
        temporary = Path(temporary)
        period = (staged / "camss-e007c-period-cfg.inc").read_text()
        anchor = "static int\ne007c_rear_fill_startup_packet("
        if period.count(anchor) != 1:
            raise RuntimeError("period provider extraction anchor drift")
        (temporary / "e007c-period-types.h").write_text(period[:period.index(anchor)])
        if args.linear_full_nv12 and args.private_retained_oracle:
            raise RuntimeError("8-bit diagnostic output cannot be claimed exact to compressed 10-bit oracle")
        # Put fixture beside the temporary translation unit so every included
        # packer and binder resolves to --staged, rather than HERE implicitly.
        (temporary / "rear-geometry-host-fixture.h").write_bytes(
            (HERE / "rear-geometry-host-fixture.h").read_bytes())
        test_source = (HERE / "test-rear-startup-geometry.c").read_text()
        if args.linear_full_nv12:
            test_source = test_source.replace("value == 1023", "value == (path ? 1023U : 255U)")
            anchor = "\t\tCHECK(base[p].regs.mnds.input_width == 4064);"
            test_source = test_source.replace(anchor,
                "\t\tCHECK(base[p].regs.geometry.full.bit_width == 8);\n"
                "\t\tCHECK(base[p].regs.geometry.ds4.bit_width == 10 && base[p].regs.geometry.ds16.bit_width == 10);\n" + anchor)
        (temporary / "test-rear-startup-geometry.c").write_text(test_source)
        results = []
        for compiler in ("gcc", "clang"):
            executable = shutil.which(compiler)
            if not executable:
                raise RuntimeError("required compiler absent: " + compiler)
            binary = temporary / (compiler + "-geometry")
            checked([executable, "-std=gnu11", "-Wall", "-Wextra", "-Werror",
                     "-O1", "-g", "-fsanitize=address,undefined",
                     "-fno-omit-frame-pointer", "-I" + str(temporary),
                     "-I" + str(staged), str(temporary / "test-rear-startup-geometry.c"),
                     "-o", str(binary)])
            env = dict(os.environ, ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",
                       UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1")
            run = checked([str(binary)], env=env)
            if "NATIVE_REAR_GEOMETRY_PASS" not in run.stdout:
                raise RuntimeError("geometry test result absent")
            results.append({"compiler": compiler, "compile_Werror": True,
                            "sanitizers": ["ASAN", "UBSAN"], "stdout": run.stdout.strip(),
                            "stderr": run.stderr})
        report = {"status": "PASS_HOSTED_REAR_GEOMETRY_COMPOSER",
                  "actual_geometry_period_disable_packers_and_binder": True,
                  "unrelated_full_packet_fields_omitted_in_host_fixture": True,
                  "results": results, "hardware_access": False,
                  "ready_or_sealed_state_granted": False,
                  "linear_NV12_or_full_rear_bootstrap_proven": False}
        if args.private_retained_oracle:
            report["retained_oracle"] = private_oracle(staged, temporary)
    report["linear_FULL_NV12"] = args.linear_full_nv12
    report["FULL_output_bits"] = 8 if args.linear_full_nv12 else 10
    report["fixture_and_translation_unit_resolve_actual_staged_includes"] = True
    args.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))

if __name__ == "__main__":
    main()
