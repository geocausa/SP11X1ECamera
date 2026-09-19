#!/usr/bin/env python3
"""Reconcile consumed E004gb original evidence; OFFLINE, no camera or debugger."""
from pathlib import Path
from hashlib import sha256
from zipfile import ZipFile
import re
import json

HERE=Path(__file__).resolve().parent
E=HERE/"evidence"
ZIP=E/"ORIGINAL-WINDOWS-LOGS.zip"
ZIP_SHA="330afa1f20fc2714d8e8a172c6d754dbb4d32e5dc1a41e174825bb2c0eb0bfbf"
POSTBOOT_SHA="fb1cf93cbe78788094452a7c2596f542619d3b9958f67620001ed51138e60bd0"
SHA={
"e004gb-flash-enable-kd.log":"058d15d56fdfe31a5b4dbae54ae1544cb0788fba83fc82b57c696d26fde609df",
"e004gb-observer-kd.log":"cf889c909142b786a8778fe7528b7b315af64eb3742c71fd61addf29286997ae",
"CAPTURE-ORIGINAL-WINDOWS.txt":"12675cc0bac2b70775215c3b6234d79c527965825de9a842739d63df725c07fc",
"SESSION_COMPLETED_WINDOWS.json":"bb7d13ab98af0813542f07453e470054e030f747c63e5d8e532bc59ac92c5bcb",
"WINDOWS_ONESHOT_CONSUMED.json":"b70dc8be4b834c10190b15d6cbd0e436b90d3a302a327f0af192d0216d04cac8",
"KD_DRY_VALIDATED.json":"77807c037527fc1e81ed6f1d287061c3ed9f2a8aae9f4a5f01536779ea678827",
"KD_ARMED_CONFIRMED.json":"3bf7204639f920b01d64afb582e390443cfa98825e52ab33ce743247d1d8be1f",
"WINDOWS_CAPTURE_ATTEMPTED.json":"8b5021832299e281e167c7604d6f002bbec04d9aa5d4982c3fb9f1bd1b821258"}
TARGETS=[0xee3e,0xee3f,0xee40,0xee41,0xee46,0xee4a,0xee4b,0xee4c,0xee4d,0xee4e,0xee67]
SKIPS=[0xee3d,0xee42,0xee45,0xee47,0xee49,0xee4f,0xee66,0xee68]
# reg, mask, Windows helper original byte, requested merged byte, post helper buffer
EXPECTED=[
(0xee4a,0x70,0x01,0x00,0x01),(0xee4b,0x70,0x01,0x00,0x01),
(0xee4c,0x70,0x01,0x00,0x01),(0xee4d,0x70,0x01,0x00,0x01),
(0xee4a,0x07,0x01,0x05,0x05),(0xee4d,0x07,0x01,0x05,0x05),
(0xee67,0x01,0x01,0x00,0x00),(0xee46,0x80,0x00,0x80,0x80),
(0xee4e,0x0f,0x00,0x09,0x09),(0xee46,0x80,0x80,0x00,0x00),
(0xee4e,0x0f,0x09,0x00,0x00)]
PRE=re.compile(r"^E004GB_PRE hit=(\d+) reg=([0-9a-f]{4}) mask=([0-9a-f]+) read_rc=([0-9a-f]+) ")
POST=re.compile(r"^E004GB_POST hit=(\d+) reg=([0-9a-f]{4}) mask=([0-9a-f]+) write_rc=([0-9a-f]+) ")
BYTE=re.compile(r"[0-9a-f]{8}\x60[0-9a-f]{8}\s+([0-9a-f]{2})\s+[.]\s*$",re.I)

def need(ok,reason):
    if not ok: raise ValueError("E004GB_EVIDENCE_FAIL_CLOSED "+reason)

def originals():
    need(ZIP.exists() and sha256(ZIP.read_bytes()).hexdigest()==ZIP_SHA,"archive changed")
    with ZipFile(ZIP) as z:
        need(len(z.namelist())==len(SHA) and set(z.namelist())==set(SHA),
             "archive names changed")
        a={n:z.read(n) for n in SHA}
    for n,h in SHA.items():
        need(sha256(a[n]).hexdigest()==h,"original checksum "+n)
    return a

def dry_check(s):
    need("E004GB_DRY_BEGIN" in s and "E004GB_DRY_END_STAY_BROKEN" in s,
         "live MASM dry markers")
    seen=re.findall(r"(?m)^E004GB_DRY_(TARGET|SKIP) reg=([0-9a-f]{4})\s*$",s)
    expected=[("TARGET",f"{r:04x}") for r in TARGETS]+[("SKIP",f"{r:04x}") for r in SKIPS]
    need(len(seen)==19 and sorted(seen)==sorted(expected),"dry target or exclusion wrong")
    need("E004GB_DRY_POSTREG raw=1234ee4a reg=ee4a" in s
         and "E004GB_ARM_BEGIN" not in s,"post-reg or premature arm")
    return True

