#!/usr/bin/env python3
from pathlib import Path
import json,sys

d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004bm VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_COMPILE_ONLY_PROTECTED_SAMPLE_SCAFFOLD_ZERO_RUNTIME_TEXT_DIFF","status")

build=(d/"evidence/BUILD-AND-NO-RUNTIME-DIFF.txt").read_text(errors="replace")
for x in (
 "baseline_text=fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e",
 "scaffold_text=fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e",
 "TEXT_BYTE_IDENTICAL=1",
 "baseline_vermagic=7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64",
 "scaffold_vermagic=7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64",
 "camss_protected_sample_compile_contract",
):
    need(x in build,"build evidence missing "+x)

patch=(d/"CAMSS-PROTECTED-SAMPLE-SCAFFOLD.patch").read_text(errors="replace")
for x in (
 '#include "camss-protected-sample.h"',
 "CAMSS_PROTECTED_SAMPLE_ID_BYTES 16",
 "CAMSS_PROTECTED_SAMPLE_MAX_PLANES 3",
 "struct camss_protected_sample",
 "struct camss_protected_sample_ops",
 "camss_protected_sample_compile_contract",
):
    need(x in patch,"patch contract missing "+x)

for bad in ("qcom_scm","qcomtee","assign_mem","mem_assign","dma_heap","hyp_assign","vmid"):
    need(bad.lower() not in patch.lower(),"forbidden implementation symbol in patch: "+bad)

post=(d/"evidence/POST-BUILD-STATE.txt").read_text(errors="replace")
for x in (
 "kernel=7.1.5-sp11-render-parity-v4+",
 "2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4",
 "69fdbb6364a772d5b9fe50114878bbc7a1a1ffc61e62af1e71c79fd16e94c982",
 "98474729d5036a4e1770e3ab7d275ccaaba143b22202468e4ad8b93c0cbec2cb",
):
    need(x in post,"post-build state missing "+x)

need(r["scaffold"]["backend_instance_present"] is False,"backend instance")
need(r["scaffold"]["runtime_selector_present"] is False,"runtime selector")
need(r["scaffold"]["queue_selector_present"] is False,"queue selector")
need(r["build"]["text_byte_identical"] is True,"text identity")
need(r["production_source_unchanged"] is True,"production source")
for k,v in r["prohibited_runtime_features"].items():
    need(v is False,"prohibited runtime feature "+k)
need(r["linux_secure_runtime_executed"] is False,"secure runtime")

print("E004bm VERIFY: PASS")
print(" - scaffold compiles against the current CAMSS source")
print(" - baseline and scaffold executable .text are byte-identical")
print(" - no protected-memory backend or activation path exists")
print(" - production CAMSS source and Golden runtime remain unchanged")
