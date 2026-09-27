#!/usr/bin/env python3
from pathlib import Path
import re

D=Path(__file__).resolve().parent
R=D.parents[2]
CSID=D/"camss-csid-e008a-rear-quiesce.inc"
VFE=D/"camss-vfe-e008a-rear-bus-stop.inc"
BASE=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss")
QBUS=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/qcom-camera-kernel-KleeUI/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe_bus/cam_vfe_bus_ver3.c")

def req(x,msg):
    if not x: raise AssertionError(msg)

cs=CSID.read_text()
vf=VFE.read_text()
base_csid=(BASE/"camss-csid-680.c").read_text()
base_csid_h=(BASE/"camss-csid.h").read_text()
base_csid_core=(BASE/"camss-csid.c").read_text()
base_vfe=(BASE/"camss-vfe-680.c").read_text()
base_vfe_h=(BASE/"camss-vfe.h").read_text()
qbus=QBUS.read_text()

# CSID helper must use the exact physically accepted reset completion ingredients.
for token in ("SP11_CSID_TOP_IRQ_MASK_MODE0","CSID_RESET_CFG_MODE_IMMEDIATE",
              "CSID_RESET_CFG_LOCATION_COMPLETE","CSID_RESET_CMD_HW_RESET",
              "SP11_CSID_RESET_TIMEOUT_MS","wait_for_completion_timeout"):
    req(token in base_csid and token in cs,"CSID reset source lock "+token)
req("u32 irq;" in base_csid_h,"CSID irq field")
req("devm_request_irq(dev, csid->irq" in base_csid_core,"CSID real Linux IRQ request")
req(cs.count("synchronize_irq(csid->irq)") == 2,"two CSID IRQ barriers")
for mask in ("CSID_TOP_IRQ_MASK","CSID_BUF_DONE_IRQ_MASK","CSID_IPP_IRQ_MASK",
             "CSID_CSI2_RX_IRQ_MASK","CSID_CSI2_RDIN_IRQ_MASK"):
    req(mask in cs,"CSID mask "+mask)
for stat in ("CSID_TOP_IRQ_STATUS","CSID_CSI2_RX_IRQ_STATUS","CSID_BUF_DONE_IRQ_STATUS",
             "CSID_IPP_IRQ_STATUS","CSID_CSI2_RDIN_IRQ_STATUS"):
    req(stat in cs,"CSID final status "+stat)
req("exact_rear_owner" in cs,"CSID explicit owner gate")
req("return -EIO;" in cs and "return -EBUSY;" in cs,"CSID fail closed")

# Current VFE680 completion ISR is deliberately inert in this accepted tree.
req(re.search(r'static irqreturn_t vfe_isr\(.*?\)\s*\{\s*return IRQ_HANDLED;\s*\}',base_vfe,re.S) is not None,
    "VFE680 ISR no-op")
req("u32 irq;" in base_vfe_h,"VFE irq field")
req("synchronize_irq(vfe->irq)" in vf,"VFE hygiene IRQ barrier")

# Qualcomm BUS-v3 and local generic VFE both use exact CFG=0 stop semantics.
m=re.search(r'cam_vfe_bus_ver3_stop_wm\s*\(.*?cam_io_w_mb\(0x0,\s*common_data->mem_base\s*\+\s*rsrc_data->hw_regs->cfg\)', qbus, re.S)
req(m is not None,"Qualcomm BUS-v3 WM cfg zero")
req(re.search(r'static void vfe_wm_stop.*?writel\(0,\s*vfe->base \+ VFE_BUS_WRITE_CLIENT_CFG',base_vfe,re.S) is not None,
    "local generic VFE680 WM cfg zero")

m=re.search(r'e008a_rear_wms\[E008A_REAR_WM_COUNT\]\s*=\s*\{(.*?)\};', vf, re.S)
req(m is not None,"rear WM table")
wms=[int(x) for x in re.findall(r'\b\d+\b', m.group(1))]
req(wms==[0,1,2,3,11,12,13,14,16,18],("rear WM list",wms))
req("writel(0, vfe->base +" in vf and "VFE_BUS_WRITE_CLIENT_CFG" in vf,"VFE ten-WM zero writes")
for token in ("VFE_TOP_IRQn_MASK(vfe, 0)","VFE_TOP_IRQn_MASK(vfe, 1)",
              "VFE_BUS_IRQn_MASK(vfe, 0)","VFE_BUS_IRQn_MASK(vfe, 1)"):
    req(token in vf,"VFE IRQ mask "+token)
req("wmb();" in vf,"VFE write ordering")
req("exact_rear_owner" in vf,"VFE explicit owner gate")

# No accidental ownership release, submission, camera activation or registration.
joined=cs+"\n"+vf
for forbidden in ("dma_free","dma_unmap","vb2_buffer_done","camss_rtcdm1_windows_fifo0_commit",
                  "rtcdm1_submit","module_init(","module_platform_driver","v4l2_subdev_call",
                  "media_pipeline","kfree("):
    req(forbidden not in joined,"forbidden E008a action "+forbidden)

print("E008A_VERIFY_PASS")
