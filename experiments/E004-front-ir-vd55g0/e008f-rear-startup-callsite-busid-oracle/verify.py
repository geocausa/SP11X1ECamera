#!/usr/bin/env python3
import hashlib, json, re, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DRV = ROOT/"experiments/E001-windows-oracle-map/oracle-local/qccamisp8380.sys"
BF = ROOT/"experiments/E004-front-ir-vd55g0/e004oj-bf-resource-zero-register-offset-static/RESULT.json"
E = HERE.parent/"e008e-rear-startup-order-windows-oracle"

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

safe = json.loads((HERE/"SAFE-DETAIL.json").read_text())
run = json.loads((HERE/"WINDOWS-RUNTIME.json").read_text())
res = json.loads((HERE/"RESULT.json").read_text())
bfr = json.loads(BF.read_text())

assert sha(HERE/"SAFE-DETAIL.json") == "e472a4d14aefaa1a6569d80456d92a92d57d0f705d6dabcd9ee276d06d961c75"
assert sha(HERE/"WINDOWS-RUNTIME.json") == "d9f5d4e8b344484a116b3409da8f11188df9afbd99bdce20f7a763827590720d"
assert sha(HERE/"holder.ps1") == "2af5ea088df42d28160d6e2a2a26a0089fff76622956122682fd3660dca14ef8"
assert sha(DRV) == "64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c"
assert run["holder_identity"] == "E008F" and run["holder_consumed"] is True
assert run["record_start_status"] == "Success" and run["record_stop_pass"] is True
assert run["valid_4k_handles"] == 88 and run["protected_golden_restored"] is True
assert run["linux_native_rear_isp_runtime_performed"] is False
assert not run["pixel_bytes_read"] and not run["pixel_data_exported"] and not run["dma_contents_exported"]
assert safe["event_count"] == len(safe["events"]) == 49
assert safe["first_six_batches"] == [{"index":str(i),"count":("4" if i==0 else "6")} for i in range(6)]

cfg = ["3000","3000","3001","3002","301c","3010","300f","300e","300c","300d"]
one = ["3000","3001","3002","301c","3010","300f","300e","300c","300d"]
assert safe["bus_config_ids"] == cfg
assert [x["id"] for x in safe["bus_set"]] == one
assert all(x["arg"] == "1" for x in safe["bus_set"])
assert [x["id"] for x in safe["initial_address_writes"]] == cfg
assert [x["arg"] for x in safe["initial_address_writes"]] == ["0","1"] + ["0"]*8
assert not safe["contains_pixel_data"] and not safe["contains_dma_contents"] and not safe["contains_iova_values"]

ev = safe["events"]
assert ev[:4] == ["E008F EV CDM804","E008F EV IFE804","E008F EV CALL_A_SELECTOR2","E008F EV BATCH 0 COUNT=4"]
assert ev[14:23] == [f"E008F EV BUS_SET ID={x} ARG=1" for x in one]
assert ev[23:33] == [f"E008F EV ADDR ID={i} ARG={a}" for i,a in zip(cfg,["0","1"]+["0"]*8)]
assert ev[33:38] == ["E008F EV CALL_A_SELECTOR2","E008F EV BATCH 1 COUNT=6",
                     "E008F EV CSID_START_CALL","E008F EV ISP_START_DONE",
                     "E008F EV CALL_B_SELECTOR2"]
assert bfr["BF_resource_ID"] == "0x300d"

dis = subprocess.check_output(["llvm-objdump","-d","--start-address=0x140024900",
                               "--stop-address=0x140024930",str(DRV)], text=True)
assert re.search(r"140024918:.*mov\s+w1, #0x2", dis)
assert re.search(r"14002491c:.*bl\s+0x140028480", dis)
dis2 = subprocess.check_output(["llvm-objdump","-d","--start-address=0x140025eb0",
                                "--stop-address=0x140025ed0",str(DRV)], text=True)
assert re.search(r"140025ec4:.*mov\s+w1, #0x2", dis2)
assert re.search(r"140025ec8:.*bl\s+0x140028480", dis2)

assert (E/"RESULT.json").exists()
assert res["status"] == "PASS" and res["bf_resource_id"] == "0x300d"
print("E008f VERIFY PASS")
