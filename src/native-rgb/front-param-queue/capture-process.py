#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Bounded child capture with private file logs and process-group cleanup."""
from pathlib import Path
import json,os,signal,subprocess,time
def capture(args, directory, environment, timeout=40, trace=True):
    directory=Path(directory)
    command=(["strace","--kill-on-exit","-ff","-e","trace=process,signal","-o",str(directory/"PRIVATE-PROCESS-TRACE")]+args) if trace else args
    timed_out=False
    with (directory/"PRIVATE-CAM-STDOUT.txt").open("w") as out,(directory/"PRIVATE-CAM-STDERR.txt").open("w") as err:
        child=subprocess.Popen(command,stdout=out,stderr=err,env=environment,start_new_session=True)
        try:
            child.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out=True
            states=[]
            for p in Path("/proc").glob("[0-9]*"):
                try:
                    if os.getpgid(int(p.name))==child.pid:
                        states.append({"pid":int(p.name),"name":(p/"comm").read_text().strip(),
                                       "wchan":(p/"wchan").read_text().strip(),
                                       "state":next(line for line in (p/"status").read_text().splitlines() if line.startswith("State:"))})
                except (FileNotFoundError,ProcessLookupError):pass
            (directory/"PRIVATE-TIMEOUT-PROCESSES.json").write_text(json.dumps(states,indent=2)+"\n")
        finally:
            try:os.killpg(child.pid,signal.SIGTERM)
            except ProcessLookupError:pass
            try:child.wait(timeout=2)
            except subprocess.TimeoutExpired:
                try:os.killpg(child.pid,signal.SIGKILL)
                except ProcessLookupError:pass
                child.wait(timeout=5)
            # A reaped leader can still leave an IPA descendant with log FDs.
            try:os.killpg(child.pid,signal.SIGKILL)
            except ProcessLookupError:pass
    info={"returncode":child.returncode,"timed_out":timed_out,"signal_trace_enabled":trace,
          "log_files_direct_no_communicate_pipe":True}
    (directory/"PROCESS-RESULT.json").write_text(json.dumps(info,indent=2)+"\n")
    return subprocess.CompletedProcess(command,child.returncode,
        (directory/"PRIVATE-CAM-STDOUT.txt").read_text(),(directory/"PRIVATE-CAM-STDERR.txt").read_text()),info
