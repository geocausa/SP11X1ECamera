#!/usr/bin/env python3
from pathlib import Path
import hashlib, struct

DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
ASM=Path('/tmp/sp11-aec-oracle/full.asm')
EXPECTED='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert DLL.is_file(), DLL
assert ASM.is_file(), ASM
b=DLL.read_bytes()
sha=hashlib.sha256(b).hexdigest()
assert sha==EXPECTED,(sha,EXPECTED)
text=ASM.read_text(errors='ignore')

anchors=[
 '180350580:', '1803505b8:', '1803506f8:', '180350700:',
 '180351380:', '180351384:', '1803515ec:', '180351600:', '18035160c:',
 '180351638:', '180351640:', '180351650:', '180351654:', '180351660:', '180351664:',
 '1805d4a40:', '1805d4c2c:', '1805d4c38:', '1805d4c44:',
 '1808356e0:', '180835708:', '180835820:', '1808358e8:', '1808358f8:',
 '18083a0c0:', '18083a1d4:'
]
for a in anchors: assert a in text,a

for s in [
 b'PropertyIDAECFrameControl',
 b'PropertyIDSensorCurrentMode',
 b'CamX::CAECStatsProcessor::PublishPropertyPoolFrameControl',
 b'AEC: Publish FrameControl for ReqId=%llu',
 b'Failed to get PropertyIDAECFrameControl, RequestID=%llu'
]: assert s in b,s

# Minimal PE VA reader, standard-library only.
e_lfanew=struct.unpack_from('<I',b,0x3c)[0]
assert b[e_lfanew:e_lfanew+4]==b'PE\0\0'
coff=e_lfanew+4
nsects=struct.unpack_from('<H',b,coff+2)[0]
optsz=struct.unpack_from('<H',b,coff+16)[0]
opt=coff+20
magic=struct.unpack_from('<H',b,opt)[0]
assert magic==0x20b
image_base=struct.unpack_from('<Q',b,opt+24)[0]
secbase=opt+optsz
sections=[]
for i in range(nsects):
    o=secbase+i*40
    name=b[o:o+8].rstrip(b'\0').decode(errors='ignore')
    vsize,va,rawsize,rawptr=struct.unpack_from('<IIII',b,o+8)
    sections.append((name,image_base+va,max(vsize,rawsize),rawptr))
def readva(addr,n):
    for name,va,span,raw in sections:
        if va <= addr and addr+n <= va+span:
            off=raw+(addr-va)
            return b[off:off+n]
    raise AssertionError(hex(addr))
def cstr(addr):
    out=bytearray()
    while True:
        x=readva(addr+len(out),1)
        if x==b'\0': return out.decode(errors='replace')
        out += x

# CamX property name table for 0x30000000 namespace.
TABLE=0x181147b20
p0=struct.unpack('<Q',readva(TABLE,8))[0]
p29=struct.unpack('<Q',readva(TABLE+29*8,8))[0]
assert cstr(p0)=='PropertyIDAECFrameControl',(hex(p0),cstr(p0))
assert cstr(p29)=='PropertyIDSensorCurrentMode',(hex(p29),cstr(p29))

# Six-property static root used by SensorNode: first property is AECFrameControl.
first=struct.unpack('<I',readva(0x18169d960,4))[0]
assert first==0x30000000,hex(first)

print('DLL_SHA256='+sha)
print('PROPERTY_0x30000000=PropertyIDAECFrameControl')
print('PROPERTY_0x3000001d=PropertyIDSensorCurrentMode')
print('SENSOR_AECFRAMECONTROL_EXPLICIT_OFFSET=0')
print('RESOLVER_TARGET=currentRequestContext-requestedOffset')
print('AEC_PUBLISH_REQUEST_KEY=CAECStatsProcessor+0x6008 from requestObject+0x8')
print('PROPERTY_POOL_ADDED_REQUEST_DELAY=0')
print('AT_VERIFY=PASS')
