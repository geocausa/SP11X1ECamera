#!/usr/bin/env python3
"""E004nt rear 4K FULL WM source-only Linux DMA layout acceptance.

All tests are OFFLINE; no camera/kernel/module is loaded, no DMA allocated,
no Windows absolute image addresses or optical contents are accessed.
"""
from __future__ import annotations
import copy
import hashlib
import json
import re
import subprocess
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
NR=ROOT/"experiments/E004-front-ir-vd55g0/e004nr-rear-pix-kernel-source-profile"
NS=ROOT/"experiments/E004-front-ir-vd55g0/e004ns-rear-csid1-ipp-offline"
SRC=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss")
BUILD=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/e004nt-rear-4k-buffer-build/camss")
EXPECTED_MODULE="f5cc00181a2d1966cd9499544067b1a920e76bf4db73e8063bae052540fb0b04"
EXPECTED_INC="05a27b12384c1267787b193eb0d8d13abe57a4d189778dbe9a52490f180046e6"
EXPECTED_BASE={
"camss.c":"788243cbf08d1f8cc1500a8c7177e30095875bd3b3be54bf0ac0fdec106dba91",
"camss-csid-680.c":"9c79fec22fc63738dd05b33aa7d43f4a68be4935b522fa35354a0170c498ae90",
"camss-vfe-680.c":"99b7f9c18456e1926a5ad82b56a9b025a798add797c09490b645d9907b3a3208",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_layout(data,wm,values,source):
    assert data["schema"]=="sp11-e004nt-windows-rear-VFE1-FULL-WM0-WM1-RELATIVE-only-v1"
    assert data["no_absolute_DMA_addresses_memory_pointers_or_pixels_exported"] is True
    assert data["original_SP7_KD_logs_remain_private"] is True
    assert len(data["phases"])==2
    a,b=data["phases"]
    assert [a["phase"],b["phase"]]==["LIVE1","LIVE2"]
    assert {k:v for k,v in a.items() if k!="phase"}=={
        k:v for k,v in b.items() if k!="phase"}
    assert wm["schema"]=="sp11-e004nr-rear-oem-Windows-VFE1-output-WM-safe-scalar-v1"
    assert len(wm["phases"])==2
    assert wm["phases"][0]["write_masters"]==wm["phases"][1]["write_masters"]
    v=values
    expected={
      "Y_META_OFFSET":0,"Y_DATA_OFFSET":0x11000,
      "C_META_OFFSET":0xa9d000,"C_DATA_OFFSET":0xaa6000,
      "Y_FRAME_INCR":0xa9d000,"C_FRAME_INCR":0x559000,
      "TOTAL_BYTES":0xff6000,"Y_WIDTH":3840,"Y_ROWS":2160,
      "C_WIDTH":3840,"C_ROWS":1080,"WM_STRIDE":5120,
      "FULL_PACKER_CFG":0xb,"FULL_META_CFG":0x800,
    }
    assert v==expected
    assert v["Y_FRAME_INCR"]+v["C_FRAME_INCR"]==v["TOTAL_BYTES"]
    assert v["C_META_OFFSET"]==v["Y_FRAME_INCR"]
    assert v["Y_DATA_OFFSET"]+v["WM_STRIDE"]*v["Y_ROWS"] <= v["C_META_OFFSET"]
    assert v["C_DATA_OFFSET"]+v["WM_STRIDE"]*v["C_ROWS"] <= v["TOTAL_BYTES"]
    assert v["C_META_OFFSET"] % 4096 == 0
    assert v["TOTAL_BYTES"] % 4096 == 0
    assert v["TOTAL_BYTES"] < 2**32
    assert v["C_DATA_OFFSET"]-v["C_META_OFFSET"] == 0x9000
    expected_keys={
      "phase","y_metadata_relative_offset","y_image_relative_offset",
      "c_metadata_relative_offset","c_image_relative_offset",
      "c_image_relative_to_c_metadata","y_WM_frame_increment_bytes",
      "c_WM_frame_increment_bytes","single_window_total_bytes",
      "y_WM_hardware_stride_bytes","c_WM_hardware_stride_bytes",
      "y_rows","c_rows",
      "metadata_offsets_at_both_plane_starts_page_aligned",
      "configured_row_extents_fit_in_each_WM_frame_increment",
    }
    for phase,hw in zip(data["phases"],wm["phases"]):
        assert phase["phase"]==hw["phase"]
        assert set(phase)==expected_keys
        assert phase["y_metadata_relative_offset"]==v["Y_META_OFFSET"]
        assert phase["y_image_relative_offset"]==v["Y_DATA_OFFSET"]
        assert phase["c_metadata_relative_offset"]==v["C_META_OFFSET"]
        assert phase["c_image_relative_offset"]==v["C_DATA_OFFSET"]
        assert phase["c_image_relative_to_c_metadata"] == (
            v["C_DATA_OFFSET"]-v["C_META_OFFSET"])
        assert phase["y_WM_frame_increment_bytes"]==v["Y_FRAME_INCR"]
        assert phase["c_WM_frame_increment_bytes"]==v["C_FRAME_INCR"]
        assert phase["single_window_total_bytes"]==v["TOTAL_BYTES"]
        assert phase["y_WM_hardware_stride_bytes"]==v["WM_STRIDE"]
        assert phase["c_WM_hardware_stride_bytes"]==v["WM_STRIDE"]
        assert phase["y_rows"]==v["Y_ROWS"] and phase["c_rows"]==v["C_ROWS"]
        assert phase["metadata_offsets_at_both_plane_starts_page_aligned"] is True
        assert phase["configured_row_extents_fit_in_each_WM_frame_increment"] is True
        y,c=hw["write_masters"][:2]
        assert y["wm"]==0 and c["wm"]==1
        assert [int(w["wm_config"],16) for w in (y,c)]==[0x11,0x11]
        assert [int(w["frame_increment"],16) for w in (y,c)]==[
            v["Y_FRAME_INCR"],v["C_FRAME_INCR"]]
        assert [int(w["wm_stride"],16) for w in (y,c)]==[
            v["WM_STRIDE"],v["WM_STRIDE"]]
        assert [int(w["packer_config"],16) for w in (y,c)]==[
            v["FULL_PACKER_CFG"],v["FULL_PACKER_CFG"]]
        assert [int(w["metadata_config"],16) for w in (y,c)]==[
            v["FULL_META_CFG"],v["FULL_META_CFG"]]
        assert [int(w["image_geometry"],16) for w in (y,c)]==[
            v["Y_ROWS"]<<16 | v["Y_WIDTH"],
            v["C_ROWS"]<<16 | v["C_WIDTH"]]
    # Source must enforce a private 32-bit DMA span in the same CAMSS/IOMMU
    # and MUST NOT pretend a multi-entry vb2 SG table is contiguous.
    assert "dma_alloc_coherent(dev, VFE680_E004NT_REAR_TOTAL_BYTES," in source
    assert "dma_free_coherent(dev, VFE680_E004NT_REAR_TOTAL_BYTES," in source
    assert "dma_free_coherent(vfe->camss->dev, surface->size," in source
    assert "vfe680_x1e_dma_span_32bit(surface->dma," in source
    assert "vfe680_x1e_dma_span_32bit(surface->dma, surface->size)" in source
    assert "IS_ALIGNED(surface->dma, 4096U)" in source
    assert "surface->size != VFE680_E004NT_REAR_TOTAL_BYTES" in source
    assert source.count("surface->in_flight")>=3
    assert "if (surface->in_flight)\n\t\treturn -EBUSY;" in source
    assert "memset(surface->cpu, 0, surface->size);" in source
    assert "static_assert(VFE680_E004NT_REAR_Y_DATA_OFFSET +" in source
    assert "static_assert(VFE680_E004NT_REAR_C_DATA_OFFSET +" in source
    assert "static_assert(VFE680_E004NT_REAR_Y_FRAME_INCR +" in source
    assert "out->y_meta = base + VFE680_E004NT_REAR_Y_META_OFFSET;" in source
    assert "out->y_image = base + VFE680_E004NT_REAR_Y_DATA_OFFSET;" in source
    assert "out->c_meta = base + VFE680_E004NT_REAR_C_META_OFFSET;" in source
    assert "out->c_image = base + VFE680_E004NT_REAR_C_DATA_OFFSET;" in source
    assert source.count("return -EOPNOTSUPP;")==1
    assert "static int __used\nvfe680_e004nt_rear_4k_runtime_authorization(" in source
    assert "vb2_dma_sg_plane_desc(" not in source
    return True


def check_build():
    manifest=json.loads((HERE/"BUILD-RESULT.json").read_text())
    assert manifest["schema"]=="sp11-e004nt-isolated-rear-4k-VFE1-coherent-layout-build-scalar-v1"
    assert manifest["identity"]=="E004nt"
    assert manifest["parent_git_revision"]=="4684273a318856266b35d222de4e8cbf0240fb3c"
    assert manifest["isolated_arm64_compiled_module_sha256"]==EXPECTED_MODULE
    assert manifest["isolated_compiled_rear_4k_DMA_source_sha256"]==EXPECTED_INC
    assert manifest["original_integrated_kernel_camss_sources_unchanged"] is True
    assert manifest["new_rear_runtime_call_sites_added"] is False
    assert manifest["new_rear_runtime_authorization_unconditionally_denied"] is True
    assert manifest["new_kernel_module_installed_or_loaded"] is False
    assert manifest["Linux_DMA_coherent_buffer_actually_allocated_on_Golden"] is False
    assert manifest["Windows_absolute_DMA_register_addresses_exported"] is False
    assert manifest["Linux_native_rear_4k_ISP_optical_frame_proven"] is False
    assert sha(BUILD/"qcom-camss.ko")==EXPECTED_MODULE
    assert sha(HERE/"camss-vfe-e004nt-rear-4k-buffer.inc")==EXPECTED_INC
    markers={
     "camss.c":'#include "camss-e004nr-rear-profile.inc"\n\n',
     "camss-csid-680.c":'#include "camss-csid-e004ns-rear-ipp.inc"\n\n',
     "camss-vfe-680.c":'#include "camss-vfe-e004nt-rear-4k-buffer.inc"\n\n',
    }
    for name,marker in markers.items():
        original=(SRC/name).read_text()
        staged=(BUILD/name).read_text()
        assert sha(SRC/name)==EXPECTED_BASE[name]
        assert staged.count(marker)==1
        assert staged.replace(marker,"")==original
        assert marker not in original
    assert (BUILD/"camss-e004nr-rear-profile.inc").read_bytes()==(
        NR/"camss-e004nr-rear-profile.inc").read_bytes()
    assert (BUILD/"camss-csid-e004ns-rear-ipp.inc").read_bytes()==(
        NS/"camss-csid-e004ns-rear-ipp.inc").read_bytes()
    assert (BUILD/"camss-vfe-e004nt-rear-4k-buffer.inc").read_bytes()==(
        HERE/"camss-vfe-e004nt-rear-4k-buffer.inc").read_bytes()
    assert all(name+"(" not in (BUILD/"camss-vfe-680.c").read_text() for name in (
        "vfe680_e004nt_rear_surface_alloc",
        "vfe680_e004nt_rear_surface_addrs",
        "vfe680_e004nt_rear_surface_free",
        "vfe680_e004nt_rear_4k_runtime_authorization",
    ))
    syms=subprocess.check_output([
       "aarch64-linux-gnu-nm","-a",str(BUILD/"qcom-camss.ko")],text=True)
    for name in manifest["retained_rear_compiled_symbols"]:
        assert name in syms
    assert "warning:" not in (BUILD/"E004NT-CAMSS-BUILD.log").read_text()
    assert "error:" not in (BUILD/"E004NT-CAMSS-BUILD.log").read_text()
    vm=subprocess.check_output(
        ["modinfo","-F","vermagic",str(BUILD/"qcom-camss.ko")],text=True).strip()
    assert vm=="7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64"


if __name__=="__main__":
    layout=json.loads((HERE/"RELATIVE-RESULT.json").read_text())
    wm=json.loads((NR/"WM-RESULT.json").read_text())
    source=(HERE/"camss-vfe-e004nt-rear-4k-buffer.inc").read_text()
    values={
      name:int(v,0) for name,v in re.findall(
       r"^#define\s+VFE680_E004NT_REAR_([A-Z0-9_]+)\s+(0x[0-9a-fA-F]+|\d+)U\s*$",
       source,re.M)
    }
    check_layout(layout,wm,values,source)
    check_build()
    mutation_cases=(
      ("wrong_y_meta", lambda l,w,v:v.__setitem__("Y_META_OFFSET",0x1000)),
      ("wrong_y_data",lambda l,w,v:v.__setitem__("Y_DATA_OFFSET",0x6000)),
      ("wrong_c_meta",lambda l,w,v:v.__setitem__("C_META_OFFSET",0x4f2000)),
      ("wrong_c_data",lambda l,w,v:v.__setitem__("C_DATA_OFFSET",0xaa5000)),
      ("too_small_total",lambda l,w,v:v.__setitem__("TOTAL_BYTES",0xff5000)),
      ("wrong_stride",lambda l,w,v:v.__setitem__("WM_STRIDE",3840)),
      ("wrong_y_rows",lambda l,w,v:v.__setitem__("Y_ROWS",1440)),
      ("wrong_c_rows",lambda l,w,v:v.__setitem__("C_ROWS",720)),
      ("wrong_y_incr",lambda l,w,v:v.__setitem__("Y_FRAME_INCR",0xa9c000)),
      ("wrong_c_incr",lambda l,w,v:v.__setitem__("C_FRAME_INCR",0x558000)),
      ("wrong_packer",lambda l,w,v:v.__setitem__("FULL_PACKER_CFG",0xa)),
      ("wrong_meta_cfg",lambda l,w,v:v.__setitem__("FULL_META_CFG",0x400)),
      ("windows_two_phase_disagree",lambda l,w,v:l["phases"][1].__setitem__("c_image_relative_offset",0xaa7000)),
      ("non_pagealigned_meta",lambda l,w,v:l["phases"][0].__setitem__("metadata_offsets_at_both_plane_starts_page_aligned",False)),
      ("not_complete_window",lambda l,w,v:l["phases"][0].__setitem__("single_window_total_bytes",0xff5000)),
      ("unsafe_wm1_frame_incr",lambda l,w,v:w["phases"][1]["write_masters"][1].__setitem__("frame_increment","0x00550000")),
      ("dma_pointer_leak",lambda l,w,v:l["phases"][0].__setitem__("Windows_DMA_addr",0x10000)),
      ("faked_optical_proof",lambda l,w,v:l.__setitem__("no_absolute_DMA_addresses_memory_pointers_or_pixels_exported",False)),
    )
    for name,mut in mutation_cases:
        l,w,v=copy.deepcopy(layout),copy.deepcopy(wm),dict(values)
        mut(l,w,v)
        try:check_layout(l,w,v,source)
        except (AssertionError,KeyError):
            continue
        raise SystemExit("E004NT_FAIL_OPEN_NEGATIVE_CASE "+name)
    print("PASS_E004NT_TWO_WINDOWS_REAR_4K_WM_YC_RELATIVE_LAYOUT_"
          "ARM64_COMPILED_COHERENT_DMA_SPAN_32BIT_METADATA_BOUNDS_"
          "18_NEGATIVE_CASES_NO_MODULE_LOADED_REAR_RUNTIME_DENIED")
