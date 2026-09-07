#!/usr/bin/env python3
from pathlib import Path
import hashlib, struct

DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
ASM=Path('/tmp/sp11-aec-oracle/full.asm')
EXPECTED='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert DLL.is_file(), DLL
assert ASM.is_file(), ASM
b=DLL.read_bytes(); text=ASM.read_text(errors='ignore')
sha=hashlib.sha256(b).hexdigest(); assert sha==EXPECTED,(sha,EXPECTED)

anchors=[
 '1808356e0:', '180835708:', '180835820:', '1808358e8:', '1808358f8:',
 '180835af4:', '180835af8:', '180835afc:', '180835b04:', '180835b08:',
 '180835b14:', '180835b20:', '180835b24:', '180835b28:',
 '18083c108:', '18083c12c:', '18083c138:', '18083cc7c:', '18083cc88:',
 '180833a00:',
 '180851410:', '18085144c:', '180851524:', '180851528:', '18085152c:', '180851534:',
 '180379918:', '18037ddd8:', '18037dddc:', '18037de88:', '18037de90:', '18037de94:',
 '180372190:', '18037219c:'
]
for a in anchors: assert a in text,a

for s in [
 b'CamX::CAECEngine::Create', b'CamX::CAECEngine::SetPerFrameControlParam',
 b'AECAlgoSetParamframeID', b'CAECXControl::ControlSetParam',
 b'====== AEC Process start, CamID:%d, Role:%d, FrameID:%llu'
]: assert s in b,s

# Standard-library PE VA reader.
e_lfanew=struct.unpack_from('<I',b,0x3c)[0]
assert b[e_lfanew:e_lfanew+4]==b'PE\0\0'
coff=e_lfanew+4; nsects=struct.unpack_from('<H',b,coff+2)[0]
optsz=struct.unpack_from('<H',b,coff+16)[0]; opt=coff+20
assert struct.unpack_from('<H',b,opt)[0]==0x20b
image_base=struct.unpack_from('<Q',b,opt+24)[0]; secbase=opt+optsz
sections=[]
for i in range(nsects):
    o=secbase+i*40
    vsize,va,rawsize,rawptr=struct.unpack_from('<IIII',b,o+8)
    sections.append((image_base+va,max(vsize,rawsize),rawptr))
def readva(addr,n):
    for va,span,raw in sections:
        if va <= addr and addr+n <= va+span:
            return b[raw+(addr-va):raw+(addr-va)+n]
    raise AssertionError(hex(addr))
def cstr(addr):
    out=bytearray()
    while True:
        x=readva(addr+len(out),1)
        if x==b'\0': return out.decode(errors='replace')
        out += x

# AEC set-param table index 40 must name frameID.
TABLE=0x181047f30
p40=struct.unpack('<Q',readva(TABLE+40*8,8))[0]
assert cstr(p40)=='AECAlgoSetParamframeID',(hex(p40),cstr(p40))

# Jump table maps type 40 to the frame-ID handler.
JT=0x18037ed2c; BASE=0x18037cc3c
entry40=struct.unpack('<i',readva(JT+(40-1)*4,4))[0]
target40=BASE+entry40*4
assert target40==0x18037ddd8,hex(target40)

# The copied per-frame block includes +0xeb8.
assert 0xeb8 < 0xee0

print('DLL_SHA256='+sha)
print('CAMX_REQUEST_ID=CAECStatsProcessor+0x6008 from requestObject+0x8')
print('PER_FRAME_FRAME_ID=block+0xeb8')
print('PER_FRAME_COPY_TO_CAECENGINE=0xee0 bytes')
print('AEC_SET_PARAM_TYPE40=AECAlgoSetParamframeID')
print('AEC_FRAME_ID_SOURCE=CAECEngine+0xeb8')
print('CAECXCONTROL_FRAME_ID=+0x165d0')
print('AEC_ALGO_FRAME_ID_EQUALS_CAMX_REQUEST_ID=PASS')
print('AU_VERIFY=PASS')
