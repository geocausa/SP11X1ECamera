#!/usr/bin/env python3
"""Reproducible OFFLINE E004fz rollback patch result; not emitter authorization."""
from hashlib import sha256
from pathlib import Path
import json
import subprocess

from generate_patch import BASE,PRIOR,PATCH,base_after_0003,produce,require

HERE=Path(__file__).resolve().parent
E=HERE/"evidence"
SHA_0004="cbc8bc73882fd258e81549e96323f11c7bdefa2fefed6870f7da82be838b55ce"
SHA_COMBINED="6c7ccabfad2e67a19dfb3330ca831abb7e688108f55eee78c5c525e78db0b06a"

def execute(name, marker, timeout):
    response=subprocess.run(["python3",str(HERE/name)],
                            capture_output=True,text=True,check=False,timeout=timeout)
    require(response.returncode==0 and marker in response.stdout,
            name+" failed: "+response.stderr[-1100:]+response.stdout[-350:])
    return response.stdout

def main():
    before,after,patch=produce()
    require(PATCH.is_file() and sha256(PATCH.read_bytes()).hexdigest()==SHA_0004
            and PATCH.read_text()==patch,"source-only patch drift")
    require(sha256(after.encode()).hexdigest()==SHA_COMBINED,
            "combined driver source drift")
    harness=execute("test_rollback.py","E004FZ_ACTUAL_PATCHED_C=PASS",85)
    build=execute("test_kernel_build.py",
                  "E004FZ_ISOLATED_GOLDEN_KERNEL_BUILD=PASS",175)
    require("ASAN_UBSAN=PASS" in harness and
            "ROLLBACK_BUS_FAILURE=EXPLICITLY_UNSAFE_LOGGED" in harness,
            "fault-injection safety limitation lost")
    require("MODULE_LOADED=NO EMITTER=OFF" in build,
            "isolated module build contract lost")
    result={
        "experiment":"E004fz",
        "status":"PASS_OFFLINE_FLASH_ERROR_ROLLBACK_SOURCE_AND_FAULT_TESTS",
        "baseline_source_sha256":sha256(BASE.read_bytes()).hexdigest(),
        "prior_timer_patch_sha256":sha256(PRIOR.read_bytes()).hexdigest(),
        "uninstalled_error_rollback_patch_sha256":SHA_0004,
        "combined_source_sha256":SHA_COMBINED,
        "original_error_preserved_by_dispatcher":True,
        "rollback_attempts_after_failed_initial_disarm":True,
        "rollback_attempts_after_failed_final_arm":True,
        "software_rollback_order":"best effort channel disable then module disable",
        "failure_stages_simulated":6,
        "failed_initial_and_final_hardware_disarm_simulated":True,
        "failed_rollback_reads_or_writes_physically_proven_safe":False,
        "address_and_undefined_sanitizers":"PASS",
        "isolated_kernel_module_build":"PASS W=1 on Golden headers",
        "patch_installed":False,
        "module_loaded":False,
        "pmic_values_read_or_written":False,
        "ir_emitter_activated":False,
        "independent_hardware_cutoff_verified":False,
        "current_and_irradiance_limits_verified":False,
        "allowed_to_enable_ir_emitter":False,
        "important_limitations":[
            "An SPMI bus failure may leave LEDs enabled even after both software disarm attempts fail.",
            "Disabling a shared flash module cannot be guaranteed when another LED owns live channels.",
            "An auto-Golden reboot, watchdog or user-space timeout does not independently extinguish a stuck emitter.",
            "No current/irradiance limits, electrical pulse widths or hard fault-off path have been physically established."
        ],
        "next_gate":"A separately scoped Windows KDNET shutdown-path review and independent electrical/optical off/current authority, with no Linux illumination until verified."
    }
    E.mkdir(exist_ok=True)
    (E/"RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004FZ_RESULT=PASS OFFLINE_ROLLBACK_TESTS=PASS MODULE_BUILD=PASS")
    print("HARDWARE_FAULT_OFF_PROVEN=NO EMITTER_ENABLE_AUTHORIZED=NO GOLDEN_UNCHANGED=YES")

if __name__=="__main__":
    main()
