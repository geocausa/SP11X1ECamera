#!/usr/bin/env python3
"""Source-locked *conditional* AVStream -> ISP callback -> nested interface route.

Read-only on the exact private same-SP11 original AVStream and ISP OEM binaries.
No claim a particular ISP interface ran for the live rear VideoRecord profile.
"""
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump")
AVS=ROOT/"surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/surfacecamavs8380.sys"
ISP=ROOT/"qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys"
AVS_SHA="b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed"
ISP_SHA="64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
BASE=0x140000000
def instructions(path,lo,hi):
    output=subprocess.check_output(["llvm-objdump","-d",
        f"--start-address={BASE+lo:#x}",f"--stop-address={BASE+hi:#x}",
        str(path)],text=True)
    rx=re.compile(r"^([0-9a-f]{9,}):[ \t]+[0-9a-f]{8}[ \t]+([a-z.]+)[ \t]*([^\r\n]*)$",re.M)
    return {int(m.group(1),16)-BASE:(m.group(2),m.group(3).split("//",1)[0].strip())
            for m in rx.finditer(output)}
def at(rows,rva,mn,params):
    assert rows.get(rva)==(mn,params),(
        f"E004OC_ISP_CALLBACK_FAIL_CLOSED RVA{rva:x} {rows.get(rva)} expected {mn} {params}")
def verify():
    assert hashlib.sha256(AVS.read_bytes()).hexdigest()==AVS_SHA
    assert hashlib.sha256(ISP.read_bytes()).hexdigest()==ISP_SHA
    av=instructions(AVS,0x20dc8,0x20e34)
    isp_reg=instructions(ISP,0x566c,0x5694)
    isp=instructions(ISP,0x4e50,0x4f4c)
    tail=instructions(ISP,0x50c4,0x5218)
    a={
       0x20dd8:("ldrb","w10, [x9, #0x30]"),
       0x20ddc:("cbnz","w10, 0x140020dfc <.text+0x1fdfc>"),
       0x20dfc:("ldr","x10, [x9, #0x40]"),
       0x20e14:("mov","x3, x2"),
       0x20e18:("mov","w2, w1"),
       0x20e1c:("ldr","x1, [x9, #0x38]"),
       0x20e30:("blr","x15"),
    }
    b={
       0x5684:("adrp","x9, 0x140004000 <.text+0x3000>"),
       0x5688:("add","x9, x9, #0xe30"),
       0x568c:("stp","x22, x9, [x8, #0x10]"),
    }
    c={
       0x4e54:("mov","x24, x1"),
       0x4e58:("mov","w22, w2"),
       0x4ed0:("sub","w8, w22, #0x19"),
       0x4ed4:("cmp","w8, #0x8"),
       0x4edc:("b.hi","0x1400050c4 <.text+0x40c4>"),
    }
    e={
       0x50c4:("cmp","w22, #0x801"),
       0x50cc:("cmp","w22, #0x803"),
       0x50d4:("cmp","w22, #0x80d"),
       0x50dc:("cmp","w22, #0x80e"),
       0x50e0:("b.ne","0x1400051e0 <.text+0x41e0>"),
       0x51e0:("ldr","x0, [x24, #0x10]"),
       0x51f4:("ldr","x8, [x0]"),
       0x51fc:("mov","w1, w22"),
       0x5210:("blr","x15"),
    }
    for rows,group in ((av,a),(isp_reg,b),(isp,c),(tail,e)):
        for rva,(mn,params) in group.items():at(rows,rva,mn,params)
    # For the cited engine selectors, neither the 0x19..0x21 ISP-special
    # dispatch nor the separately tested 0x801/0x803/0x80d/0x80e branches
    # claim them. Their static conditional route goes via the x24+0x10
    # nested callback, NOT a direct VFE register write in this wrapper.
    for selector in (0x804,0x805,0x809):
        assert selector-0x19>8
        assert selector not in (0x801,0x803,0x80d,0x80e)
    recorded=json.loads((HERE/"RESULT.json").read_text())
    assert recorded["AVStream_real_session_rear_selected_device_interface_identified"] is False
    assert recorded["OEM_interface_selector_values_decoded_into_native_hardware_commands"] is False
    assert recorded["Windows_live_rear_BF_event_observed"] is False
    print("PASS_E004OC_ISP_CONDITIONAL_ENGINE_SELECTOR_DELEGATION_"
          f"{len(a)+len(b)+len(c)+len(e)}_SOURCE_LOCKED_ARM64_ANCHORS_"
          "SELECTORS_804_805_809_FORWARDED_TO_NESTED_INTERFACE_"
          "LIVE_BACKEND_UNPROVEN_NATIVE_LINUX_HARDWARE_SEMANTICS_UNPROVEN")
if __name__=="__main__":verify()
