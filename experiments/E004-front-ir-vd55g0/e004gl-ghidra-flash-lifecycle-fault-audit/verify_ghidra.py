#!/usr/bin/env python3
"""Reproduce narrow Ghidra decomp/callgraph assertions on pinned original ARM64 PEs.

All project/log files live in a disposable temporary directory, not Git.
Original Windows images are read-only. No Windows runtime/hardware access.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
from hashlib import sha256
import os
import shutil
import subprocess

HERE=Path(__file__).resolve().parent
ARCH=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
GHIDRA=shutil.which("analyzeHeadless") or "/home/geoca/Desktop/Ghidra/support/analyzeHeadless"
EXPECTED={
    "qccamflash8380.sys":(
        "6bc1d698bc3b6da16974cd6f3ea89dc1ba6a8ea102eebe1a5d41129b4eb9ba2b",
        "E004GL_GHIDRA_FLASH_DECOMP=PASS",
        "E004GL_GHIDRA_TIMER_CALLERS=0x4938,0x5b2c"),
    "qcpmic8380.sys":(
        "756b5c2e4eb8d5a2bdc0dcc0f7f5703eef79dec0c963155c54e42097bc2f790e",
        "E004GL_GHIDRA_PMIC_DECOMP=PASS",
        "timer_callback_indirect_table=VERIFIED"),
}

def require(ok,why):
    if not ok:raise RuntimeError("E004GL_GHIDRA_REPRO_FAIL_CLOSED "+why)

def main():
    require(Path(GHIDRA).is_file(),"Ghidra headless executable unavailable")
    require((HERE/"VerifyFlashLifecycleGhidra.java").is_file(),"targeted Ghidra script missing")
    with TemporaryDirectory(prefix="e004gl-ghidra-private-") as workspace:
        project=Path(workspace)/"projects"
        project.mkdir()
        for index,(name,(pinned,*markers)) in enumerate(EXPECTED.items()):
            locations=list(ARCH.glob("*/"+name))
            require(len(locations)==1,"ambiguous original Windows driver "+name)
            source=locations[0]
            require(sha256(source.read_bytes()).hexdigest()==pinned,
                    "original OEM binary hash mismatch "+name)
            cmd=[GHIDRA,str(project),"SP11_E004GL_"+str(index),"-import",str(source),
                 "-postScript","VerifyFlashLifecycleGhidra.java",
                 "-scriptPath",str(HERE),"-analysisTimeoutPerFile","125",
                 "-max-cpu","2","-deleteProject"]
            run=subprocess.run(cmd,capture_output=True,text=True,timeout=255,
                               env={**os.environ,"JAVA_TOOL_OPTIONS":"-Djava.awt.headless=true"})
            output=run.stdout+"\n"+run.stderr
            require(run.returncode==0,"headless import/decomp failed "+name+
                    "\n"+output[-1300:])
            for marker in markers+["E004GL_GHIDRA_DONE="+name]:
                require(marker in output,"missing verified marker "+name+": "+marker+
                        "\n"+output[-1300:])
            require("E004GL_GHIDRA_FAIL_CLOSED" not in output,
                    "Ghidra reported failed invariant "+name)
            print("E004GL_GHIDRA_ORIGINAL_PE="+name+" VERIFIED=PASS SHA256_PINNED=YES")
    print("E004GL_GHIDRA_FLASH_AND_PMIC_DECOMP_CALLGRAPH=PASS")
    print("ORIGINAL_WINDOWS_DRIVER_BYTES=NOT_COMMITTED HARDWARE_ACCESS=NO")

if __name__=="__main__":main()
