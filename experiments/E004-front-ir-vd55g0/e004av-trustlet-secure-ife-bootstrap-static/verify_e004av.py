#!/usr/bin/env python3
from pathlib import Path
import json,sys

d=Path(__file__).resolve().parent
def fail(m):
    print("E004av VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
if r.get("status")!="PASS_SECURE_IFE_BOOTSTRAP_AND_HW_VERSION_STATIC": fail("status")
if r.get("runtime_executed") is not False or r.get("linux_secureisp_runtime_authorized") is not False:
    fail("runtime boundary")
i=r["init"]
for k,v in {
    "task_class":1,
    "task_id":0,
    "task_output_bytes":4,
    "task_output_source":"first 32-bit value at secure mapped base",
    "kmd_label":"IFE_HW_VERSION",
    "runtime_value":"not-captured-in-e004av",
}.items():
    if i.get(k)!=v: fail("init "+k)
cmd=r["trustlet_internal_commands"]
if cmd!={"device_config":"0x802","send_csl_packet":"0x803","device_start":"0x804","device_stop":"0x805"}:
    fail("internal command map")
w=r["secure_worker"]
for k in ("secure_ife_manager","secure_csid_logic","csl_iq_packet_processing","secure_output_buffer_handling"):
    if not w.get(k): fail("worker "+k)
if w.get("active_surface_ir_core_id")!="unproven": fail("active core overclaim")
if r["base_topology"].get("active_core_inference")!="none": fail("topology overclaim")

boot=(d/"evidence/TRUSTLET-BOOTSTRAP-DECOMP.txt").read_text(errors="replace")
for s in [
    "case 0:",
    "FUN_1800086a8(DAT_18003d1f0",
    "ISPDriverInit",
    "FUN_180008f60",
    "ISPDriverConfig",
    "*param_2 = *puVar3",
    "*param_4 = 4",
]:
    if s not in boot: fail("bootstrap "+s)

kmd=(d/"evidence/KMD-INIT-RETURN.txt").read_text(errors="replace")
for s in ["FUN_140004a90(0,0","IFE_HW_VERSION","local_164"]:
    if s not in kmd: fail("KMD init "+s)

inner=(d/"evidence/TRUSTLET-INTERNAL-COMMANDS.txt").read_text(errors="replace")
for s in [",0x802,",",0x803,",",0x804,",",0x805,"]:
    if s not in inner: fail("inner command "+s)

hal=(d/"evidence/SECURE-HAL-INDEX.txt").read_text(errors="replace")
for s in ["DAL_secure_ife","DAL_secure_csid","DAL_csid_process_iq_packet","Register_secure_CSID"]:
    if s not in hal: fail("HAL marker "+s)

top=(d/"evidence/BASE-TOPOLOGY.txt").read_text()
for s in [
    "mapped_windows_secureisp_resource_size=0x4000",
    "core=0 csid_derived_offset=0x4000",
    "core=2 csid_derived_offset=0x0000",
    "interpretation=pointer arithmetic only; active secure core is not inferred",
    "runtime_executed=no",
]:
    if s not in top: fail("topology "+s)

print("E004av VERIFY: PASS")
print(" - task-0 feeds the secure aperture into the trustlet ISP manager")
print(" - 4-byte task-0 return is statically identified as IFE_HW_VERSION")
print(" - secure config/start/stop/CSL tasks map into the trustlet ISP worker")
print(" - secure IFE/CSID HAL logic lives inside the trustlet")
print(" - active Surface IR core/register route is deliberately not inferred")
print(" - no Linux secure-camera runtime occurred")
