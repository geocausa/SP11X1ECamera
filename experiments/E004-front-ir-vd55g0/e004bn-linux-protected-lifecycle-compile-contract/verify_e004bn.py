#!/usr/bin/env python3
from pathlib import Path
import json,sys

d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004bn VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_COMPILE_ONLY_THREE_DOMAIN_PROTECTED_LIFECYCLE_CONTRACT","status")

ev=(d/"evidence/BUILD-AND-LIFECYCLE-SEPARATION.txt").read_text(errors="replace")
for x in (
 "baseline_text=fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e",
 "scaffold_text=fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e",
 "TEXT_BYTE_IDENTICAL=1",
 "struct camss_protected_queue_contract",
 "struct camss_protected_sample_ops",
 "struct camss_secure_lane_ops",
 "struct camss_protected_lifecycle_contract",
):
    need(x in ev,"build/lifecycle evidence missing "+x)

patch=(d/"CAMSS-PROTECTED-LIFECYCLE-SCAFFOLD.patch").read_text(errors="replace")
for x in (
 "cpu_mappable",
 "ordinary_sg_fallback",
 "read_io_allowed",
 "mmap_io_allowed",
 "dmabuf_import_requires_protected_proof",
 "struct camss_protected_sample_ops",
 "struct camss_secure_lane_ops",
 "sample_ops;",
 "lane_ops;",
):
    need(x in patch,"contract missing "+x)

for bad in ("qcom_scm","qcomtee","assign_mem","mem_assign","dma_heap","hyp_assign","vmid","tzapp"):
    need(bad.lower() not in patch.lower(),"forbidden implementation symbol "+bad)

need(r["domains"]["represented_separately"] is True,"domain separation")
for k in ("contract_instance_present","sample_ops_instance_present","lane_ops_instance_present",
          "queue_selector_present","v4l2_control_present","secure_backend_present"):
    need(r["runtime"][k] is False,"runtime path present: "+k)
need(r["build"]["text_byte_identical"] is True,"text identity")
for k,v in r["safety"].items():
    if k=="production_source_unchanged":
        need(v is True,k)
    else:
        need(v is False,k)

print("E004bn VERIFY: PASS")
print(" - queue, sample and lane ownership are separate compile-time contracts")
print(" - no backend, selector or operation instance exists")
print(" - executable .text remains byte-identical to baseline")
print(" - production source and Golden runtime remain untouched")
