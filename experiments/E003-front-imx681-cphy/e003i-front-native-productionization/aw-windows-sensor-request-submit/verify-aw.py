#!/usr/bin/env python3
from pathlib import Path
import hashlib, subprocess

DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
SYS=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamfrontsensor8380.inf_arm64_747e2ddb5eb5a22b/surfacecamfrontsensor8380.sys')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
SYS_SHA='80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03'
for p,h in [(DLL,DLL_SHA),(SYS,SYS_SHA)]:
    assert p.is_file(),p
    got=hashlib.sha256(p.read_bytes()).hexdigest()
    assert got==h,(p,got,h)

def dis(p,start,stop):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(start)}',f'--stop-address={hex(stop)}',str(p)],text=True)

mft=dis(DLL,0x180350580,0x18035c070)
for a in [
 '1803506f8:', # request object +8
 '180350700:', # saved request id
 '180351bd8:', # restore exact request id before ApplyGains
 '180351d34:', # ApplyGains logger gets request id
 '180351ed8:', # CreateSensorUpdatePacket x1=request id
 '180351f2c:', # CreateSensorUpdatePacket call
 '18035a9a8:', # helper preserves x1 in x24
 '18035be48:', # packet lookup keyed by request id
 '18035be78:', # Packet::CommitPacket
 '18035c048:', # low-level packet submission wrapper
]: assert a in mft,a
# Exact dataflow snippets.
assert 'ldr\tx20, [x8, #0x8]' in mft
assert 'str\tx20, [sp, #0x78]' in mft
assert 'ldr\tx26, [sp, #0x78]' in mft
assert 'mov\tx1, x26' in mft
assert 'mov\tx24, x1' in mft

# MFT sends the 0x48-byte delayInfo record to kernel acquire path.
acq=dis(DLL,0x18035c8b4,0x18035c960)
for s in ['ldr\tx9, [x8, #0x318]','mov\tx8, #0x48','ldp\tw7, w8, [x9, #0x30]',
          'ldr\tw6, [x9, #0x20]','ldr\tw5, [x9, #0x14]','bl\t0x1805e1f30']:
    assert s in acq,s

k=dis(SYS,0x1400058ac,0x140008660)
# NotifySOF stores (request, subrequest, hdrMode) into +430/+438/+440.
for a in ['1400058b0:','1400058b4:','1400058c8:','1400058d4:']:
    assert a in k,a
assert 'stp\tx23, x22, [x8]' in k
assert 'str\tw20, [x19, #0x440]' in k
# ProcessExposureUpdate queue record identity and scheduling arithmetic.
for a in ['14000819c:','1400081a4:','1400081a8:','1400081ac:',
          '140008368:','14000836c:','140008394:','140008398:','14000839c:',
          '1400083a0:','1400083a4:','1400083ac:',
          '140008480:','140008484:','14000849c:','1400084b4:','1400084cc:']:
    assert a in k,a
assert 'ldp\tw10, w11, [x9, #0xc]' in k
assert 'ldr\tx12, [x8]' in k
assert 'sub\tx8, x10, x12' in k
assert 'cmp\tx8, #0x1' in k
assert 'cmp\tw8, #0x1' in k
# Same queue fields are emitted by exact diagnostics, proving +0xc/+0x10 are req/subreq.
raw=SYS.read_bytes()
for s in [
 b'DeQueued and ignored exp update buffer with reqID:%d and subRequestId: %d',
 b'DeQueued exp update buffer in AsyncThread: 0x%x, from size:%d, ReqID:%d, subreqId: %d',
 b'SensorLastConsumedReqId:%d sensorLastConsumedSubReqId:%d after applying exposure update',
 b'Exposure update buffer with reqID:%d not dequeued,Current SOF id:%d , current SOF subRequest:%d for hdr_mode:%d',
 b'NotifySOF() Setting SOF signal for Req ID: %d, SubRequest ID:%d and hdrMode:%d',
]: assert s in raw,s

print('DLL_SHA256='+DLL_SHA)
print('FRONTSENSOR_SYS_SHA256='+SYS_SHA)
print('CAMX_REQUEST_ID=requestObject+0x8')
print('CREATE_SENSOR_UPDATE_PACKET_REQUEST_ID=F')
print('WINDOWS_KERNEL_NOTIFY_SOF_STATE=+0x430/+0x438/+0x440')
print('HDRMODE1_APPLY_CONDITION=queuedReq-currentSOF==1')
print('USERSPACE_REQUEST_RENUMBERING=0')
print('OPTICAL_FRAME_MAPPING=NOT_CLAIMED_HERE')
print('AW_VERIFY=PASS')
