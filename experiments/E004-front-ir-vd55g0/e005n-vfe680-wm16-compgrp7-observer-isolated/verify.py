#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re, subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
SRC=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss")
FIRST=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e005n-vfe680-wm16-compgrp7-observer-build")
B=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e005n-vfe680-wm16-compgrp7-observer-build-fix1")

def req(x,msg):
    if not x: raise AssertionError("E005N_FAIL_CLOSED "+msg)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def strip_comments(s):
    s=re.sub(r"/\*.*?\*/","",s,flags=re.S)
    s=re.sub(r"//.*","",s)
    return s

def main():
    accepted={
      "camss-vfe-680.c":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208",
      "camss-vfe.h":"440b03e1d2701c311cddc6beeae70bccfea5f472f75790a1879167d66395e857",
      "camss-vfe.c":"98474729d5036a4e1770e3ab7d275ccaaba143b22202468e4ad8b93c0cbec2cb",
    }
    for n,w in accepted.items(): req(sha(SRC/n)==w,"accepted source changed "+n)

    obs=HERE/"camss-vfe-e005n-wm16-observer.inc"
    req(sha(obs)=="0201f008b741967fcf2840062cb0607279a8a22d8a0cb8f9c26d7d22bf3a7e27","observer hash")
    code=strip_comments(obs.read_text())
    for needle in ("VFE680_E005N_WM16              16",
                   "VFE680_E005N_COMP_GRP7_DONE    BIT(7)",
                   "VFE_BUS_ADDR_STATUS0(vfe, VFE680_E005N_WM16)",
                   "VFE_BUS_IRQn_CLEAR(vfe, 0)",
                   "VFE_BUS_IRQ_GLOBAL_CLEAR(vfe)"):
        req(needle in code,"observer contract "+needle)
    req(code.count("vfe680_e005n_arm_wm16_compgrp7(")==1,"arm helper must remain definition-only")
    for forbidden in ("vfe_buf_done(", "vb2_buffer_done(", "dma_unmap", "dma_free", "camss_buf_done("):
        req(forbidden not in code,"forbidden retirement API "+forbidden)

    req(FIRST.is_dir(),"first consumed build missing")
    req(not (FIRST/"qcom-camss.ko").exists(),"first failed build unexpectedly has module")
    req(sha(B/"qcom-camss.ko")=="63d238b9eee09558487b94619a350f340e55f0e4333fadd1dfdb2b65ad1b5077","fix1 module hash")
    req((B/"qcom-camss.ko").stat().st_size==13738248,"fix1 module size")
    log=(B/"E005N-CAMSS-BUILD.log").read_text(errors="replace")
    req(not re.search(r"(warning:|error:)",log,re.I),"W=1 warning/error")
    verm=subprocess.check_output(["modinfo","-F","vermagic",str(B/"qcom-camss.ko")],text=True).strip()
    req(verm=="7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64","vermagic")

    iv=(B/"camss-vfe-680.c").read_text()
    req("vfe680_e005n_observe_wm16(vfe, bus0);" in iv,"observer wired into isolated ISR")
    req("vfe680_e005n_ack_snapshot(vfe, top0, top1, bus0, bus1);" in iv,"isolated ACK wired")
    req(iv.count("vfe680_e005n_arm_wm16_compgrp7(")==0,"isolated translation unit must have no direct arm call")
    isr=re.search(r"static irqreturn_t vfe_isr\(int irq, void \*dev\)\s*\{(.*?)\n\}",iv,re.S)
    req(isr is not None,"isolated ISR")
    body=isr.group(1)
    req(body.find("vfe680_e005n_observe_wm16") < body.find("vfe680_e005n_ack_snapshot"),"observe before ACK")

    saved=json.loads((HERE/"RESULT.json").read_text())
    for k in ("module_installed","module_loaded","live_camera_session",
              "live_rear_compgrp7_wm16_completion_proven",
              "fifo8_generation_matched_to_wm16_consumed_addr_proven",
              "dma_iommu_safe_retirement_proven",
              "native_rear_hardware_isp_runtime_authorized"):
        req(saved[k] is False,"must stay false "+k)

    print("PASS_E005N_ISOLATED_VFE680_WM16_COMPGRP7_OBSERVER_COMPILED_ZERO_WARNINGS_NO_LOAD_REAR_DENIED")

if __name__=="__main__": main()
