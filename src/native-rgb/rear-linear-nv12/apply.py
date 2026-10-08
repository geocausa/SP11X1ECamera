#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Cold linear rear overlay for an isolated diagnostic only; no public ABI."""
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent
def once(text,old,new):
 if text.count(old)!=1: raise RuntimeError("rear NV12 anchor drift: "+old[:90])
 return text.replace(old,new,1)
def apply(camss):
 camss=Path(camss)
 names=["camss-vfe-e004nt-rear-4k-buffer.inc","camss-vfe-e004nu-rear-ten-wm.inc",
        "camss-vfe-e008d-rear-dma.inc","camss-vfe-e008h-rear-prime.inc",
        "camss-e007z-rear-retirement.inc","native-rear-startup-geometry.inc",
        "native-rear-vfe-config.inc"]
 texts={n:(camss/n).read_text() for n in names}
 n=names[0];s=texts[n]
 replacements={
 "VFE680_E004NT_REAR_Y_DATA_OFFSET":"0U",
 "VFE680_E004NT_REAR_C_META_OFFSET":"NATIVE_REAR_NV12_UV_OFFSET",
 "VFE680_E004NT_REAR_C_DATA_OFFSET":"NATIVE_REAR_NV12_UV_OFFSET",
 "VFE680_E004NT_REAR_Y_FRAME_INCR":"NATIVE_REAR_NV12_Y_BYTES",
 "VFE680_E004NT_REAR_C_FRAME_INCR":"NATIVE_REAR_NV12_UV_BYTES",
 "VFE680_E004NT_REAR_TOTAL_BYTES":"NATIVE_REAR_NV12_ALLOCATION_BYTES",
 "VFE680_E004NT_REAR_WM_STRIDE":"NATIVE_REAR_NV12_STRIDE",
 "VFE680_E004NT_REAR_FULL_PACKER_CFG":"NATIVE_REAR_NV12_PACKER",
 "VFE680_E004NT_REAR_FULL_META_CFG":"0U"}
 for macro,value in replacements.items():
  s,count=re.subn(r"(?m)^(#define "+macro+r"\s+)\S+",lambda m:m[1]+value,s)
  if count!=1:raise RuntimeError("rear NV12 define drift "+macro)
 s=once(s,"#define VFE680_E004NT_REAR_Y_META_OFFSET",'#include "native-rear-nv12-layout.h"\n\n#define VFE680_E004NT_REAR_Y_META_OFFSET')
 s=once(s,"VFE680_E004NT_REAR_C_FRAME_INCR ==\n\t      VFE680_E004NT_REAR_TOTAL_BYTES",
        "VFE680_E004NT_REAR_C_FRAME_INCR <=\n\t      VFE680_E004NT_REAR_TOTAL_BYTES")
 s=once(s,"\tout->y_meta = base + VFE680_E004NT_REAR_Y_META_OFFSET;","\tout->y_meta = 0;")
 s=once(s,"\tout->c_meta = base + VFE680_E004NT_REAR_C_META_OFFSET;","\tout->c_meta = 0;")
 texts[n]=s
 n=names[1];s=texts[n]
 for wm in [0,1]:
  pat=r"(?m)^\t\{ \.wm = "+str(wm)+r",.*?\},$"
  line=re.search(pat,s).group()
  # Only FULL contracts change; every auxiliary contract stays byte-identical.
  values={"cfg":"NATIVE_REAR_NV12_ENABLED_CFG",
          "frame_incr": "NATIVE_REAR_NV12_UV_BYTES" if wm else "NATIVE_REAR_NV12_Y_BYTES",
          "image_cfg2":"NATIVE_REAR_NV12_STRIDE","packer":"NATIVE_REAR_NV12_PACKER"}
  for key in ["bw_limit","meta_cfg","mode_cfg","stats_ctrl","ctrl2","loss0","loss1"]:
   values[key]="0U"
  changed=line
  for key,value in values.items():
   changed,count=re.subn(r"(\."+key+r" = )\S+?(?=,| \})",lambda m:m[1]+value,changed)
   if count!=1:raise RuntimeError("rear NV12 WM field drift")
  s=once(s,line,changed)
 s=once(s,"y->cfg != 0x11U || c->cfg != 0x11U",
        "y->cfg != NATIVE_REAR_NV12_ENABLED_CFG || c->cfg != NATIVE_REAR_NV12_ENABLED_CFG")
 texts[n]=s
 n=names[4];s=texts[n]
 for wm in [0,1]:
  pattern=r"(?m)^\t\{ \.wm = "+str(wm)+r", .*?\},$"
  line=re.search(pattern,s).group()
  value="NATIVE_REAR_NV12_UV_BYTES" if wm else "NATIVE_REAR_NV12_Y_BYTES"
  changed=re.sub(r"\.required_bytes = \S+"," .required_bytes = "+value+",",line)
  changed=re.sub(r"\.image_offset = \S+"," .image_offset = 0U",changed)
  s=once(s,line,changed)
 texts[n]=s
 # Public input remains the reviewed 10-bit sensor/tuning contract. The compiled
 # diagnostic changes FULL output only, before sealing, packing or DMA mapping.
 n=names[5];s=texts[n]
 anchor="\tnative_rear_geometry_path(&geometry.ds4,"
 s=once(s,anchor,"\t/* Cold diagnostic FULL NV12; auxiliary DS output stays 10-bit. */\n\tgeometry.full.bit_width = 8;\n"+anchor)
 texts[n]=s
 n=names[2];s=texts[n]
 anchor="\t/* There is intentionally NO later write of c->cfg with EN set. */"
 s=once(s,anchor,"\tif (c->wm < 2) {\n\t\tnative_rear_nv12_write_full_disabled(vfe, c->wm);\n\t\treturn;\n\t}\n\n"+anchor)
 anchor="\tfor (i = 0; i < VFE680_E004NU_REAR_CLIENTS; i++)\n\t\te008d_rear_write_static_disabled("
 s=once(s,anchor,"\tret = native_rear_nv12_cold_admit(vfe);\n\tif (ret)\n\t\treturn ret;\n\n"+anchor)
 s=once(s,"\tset->prepared_disabled = true;","\tret = native_rear_nv12_full_readback(vfe);\n\tif (ret)\n\t\treturn ret;\n\tdev_info(vfe->camss->dev, \"NATIVE_REAR_NV12_READBACK_PASS width=3840 height=2160 stride=3840 bytes=12441600 full_bits=8 ds_bits=10\\n\");\n\tset->prepared_disabled = true;")
 texts[n]=s
 # Metadata address register access is absent for every initial and Epoch retarget.
 for n in names[2:4]:
  s=texts[n]
  # Exact blocks, bounded to each known function.
  s=re.sub(r"\n\t\tif \((?:addr\.wm\[i\]|c->wm) == 0\)\n\t\t\twritel_relaxed\(.*?VFE680_X1E_BUS_META_ADDR\);\n\t\telse if \((?:addr\.wm\[i\]|c->wm) == 1\)\n\t\t\twritel_relaxed\(.*?VFE680_X1E_BUS_META_ADDR\);","",s,flags=re.S)
  s=re.sub(r"\n\t\tif \((?:addr\.wm\[i\]|c->wm) == [01] &&\n\t\t    readl_relaxed\(cfg \+ VFE680_X1E_BUS_META_ADDR\) !=\n\t\t    .*?\)\n\t\t\treturn -EIO;","",s)
  if "VFE680_X1E_BUS_META_ADDR" in s:raise RuntimeError("FULL metadata access survived")
  texts[n]=s
 n=names[6];s=texts[n]
 s=once(s," ret=native_rear_noc_prepare(vfe);"," ret=native_rear_nv12_cold_admit(vfe);\n if (ret)\n  return ret;\n ret=native_rear_noc_prepare(vfe);")
 s=once(s," writel(VFE680_X1E_WINDOWS_UBWC_STATIC_CTRL,vfe->base+VFE680_X1E_BUS_UBWC_STATIC_CTRL);\n","")
 s=once(s,"(bus_mask!=VFE680_X1E_SP11_DAL_BUS_MASK0 && bus_mask!=VFE680_X1E_WINDOWS_BUS_MASK0) ||\n     readl(vfe->base+VFE680_X1E_BUS_UBWC_STATIC_CTRL)!=VFE680_X1E_WINDOWS_UBWC_STATIC_CTRL)",
        "(bus_mask!=VFE680_X1E_SP11_DAL_BUS_MASK0 && bus_mask!=VFE680_X1E_WINDOWS_BUS_MASK0))")
 s=s.replace("The current rear FULL surface contract is QC10C compressed.","This isolated rear FULL surface is cold linear NV12.")
 texts[n]=s
 c=(camss/"camss-vfe-680.c").read_text()
 c=once(c,'#include "camss-vfe-e008d-rear-dma.inc"','#include "native-rear-nv12-bus.inc"\n#include "camss-vfe-e008d-rear-dma.inc"')
 texts["camss-vfe-680.c"]=c
 # Reject any unexpected source drift before mutating this fresh staging tree.
 for n,t in texts.items(): (camss/n).write_text(t)
 for n in ["native-rear-nv12-layout.h","native-rear-nv12-bus.inc"]:
  (camss/n).write_bytes((HERE/n).read_bytes())
 return {"rear_full_storage":"linear_NV12","width":3840,"height":2160,
         "stride":3840,"image_bytes":12441600,"allocation_bytes":12443648,
         "FULL_bits":8,"DS_bits":10,"public_video_buffers_exposed":False,
         "modified_files":names,"cold_only":True,"pixel_CPU_processing":False}
