#!/usr/bin/env python3
"""E004hq: reject alternate SPMI callback/archived live identity tampering."""
from pathlib import Path
import importlib.util
import pefile
import zipfile
import json

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("e004hq_verify",HERE/"verify_alternate.py")
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
spmi=m.original("qcspmi8380",m.SPMI_SHA)
pmic=m.original("qcpmic8380",m.PMIC_SHA)
observed=m.audit(spmi,pmic)
assert observed["provider_original_masked_rmw_callback_rva"]=="0x1920"
assert observed["alternate_rmw_writes_without_direct_call_to_spmi_plus1660"] is True
assert observed["real_rmw_callback_entry_ever_observed"] is False
assert observed["original_idle_0x93_first_writer_identified"] is False
arch=next((m.HN/"evidence").glob("ORIGINAL-SP7-READONLY-SPMI-LIVE-INTERFACE-KD-*.zip"))
with zipfile.ZipFile(arch) as z:original=z.read(z.namelist()[0])
hp=json.loads((m.HP/"evidence/RESULT.json").read_text())
m.verify_prior(original,hp)
for bad in (
    original.replace(b"3dea1920",b"3dea1660"),
    original.replace(b"3dea1660",b"3dea1920"),
):
    try:m.verify_prior(bad,hp)
    except AssertionError:pass
    else:raise AssertionError("E004HQ_LIVE_SPMI_POINTER_TAMPER_ACCEPTED")
for field,value in (
    ("original_filtered_spmi_entry_rva","0x1920"),
    ("actual_timer_address_span_callback_hit_markers",1),
    ("original_raw_lowlevel_timer_callback_complete_absence_proven",True),
    ("independent_early_callback_positive_control_hit",False),
):
    changed=hp.copy();changed[field]=value
    try:m.verify_prior(original,changed)
    except AssertionError:pass
    else:raise AssertionError("E004HQ_PREVIOUS_TIMER_OBSERVER_SCOPE_TAMPER_ACCEPTED "+field)
mutations=[("spmi",rva) for rva,_,_ in m.PROVIDER]
mutations += [("pmic",rva) for rva,_,_ in m.CONSUMER]
for name,rva in mutations:
    source=spmi if name=="spmi" else pmic
    raw=bytearray(source.__data__)
    raw[source.get_offset_from_rva(rva)]^=0x40
    wrong=pefile.PE(data=bytes(raw))
    try:
        m.audit(wrong,pmic) if name=="spmi" else m.audit(spmi,wrong)
    except AssertionError:pass
    else:raise AssertionError("E004HQ_ORIGINAL_CALLBACK_MUTATION_ACCEPTED "+name+" "+hex(rva))
print("E004HQ_TWO_LIVE_CALLBACK_SLOTS_AND_ORIGINAL_ARM64_NEGATIVES=PASS COUNT="+str(len(mutations)+6))
print("E004HQ_ACTUAL_TIMER_ORIGINAL_FIRST_WRITER_AND_EMITTER_CUTOFF_STILL_UNOBSERVED")
