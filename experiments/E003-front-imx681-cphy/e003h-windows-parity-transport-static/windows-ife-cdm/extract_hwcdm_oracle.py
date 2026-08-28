#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path

RAW_SHA256 = "458b05c41718c7d01d0efb2921d1f6e2e4323e94e24447e379499544ca21cc1a"
MODULE_BASE = 0xFFFFF80268B90000
RT0_VA = 0xFFFF988134A3B000
RT1_VA = 0xFFFF988134A3C000
RT0_PA = 0x0AC25000
RT1_PA = 0x0AC26000
DD_RE = re.compile(r"^([0-9a-fA-F]{8})`([0-9a-fA-F]{8})\s+((?:[0-9a-fA-F]{8}(?:\s+|$))+)")

def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def section(lines: list[str], begin: str, end: str) -> list[str]:
    try:
        a=lines.index(begin); b=lines.index(end,a+1)
    except ValueError as e:
        raise SystemExit(f"missing marker: {e}")
    return lines[a+1:b]

def parse_dd(lines: list[str], base: int) -> dict[int,int]:
    out={}
    for line in lines:
        m=DD_RE.match(line.strip())
        if not m: continue
        addr=int(m.group(1)+m.group(2),16)
        vals=[int(x,16) for x in m.group(3).split()]
        for i,v in enumerate(vals):
            out[addr-base+4*i]=v
    return out

def need(cond: bool, msg: str) -> None:
    if not cond: raise SystemExit(msg)

