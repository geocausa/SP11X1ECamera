#!/usr/bin/env python3
from pathlib import Path
import hashlib, struct

DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
ASM=Path('/tmp/sp11-aec-oracle/full.asm')
BLOB=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamfrontsensor_extension8380.inf_arm64_5a4c66ce4812274e/com.surface.sensormodule.ffc_imx681.bin')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
BLOB_SHA='f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c'
for p in (DLL,ASM,BLOB): assert p.is_file(),p

dll=DLL.read_bytes(); blob=BLOB.read_bytes(); asm=ASM.read_text(errors='ignore')
assert hashlib.sha256(dll).hexdigest()==DLL_SHA
assert hashlib.sha256(blob).hexdigest()==BLOB_SHA
assert blob.startswith(b'QTI Chromatix Header')
assert b'Parameter Parser V3.4.0' in blob

# Chromatix V3.4 descriptor table for this exact blob.
# Header points at the serialized data segment. Descriptors start at 0xc0,
# are 0x38 bytes each, and carry {parent/type, dataOffset, dataSize, id, name[40]}.
DATA_START=struct.unpack_from('<I',blob,0xb8)[0]
DATA_SIZE=struct.unpack_from('<I',blob,0xbc)[0]
assert DATA_START==0x298b4 and DATA_SIZE==0xa464
assert DATA_START+DATA_SIZE==0x33d18
BASE=0xc0; STRIDE=0x38

def desc(rid):
    o=BASE+(rid-1)*STRIDE
    a,doff,size,got=struct.unpack_from('<IIII',blob,o)
    assert got==rid,(rid,got)
    name=blob[o+16:o+56].split(b'\0',1)[0].decode(errors='replace')
    raw=blob[DATA_START+doff:DATA_START+doff+size]
    assert len(raw)==size
    return {'id':rid,'name':name,'doff':doff,'size':size,'raw':raw}

# The delayType element is the generated 52-byte record parsed by 0x18087ff50.
d=desc(0xb94)
assert d['name']=='delayType' and d['size']==52
words=list(struct.unpack('<13I',d['raw']))
assert words==[1,0xb94,1,0xb95,1,0xb96,1,0xb97,2,0,0,0,0xb98],words

# Serialized child references are zero-based node-table indices. The descriptor
# IDs in the blob are one-based, so index N resolves to descriptor ID N+1.
def scalar_ref(index):
    x=desc(index+1)
    assert x['size']==4,(index,x['name'],x['size'])
    return struct.unpack('<I',x['raw'])[0]

# Exact generated parser layout (0x18087ff50):
#   +0x00 presence / +0x08 first optional scalar
#   +0x0c presence / +0x14 linecount
#   +0x18 presence / +0x20 gain
#   +0x24 presence / +0x2c frameLengthLines
#   +0x30 maxPipeline (direct dword)
#   +0x34 frameSkip   (direct dword)
assert words[0]==1
selector=scalar_ref(words[1])
assert words[2]==1; linecount=scalar_ref(words[3])
assert words[4]==1; gain=scalar_ref(words[5])
assert words[6]==1; fll=scalar_ref(words[7])
max_pipeline=words[8]; frame_skip=words[9]
assert selector==0
assert (linecount,gain,fll,max_pipeline,frame_skip)==(2,2,2,2,0), (linecount,gain,fll,max_pipeline,frame_skip)

# Generated delay-record parser anchors: child values to +14/+20/+2c, then
# direct maxPipeline/frameSkip dwords to +30/+34.
anchors=[
 '18087ff50:',
 '18087ff70:', '18087ff7c:', '18087ff88:', '18087ff94:', '18087ffa0:',
 '1808801c8:', '1808801cc:',
 '1808802bc:', '1808802c0:',
 '1808803b0:', '1808803b4:',
 '1808803dc:', '180880404:',
 '180880414:', '180880448:',
 # SensorNode runtime field-use / equality skip logic.
 '18035a2c0:', '18035a2ec:', '18035a2f4:', '18035a2f8:', '18035a2fc:',
 '18035a348:', '18035a350:', '18035a354:', '18035a358:', '18035a35c:',
 '18035a3c8:', '18035a3d0:', '18035a3d4:', '18035a3d8:', '18035a3dc:',
 # Kernel diagnostic pulls linecount/gain/maxPipeline/frameSkip from same record.
 '18035c910:', '18035c918:', '18035c91c:', '18035c920:'
]
for a in anchors: assert a in asm,a
for s in [
 b'CamX::SensorNode::HandleDelayInfo',
 b'Sensor Delay Info sent to Kernel: linecount = %d, gain = %d, maxPipeline = %d, frameSkip = %d.'
]: assert s in dll,s

# With every exposure-control delay equal to maxPipeline, each HandleDelayInfo
# branch takes its >= skip and never enters maxPipeline-fieldDelay history lookup.
assert linecount==max_pipeline and gain==max_pipeline and fll==max_pipeline

print('DLL_SHA256='+DLL_SHA)
print('IMX681_BLOB_SHA256='+BLOB_SHA)
print(f'DELAY_SELECTOR={selector}')
print(f'LINECOUNT_DELAY={linecount}')
print(f'GAIN_DELAY={gain}')
print(f'FLL_DELAY={fll}')
print(f'MAX_PIPELINE={max_pipeline}')
print(f'FRAME_SKIP={frame_skip}')
print('HANDLE_DELAY_HISTORY_REALIGN=0')
print('IMX681_SENSOR_DELAY_FRAMES=2')
print('AV_VERIFY=PASS')
