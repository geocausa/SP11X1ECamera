#!/usr/bin/env python3
"""E004nq physical Windows OEM rear PIX route acceptance gate (offline scalar only).

This intentionally MUST NOT arm a camera, mutate the Golden kernel, export
frame bytes, or authorize a rear Linux ISP hardware frame from Windows proof.
"""
import copy
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
FRONT=ROOT/"experiments/E003-front-imx681-cphy/e003g-windows-csid-vfe-oracle/route-oracle-summary.json"

def verify(phys,win,front,state=None):
    assert phys["schema"]=="sp11-e004nq-rear-windows-physical-dd-slash-p-5phase-scalar-v1"
    assert phys["source_private_SP7_KD_mmio_logs"] and len(phys["source_private_SP7_KD_mmio_logs"])==5
    assert "dd /p" in phys["acquisition"]
    assert phys["parent_source_revision"]=="eba30fea25c6fb770ad79f5bcf3abf67aa6626aa"
    assert phys["phases"]==["IDLE","LIVE1","POST","LIVE2","POST2"]
    assert "rear VideoRecord 3840x2160 NV12" in phys["acquisition"]
    assert phys["rear_OEM_Windows_VFE1_PIX_3840x2160_confirmed_across_two_live_passes"] is True
    assert phys["rear_OEM_Windows_CSID1_IPP_enabled_confirmed_across_two_live_passes"] is True
    assert phys["image_dma_addresses_RAW_optical_pixels_images_thumbnails_hashes_exported"] is False
    assert phys["Linux_rear_native_4k_ISP_optical_frame_proven"] is False
    regions=phys["region_stats"]
    assert len(regions)==6
    expected=(
        ("WRAPPER",1024,3,3,0),
        ("CSID0",2048,79,79,0),
        ("CSID1",2048,110,108,11),
        ("CSIPHY1",2048,103,101,7),
        ("VFE0",4096,0,0,0),
        ("VFE1",4096,219,219,36),
    )
    for got,(name,n,live1,live2,diff) in zip(regions,expected):
        assert got["region"]==name
        assert got["complete_dwords_each_phase"]==n
        assert got["idle_all_sentinel"] is True
        assert got["LIVE1_nonzero_nonsentinel_dwords"]==live1
        assert got["LIVE2_nonzero_nonsentinel_dwords"]==live2
        assert got["LIVE1_vs_LIVE2_dword_differences"]==diff
        assert got["POST_vs_IDLE_dword_differences"]==0
        assert got["POST2_vs_IDLE_dword_differences"]==0
    phases=phys["live_physical_config"]
    assert len(phases)==2
    for p,tag in zip(phases,("LIVE1","LIVE2")):
        assert p["phase"]==tag
        wrapper=p["wrapper"]
        assert len(wrapper)==3
        assert [x["config"] for x in wrapper]==["0x00000001","0x00000101","0x00000001"]
        assert [x["output_ife_enable"] for x in wrapper]==[False,True,False]
        c0,c1=p["csid"]
        assert (c0["instance"],c0["ipp_cfg0"],c0["ipp_path_enabled"])==(0,"0x00000000",False)
        assert c1["instance"]==1 and c1["ipp_path_enabled"] is True
        assert c1["rx_cfg0"]=="0x10232103" and c1["rx_cfg1"]=="0x00000001"
        rx=int(c1["rx_cfg0"],16)
        assert (rx&0xf)+1==4  # four physical D-PHY lanes
        assert (rx>>24)&1==0  # D-PHY, unlike front C-PHY
        # CSID680 PHY_NUM_SEL uses one-based encoded numbering on this SP11:
        # known front CSIPHY2 selects 3; physical rear CSIPHY1 selects 2.
        assert (rx>>20)&0xf==2
        assert c1["ipp_cfg0"]=="0x802b2000" and c1["ipp_cfg1"]=="0x00007241"
        assert c1["raw10_csi_data_type"]==0x2b
        assert c1["hcrop"]=="0x0fdf0000" and c1["vcrop"]=="0x08ed0000"
        assert (c1["x_start"],c1["x_end"],c1["y_start"],c1["y_end"])==(0,4063,0,2285)
        assert c1["format_measure"]=="0x08ee0fe0"
        assert (c1["measured_width"],c1["measured_height"])==(4064,2286)
        assert len(p["vfe"])==2
        v0,v1=p["vfe"]
        assert v0["instance"]==0 and v0["enabled_clients"]==[]
        assert v1["instance"]==1
        assert v1["hardware_version"]=="0x30000002" and v1["bus_version"]=="0x20020000"
        clients=v1["enabled_clients"]
        assert [x["wm"] for x in clients]==[0,1,2,3,11,12,13,14,16,18]
        for i,name,w,h,stride,packer in (
            (0,"FULL_Y",3840,2160,5120,"0x0000000b"),
            (1,"FULL_C",3840,1080,5120,"0x0000000b"),
            (2,"DS4",480,270,3840,"0x0000000a"),
            (3,"DS16",120,68,1024,"0x0000000a"),
        ):
            x=clients[i]
            assert (x["wm"],x["name"],x["width"],x["height"],x["stride"],x["packer_config"])==(
                i,name,w,h,stride,packer)
            assert x["config"]=="0x00000011"
        assert [x["config"] for x in clients[4:]]==[
            "0x00010001"]*4+["0x00020001","0x00010001"]
    assert win["schema"]=="sp11-e004nq-windows-rear-videorecord-2phase-scalar-v1"
    assert win["experiment"]=="E004nq"
    assert win["same_SP11_OEM_rear_source"]=="Surface Camera Rear Color VideoRecord NV12 3840x2160"
    assert win["Windows_rear_two_distinct_successful_StartAsync_and_StopAsync_phases"] is True
    assert win["Windows_rear_first_live_3840x2160_frame_handles"]==861
    assert win["Windows_rear_second_live_3840x2160_frame_handles"]==338
    assert win["Windows_holder_atomically_consumed_once_at_script_entry"] is True
    assert win["Windows_Scheduled_Task_manually_started_once_with_no_future_trigger_and_unregistered"] is True
    assert win["Windows_camera_session_done"] is True
    assert win["Windows_optical_frames_or_images_exported"] is False
    assert win["Linux_rear_native_4k_ISP_hardware_frame_proven"] is False
    assert front["route_decode"]["csid1_rx"]["cfg0"]=="0x11300000"
    assert front["route_decode"]["csid1_rx"]["phy_num_sel"]==3
    assert front["route_decode"]["csid1_rx"]["phy_type_sel"]==1
    assert front["route_decode"]["vfe"]["windows_full_output"]=={
        "width":2560,"height":1440,"chroma_height":720}
    if state is not None:
        s=state["latest_windows_rear_physical_mmio_oracle"]
        assert s["identity"]=="E004nq"
        assert s["Windows_rear_OEM_CSID1_VFE1_PIX_path_physically_proven"] is True
        assert s["Windows_rear_CSID0_VFE0_processed_path_physically_proven"] is False
        assert s["Linux_rear_native_4k_ISP_optical_frame_proven"] is False
    return True

