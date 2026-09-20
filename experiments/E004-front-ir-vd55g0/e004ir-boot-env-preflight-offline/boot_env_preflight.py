#!/usr/bin/env python3
"""E004ir: read-only GRUB one-shot preflight and fail-closed boot audit.

NO camera IO, GRUB mutation, package install, service enabling or reboot.
Never repairs damaged grubenv or treats later Golden readability as proof
that a candidate boot's environment was healthy.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import subprocess
import sys

EXPECTED_SAVED="sp11-audio-fullio-v19c"
EXPECTED_CANDIDATE_MARKER="sp11_camera_e004ir_diagnostic=1"

def audit(grubenv: Path, cmdline: Path, *, require_candidate: bool=False) -> dict:
    # The ONLY GRUB command in this audit is the read-only list command.
    # A malformed block must never be treated as an empty next_entry.
    c=subprocess.run(["/usr/bin/grub-editenv",str(grubenv),"list"],
                     capture_output=True,text=True,timeout=12)
    if c.returncode != 0:
        raise ValueError("GRUB_ENV_UNREADABLE_OR_INVALID: "+c.stderr.strip()[:180])
    entries={}
    for line in c.stdout.splitlines():
        if "=" not in line:
            raise ValueError("GRUB_ENV_MALFORMED_VARIABLE")
        k,v=line.split("=",1)
        if not k or k in entries:
            raise ValueError("GRUB_ENV_DUPLICATE_OR_EMPTY_KEY")
        entries[k]=v
    if entries.get("saved_entry")!=EXPECTED_SAVED:
        raise ValueError("PERSISTENT_GOLDEN_ENTRY_NOT_PROVEN")
    if "next_entry" not in entries or entries["next_entry"] != "":
        raise ValueError("GRUB_ONE_SHOT_NOT_CONSUMED_OR_MISSING")
    words=cmdline.read_text().split()
    if require_candidate and EXPECTED_CANDIDATE_MARKER not in words:
        raise ValueError("CANDIDATE_CMDLINE_MARKER_ABSENT")
    if require_candidate and len(words)!=len(set(words)):
        raise ValueError("DUPLICATED_CMDLINE_WORDS")
    if require_candidate and not any(w.startswith("sp11_entry=7.1.5-sp11-camera-e004ir") for w in words):
        raise ValueError("CANDIDATE_BOOT_ID_MISMATCH")
    return {"status":"PASS_READ_ONLY_GRUB_ENV_PREFLIGHT",
            "saved_entry":EXPECTED_SAVED,"next_entry":"",
            "candidate_marker_checked":require_candidate,
            "camera_access_authorized":False,
            "hardware_modules_loaded":False,
            "grub_environment_modified":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--grubenv",type=Path,required=True)
    ap.add_argument("--cmdline",type=Path,required=True)
    ap.add_argument("--require-candidate",action="store_true")
    args=ap.parse_args()
    try: print(json.dumps(audit(args.grubenv,args.cmdline,
                                require_candidate=args.require_candidate),
                          sort_keys=True))
    except (ValueError,OSError,subprocess.TimeoutExpired) as err:
        print("E004IR_FAIL_CLOSED "+str(err),file=sys.stderr)
        raise SystemExit(1)
if __name__=="__main__":main()
