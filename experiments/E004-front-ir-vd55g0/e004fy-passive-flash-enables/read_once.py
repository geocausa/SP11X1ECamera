#!/usr/bin/env python3
"""Consume E004fy BEFORE six exact passive PMIC register reads. Never retry."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json
import subprocess
import sys
import os
import re
from prepare import ADDRS, OFFSETS, E, HERE, check, require

P=E/"PREPARED.json"
C=E/"CONSUMED.json"
R=E/"RESULT.json"
PRIVILEGED = r"""
import os,sys
f="/sys/kernel/debug/regmap/0-01/registers"
addresses=(0xee46,0xee4a,0xee4b,0xee4c,0xee4d,0xee4e)
fd=os.open(f,os.O_RDONLY|os.O_CLOEXEC|os.O_NOFOLLOW)
try:
    for address in addresses:
        data=os.pread(fd,9,address*9)
        if len(data)!=9 or data[:6].lower()!=f"{address:04x}: ".encode():
            raise RuntimeError("unexpected record address/length")
        if data[8:] != b"\n":
            raise RuntimeError("unexpected record formatting")
        sys.stdout.buffer.write(data)
finally:
    os.close(fd)
"""

def main():
    require(P.is_file() and not C.exists() and not R.exists(),
            "prepared or consumed state differs")
    prepared=json.loads(P.read_text())
    require(prepared["status"]=="PREPARED_UNCONSUMED"
            and prepared["addresses"]==[f"0x{x:04x}" for x in ADDRS]
            and prepared["offsets"]==list(OFFSETS)
            and prepared["total_max_register_bytes"]==54,
            "prepared target/dimensions differ")
    live=check()
    require(live["access_metadata_sha256"]==prepared["access_metadata_sha256"]
            and live["boot"]==prepared["boot"], "live PMIC metadata changed")
    consumed={
        "experiment":"E004fy", "status":"CONSUMED_BEFORE_REGISTER_IO",
        "attempts":1, "golden_boot":prepared["boot"],
        "prepared_sha256":sha256(P.read_bytes()).hexdigest(),
        "read_only_addresses":prepared["addresses"],"writes_requested":False,
        "emitter_activation_requested":False,
    }
    with C.open("x") as f:
        json.dump(consumed,f,indent=2)
        f.write("\n"); f.flush(); os.fsync(f.fileno())
    result={
        "experiment":"E004fy","identity_consumed":True,
        "boot":prepared["boot"],"spmi":"0-01",
        "register_addresses":prepared["addresses"],
        "read_only_register_bytes_requested":54,
        "register_writes_requested":False,"emitter_activation_requested":False,
        "independent_physical_shutoff_verified":False,
        "safe_current_or_irradiance_verified":False,
        "emitter_activation_authorized":False,
    }
    try:
        process=subprocess.run(["sudo","-n",sys.executable,"-c",PRIVILEGED],
                               capture_output=True,timeout=18,check=False)
        require(process.returncode==0 and len(process.stdout)==54,
                "read failed or unexpected size")
        vals={}
        for i,address in enumerate(ADDRS):
            line=process.stdout[i*9:(i+1)*9].decode("ascii")
            match=re.fullmatch(rf"{address:04x}: ([0-9a-fA-F]{{2}}|XX)\n",line)
            require(match is not None, "unexpected address or unreadable layout")
            vals[f"0x{address:04x}"]=match.group(1).lower()
        result["status"]="PASS_SINGLE_PASSIVE_IDLE_FLASH_ENABLE_TRIGGER_READ"
        result["idle_register_bytes"]=vals
        result["conditional_module_enable_bit7"]= bool(int(vals["0xee46"],16)&0x80) if vals["0xee46"]!="xx" else None
        result["conditional_channel_enable_mask_low4"]=int(vals["0xee4e"],16)&0x0f if vals["0xee4e"]!="xx" else None
        result["interpretation"]="Idle configuration only; physical LED state, Windows stream behaviour and fault shutoff not established."
    except Exception as err:
        result["status"]="INCONCLUSIVE_ONE_SHOT_CONSUMED"
        result["read_failure_type"]=type(err).__name__
        result["same_boot_retry_allowed"]=False
    R.write_text(json.dumps(result,indent=2)+"\n")
    print("E004FY="+result["status"])
    print("ID_CONSUMED=YES WRITES=ZERO EMITTER=OFF")
    print("IDLE_BYTES="+json.dumps(result.get("idle_register_bytes",{})))

if __name__=="__main__":
    main()
