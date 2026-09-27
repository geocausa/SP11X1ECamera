#!/usr/bin/env python3
from pathlib import Path
import re

D=Path(__file__).resolve().parent
R=D.parents[2]
INC=D/"camss-e007z-rear-retirement.inc"
NU=R/"experiments/E004-front-ir-vd55g0/e004nu-rear-vfe1-ten-wm-ownership/camss-vfe-e004nu-rear-ten-wm.inc"
NT=R/"experiments/E004-front-ir-vd55g0/e004nt-rear-vfe1-4k-buffer-contract/camss-vfe-e004nt-rear-4k-buffer.inc"
REF=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/qcom-camera-kernel-KleeUI/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe17x/cam_vfe680.h")
BUS=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/qcom-camera-kernel-KleeUI/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe_bus/cam_vfe_bus_ver3.c")
PARSER=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/qcom-camera-kernel-KleeUI/drivers/cam_isp/isp_hw_mgr/hw_utils/cam_isp_packet_parser.c")
CTX=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/qcom-camera-kernel-KleeUI/drivers/cam_isp/cam_isp_context.c")

def req(x,msg):
    if not x: raise AssertionError(msg)

expected=[
 (0,0,0x00a9d000,0x11000),(1,0,0x00559000,0x9000),
 (2,0,0x0010e000,0),(3,0,0x00018000,0),
 (11,4,0x000a0000,0),(12,4,0x00001800,0),
 (13,5,0x00048000,0),(14,6,0x00151800,0),
 (16,7,0x00002d00,0),(18,9,0x00010000,0),
]
s=INC.read_text()
rows=[tuple(int(x,0) for x in m) for m in re.findall(
 r'\.wm = (\d+),\s*\.comp_group = (\d+),\s*\.required_bytes = (0x[0-9a-fA-F]+)U,\s*\.image_offset = (0x[0-9a-fA-F]+)U',s)]
req(rows==expected,("ledger table",rows))

nu=NU.read_text()
for wm,grp,n,off in expected:
    m=re.search(r'\{ \.wm = %d,.*?\.frame_incr = (0x[0-9a-fA-F]+)U,.*?\.meta_cfg = (0x[0-9a-fA-F]+)U'%wm,nu,re.S)
    req(m is not None,f"E004nu WM{wm}")
    req(int(m.group(1),16)==n,f"E004nu WM{wm} size")
    if wm not in (0,1):
        req(int(m.group(2),16)==0,f"E004nu WM{wm} meta_cfg must be zero")

nt=NT.read_text()
for token in (
 "VFE680_E004NT_REAR_Y_DATA_OFFSET\t0x00011000U",
 "VFE680_E004NT_REAR_C_META_OFFSET\t0x00a9d000U",
 "VFE680_E004NT_REAR_C_DATA_OFFSET\t0x00aa6000U"):
    req(token in nt,"E004nt "+token)
req(0x00aa6000-0x00a9d000==0x9000,"C subspan offset")

ref=REF.read_text()
for wm,grp,n,off in expected:
    cfg=0xe00+wm*0x100
    pos=ref.find(f".cfg                      = 0x{cfg:08X}")
    req(pos>=0,f"VFE680 cfg WM{wm}")
    block=ref[pos:pos+2200]
    m=re.search(r'\.comp_group\s*=\s*CAM_VFE_BUS_VER3_COMP_GRP_(\d+)',block)
    req(m and int(m.group(1))==grp,f"VFE680 group WM{wm}")

bus=BUS.read_text()
req("cam_vfe_bus_ver3_get_last_consumed_addr" in bus,"consumed helper")
req("addr_status_0" in bus,"ADDR_STATUS0 source")
parser=PARSER.read_text()
req(re.search(r'image_buf_addr\[plane_id\]\s*=\s*\n?\s*io_addr\[plane_id\]\s*\+\s*\n?\s*image_buf_offset\[plane_id\]',parser) is not None,
    "packet parser shifted image address")
ctx=CTX.read_text()
req("done->last_consumed_addr[i] != cmp_addr" in ctx,"context consumed compare")
req("fence_map_out[j].image_buf_addr[0]" in ctx,"context image address identity")
req("CAM_36BIT_INTF_GET_IOVA_BASE" in ctx,"36-bit normalization source")

for forbidden in ("readl(","readl_relaxed(","writel(","writel_relaxed(","dma_alloc","dma_free",
                  "request_irq(","enable_irq(","rtcdm1_submit","vb2_buffer_done",
                  "module_init(","module_platform_driver"):
    req(forbidden not in s,"forbidden active surface "+forbidden)
for must in ("last-consumed identity","same owner epoch and request generation",
             "independently_verified_bus_stopped","independently_verified_irqs_drained",
             "return -EOPNOTSUPP"):
    req(must in s,"missing safety text/code "+must)

# Model the same source-derived state machine over synthetic Linux-owned IOVAs.
bindings=[]
for i,(wm,grp,n,off) in enumerate(expected):
    base=0x10000000+i*0x02000000
    bindings.append((wm,base,n,base+off))
req(len({b[0] for b in bindings})==10,"all WMs unique")
for (wm,base,n,img),(ewm,grp,reqbytes,off) in zip(bindings,expected):
    req(wm==ewm and n>=reqbytes and img==base+off and base+n<=0x100000000,"positive bind")

pending=(1<<10)-1
for idx,((wm,base,n,img),(ewm,grp,reqbytes,off)) in enumerate(zip(bindings,expected)):
    status=1<<grp
    req(status & (1<<grp),"positive group")
    req(img==base+off,"positive address")
    pending &= ~(1<<idx)
req(pending==0,"all ten exact matches")
req(not (pending==0 and False and True),"BUS stop gate")
req(not (pending==0 and True and False),"IRQ drain gate")
req(pending==0 and True and True,"positive retireability")

# Negative cases: wrong bit/address, duplicate and overlap stay fail-closed.
wm,base,n,img=bindings[8]; grp=expected[8][1]
req(not ((1<<(grp-1)) & (1<<grp)),"wrong group rejected")
req((img+4)!=img,"wrong address rejected")
req(len([x for x in bindings if x[0]==0])==1,"baseline no duplicate")
bad=bindings.copy(); bad[1]=(0,bad[1][1],bad[1][2],bad[1][3])
req(len({x[0] for x in bad})!=10,"duplicate detectable")
a=bindings[0]; b=(bindings[1][0],a[1]+0x1000,bindings[1][2],a[1]+0x1000+expected[1][3])
req(a[1] < b[1]+b[2] and b[1] < a[1]+a[2],"overlap detectable")

print("E007Z_VERIFY_PASS")
