#!/usr/bin/env python3
"""Static preflight; this does not arm KDNET or access the Windows camera."""
from pathlib import Path
import subprocess
import tempfile
import re
import hashlib

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OLDER=ROOT/"experiments/E004-front-ir-vd55g0/e004fp-windows-pmic-register-trace-corrected"
DIS=ROOT/"experiments/E004-front-ir-vd55g0/e004fi-native-ir-pmic-routing/build/qcpmic.dis"
SRC=DIS.read_text(errors="replace")
for s in ("140023aa8:","orr\tw27, w24, w8, lsl #16",
          "140023af8:","140023bec:","140023bcc:","strb\tw8, [x21]",
          "140023b0c:","uxtb\tw24, w0"):
    assert s in SRC, s
prior=(OLDER/"capture.ps1").read_text()
cap=(HERE/"capture.ps1").read_text()
assert cap==prior.replace("E004FP","E004GA")
for token in ("frames -lt 12", "AddSeconds(5)", "TryAcquireLatestFrame"):
    assert token in cap
for forbidden in ("TrySet","SetValue","FlashControl","ExposureControl.Set",
                  "FocusControl","ZoomControl","SoftwareBitmap.CopyToBuffer"):
    assert forbidden not in cap
with tempfile.TemporaryDirectory(prefix="sp11-e004ga-kd-static-") as tmp:
    proc=subprocess.run(["python3",str(HERE/"generate_kd.py"),
                         "--pmic-base","fffff80012345000","--output",tmp],
                        capture_output=True,text=True,check=False,timeout=12)
    assert proc.returncode==0, proc.stderr
    arm=(Path(tmp)/"arm.kd").read_text()
    dry=(Path(tmp)/"validate.kd").read_text()
    for value in ("fffff80012368af8","fffff80012368bec",
                  "0xee3e","0xee41","0xee46","0xee4a","0xee4e","0xee67",
                  "(@w27 & 0xffff)","@sp+0x18","@sp+0x10",
                  "E004GA_ARMED_STAY_BROKEN","bd 0","bd 1"):
        assert value in arm,value
    assert "E004GA_ARMED_STAY_BROKEN" in arm and not re.search(r"(?m)^g\s*$",arm)
    assert not any(x in arm+dry for x in ("&&","||","E004FP"))
    for target in ("ee3e","ee41","ee46","ee4a","ee4d","ee4e","ee67"):
        assert "E004GA_DRY_TARGET reg=%x" in dry and "0x"+target in dry
    for skip in ("ee42","ee45","ee47","ee4f","ee68"):
        assert "0x"+skip in dry
    assert "E004GA_DRY_END_STAY_BROKEN" in dry
    print("E004GA_STATIC=PASS OBSERVER=MASKED_RMW READ_ONLY TARGETS=11")
    print("ARM_REMAINS_BROKEN=YES CAPTURE_BOUNDED=12FRAMES_5SEC MEDIA_SAVED=NO")
    print("GENERATOR_SHA256="+hashlib.sha256((HERE/"generate_kd.py").read_bytes()).hexdigest())
    print("CAPTURE_SHA256="+hashlib.sha256((HERE/"capture.ps1").read_bytes()).hexdigest())
