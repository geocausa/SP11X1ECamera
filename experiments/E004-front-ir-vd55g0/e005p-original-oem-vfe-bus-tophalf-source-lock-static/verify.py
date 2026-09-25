#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OEM = ROOT / "experiments/E001-windows-oracle-map/oracle-local/qccamisp8380.sys"
QHDR = Path("/home/geoca/.cache/qualcomm-camera-driver/camera/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe17x/cam_vfe680.h")
OEM_SHA = "64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"

def req(ok, msg):
    if not ok:
        raise AssertionError("E005P_FAIL_CLOSED " + msg)

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    req(OEM.is_file(), "same-SP11 OEM binary missing")
    req(sha(OEM) == OEM_SHA, "OEM SHA")
    req(QHDR.is_file(), "pinned Qualcomm VFE680 header missing")
    dis = subprocess.check_output(["llvm-objdump","-d","--no-show-raw-insn",str(OEM)], text=True, errors="replace")

    anchors = (
        r"14002247c:.*mov\s+x9, #0xc00",
        r"140022480:.*mov\s+x8, #0x1200",
        r"14002248c:.*str\s+x8, \[x20, #0x150\]",
        r"14001dc54:.*ldr\s+x8, \[x19, #0x150\].*?14001dc58:.*ldr\s+w8, \[x8, #0x28\]",
        r"14001dc60:.*ldr\s+x8, \[x19, #0x150\].*?14001dc64:.*ldr\s+w8, \[x8, #0x2c\]",
        r"14001dcec:.*ldr\s+x9, \[x19, #0x150\].*?14001dcf0:.*str\s+w8, \[x9, #0x3c\]",
        r"14001dcf8:.*ldr\s+x9, \[x19, #0x150\].*?14001dcfc:.*str\s+w8, \[x9, #0x40\]",
        r"14001dd00:.*ldr\s+x8, \[x19, #0x150\].*?14001dd04:.*str\s+w10, \[x8, #0x30\]",
        r"14001eff0:.*ldp\s+w8, w2, \[x23, #0x4\]",
        r"14001f048:.*ubfx\s+w15, w2, #7, #1",
        r"14001f188:.*cbz\s+w15,.*?14001f190:.*mov\s+w15, #0xf",
    )
    for pat in anchors:
        req(re.search(pat, dis, re.S) is not None, "OEM instruction anchor: "+pat)

    lines=dis.splitlines()
    ldr_re=re.compile(r"^(?P<addr>[0-9a-f]+):.*\bldr\s+x(?P<dst>\d+), \[x(?P<src>\d+), #0x150\]")
    acc_re=re.compile(r"^(?P<addr>[0-9a-f]+):.*\b(?P<op>ldr|str)\s+w\d+, \[x(?P<base>\d+), #0x(?P<off>[0-9a-f]+)\]")
    accesses=[]
    for i,line in enumerate(lines):
        m=ldr_re.search(line)
        if not m:
            continue
        reg=m.group("dst")
        for j in range(i+1,min(i+18,len(lines))):
            if re.search(r"\b(?:ldr|mov|add|sub|adrp|adr)\s+x"+reg+r"\b", lines[j]) and f"[x{reg}," not in lines[j]:
                break
            a=acc_re.search(lines[j])
            if a and a.group("base")==reg:
                accesses.append((a.group("op"),int(a.group("off"),16)))
    req(sum(1 for op,off in accesses if op=="str" and off==0x20)==0, "bounded scan canonical clear0 stores")
    req(sum(1 for op,off in accesses if op=="str" and off==0x24)==0, "bounded scan canonical clear1 stores")
    req(sum(1 for op,off in accesses if op=="str" and off==0x3c)>=1, "OEM +0x3c writeback")
    req(sum(1 for op,off in accesses if op=="str" and off==0x40)>=1, "OEM +0x40 writeback")

    h=QHDR.read_text()
    for needle in (
        ".clear_reg_offset  = 0x00000C20",
        ".clear_reg_offset  = 0x00000C24",
        ".status_reg_offset = 0x00000C28",
        ".status_reg_offset = 0x00000C2C",
        ".global_irq_cmd_offset    = 0x00000C30",
    ):
        req(needle in h, "reference VFE680 IRQ map: "+needle)
    req(re.search(r"/\* BUS Client 16 STATS BAF \*/.*?\.cfg\s*=\s*0x00001E00.*?\.addr_status_0\s*=\s*0x00001E70.*?\.comp_group\s*=\s*CAM_VFE_BUS_VER3_COMP_GRP_7", h, re.S) is not None, "reference WM16 STATS_BAF group7")
    req(re.search(r"\.if_frameheader_cfg\s*=\s*\{\s*0x00000C34,\s*0x00000C38,\s*0x00000C3C,\s*0x00000C40,\s*0x00000C44", h, re.S) is not None, "reference c3c/c40 frame-header semantics")

    o=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e005o-windows-live-bf-fifo8-matcher-vs-vfe-bus7/RESULT.json").read_text())
    req(o["exact_live_marker_counts"]["bf_event"]==22, "E005o BF baseline")
    req(o["exact_live_marker_counts"]["fifo8_nonnull"]==22, "E005o FIFO baseline")
    req(o["exact_live_marker_counts"]["matcher_nonnull"]==22, "E005o matcher baseline")
    req(o["native_rear_hardware_isp_runtime_authorized"] is False, "E005o rear denied")

    d=json.loads((HERE/"RESULT.json").read_text())
    req(d["oem_bf_event"]["raw_source"]=="TOP_STATUS1_BIT7", "BF source")
    req(d["oem_bf_event"]["not_directly_sourced_from_bus_status0_bit7"] is True, "BF/BUS distinction")
    req(d["oem_full_ife"]["direct_context150_canonical_clear0_0x20_store_sites_observed"]==0, "saved clear0 scan")
    req(d["oem_full_ife"]["direct_context150_canonical_clear1_0x24_store_sites_observed"]==0, "saved clear1 scan")
    for _,v in d["not_proven"].items():
        req(v is True, "unproven predicates remain explicit")
    req(d["linux_port_policy"]["copy_oem_c3c_c40_writeback_into_linux"] is False, "do not port unresolved OEM writes")
    req(d["linux_port_policy"]["keep_e005n_unloaded_from_this_static_result_alone"] is True, "E005n stays unloaded")
    req(d["linux_port_policy"]["native_rear_hardware_isp_runtime_authorized"] is False, "rear denied")
    print("PASS_E005P_OEM_TOPHALF_RAW_TOP_BUS_SOURCE_LOCK_BF_TOP1BIT7_C3C40_DIVERGENCE_STATIC_ONLY_REAR_DENIED")

if __name__=="__main__":
    main()