def source_guard():
    s=(HERE/"parse-sp7-kd-physical-mmio.ps1").read_text()
    h=(HERE/"hold-rear-two-physical-phases.ps1").read_text()
    assert "dd /p" in s and "Get-Reg" in s
    assert "WM image_addr" not in s
    assert "0xe00+$i*0x100" in s
    assert "CreateNew" in h and "Surface Camera Rear" in h
    assert "VideoRecord" in h and "NV12" in h
    assert "E004NQ-SIGNAL-GO2.txt" in h
    assert "CopyToBuffer" not in h and "LockBuffer" not in h
    assert "C:\\Users\\" not in (HERE/"RESULT.json").read_text()
    return True

if __name__=="__main__":
    phys=json.loads((HERE/"RESULT.json").read_text())
    win=json.loads((HERE/"WINDOWS-RESULT.json").read_text())
    front=json.loads(FRONT.read_text())
    import yaml
    state=yaml.safe_load((ROOT/"state/project.yaml").read_text())
    verify(phys,win,front,state)
    source_guard()
    mutation_cases=(
      ("wrong_csiphy",lambda p,w:p["live_physical_config"][0]["csid"][1].__setitem__("rx_cfg0","0x11300000")),
      ("wrong_csid",lambda p,w:p["live_physical_config"][1]["wrapper"][1].__setitem__("output_ife_enable",False)),
      ("rear_csid0_claim",lambda p,w:p["live_physical_config"][0]["csid"][0].__setitem__("ipp_path_enabled",True)),
      ("front_crop_injected",lambda p,w:p["live_physical_config"][1]["csid"][1].__setitem__("x_end",3839)),
      ("wrong_full_stride",lambda p,w:p["live_physical_config"][0]["vfe"][1]["enabled_clients"][0].__setitem__("stride",3840)),
      ("wrong_full_height",lambda p,w:p["live_physical_config"][1]["vfe"][1]["enabled_clients"][0].__setitem__("height",1440)),
      ("fake_vfe0",lambda p,w:p["live_physical_config"][0]["vfe"][0].__setitem__("enabled_clients",[{"wm":0}])),
      ("post_not_idle",lambda p,w:p["region_stats"][1].__setitem__("POST_vs_IDLE_dword_differences",1)),
      ("fake_hardware_frame",lambda p,w:p.__setitem__("Linux_rear_native_4k_ISP_optical_frame_proven",True)),
      ("wrong_source",lambda p,w:w.__setitem__("same_SP11_OEM_rear_source","Surface Camera Front")),
    )
    for name,mut in mutation_cases:
        p,w=copy.deepcopy(phys),copy.deepcopy(win)
        mut(p,w)
        try: verify(p,w,front)
        except AssertionError: pass
        else: raise SystemExit("E004NQ_NEGATIVE_GATE_FAILED "+name)
    print("PASS_E004NQ_REAL_WINDOWS_REAR_DPHY4_CSID1_IPP4064x2286_VFE1_FULL3840x2160_STRIDE5120_"
          "2_LIVE_5_PHASE_10_NEGATIVE_TESTS_GOLDEN_HARDWARE_LINUX_UNPROVEN")
