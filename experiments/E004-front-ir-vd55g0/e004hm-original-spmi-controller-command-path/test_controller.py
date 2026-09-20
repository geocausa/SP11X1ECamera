#!/usr/bin/env python3
"""E004hm: original SPMI register-store, command and status mutation negatives."""
from pathlib import Path
import importlib.util
import pefile

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hm_verifier",HERE/"verify_controller.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
spmi=m.original("qcspmi8380",m.SPMI_SHA)
pmic=m.original("qcpmic8380",m.PMIC_SHA)
data=m.audit(spmi,pmic)
assert m.prior()
assert data["original_spmi_controller_command_mmio_write_rva"]=="0x67e0"
for key in ("mmio_stores_guarantee_actual_physical_pmic_write",
            "finite_host_poll_counter_is_autonomous_emitter_watchdog",
            "real_windows_spmi_callback_hit_this_stage",
            "actual_controller_mmio_status_observed_this_stage",
            "first_writer_of_idle_timer_byte_0x93_identified",
            "real_light_pulse_current_irradiance_or_fault_off_measured"):
    assert data[key] is False,key

cases=(("spmi",rva) for rva,_,_ in m.SPMI_OPCODES)
cases=list(cases)+[("pmic",rva) for rva,_,_ in m.PMIC_OPCODES]+[
    ("spmi",0x3e88),("spmi",0x3e74)]
for name,rva in cases:
    original=spmi if name=="spmi" else pmic
    mutated=bytearray(original.__data__)
    mutated[original.get_offset_from_rva(rva)]^=0x40
    wrong=pefile.PE(data=bytes(mutated))
    try:m.audit(wrong,pmic) if name=="spmi" else m.audit(spmi,wrong)
    except AssertionError:pass
    else:raise AssertionError("E004HM_ORIGINAL_INSTRUCTION_MUTATION_ACCEPTED "+
                              name+" "+hex(rva))
print("E004HM_ORIGINAL_SPMI_CONTROLLER_MMIO_STATUS_NEGATIVES=PASS COUNT="+str(len(cases)))
print("E004HM_CPU_CONTROLLER_STATUS_NOT_REAL_IR_EMISSION_OR_AUTONOMOUS_CUTOFF=PASS")