def displayed_byte(line):
    m=BYTE.search(line)
    need(m is not None,"KD register buffer display not parseable")
    return int(m.group(1),16)

def parse_trace(s):
    lines=s.splitlines()
    pre=[];post=[]
    for i,line in enumerate(lines):
        m=PRE.match(line)
        if m:
            need(i+1<len(lines),"truncated read buffer")
            pre.append((int(m.group(1)),int(m.group(2),16),int(m.group(3),16),int(m.group(4),16))+
                       (displayed_byte(line),displayed_byte(lines[i+1])))
        m=POST.match(line)
        if m:
            post.append((int(m.group(1)),int(m.group(2),16),int(m.group(3),16),int(m.group(4),16))+
                        (displayed_byte(line),))
    need(len(pre)==len(post)==11,"RMW helper call count not eleven")
    result=[]
    for n,(a,b,exp) in enumerate(zip(pre,post,EXPECTED),1):
        hit,reg,mask,readrc,old,wanted=a
        posthit,postreg,postmask,writerc,buffer=b
        need(hit==posthit==n and reg==postreg and mask==postmask
             and readrc==writerc==0,"unpaired or unsuccessful helper call "+str(n))
        need((reg,mask,old,wanted,buffer)==exp,"changed register bytes at hit "+str(n))
        result.append({"hit":n,"register":f"0x{reg:04x}","mask":f"0x{mask:02x}",
                       "helper_read_byte":f"0x{old:02x}",
                       "helper_requested_byte":f"0x{wanted:02x}",
                       "post_helper_buffer":f"0x{buffer:02x}",
                       "read_rc":readrc,"write_rc":writerc})
    s=s.replace("\r\n","\n")
    need("E004GB_ARM_BEGIN" in s and "E004GB_ARMED_STAY_BROKEN" in s,
         "observer was not armed")
    need("0: kd> bc *\n0: kd> bl\n\n0: kd> .logclose" in s,
         "KD breakpoint clearing/log closure missing")
    need("Syntax error" not in s and "Malformed string" not in s,
         "WinDbg observer execution error")
    return result

def capture_check(s):
    s=s.replace("\r\n","\n").replace("\r","\n")
    need("E004GB_SOURCE subtype=NV12 width=644 height=604 fps=60/1" in s,
         "unexpected capture format")
    for marker in ("E004GB_INIT_PASS","E004GB_START=Success",
                   "E004GB_ACQUIRED=12","E004GB_STOP_PASS","E004GB_END "):
        need(marker in s,"missing capture lifecycle "+marker)
    frames=[int(x) for x in re.findall(r"(?m)^E004GB_FRAME n=(\d+) ",s)]
    need(frames==list(range(1,13)),"12-frame sequence changed")
    readings=re.findall(r"(?m)^E004GB_EXPOSURE phase=(?:initialized|frame-\d+) auto=(\w+) .*?value_ticks=(\d+)$",s)
    need(len(readings)==13 and set(readings)=={("True","5000")},
         "Windows API exposure readback changed")
    return {"frames_acquired":12,"stop":"PASS","format":"NV12","width":644,
            "height":604,"reported_fps":"60/1","image_files_saved":False}

