#!/usr/bin/env python3
"""E004pi: two SHA-pinned PRIVATE original Windows live rear register snapshots,
scalars ONLY, + offline C11 domain separation. Does NOT arm CAMSS rear ISP.

SP7 original logs remain PRIVATE ON SP7. The companion read-only PowerShell
script verifies their SHA in place. SP11 verifies returned scalar result and
the script bytes; it cannot independently re-open those private SP7 logs.
"""
import copy
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
NATIVE_CSID=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/camss-csid-680.c")
NATIVE_VFE=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/camss-vfe-680.c")
HASHES={
    "read-original-sp7-live-rear-irq-scalars.ps1":"3717a339158777b6c35da009b2f6eaaf25272a9ef15f4f4bee416c5251fd182b",
    "bf-wm16-domain-gate.h":"b28fa2be362d78935642d202ca407f6c790edec155dcbb5eea714bdbe630258d",
    "test-bf-wm16-domain-gate.c":"9c7a49458517923bc71b07c65fa22f7a041e3cd7bd4762c548805208e36a6813",
}
NATIVE_CSID_SHA="9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90"
NATIVE_VFE_SHA="99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208"
ORIGINAL_HASHES=(
    "4dde22d019d006151633916583e88d19bd50f65b059c35c1978defc7929b268c",
    "fea13ae844c949bb722d74fbb2b5c48510178c055550b9d31268a351257986f9",
)
def require(condition,why):
    if not condition:raise AssertionError("E004PI_FAIL_CLOSED "+why)
def status_gate(sample,independent_VFE1_wm16_irq=False,
                wm16_per_frame_bus_quiescent=False,
                dma_iommu_generation_fenced=False,
                shared_VFE1_owner_and_fifo8_same_frame=False):
    # A CSID bit7 snapshot and an enabled WM16/config/addr are NOT
    # independent VFE WM16 completion or a per-frame buffer-lifetime fence.
    return bool(sample["csid1_buf_done_status_bit7_set"]
                and sample["csid1_buf_done_mask_bit7_enabled"]
                and sample["vfe1_wm16_enabled"]
                and independent_VFE1_wm16_irq is True
                and wm16_per_frame_bus_quiescent is True
                and dma_iommu_generation_fenced is True
                and shared_VFE1_owner_and_fifo8_same_frame is True)
def validate(x):
    require(x["schema"]=="sp11-e004pi-original-Windows-rear4k-two-live-CSID1-BUF_DONE_bit7-mask-and-WM16-observation-v1","schema")
    require(x["parent_git_revision"]=="86b0f33afaa241b2633a8fdb1c80ea7ba2f72fe9","parent")
    require(x["source"]=="original_same_SP11_rear_VideoRecord_3840x2160_NV12_windows_KD_dd_slash_p_two_existing_live_captures_SP7_READ_ONLY","same-SP11 original verified user")
    require(x["physical_evidence_class"]=="P_existing_original_Windows_REGISTER_SNAPSHOTS_NOT_EVENT_OR_DMA_FENCE","snapshot vs event")
    true=("same_original_rear4k_two_live_physical_CSID1_BUF_DONE_bit7_set_and_unmasked",
          "original_zero_preparer_CSID_BUF_DONE_bit7_to_conditional_BF_event0x0f_source_proven",
          "accepted_native_CSID_ISR_already_ACKs_BUF_DONE")
    false=("original_private_KD_log_bytes_copied_to_Linux_or_repo",
           "private_DMA_or_physical_addresses_or_optical_pixels_exported",
           "original_live_rear4k_selected_BF_handler_and_event0x0f_observed",
           "original_per_frame_FIFO8_group8_matching_WM16_DMA_completion_observed",
           "accepted_native_VFE680_ISR_implements_WM16_BUS_IRQ_retirement",
           "native_rear_VFE1_WM16_generation_matched_DMA_IOMMU_safe_retirement_proven",
           "rear_hardware_ISP_runtime_authorized",
           "Golden_boot_kernel_camera_hardware_modified")
    for key in true:require(x[key] is True,key+" must be true")
    for key in false:require(x[key] is False,key+" MUST remain false")
    require(len(x["live_snapshots"])==2,"two existing independent original Windows rear4K windows")
    for s,(phase,sha,clear) in zip(x["live_snapshots"],zip(("LIVE1","LIVE2"),ORIGINAL_HASHES,("0x00000080","0x00000201"))):
        require(s["phase"]==phase and s["original_same_SP11_private_Windows_phase_log_sha256"]==sha,"original same-SP11 SP7 per-phase log SHA/identity")
        require(s["evidence_kind"]=="existing_original_Windows_live_rear4k_PHYSICAL_REGISTER_SNAPSHOT_NOT_IRQ_FRAME_TRACE","per-phase evidence is snapshot only")
        for field,value in (
            ("csid1_buf_done_status","0x000002f1"),
            ("csid1_buf_done_mask","0x0001ffff"),
            ("csid1_buf_done_clear_register_readback",clear),
            ("csid1_ipp_status","0x00e11ff8"),
            ("vfe1_top_status0","0x00000000"),
            ("vfe1_top_status1","0x00030003"),
            ("vfe1_bus_status0","0x00000000"),
            ("vfe1_bus_status1","0x00000000"),
            ("vfe1_bus_mask0","0xd0000000"),
            ("vfe1_bus_mask1","0x00000000"),
            ("vfe1_wm16_cfg0","0x00020001"),
        ):require(s[field]==value,phase+" "+field)
        for field in ("csid1_buf_done_status_bit7_set",
                      "csid1_buf_done_mask_bit7_enabled",
                      "vfe1_wm16_enabled",
                      "vfe1_wm16_addr_status0_nonzero"):
            require(s[field] is True,phase+" "+field)
        require(s["original_live_BF_event0x0f_observed"] is False
                and s["independent_same_generation_VFE1_WM16_DMA_IOMMU_retirement_observed"] is False,
                phase+" snapshot not event/DMA retire")
        require(int(s["csid1_buf_done_status"],16)&int(s["csid1_buf_done_mask"],16)&(1<<7),
                phase+" physical CSID bit7 set and unmasked")
        require(int(s["vfe1_wm16_cfg0"],16)&1,phase+" physical WM16 enabled")
        require(not status_gate(s),"per-phase CSID observed cannot retire WM16")
    return True
