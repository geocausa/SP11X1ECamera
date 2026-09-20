#!/usr/bin/env python3
"""E004ix: disposable GRUB environment writer/reader concurrency test.

Never names /boot/grub/grubenv in a grub-editenv write argument.
Never installs a systemd unit, touches GRUB/NVRAM or boots any machine.
"""
from pathlib import Path
import argparse
import json
import subprocess
import tempfile

GRUB="/usr/bin/grub-editenv"
GOLDEN="sp11-audio-fullio-v19c"

def proc(*argv,timeout=10):
    return subprocess.run(argv,capture_output=True,text=True,timeout=timeout)

def fixture(path:Path):
    create=proc(GRUB,str(path),"create")
    if create.returncode: raise RuntimeError("disposable create failed: "+create.stderr)
    write=proc(GRUB,str(path),"set",f"saved_entry={GOLDEN}",
               "next_entry=","recordfail=1","initrdfail=1",
               "prev_entry=one-shot-candidate")
    if write.returncode:raise RuntimeError("disposable setup failed: "+write.stderr)

def read_state(path:Path):
    p=proc(GRUB,str(path),"list")
    parsed={}
    if p.returncode==0:
        for line in p.stdout.splitlines():
            if "=" not in line: raise RuntimeError("malformed line in disposable test")
            key,value=line.split("=",1)
            parsed[key]=value
    return p.returncode,p.stderr.strip()[:100],parsed

def concurrent_trial(path:Path):
    fixture(path)
    # Mimics grub2-common's one unset plus grub-initrd-fallback's two,
    # with an overlapping list and NO locks, on a PRIVATE temp file.
    writer1=subprocess.Popen([GRUB,str(path),"unset","recordfail"],
                             stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
    writer2=subprocess.Popen([GRUB,str(path),"unset","initrdfail"],
                             stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
    reader=proc(GRUB,str(path),"list")
    a=writer1.communicate(timeout=10)[1] or ''
    b=writer2.communicate(timeout=10)[1] or ''
    third=proc(GRUB,str(path),"unset","prev_entry")
    after2=read_state(path)
    return {"writers_failed":int(writer1.returncode!=0)+int(writer2.returncode!=0)+int(third.returncode!=0),
            "overlapping_read_failed":int(reader.returncode!=0),
            "final_read_failed":int(after2[0]!=0),
            "final_missing_golden":int(after2[2].get("saved_entry")!=GOLDEN),
            "final_missing_empty_next":int(after2[2].get("next_entry")!=""),
            "writer_1_error":a[:100],"writer_2_error":b[:100]}

def serial_trial(path:Path):
    fixture(path)
    # Strict sequence, identical original three GRUB commands.
    errors=0
    for key in ("initrdfail","prev_entry","recordfail"):
        r=proc(GRUB,str(path),"unset",key)
        errors+=int(r.returncode!=0)
    rc,stderr,state=read_state(path)
    return {"writer_failed":errors,"read_failed":int(rc!=0),
            "golden_preserved":state.get("saved_entry")==GOLDEN,
            "consumed_one_shot_preserved":state.get("next_entry")==""}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--trials",type=int,default=120)
    a=ap.parse_args()
    if not 1<=a.trials<=300:raise ValueError("trials must be 1..300")
    totals={"concurrent_writer_failures":0,"concurrent_reader_failures":0,
            "concurrent_final_reader_failures":0,"concurrent_missing_saved":0,
            "concurrent_missing_next":0,"serial_writer_failures":0,
            "serial_reader_failures":0,"serial_incorrect_state":0}
    with tempfile.TemporaryDirectory(prefix="sp11-e004ix-grubenv-fixture-",dir="/tmp") as d:
        root=Path(d)
        environment=root/"DISPOSABLE-NOT-SYSTEM.grubenv"
        for _ in range(a.trials):
            concurrent=concurrent_trial(environment)
            totals["concurrent_writer_failures"]+=concurrent["writers_failed"]
            totals["concurrent_reader_failures"]+=concurrent["overlapping_read_failed"]
            totals["concurrent_final_reader_failures"]+=concurrent["final_read_failed"]
            totals["concurrent_missing_saved"]+=concurrent["final_missing_golden"]
            totals["concurrent_missing_next"]+=concurrent["final_missing_empty_next"]
            serial=serial_trial(environment)
            totals["serial_writer_failures"]+=serial["writer_failed"]
            totals["serial_reader_failures"]+=serial["read_failed"]
            totals["serial_incorrect_state"]+=int(
                not serial["golden_preserved"] or not serial["consumed_one_shot_preserved"])
    print(json.dumps({"experiment":"E004ix","scope":"disposable GRUB file concurrency test only",
        "trials":a.trials,"totals":totals,
        "actual_golden_grubenv_touched":False,"system_services_modified":False,
        "reproduces_exact_original_machine_root_cause":False,
        "camera_access":False},sort_keys=True,indent=2))
    if totals["serial_writer_failures"] or totals["serial_reader_failures"] or totals["serial_incorrect_state"]:
        raise SystemExit("FAIL: serialized fixture operation unexpected")
if __name__=="__main__":main()
