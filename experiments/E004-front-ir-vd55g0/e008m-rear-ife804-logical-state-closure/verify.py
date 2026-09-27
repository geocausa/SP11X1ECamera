#!/usr/bin/env python3
import json,re,hashlib
from pathlib import Path

D=Path(__file__).resolve().parent
R=D.parents[2]
oracle=R/"experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-ife-start-804-oracle.json"
nu=R/"experiments/E004-front-ir-vd55g0/e004nu-rear-vfe1-ten-wm-ownership/camss-vfe-e004nu-rear-ten-wm.inc"
d8=R/"experiments/E004-front-ir-vd55g0/e008d-rear-ten-wm-linux-dma-address-provider/camss-vfe-e008d-rear-dma.inc"
f=R/"experiments/E004-front-ir-vd55g0/e008f-rear-startup-callsite-busid-oracle/SAFE-DETAIL.json"
res=json.loads((D/"RESULT.json").read_text())
o=json.loads(oracle.read_text())
safe=json.loads(f.read_text())
snu=nu.read_text(); sd8=d8.read_text()

assert o["source"]["sha256"] == res["source_driver_sha256"]
assert o["hardware_action"]["direct_mmio_in_0x804_branch"] is False
assert o["hardware_action"]["hardware_start_call_in_0x804_branch"] is False
assert o["downstream_semantics"]["override_condition"] == "camera_use_case == 4 only"
assert len(o["object_field_xrefs"]) == 6
assert safe["events"][:2] == ["E008F EV CDM804","E008F EV IFE804"]

rows=re.findall(r"\{ \.wm = (\d+),.*?\.frame_drop_period = (0x[0-9a-f]+)U, \.frame_drop_pattern = (0x[0-9a-f]+)U,",snu)
assert len(rows)==10, len(rows)
assert all(period=="0x00000000" and pattern=="0x00000001" for _,period,pattern in rows)
assert "writel_relaxed(c->frame_drop_period" in sd8
assert "writel_relaxed(c->frame_drop_pattern" in sd8
assert res["rear_active_wms"]==10
assert res["synthetic_linux_ife804_stage_required"] is False
assert res["rear_camera_use_case_numeric_promoted"] is False
assert res["runtime_actions_performed"] is False
print("E008m VERIFY PASS")