def main() -> None:
    ap=argparse.ArgumentParser()
    ap.add_argument("raw",type=Path)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args()
    raw=a.raw.read_bytes(); got=sha256(raw)
    need(got==RAW_SHA256, f"raw SHA mismatch: {got}")
    lines=raw.decode("utf-16").splitlines()

    # Exact boot/module/resource mapping proof.
    need(any("fffff802`68b90000 fffff802`68c08000   qccamisp8380" in x for x in lines),"module base mismatch")
    need(any("RTCDM0_VA=ffff988134a3b000 RTCDM1_VA=ffff988134a3c000" in x for x in lines),"RTCDM VA mismatch")
    need(any("VA ffff988134a3b000" in x for x in lines),"RT0 PTE header missing")
    need(any("VA ffff988134a3c000" in x for x in lines),"RT1 PTE header missing")
    need(any(re.search(r"pfn ac25\s+CW-GADKN-V",x) for x in lines),"RT0 PFN mismatch")
    need(any(re.search(r"pfn ac26\s+CW-GADKN-V",x) for x in lines),"RT1 PFN mismatch")

    # Native acquire path must prove HW CDM, not merely contain the breakpoint text.
    need(any(x.strip()=="===E003H_ACQUIRE_SWCDM_FIELD===" for x in lines),"SWCDM acquire breakpoint did not hit")
    need(any("SWCDM_BYTE=00" in x for x in lines),"native SWCDM byte is not zero")
    need(any(x.strip()=="===E003H_HW_CDM_BRANCH===" for x in lines),"hardware-CDM branch did not hit")
    need(not any(x.strip()=="===E003H_SW_CDM_BRANCH===" for x in lines),"software-CDM branch unexpectedly hit")

    rt0=parse_dd(section(lines,"===E003H_RTCDM0_LIVE===","===E003H_RTCDM1_LIVE==="),RT0_VA)
    rt1=parse_dd(section(lines,"===E003H_RTCDM1_LIVE===","===E003H_RTCDM_LIVE_DONE==="),RT1_VA)
    ext=parse_dd(section(lines,"===E003H_RTCDM1_EXTENDED_BEGIN===","===E003H_RTCDM1_EXTENDED_DONE==="),RT1_VA)
    post0=parse_dd(section(lines,"===E003H_RTCDM0_POST===","===E003H_RTCDM1_POST==="),RT0_VA)
    post1=parse_dd(section(lines,"===E003H_RTCDM1_POST===","===E003H_RTCDM_POST_DONE==="),RT1_VA)
    need(len(rt0)==0x100//4 and len(rt1)==0x100//4,"live 0x100-byte window incomplete")
    need(len(ext)==0x300//4,"RT1 extended window incomplete")
    need(len(post0)==0x100//4 and len(post1)==0x100//4,"post window incomplete")

    for name,r in (("rt0",rt0),("rt1",rt1)):
        need(r[0x0]==0x20010000,f"{name}: HW version mismatch")
        need(r[0x1c]==1,f"{name}: core_en mismatch")
        need(r[0x20]==0x07ff000f,f"{name}: fe_cfg mismatch")
        need(r[0x5c]==0x01000000,f"{name}: FIFO0 cfg mismatch")
    need(rt0[0x50]==0 and rt0[0x54]==0 and rt0[0xe8]==0 and rt0[0xec]==0,"RT0 unexpectedly owns a BL")
    need(rt1[0x50]==0x17b82714 and rt1[0x54]==0x00100013,"RT1 FIFO0 live BL mismatch")
    need(rt1[0xe8]==0x17b82714 and rt1[0xec]==0x00100013,"RT1 current BL mismatch")
    need(rt1[0xf0]==0x00057000,"RT1 current_used_ahb_base mismatch")
    need(rt1[0xf4]==0x0062b904,"RT1 debug_status mismatch")
    for off in (0x150,0x154,0x250,0x254,0x350,0x354):
        need(ext[off]==0,f"RT1 secondary FIFO base/len nonzero at +0x{off:x}")
    need(all(v==0x80000000 for v in post0.values()),"RT0 post power sentinel mismatch")
    need(all(v==0x80000000 for v in post1.values()),"RT1 post power sentinel mismatch")

    def regset(r: dict[int,int]) -> dict[str,str]:
        fields={
            "hw_version":0x0,"rst_cmd":0x10,"cgc_cfg":0x14,"core_cfg":0x18,"core_en":0x1c,
            "fe_cfg":0x20,"irq_context_status":0x2c,"irq0_mask":0x30,"irq0_clear":0x34,
            "fifo0_base":0x50,"fifo0_len":0x54,"fifo0_store":0x58,"fifo0_cfg":0x5c,
            "usr_data":0x80,"current_bl_base":0xe8,"current_bl_len":0xec,
            "current_used_ahb_base":0xf0,"debug_status":0xf4,
        }
        return {k:f"0x{r[o]:08x}" for k,o in fields.items()}

    summary={
        "status":"PASS",
        "policy":"Same-machine Windows is behavioral oracle. Qualcomm camera-driver commit 0f16924f... is used only to name CDM v2.1 register offsets.",
        "raw":{"bytes":len(raw),"sha256":got,"encoding":"UTF-16LE KD text log"},
        "windows_isp":{"binary_sha256":"64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c","module_base":f"0x{MODULE_BASE:016x}"},
        "native_acquire":{"sw_cdm_byte":"0x00","hardware_cdm_branch_hit":True,"software_cdm_branch_hit":False},
        "rt_cdm_resources":{
            "rt_cdm_0":{"mapped_va":f"0x{RT0_VA:016x}","physical_base":f"0x{RT0_PA:08x}"},
            "rt_cdm_1":{"mapped_va":f"0x{RT1_VA:016x}","physical_base":f"0x{RT1_PA:08x}"},
            "mapping_basis":"Windows RT_CDM_0/RT_CDM_1 resource mappings plus KD PTE PFNs ac25/ac26",
        },
        "live":{
            "rt_cdm_0":regset(rt0),
            "rt_cdm_1":regset(rt1),
            "active_front_engine":"RT_CDM_1",
            "active_front_engine_basis":"RT_CDM1 FIFO0 base/len equals current BL base/len while RT_CDM0 FIFO/current BL fields are zero",
            "rt_cdm_1_secondary_fifo_base_len_zero":True,
        },
        "post":{"rt_cdm_0_first_0x100":"all 0x80000000","rt_cdm_1_first_0x100":"all 0x80000000"},
        "qualcomm_layout_reference":{"commit":"0f16924ff6a7f9bb56a7e958016da2ed8a174f2f","compatible":"qcom,cam-rt-cdm2_1","hw_version_expected":"0x20010000","fifo0_offsets":{"base":"0x50","len":"0x54","store":"0x58","cfg":"0x5c"},"current_offsets":{"base":"0xe8","len":"0xec","used_ahb_base":"0xf0","debug_status":"0xf4"}},
        "conclusion":"The exact Windows front path requests SW_CDM=0 and executes on hardware RT_CDM1 v2.1 at physical 0x0ac26000. Direct CPU replay of VFE680 DMI selectors is not the parity architecture; a Linux parity implementation must provide equivalent RT-CDM execution or prove an exactly equivalent mechanism.",
    }
    a.out.write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))

if __name__=="__main__": main()
