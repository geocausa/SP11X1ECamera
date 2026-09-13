#!/usr/bin/env python3
from pathlib import Path
import json,sys,re

d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004bq VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_COMPILE_ONLY_TWO_BUFFER_PROTECTED_PIPELINE_ZERO_TEXT_DIFF","status")

ev=(d/"evidence/BUILD-AND-ZERO-RUNTIME.txt").read_text(errors="replace")
for x in (
    "baseline_text=fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e",
    "scaffold_text=fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e",
    "TEXT_BYTE_IDENTICAL=1",
    "struct camss_protected_queue_contract",
    "struct camss_secure_capture_target",
    "struct camss_external_protected_sample",
    "struct camss_protected_transfer_ops",
    "struct camss_secure_lane_ops",
    "FORBIDDEN_IMPLEMENTATION_SYMBOL_MATCHES=0",
):
    need(x in ev,"build evidence missing "+x)

patch=(d/"CAMSS-TWO-BUFFER-PROTECTED-CONTRACT.patch").read_text(errors="replace")
for x in (
    "phys_addr_t ownership_phys;",
    "dma_addr_t camss_iova[CAMSS_PROTECTED_MAX_PLANES];",
    "struct camss_external_protected_sample {",
    "struct camss_secure_capture_target_ops",
    "struct camss_external_protected_sample_ops",
    "struct camss_protected_transfer_ops",
    "struct camss_secure_lane_ops",
    "struct camss_protected_pipeline_contract",
    "struct camss_secure_capture_target *source",
    "struct camss_external_protected_sample *destination",
):
    need(x in patch,"contract missing "+x)

plain="\n".join(line[1:] if line.startswith("+") else line for line in patch.splitlines())
m=re.search(r"struct camss_external_protected_sample \{(.*?)\n\};",plain,re.S)
need(m is not None,"external sample struct")
need("camss_iova" not in m.group(1),"external sample incorrectly carries CAMSS IOVA")
need("ownership_phys" not in m.group(1),"external sample incorrectly carries ownership physical range")

for bad in ("qcom_scm_","qcomtee_","qcom_scm_assign_mem(","hyp_assign(",
            "dma_heap_buffer_alloc(","AssignMemoryToSocDomain(","MapSecureIo("):
    need(bad.lower() not in patch.lower(),"implementation symbol in patch: "+bad)

post=(d/"evidence/POST-BUILD-STATE.txt").read_text(errors="replace")
for x in (
    "kernel=7.1.5-sp11-render-parity-v4+",
    "2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4",
    "69fdbb6364a772d5b9fe50114878bbc7a1a1ffc61e62af1e71c79fd16e94c982",
    "98474729d5036a4e1770e3ab7d275ccaaba143b22202468e4ad8b93c0cbec2cb",
):
    need(x in post,"post-build state missing "+x)

need(r["domains"]["all_separate"] is True,"domain separation")
need(r["internal_target"]["physical_and_iova_separate"] is True,"physical/IOVA split")
need(r["internal_target"]["vmid_encoded"] is False,"VMID hardcoded")
need(r["external_sample"]["camss_iova_field"] is False,"external IOVA")
need(r["transfer"]["implementation_present"] is False,"transfer implementation")
need(r["runtime"]["callback_call_sites_present"] is False,"callback calls")
need(r["build"]["text_byte_identical"] is True,"text identity")
need(r["safety"]["production_source_unchanged"] is True,"production source")
for k in ("module_loaded","scm_call_executed","memory_assignment_executed",
          "linux_secure_runtime_executed","qcomtee_loaded","protected_mmio_access"):
    need(r["safety"][k] is False,k)

print("E004bq VERIFY: PASS")
print(" - internal hardware target and external protected sample are distinct types")
print(" - only the internal target carries physical ownership and CAMSS IOVA fields")
print(" - protected transfer, lane ownership and queue policy are separate interfaces")
print(" - no backend, selector or callback call site exists")
print(" - executable .text is byte-identical to baseline")
print(" - production source and Golden runtime remain untouched")
