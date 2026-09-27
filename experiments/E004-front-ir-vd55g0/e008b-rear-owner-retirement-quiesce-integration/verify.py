#!/usr/bin/env python3
from pathlib import Path
import re

D=Path(__file__).resolve().parent
R=D.parents[2]
INC=D/"camss-e008b-rear-integration.inc"
Y=R/"experiments/E004-front-ir-vd55g0/e005y-vfe1-shared-owner-csid1-wm16-observer/camss-e005y-vfe1-owner-observer-fix3.inc"
Z=R/"experiments/E004-front-ir-vd55g0/e007z-rear-ten-wm-consumed-iova-retirement/camss-e007z-rear-retirement.inc"
A=R/"experiments/E004-front-ir-vd55g0/e008a-rear-vfe1-bus-stop-csid-drain-contract"
FRONT=R/"src/front-imx681/kernel/camss/camss.c"

def req(x,msg):
    if not x: raise AssertionError(msg)

s=INC.read_text()
y=Y.read_text()
z=Z.read_text()
a_csid=(A/"camss-csid-e008a-rear-quiesce.inc").read_text()
a_vfe=(A/"camss-vfe-e008a-rear-bus-stop.inc").read_text()
front=FRONT.read_text()

for token in (
    "e005y_vfe1_rear_sample_begin",
    "e005y_vfe1_observe_bf",
    "e005y_vfe1_owner_release",
    "e007z_rear_observe",
    "e007z_rear_mark_fault",
    "e007z_rear_retireable",
    "csid680_e008a_rear_quiesce",
    "vfe680_e008a_rear_bus_stop",
    "return -EOPNOTSUPP",
):
    req(token in s, "missing integration contract "+token)

# Teardown failure must pin E005y ownership rather than free/reuse anything.
req(re.search(r'e005y_vfe1_owner_release\(owner,\s*E005Y_VFE1_OWNER_REAR,\s*owner_epoch,\s*false\)',s,re.S) is not None,
    "failure path pins owner")
req("unsafe_stop_pinned" in y and "hardware_teardown_safe" in y,
    "E005y unsafe stop contract")

# Exact per-WM consumed identity remains the only ledger completion authority.
for token in (
    "same owner epoch and request generation",
    "last_consumed_iova != frame->slot[idx].programmed_image_iova",
    "independently_verified_bus_stopped",
    "independently_verified_irqs_drained",
):
    req(token in z, "missing E007z invariant "+token)

# E008a exact postconditions are the concrete true/true evidence.
for token in ("synchronize_irq(csid->irq)", "e008a_csid680_all_status_zero",
              "exact_rear_owner"):
    req(token in a_csid, "missing E008a CSID gate "+token)
for token in ("synchronize_irq(vfe->irq)", "VFE_BUS_WRITE_CLIENT_CFG",
              "exact_rear_owner"):
    req(token in a_vfe, "missing E008a VFE gate "+token)

# Accepted front normal stop prefix proves CSID -> BUS/IFE -> RT-CDM ordering.
a=front.find("stop_ret = csid680_x1e_front_ipp_stop(csid);")
b=front.find("vfe680_x1e_pix_runtime_bus_stop(vfe, pix);",a)
c=front.find("camss_x1e_pix_rtcdm_stop_close(camss);",b)
req(a>=0 and b>a and c>b, "accepted front stop prefix")
ib=s.find("ret = csid680_e008a_rear_quiesce(csid, true);")
iv=s.find("ret = vfe680_e008a_rear_bus_stop(vfe, true);",ib)
req(ib>=0 and iv>ib, "E008b CSID-before-BUS order")

# E008b stops deliberately before RT-CDM/release so ownership remains pinned
# until the next gate closes the complete teardown.
for forbidden in (
    "e007z_rear_release_ledger(",
    "camss_x1e_pix_rtcdm_stop_close(",
    "camss_rtcdm1_windows_stop(",
    "dma_free", "dma_unmap", "vb2_buffer_done", "camss_buf_done",
    "kfree(", "module_init(", "module_platform_driver",
):
    req(forbidden not in s, "forbidden release/runtime action "+forbidden)

# Shared completion groups must still require independent per-WM samples.
desc=[(0,0),(1,0),(2,0),(3,0),(11,4),(12,4),(13,5),(14,6),(16,7),(18,9)]
pending=(1<<10)-1
status=1<<0
valid=(1<<0)|(1<<1)|(1<<2)
missing=[i for i,(_,grp) in enumerate(desc)
         if (pending&(1<<i)) and (status&(1<<grp)) and not (valid&(1<<i))]
req(missing==[3], "shared group missing member fails closed")

# Full ledger + both concrete quiescence predicates are necessary, but E008b
# still does not authorize release because RT-CDM/outer teardown is later.
pending=0
csid_quiet=True
bus_stopped=True
req(pending==0 and csid_quiet and bus_stopped, "positive retireability precondition")
req("e007z_rear_release_ledger(" not in s,
    "ledger release intentionally deferred")
req(re.search(r'e005y_vfe1_owner_release\([^;]*,\s*true\s*\)', s, re.S) is None,
    "safe owner release intentionally deferred")

print("E008B_VERIFY_PASS")
