#!/usr/bin/env python3
from pathlib import Path
import json, re

D=Path(__file__).resolve().parent
R=D.parents[2]
S=(D/"camss-vfe-e008d-rear-dma.inc").read_text()
NU=(R/"experiments/E004-front-ir-vd55g0/e004nu-rear-vfe1-ten-wm-ownership/camss-vfe-e004nu-rear-ten-wm.inc").read_text()
NT=(R/"experiments/E004-front-ir-vd55g0/e004nt-rear-vfe1-4k-buffer-contract/camss-vfe-e004nt-rear-4k-buffer.inc").read_text()
WM=json.loads((R/"experiments/E004-front-ir-vd55g0/e004nr-rear-pix-kernel-source-profile/WM-RESULT.json").read_text())
FRONT=(R/"src/front-imx681/kernel/camss/camss-vfe-680.c").read_text()

def req(x,msg):
    if not x:
        raise AssertionError(msg)

m=re.search(r'vfe680_e004nu_rear_wm_prepare_disabled\(.*?^}', NU, re.S|re.M)
req(m is not None, "locate E004nu helper")
old=m.group(0)
req("writel_relaxed(c->cfg, cfg + VFE680_X1E_BUS_CFG)" in old,
    "detect historical E004nu enabled-write defect")
req("vfe680_e004nu_rear_wm_prepare_disabled(" not in S,
    "never call superseded E004nu helper")

ph=WM["phases"]
req(len(ph)==2 and ph[0]["write_masters"]==ph[1]["write_masters"],
    "rear two-phase WM agreement")
rows=ph[0]["write_masters"]
ids=[x["wm"] for x in rows]
req(ids==[0,1,2,3,11,12,13,14,16,18], ("rear WM IDs",ids))
sizes={x["wm"]:int(x["frame_increment"],16) for x in rows}
req(sizes[16]==0x2d00, "BF frame increment")

for token in (
    "dma_alloc_coherent(dev, size, &buf->dma, GFP_KERNEL)",
    "vfe680_x1e_dma_span_32bit(buf->dma, size)",
    "dma_free_coherent(dev, buf->size, buf->cpu, buf->dma)",
):
    req(token in FRONT, "front coherent ownership source "+token)

for token in (
    "VFE680_E004NT_REAR_TOTAL_BYTES",
    "VFE680_E004NT_REAR_Y_DATA_OFFSET",
    "VFE680_E004NT_REAR_C_DATA_OFFSET",
):
    req(token in NT, "E004nt FULL authority "+token)
for token in (
    "vfe680_e004nt_rear_surface_alloc",
    "vfe680_e004nt_rear_surface_addrs",
):
    req(token in NT and token in S, "E004nt binding "+token)

req("aux->size = c->frame_incr;" in S, "aux size from frame increment")
req("dma_alloc_coherent(vfe->camss->dev, aux->size" in S,
    "rear aux coherent allocation")
req("vfe680_x1e_dma_span_32bit(aux->dma, aux->size)" in S,
    "whole aux DMA span bounded")
req("#define E008D_REAR_AUX_COUNT 8" in S, "eight aux outputs")
req("2, 3, 11, 12, 13, 14, 16, 18," in S, "aux WM identity")

req(S.count("VFE_BUS_WRITE_CLIENT_CFG_EN") >= 3, "enable gates present")
req("c->cfg & ~VFE_BUS_WRITE_CLIENT_CFG_EN" in S, "static cfg masks enable")
req("writel_relaxed(c->cfg, cfg + VFE680_X1E_BUS_CFG)" not in S,
    "no enabled cfg write")
req("| VFE_BUS_WRITE_CLIENT_CFG_EN" not in S, "no enable OR")
req("set->prepared_disabled = true;" in S, "prepared only after readback")

for token in (
    "VFE680_X1E_BUS_IMAGE_ADDR",
    "VFE680_X1E_BUS_META_ADDR",
    "readl_relaxed(cfg + VFE680_X1E_BUS_IMAGE_ADDR)",
    "readl_relaxed(cfg + VFE680_X1E_BUS_META_ADDR)",
):
    req(token in S, "dynamic address contract "+token)

for forbidden in (
    "vfe680_e004nu_rear_wm_prepare_disabled(",
    "camss_rtcdm1_windows_fifo0_commit",
    "camss_x1e_pix_rtcdm_open_start",
    "v4l2_subdev_call",
    "module_init(", "module_platform_driver",
    "e007z_rear_release_ledger",
):
    req(forbidden not in S, "forbidden E008d action "+forbidden)
req("return -EOPNOTSUPP;" in S, "runtime denied")

aux_total=sum(sizes[x] for x in [2,3,11,12,13,14,16,18])
req(aux_total==0x373d00, hex(aux_total))
req(0x00ff6000 + aux_total == 0x01369d00,
    hex(0x00ff6000+aux_total))

print("E008D_VERIFY_PASS")
