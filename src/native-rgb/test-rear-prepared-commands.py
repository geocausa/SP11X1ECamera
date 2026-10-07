#!/usr/bin/env python3
"""Hosted execution of actual staged rear allocator/semantic wrapper/consumer.
The semantic generator and hardware callbacks are mocks, explicitly not IQ or
hardware proof. Skeletons, layouts, E008L/E008N/E008O and validator are real code.
"""
import argparse, json, os, shutil, subprocess, tempfile
from pathlib import Path
HERE = Path(__file__).resolve().parent
def main():
    p = argparse.ArgumentParser()
    p.add_argument("--staged", type=Path, required=True)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    if a.report.exists():
        raise SystemExit("report identity already exists")
    source = a.staged.resolve()
    for name in ("camss-vfe-e008l-rear-command-dma.inc",
                 "native-rear-prepared-commands.inc",
                 "camss-vfe-e008n-rear-single-use.inc",
                 "camss-vfe-e008o-rear-semantic-state.inc"):
        assert (source/name).is_file(), name
    with tempfile.TemporaryDirectory(prefix="sp11-rear-handoff-tests-") as tmp:
        tmp = Path(tmp)
        y = (source/"camss-e007y-rear-startup.inc").read_text()
        # Actual layouts, skeletons and wrapper generator; no semantic substitute
        # is claimed for the missing producer implementation.
        prefix = y[:y.index("static int\ne007y_rear_slot(")]
        wrappers = y[y.index("static void e007y_rear_clear_output("):
                     y.index("static int\ne007y_rear_materialize(")]
        (tmp/"e007y-layout.h").write_text(prefix + wrappers)
        k = (source/"camss-vfe-e008k-rear-runner.inc").read_text()
        types = k[k.index("struct e008k_rear_request {"):
                  k.index("static int\ne008k_rear_submit_packet(")]
        validate = k[k.index("static int\ne008k_rear_validate_prepared_packets("):
                     k.index("static int\ne008k_rear_collect_done(")]
        (tmp/"e008k-prepared-validator.h").write_text(types + validate)
        results = []
        for compiler in ("gcc", "clang"):
            executable = shutil.which(compiler)
            if not executable:
                raise SystemExit("required compiler missing: "+compiler)
            binary = tmp/(compiler+"-test")
            args = [executable, "-std=gnu11", "-Wall", "-Wextra", "-Werror",
                    "-O1", "-g", "-fsanitize=address,undefined",
                    "-fno-omit-frame-pointer", "-I"+str(tmp), "-I"+str(source),
                    str(HERE/"test-rear-prepared-commands.c"), "-o", str(binary)]
            compiled = subprocess.run(args, capture_output=True, text=True)
            if compiled.returncode:
                raise RuntimeError(compiled.stdout + compiled.stderr)
            env = dict(os.environ, ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",
                       UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1")
            run = subprocess.run([str(binary)], capture_output=True,
                                 text=True, env=env)
            if run.returncode:
                raise RuntimeError(run.stdout + run.stderr)
            assert "NATIVE_REAR_PREPARED_HANDOFF_PASS" in run.stdout
            results.append({"compiler": compiler, "sanitizers": ["ASAN", "UBSAN"],
                            "stdout": run.stdout.strip(), "stderr": run.stderr,
                            "compile_Werror": True})
    report = {"gate":"rear prepared-command handoff", "status":"PASS_HOSTED_HANDOFF",
              "actual_allocator_wrapper_semantic_handoff_consumer": True,
              "semantic_providers_mocked": True, "hardware_callbacks_mocked": True,
              "runtime_hardware_proof": False, "results":results}
    a.report.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report))
if __name__=="__main__":
    main()