if __name__=="__main__":
    for name,sha in HASHES.items():
        require(hashlib.sha256((HERE/name).read_bytes()).hexdigest()==sha,"source-script or C11 offline guard SHA changed "+name)
    require(hashlib.sha256(NATIVE_CSID.read_bytes()).hexdigest()==NATIVE_CSID_SHA and
            hashlib.sha256(NATIVE_VFE.read_bytes()).hexdigest()==NATIVE_VFE_SHA,
            "same-SP11 accepted native CAMSS CSID/VFE source changed")
    csid=NATIVE_CSID.read_text();vfe=NATIVE_VFE.read_text()
    require("buf_done_val = readl(csid->base + CSID_BUF_DONE_IRQ_STATUS);" in csid and
            "writel(buf_done_val, csid->base + CSID_BUF_DONE_IRQ_CLEAR);" in csid and
            "writel(CSID_IRQ_CMD_CLEAR, csid->base + CSID_IRQ_CMD);" in csid and
            re.search(r"(?m)^#define\s+CSID_BUF_DONE_IRQ_STATUS\s+0x8c\s*$",csid) and
            re.search(r"(?m)^#define\s+CSID_BUF_DONE_IRQ_CLEAR\s+0x94\s*$",csid) and
            re.search(r"(?s)static irqreturn_t vfe_isr\(int irq, void \*dev\)\s*\{\s*return IRQ_HANDLED;\s*\}",vfe),
            "native CSID already ACKs BUF_DONE, real VFE ISR still not a WM16 retire producer")
    script=(HERE/"read-original-sp7-live-rear-irq-scalars.ps1").read_text()
    require("ReadAllText" in script and "Get-FileHash" in script and
            "ConvertTo-Json" in script and "original_live_BF_event0x0f_observed=$false" in script and
            "independent_same_generation_VFE1_WM16_DMA_IOMMU_retirement_observed=$false" in script and
            not re.search(r"(?i)\b(Remove-Item|Set-Content|Add-Content|Set-ItemProperty|Start-Process|Out-File|Copy-Item)\b",script),
            "SP7 reader must remain read-only and scalar-only")
    original=ROOT/"experiments/E004-front-ir-vd55g0/e004nq-rear-physical-mmio-5phase/RESULT.json"
    o=json.loads(original.read_text())
    require(o["rear_OEM_Windows_VFE1_PIX_3840x2160_confirmed_across_two_live_passes"] is True and
            o["rear_OEM_Windows_CSID1_IPP_enabled_confirmed_across_two_live_passes"] is True and
            o["Linux_rear_native_4k_ISP_optical_frame_proven"] is False,
            "original two verified rear 4K Windows live physical capture window scope")
    ph=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e004ph-original-type1-preparation-queue-status-provenance-static/RESULT.json").read_text())
    require(ph["original_zero_mode_CSID_BUF_DONE_status_bit7_to_type1_BF0x0f_static_proven"] is True and
            ph["same_original_rear4k_live_mode_and_BF_event0x0f_observed"] is False and
            ph["original_CSID_BUF_DONE_bit7_equals_independent_VFE_WM16_DMA_completion_proven"] is False,
            "E004ph original source predicate not physical WM16 DMA proof")
    data=json.loads((HERE/"RESULT.json").read_text())
    validate(data)
    negatives=(
        ("fake_event","original_live_rear4k_selected_BF_handler_and_event0x0f_observed",True),
        ("fake_dma","original_per_frame_FIFO8_group8_matching_WM16_DMA_completion_observed",True),
        ("fake_native_vfe","accepted_native_VFE680_ISR_implements_WM16_BUS_IRQ_retirement",True),
        ("fake_rear","rear_hardware_ISP_runtime_authorized",True),
        ("fake_golden","Golden_boot_kernel_camera_hardware_modified",True),
        ("fake_sp7_copy","original_private_KD_log_bytes_copied_to_Linux_or_repo",True),
        ("fake_windows_source","source","other_source"),
        ("fake_csids","same_original_rear4k_two_live_physical_CSID1_BUF_DONE_bit7_set_and_unmasked",False),
        ("fake_prior_static","original_zero_preparer_CSID_BUF_DONE_bit7_to_conditional_BF_event0x0f_source_proven",False),
        ("fake_csid_ack","accepted_native_CSID_ISR_already_ACKs_BUF_DONE",False),
        ("fake_native_dma","native_rear_VFE1_WM16_generation_matched_DMA_IOMMU_safe_retirement_proven",True),
        ("fake_export","private_DMA_or_physical_addresses_or_optical_pixels_exported",True),
    )
    for name,key,val in negatives:
        changed=copy.deepcopy(data);changed[key]=val
        try:validate(changed)
        except (AssertionError,KeyError,TypeError):continue
        raise AssertionError("E004PI_NEGATIVE_FAILED_OPEN "+name)
    snapshot_negatives=(
        ("status","csid1_buf_done_status","0x00000271"),
        ("mask","csid1_buf_done_mask","0x0001ff7f"),
        ("bit7","csid1_buf_done_status_bit7_set",False),
        ("mask7","csid1_buf_done_mask_bit7_enabled",False),
        ("csid_clear","csid1_buf_done_clear_register_readback","0x00000000"),
        ("vfe_bus_status0","vfe1_bus_status0","0x00000080"),
        ("vfe_bus_status1","vfe1_bus_status1","0x00000080"),
        ("wm16_cfg","vfe1_wm16_cfg0","0x00020000"),
        ("wm16_enabled","vfe1_wm16_enabled",False),
        ("wm16_addr","vfe1_wm16_addr_status0_nonzero",False),
        ("fake_live_event","original_live_BF_event0x0f_observed",True),
        ("fake_dma","independent_same_generation_VFE1_WM16_DMA_IOMMU_retirement_observed",True),
        ("fake_phase","phase","POST"),
        ("fake_source_hash","original_same_SP11_private_Windows_phase_log_sha256","0"*64),
    )
    for phase in range(2):
        for name,key,val in snapshot_negatives:
            changed=copy.deepcopy(data);changed["live_snapshots"][phase][key]=val
            try:validate(changed)
            except (AssertionError,KeyError,TypeError):continue
            raise AssertionError("E004PI_NEGATIVE_FAILED_OPEN phase"+str(phase)+" "+name)
    # Distinct-domain synthetic counterexample: VFE BUS status0/1 snapshots
    # are zero and no WM16 per-generation hardware IRQ/DMA/IOMMU evidence.
    for s in data["live_snapshots"]:
        for binary in range(16):
            safe=status_gate(s, bool(binary&1),bool(binary&2),bool(binary&4),bool(binary&8))
            require(safe==(binary==15),"offline independent-domain predicate")
            require(not status_gate(s),"original live observation alone cannot retire a rear buffer")
    with tempfile.TemporaryDirectory(prefix="e004pi-offline-",dir="/tmp") as tmp:
        source=str(HERE/"test-bf-wm16-domain-gate.c")
        for compiler,flags in (
            ("gcc",["-O2"]),
            ("clang",["-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer"]),
        ):
            binary=str(Path(tmp)/(compiler+"-bf-domain"))
            cmd=[compiler,"-std=c11","-Wall","-Wextra","-Werror","-pedantic",*flags,source,"-o",binary]
            subprocess.run(cmd,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=50)
            done=subprocess.run([binary],check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=50)
            require("PASS_E004PI_C11_DOMAIN_SEPARATION_ASSERTIONS_95_" in done.stdout and
                    "REAR_RUNTIME_DENIED" in done.stdout,compiler+" 95 C11 independent-domain assertions")
    print("PASS_E004PI_2_SHA_PINNED_ORIGINAL_WINDOWS_REAR4K_LIVE_CSID1_BUF_DONE_BIT7_MASKED_WM16_CFG_SNAPSHOTS_40_NEGATIVES_95_C11_ASSERTIONS_GCC_CLANG_ASAN_UBSAN_NO_DMA_FENCE_REAR_RUNTIME_DENIED_GOLDEN_SAFE")
