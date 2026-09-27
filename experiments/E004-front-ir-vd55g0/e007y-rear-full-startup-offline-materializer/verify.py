#!/usr/bin/env python3
from pathlib import Path
import json, subprocess, tempfile
D=Path(__file__).resolve().parent
R=D.parents[2]
INC=D/"camss-e007y-rear-startup.inc"
SAFE=D/"SAFE-STRUCTURE.json"
GEN=D/"generate-e007y.py"
def req(x,msg):
    if not x: raise AssertionError(msg)
with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    subprocess.run([str(GEN),"-o",str(td/"x.inc"),"--safe",str(td/"x.json")],check=True,stdout=subprocess.DEVNULL)
    req((td/"x.inc").read_bytes()==INC.read_bytes(),"generated include drift")
    req(json.loads((td/"x.json").read_text())==json.loads(SAFE.read_text()),"safe structure drift")
safe=json.loads(SAFE.read_text())
req(safe["classification"]=="OFFLINE_GENERATED_NO_WINDOWS_BYTES","classification")
req(safe["runtime_submission"] is False,"runtime submit policy")
req(len(safe["dmi_identity_union"])==18,"18 DMI identities")
expected=[[4,0xf1c,4,0x3c],[4,0xebc,0xc,4,0x10,0x14],[4,0xa00,0xc,4,0x10,0x14],[4,0x658,0xc,4,0x10,0x14]]
req(safe["wrapper_lengths"]==expected,"wrapper vectors")
z=json.loads((R/"experiments/E004-front-ir-vd55g0/e005z-windows-rear-rtcdm-topology-minimal/RESULT.json").read_text())
got=[[int(x,16) for x in row] for row in z["rear_startup_vectors"]]
req(got==expected,"E005z topology mismatch")
s=INC.read_text()
for forbidden in ("rtcdm1_submit","writel(","writel_relaxed(","readl(","module_init(","module_platform_driver","request_irq(","enable_irq(","dma_alloc","dma_free"):
    req(forbidden not in s,"forbidden runtime surface: "+forbidden)
for must in ("e007d_rear_fill_startup","e007v_rear_prepare_dynamic","e007v_rear_fill_slot","e007x_bhist16_startup_dmi","caller-supplied Linux-owned","e007y_rear_wrapper"):
    req(must in s,"missing integration "+must)
ns=(R/"experiments/E004-front-ir-vd55g0/e004ns-rear-csid1-ipp-offline/camss-csid-e004ns-rear-ipp.inc").read_text()
for token in ("0x02000000U","0x0fdf0000U","0x08ed0000U","0x0000001fU","0x08ee0fe0U"):
    req(token in ns and token in s,"rear CSID authority "+token)
nu=(R/"experiments/E004-front-ir-vd55g0/e004nu-rear-vfe1-ten-wm-ownership/camss-vfe-e004nu-rear-ten-wm.inc").read_text()
req("0x00190004U" in nu and "0x00190004U" in s,"WM16 image cfg0 authority")
csid=Path("/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src/drivers/media/platform/qcom/camss/camss-csid-gen3.c").read_text()
req("CSID_RUP_AUP_CMD" in csid and "0x18" in csid,"CSID RUP/AUP register authority")
req("struct e006g_rear_dynamic_payloads *dynamic;" in s,"caller-owned dynamic scratch")
req("struct e006g_rear_dynamic_payloads dyn;" not in s,"no large dynamic stack object")
print("E007Y_VERIFY_PASS")
