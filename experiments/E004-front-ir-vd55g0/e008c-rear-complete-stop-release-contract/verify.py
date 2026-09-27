#!/usr/bin/env python3
from pathlib import Path
import json, re

D=Path(__file__).resolve().parent
R=D.parents[2]
S=(D/"camss-e008c-rear-stop-release.inc").read_text()
B=(R/"experiments/E004-front-ir-vd55g0/e008b-rear-owner-retirement-quiesce-integration/camss-e008b-rear-integration.inc").read_text()
Z=(R/"experiments/E004-front-ir-vd55g0/e007z-rear-ten-wm-consumed-iova-retirement/camss-e007z-rear-retirement.inc").read_text()
Y=(R/"experiments/E004-front-ir-vd55g0/e005y-vfe1-shared-owner-csid1-wm16-observer/camss-e005y-vfe1-owner-observer-fix3.inc").read_text()
FRONT=(R/"src/front-imx681/kernel/camss/camss.c").read_text()
OE=json.loads((R/"experiments/E004-front-ir-vd55g0/e004oe-isp-manager-per-core-order-static/RESULT.json").read_text())

def req(x,msg):
    if not x: raise AssertionError(msg)

# Same-SP11 OEM static evidence is only an ordering source, not a live-rear claim.
req(OE["stop_call_stage_order_is_CSID_IFE_CDM_static_code"] is True,
    "OEM stop ordering source")
req(OE["live_rear_Windows_4k_recording_took_this_ISP_route_proven"] is False,
    "must preserve OEM runtime limitation")
req(OE["physical_stop_drained_DMA_WM16_and_BF_irq_proven"] is False,
    "must not promote old OEM evidence")

# E008c must compose E008b then CDM then outer tail.
for token in (
    "e008b_rear_quiesce_and_prove",
    "camss_x1e_pix_rtcdm_stop_close",
    "e008c_rear_rtcdm_stopped",
    "camss_x1e_pix_runner_stream(csiphy_sd, false)",
    "camss_x1e_pix_runner_stream(sensor_sd, false)",
    "e007z_rear_release_ledger",
    "v4l2_pipeline_pm_put",
    "e005y_vfe1_owner_release",
    "return -EOPNOTSUPP",
):
    req(token in S, "missing E008c stage "+token)

i_b=S.find("e008b_rear_quiesce_and_prove")
i_cdm=S.find("camss_x1e_pix_rtcdm_stop_close", i_b)
i_phy=S.find("camss_x1e_pix_runner_stream(csiphy_sd, false)", i_cdm)
i_sensor=S.find("camss_x1e_pix_runner_stream(sensor_sd, false)", i_phy)
i_ledger=S.find("e007z_rear_release_ledger", i_sensor)
i_pm=S.find("v4l2_pipeline_pm_put", i_ledger)
req(0 <= i_b < i_cdm < i_phy < i_sensor < i_ledger < i_pm,
    "E008c complete stop ordering")

# Accepted front normal path independently has CSID -> BUS -> RTCDM, then
# CSIPHY -> sensor, and PM put only after teardown_safe.
a=FRONT.find("stop_ret = csid680_x1e_front_ipp_stop(csid);")
b=FRONT.find("vfe680_x1e_pix_runtime_bus_stop(vfe, pix);",a)
c=FRONT.find("camss_x1e_pix_rtcdm_stop_close(camss);",b)
d=FRONT.find("camss_x1e_pix_runner_stream(&csiphy->subdev, false);",c)
e=FRONT.find("camss_x1e_pix_runner_stream(req->sensor, false);",d)
p=FRONT.find("v4l2_pipeline_pm_put(video_entity);",e)
req(a>=0 and a<b<c<d<e<p, "accepted front full teardown ordering")

# RTCDM stop proof must require both MMIO mask zero and Linux IRQ ownership closed.
req("!READ_ONCE(rt->irq_armed)" in S, "RTCDM Linux IRQ closed")
req("CAMSS_RTCDM_IRQ0_MASK" in S and "== 0" in S, "RTCDM IRQ0 mask readback")
req("writel_relaxed(0, rt->base + CAMSS_RTCDM_IRQ0_MASK)" in FRONT,
    "accepted RTCDM stop masks IRQ0")
req("disable_irq(rt->irq)" in FRONT and "WRITE_ONCE(rt->irq_armed, false)" in FRONT,
    "accepted RTCDM close disables Linux IRQ")

# Failure before ledger release must pin owner.
req("e008b_rear_pin_fault" in S, "failure pin helper")
req("owner_epoch, false" in S, "ledger-release failure pins owner")
req("hardware_teardown_safe" in Y and "unsafe_stop_pinned" in Y,
    "E005y pin contract")

# E007z itself must still enforce exact retirement prerequisites.
req("last_consumed_iova != frame->slot[idx].programmed_image_iova" in Z,
    "exact consumed identity")
req("independently_verified_bus_stopped" in Z and
    "independently_verified_irqs_drained" in Z,
    "independent retirement gates")

# Build-only contract must not install/submit/free DMA itself.
for forbidden in (
    "dma_free", "dma_unmap", "vb2_buffer_done", "camss_buf_done",
    "camss_rtcdm1_windows_fifo0_commit", "module_init(",
    "module_platform_driver", "kfree(",
):
    req(forbidden not in S, "forbidden E008c action "+forbidden)

print("E008C_VERIFY_PASS")
