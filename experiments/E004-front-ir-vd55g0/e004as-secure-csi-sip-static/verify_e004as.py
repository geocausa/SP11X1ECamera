#!/usr/bin/env python3
from pathlib import Path
import json, re, sys

d=Path(__file__).resolve().parent
def fail(m):
    print("E004as VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
if r.get("status")!="PASS_STATIC_SECURE_CSI_SIP_DECODE_NO_RUNTIME": fail("status")
if r.get("linux_secureisp_runtime_authorized") is not False: fail("runtime boundary")
w=r["windows_request"]
if w.get("header_dword0")!="0x02001807" or w.get("header_dword1")!="0x00000002": fail("request header")
if w.get("payload_values")!=["protect_boolean","lane_protection_bitmask"]: fail("request payload")
s=r["smccc_decode"]
expect={"fast":False,"smc64":False,"owner":2,"owner_name":"SIP","function":"0x1807","qcom_service":"0x18","qcom_command":"0x07","arginfo":"0x00000002","arginfo_matches_qcom_scm_args_2_values":True}
for k,v in expect.items():
    if s.get(k)!=v: fail("SMCCC field "+k)
l=r["linux_tree"]
if l.get("symbolic_service_0x18") or l.get("exact_service_0x18_command_0x07_wrapper"): fail("unexpected in-tree wrapper")
if not l.get("generic_qcom_scm_transport_present"): fail("generic SCM missing")
for k,v in r["runtime"].items():
    if v: fail("runtime action "+k)
if r.get("windows_identity_4096_mapping")!="unresolved": fail("identity overclaim")

dec=(d/"evidence/SMC-DECODE.txt").read_text()
for x in [
 "request_header_raw=0718000202000000",
 "call_id=0x02001807",
 "arginfo=0x00000002",
 "owner=2",
 "function=0x1807",
 "qcom_service=0x18",
 "qcom_command=0x07",
 "argument_0=protect_boolean",
 "argument_1=lane_protection_bitmask",
 "runtime_executed=no",
]:
    if x not in dec: fail("decode evidence "+x)

qc=(d/"evidence/QCTREE-PASSTHROUGH-DECOMP.txt").read_text()
for x in [
 "PassThroughServiceSipSyscall",
 "puVar5 = *(undefined4 **)(param_5 + 0x10)",
 "FUN_14002c460(param_1,*puVar5,puVar5[1],param_4",
 "SipArmV8Syscall",
]:
    if x not in qc: fail("QcTrEE evidence "+x)

km=(d/"evidence/SECUREISP-CONFIG-DECOMP.txt").read_text()
for x in [
 "local_d0 = DAT_140001d08",
 "uStack_c8 = uVar9",
 "local_c0 = param_2",
 "uVar9 = (ulonglong)param_3",
]:
    if x not in km: fail("SecureISP evidence "+x)

abi=(d/"evidence/LINUX-SCM-ABI.txt").read_text()
for x in [
 "#define ARM_SMCCC_OWNER_SIP",
 "#define SCM_SMC_FNID(s, c)",
 "smc.args[0] = ARM_SMCCC_CALL_VAL",
 "smc.args[1] = desc->arginfo",
 "--- service 0x18 symbolic definition ---\nNONE",
 "--- exact svc18/cmd07 wrapper search ---\nNONE",
]:
    if x not in abi: fail("Linux ABI evidence "+x)

print("E004as VERIFY: PASS")
print(" - QcTrEE PassThrough is statically confirmed as the SIP bridge")
print(" - SecureISP request header is exact and carries two value arguments")
print(" - opaque call decodes to Qualcomm SIP service 0x18 / command 0x07")
print(" - current Linux qcom_scm has generic transport but no svc18/cmd07 wrapper")
print(" - no Linux secure-camera runtime occurred")