def verify():
    post=E/"POSTBOOT.txt"
    marker_file=E/"CONSUMED.json"
    need(post.is_file() and sha256(post.read_bytes()).hexdigest()==POSTBOOT_SHA,
         "Golden postboot original evidence changed")
    need(marker_file.is_file() and sha256(marker_file.read_bytes()).hexdigest()==
         "e54e219a3a567d58dd1f2afbd0d6b0f2983e426e934209c2e60e73850e04ee0b",
         "consumed marker changed")
    post_text=post.read_text()
    marker=json.loads(marker_file.read_text())
    for item in ("E004GB_GOLDEN_POSTBOOT",
                 "6ca88e8c-525b-4944-bffa-037a4337a01d",
                 "FLASH_DT_STATUS=disabled", "saved_entry=sp11-audio-fullio-v19c",
                 "next_entry=\n", "BootCurrent: 0005",
                 "BootOrder: 0005,0004,0000,0001,0002,0006",
                 "nodes=no modules=none active_processes=no", "OVERLAP_GUARD=PASS"):
        need(item in post_text,"postboot Golden/flash/camera evidence: "+item)
    need(marker["identity_consumed"] is True
         and marker["status"]=="COMPLETED_WINDOWS_OEM_PREVIEW_AND_RETURNED_GOLDEN_ONE_SHOT_CONSUMED"
         and marker["golden_boot_id"]=="6ca88e8c-525b-4944-bffa-037a4337a01d"
         and marker["postboot_evidence_sha256"]==POSTBOOT_SHA
         and marker["same_identity_rerun_allowed"] is False
         and marker["native_linux_emitter_authorized"] is False,
         "consumed or native illumination contract changed")
    a=originals()
    kd=a["e004gb-observer-kd.log"].decode("ascii")
    dry=a["e004gb-flash-enable-kd.log"].decode("ascii")
    for s in (kd,dry):
        need(not re.search(r"(?i)\bkey\s*[:=]\s*[A-Za-z0-9.+/-]{8,}",s),
             "credential-like data in original KD log")
    dry_check(dry)
    rows=parse_trace(kd)
    capture=capture_check(a["CAPTURE-ORIGINAL-WINDOWS.txt"].decode("ascii"))
    markers={n:json.loads(a[n]) for n in a if n.endswith(".json")}
    need(markers["WINDOWS_ONESHOT_CONSUMED.json"]["windows_boot_occurred"]
         and markers["WINDOWS_ONESHOT_CONSUMED.json"]["one_shot_reboot_reuse_allowed"] is False,
         "one-shot identity not consumed")
    done=markers["SESSION_COMPLETED_WINDOWS.json"]
    need(done["preview_frames"]==12 and done["capture_stop"]=="PASS"
         and done["kd_pre_hits"]==done["kd_post_hits"]==11,
         "SP7 completion marker differs")
    need(done["kd_original_sha256"]==SHA["e004gb-observer-kd.log"]
         and done["windows_capture_original_sha256"]==SHA["CAPTURE-ORIGINAL-WINDOWS.txt"],
         "SP7 original evidence marker digest differs")
    signed=markers["KD_DRY_VALIDATED.json"]
    need(signed["status"]=="LIVE_KD_MASM_DRY_PASS_BEFORE_HOOK_ARM"
         and signed["raw_dry_log_sha256"]==SHA["e004gb-flash-enable-kd.log"]
         and signed["target_count"]==11 and signed["excluded_count"]==8,
         "live KD dry validation signature differs")
    need(markers["KD_ARMED_CONFIRMED.json"]["hook_count"]==2
         and markers["WINDOWS_CAPTURE_ATTEMPTED.json"]["attempt_limit"]==1,
         "KD/capture one-use contract differs")
    for key in ("physical_emitter_current_or_optical_pulse_measured",
                "independent_fault_off_verified","native_linux_emitter_authorized"):
        need(done[key] is False,"unsupported physical safety conclusion")
    return {
        "experiment":"E004gb",
        "status":"PASS_BOUNDED_WINDOWS_PMIC_FLASH_ENABLE_DISABLE_HELPER_OBSERVATION",
        "identity_consumed":True,"golden_postboot_verified":True,
        "golden_boot_id":"6ca88e8c-525b-4944-bffa-037a4337a01d",
        "postboot_sha256":POSTBOOT_SHA,"original_archive_sha256":ZIP_SHA,
        "original_member_sha256":SHA,
        "windows_pmic_module":"qcpmic8380.sys",
        "fresh_windows_module_base":"fffff802a5e40000",
        "live_kd_masm_dry_targets_passed":11,
        "live_kd_masm_dry_exclusions_passed":8,
        "kd_pre_calls":11,"kd_post_calls":11,
        "observed_masked_helper_calls":rows,
        "timer_register_access_observed_in_selected_helper":False,
        "module_enable_request":"ee46 mask 80: 00 -> 80, helper return 0",
        "channel_enable_request":"ee4e mask 0f: 00 -> 09, helper return 0",
        "module_disable_request":"ee46 mask 80: 80 -> 00, helper return 0",
        "channel_disable_request":"ee4e mask 0f: 09 -> 00, helper return 0",
        "capture":capture,
        "kd_breakpoints_cleared":True,
        "direct_post_write_pmic_readback_performed":False,
        "physical_led_pulse_duration_measured":False,
        "actual_led_current_or_irradiance_measured":False,
        "independent_stuck_trigger_or_host_failure_off_verified":False,
        "native_linux_emitter_activation_authorized":False,
        "limitations":[
            "The trace records successful Windows PMIC helper calls and buffer values, not physical LED emission or direct post-write PMIC register readback.",
            "No timer-register access hit this masked helper in the one bounded preview; timer state or independent hardware cutoff cannot be inferred.",
            "The Windows module-disable request preceded channel-disable request in this trace; physical off timing was not observed.",
            "The optical-current, irradiance, pulse-width and host-crash/stuck-trigger safety evidence required by E004fs remains missing."
        ]}

if __name__=="__main__":
    result=verify()
    (E/"RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
    print("E004GB_EVIDENCE=PASS WINDOWS_FRAMES=12 KD_PRE=11 KD_POST=11")
    print("MODULE_00_80_00=PASS CHANNEL_00_09_00=PASS TIMER_HELPER_HITS=0")
    print("PHYSICAL_SHUTOFF=UNPROVEN LINUX_IR_EMITTER_AUTHORIZED=NO")
