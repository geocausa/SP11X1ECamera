#!/usr/bin/env python3
import hashlib, json, re, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

DRV = ROOT/"experiments/E001-windows-oracle-map/oracle-local/qccamisp8380.sys"
E005Z = ROOT/"experiments/E004-front-ir-vd55g0/e005z-windows-rear-rtcdm-topology-minimal/README.md"
E006A = ROOT/"experiments/E004-front-ir-vd55g0/e006a-windows-rear-rtcdm-targeted-corpus/STRUCTURAL-DECODE.json"
E007Y = ROOT/"experiments/E004-front-ir-vd55g0/e007y-rear-full-startup-offline-materializer/RESULT.json"
E007Y_SRC = ROOT/"experiments/E004-front-ir-vd55g0/e007y-rear-full-startup-offline-materializer/camss-e007y-rear-startup.inc"
E008F = ROOT/"experiments/E004-front-ir-vd55g0/e008f-rear-startup-callsite-busid-oracle/SAFE-DETAIL.json"
E003H = ROOT/"experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/VFE1-POST-START-OWNERSHIP-STATIC.md"
VIDEO = ROOT/"src/front-imx681/kernel/camss/camss-video.c"
E004LR = ROOT/"experiments/E004-front-ir-vd55g0/e004lr-guarded-rgb-raw-frames-one-shot/RESULT.json"
RES = HERE/"RESULT.json"

HASHES = {
    DRV:"64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c",
    E005Z:"efdb22a116334c4309ed9999465088166a4126b74790cd7a37fca4bc2f8c984b",
    E006A:"5344b6db9e5e0c8cb29685b9b1fbd9a21cc7bcd3a157c0ca64720df0d2ba53e1",
    E007Y:"0160f11c1eb151c1242c3ed265e95ad4c00d19669ff321b18efee682b1c58841",
    E007Y_SRC:"eb7817024701cfa62660182db4b97bafab7f76d9cb13323a774bea2f1e8eac2a",
    E008F:"e472a4d14aefaa1a6569d80456d92a92d57d0f705d6dabcd9ee276d06d961c75",
    E003H:"520105f724256e8fc2c13d46bf69705138002aed1e259c6615da847cea8c6594",
    VIDEO:"c046b3156f5507755fd6df6cc5398ea1513ce4365ee1feb9395828f2495121ac",
    E004LR:"adbbf247049c478c35915f5ada750cb6c5e6f412e66c1afed9b95a68491483ca",
}

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

for p,h in HASHES.items():
    assert sha(p) == h, (p, sha(p), h)

b = DRV.read_bytes()
def text_rva_to_file(rva):
    assert 0x1000 <= rva < 0x3e000
    return 0x400 + (rva - 0x1000)
off = text_rva_to_file(0x39ba8)
end = b.index(b"\0", off)
assert b[off:end].decode("ascii") == "CSID%d DAL_csid_process_iq_packet cslPacket %#p, requestId %d"

dis = subprocess.check_output(
    ["llvm-objdump","-d","--start-address=0x1400246f0","--stop-address=0x140024a30",str(DRV)],
    text=True)
assert re.search(r"140024918:.*mov\s+w1, #0x2", dis)
assert re.search(r"14002491c:.*bl\s+0x140028480", dis)
dis2 = subprocess.check_output(
    ["llvm-objdump","-d","--start-address=0x140025eb0","--stop-address=0x140025ed0",str(DRV)],
    text=True)
assert re.search(r"140025ec4:.*mov\s+w1, #0x2", dis2)
assert re.search(r"140025ec8:.*bl\s+0x140028480", dis2)

e003h = E003H.read_text()
assert "Epoch0 then calls RT-CDM dispatcher RVA `0x28480` at `0x25ec8` with selector `2`" in e003h
assert "IFE Epoch0 -> complete VFE1 BUS IOVA update -> queued RT-CDM BL consume/program -> completion dispatch/retirement" in e003h

z = E005Z.read_text()
for s in [
    "Startup / first four batches:",
    "batch 1: 4 BLs = 0x4, 0xF1C, 0x4, 0x3C",
    "batch 2: 6 BLs = 0x4, 0xEBC, 0xC, 0x4, 0x10, 0x14",
    "batch 3: 6 BLs = 0x4, 0xA00, 0xC, 0x4, 0x10, 0x14",
    "batch 4: 6 BLs = 0x4, 0x658, 0xC, 0x4, 0x10, 0x14",
]:
    assert s in z

a = json.loads(E006A.read_text())
assert a["capture_indexing"]["capture_n_is_zero_based_batch_index"] is True
st = sorted(a["startup"], key=lambda x:x["capture_n"])
assert [x["capture_n"] for x in st] == [0,1,2,3]
assert [x["logical_batch"] for x in st] == [1,2,3,4]
assert [x["main_bytes"] for x in st] == [0xf1c,0xebc,0xa00,0x658]
assert [x["dmi_count"] for x in st] == [17,16,10,3]

y = json.loads(E007Y.read_text())
assert y["startup_packets"] == 4
assert y["main_bytes"] == [0xf1c,0xebc,0xa00,0x658]
assert y["dmi_counts"] == [17,16,10,3]
ys = E007Y_SRC.read_text()
assert "ARRAY_SIZE(e007y_startup_variants) == E007Y_STARTUP_PACKETS" in ys

f = json.loads(E008F.read_text())
ev = f["events"]
a2 = [i for i,x in enumerate(ev) if x == "E008F EV CALL_A_SELECTOR2"]
b2 = [i for i,x in enumerate(ev) if x == "E008F EV CALL_B_SELECTOR2"]
assert len(a2) == 2 and len(b2) >= 3
assert a2[0] < ev.index("E008F EV BATCH 0 COUNT=4")
assert a2[1] < ev.index("E008F EV BATCH 1 COUNT=6") < ev.index("E008F EV CSID_START_CALL") < ev.index("E008F EV ISP_START_DONE")
assert ev.index("E008F EV ISP_START_DONE") < b2[0] < ev.index("E008F EV BATCH 2 COUNT=6")
assert b2[1] < ev.index("E008F EV BATCH 3 COUNT=6")
assert b2[2] < ev.index("E008F EV BATCH 4 COUNT=6")

v = VIDEO.read_text()
needle = """entity = pad->entity;
		subdev = media_entity_to_v4l2_subdev(entity);

		ret = v4l2_subdev_call(subdev, video, s_stream, 1);"""
assert needle in v
lr = json.loads(E004LR.read_text())
assert lr["real_libcamera_raw_streamon_and_streamoff"] is True
assert lr["native_full_graph_neutral_before_and_after_each"] is True
assert lr["automatic_golden_return"] is True
assert lr["ir_emitter_enabled"] is False
assert lr["kernel_ir_standby_readback"] == "stream=0 illumination=0"
rear = lr["rear_ov13858"]
assert rear["frames"] == 6
assert rear["sequences"] == [0,1,2,3,4,5]
assert rear["libcamera_start_and_stop"] == "completed"
assert rear["whole_kernel_media_graph_after_session"] == "neutral"

res = json.loads(RES.read_text())
assert res["classification"] == "STATIC_CORRELATION_PASS"
assert [x["e007y_packet"] for x in res["rear_startup_packets"]] == [0,1,2,3]
assert res["first_steady_e008f_batch"] == 4
assert res["front_all_four_pre_csid_order_reusable_for_rear"] is False
assert res["linux_source_activation_order"] == ["CSID1_IPP","CSIPHY1","OV13858"]
assert res["new_windows_oracle_required_for_closed_edges"] is False
print("E008g VERIFY PASS")
