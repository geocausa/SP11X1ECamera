#!/usr/bin/env python3
from pathlib import Path
import json, struct
P=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/private/e006a/E006A-PRIVATE-SELECTED.json")
def req(x,msg):
    if not x: raise AssertionError(msg)
j=json.loads(P.read_text(encoding="utf-8-sig"))
rec={(x["n"],x["idx"]):bytes.fromhex(x["hex"]) for x in j["records"]}
change_vfe=struct.pack("<I",0x0800f000)
change_csid=struct.pack("<I",0x08057000)
extra=struct.pack("<III",0x04000001,0x00001e0c,0x00190004)
common=struct.pack("<IIII",0x03000002,0x0000035c,0x0fdf0000,0x08ed0000)
packet0=struct.pack("<15I",0x03000001,0x00000330,0x02000000,0x03000002,0x0000037c,0x00000001,0x00000000,0x03000002,0x0000035c,0x0fdf0000,0x08ed0000,0x03000002,0x00000384,0x0000001f,0x08ee0fe0)
req(rec[(0,2)]==change_csid,"packet0 CSID change")
req(rec[(0,3)]==packet0,"packet0 rear CSID companion")
for packet in (1,2,3):
    req(rec[(packet,0)]==change_vfe,f"packet{packet} VFE change")
    req(rec[(packet,2)]==extra,f"packet{packet} rear WM16 extra")
    req(rec[(packet,3)]==change_csid,f"packet{packet} CSID change")
    req(rec[(packet,4)]==common,f"packet{packet} common CSID crop")
    irq=struct.pack("<IIIII",0x04000001,0x00000018,0x01f501f5,0x06000000,packet)
    req(rec[(packet,5)]==irq,f"packet{packet} IRQ wrapper")
print("E007Y_PRIVATE_WRAPPER_IDENTITY_PASS")
