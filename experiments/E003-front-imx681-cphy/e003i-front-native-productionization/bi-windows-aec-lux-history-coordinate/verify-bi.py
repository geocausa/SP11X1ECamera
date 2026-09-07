#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, math, re, struct, subprocess, sys

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
AB2=BASE/'ab-clean-lux-reconstruction'/'E003I-AB2-LUX-OPERANDS.log'
AB2_SHA='dd28cfef64fa46e67577617857b1209c8d7dd6293513ff43e682fdfacdfbf5ad'
AQ=BASE/'aq-windows-aec-arbitration-table'/'TABLE681.fixture.json'
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
assert AB2.is_file() and hashlib.sha256(AB2.read_bytes()).hexdigest()==AB2_SHA

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True)
def need(t,*xs):
    for x in xs: assert x in t,x

def fresh(rel,script,marker):
    p=BASE/rel/script
    cp=subprocess.run([sys.executable,str(p)],cwd=p.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode: raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,(rel,marker,cp.stdout)

def f32(x): return struct.unpack('<f',struct.pack('<f',float(x)))[0]
def bits(x): return struct.unpack('<I',struct.pack('<f',f32(x)))[0]
def from_bits(b): return struct.unpack('<f',struct.pack('<I',b))[0]

# Fresh upstream closures: BH fixes the 0x10 payload header, AX fixes the
# selected convergence-record coordinate and rich/history propagation, AR/AQ
# fix the active table base and log1.03 coordinate family.
fresh('bh-native-aec-request-state','verify-bh.py','BH_VERIFY=PASS')
fresh('ax-windows-aec-convergence-history-loop','verify-ax.py','AX_VERIFY=PASS')
fresh('ar-windows-aec-exposure-coordinate','verify-ar.py','AR_VERIFY=PASS')

# RunControl builds the selected lane from compact convergence output, then
# exposure/base -> double log -> shared reciprocal-log(1.03f) -> float coord.
rc=dis(0x18038a138,0x18038a200)
need(rc,
 '18038a138:','str\tx8, [x19, #0x268]',
 '18038a174:','ldr\tx8, [x19, #0x668]',
 '18038a17c:','ldr\tx8, [x8, x10, lsl #3]',
 '18038a180:','str\tx8, [x9, #0xf8]',
 '18038a1b4:','ldr\tx8, [x8, #0xf8]',
 '18038a1bc:','fdiv\ts16, s16, s8',
 '18038a1d4:','bl\t0x180cc2e98',
 '18038a1d8:','ldr\ts16, [x21, #0xa10]',
 '18038a1e0:','fmul\td16, d0, d16',
 '18038a1e4:','fcvt\ts16, d16',
 '18038a1f4:','str\ts16, [x8, x19]')
# Geometry proved by AX: selected array starts child+e0, stride 28; +10 coord.
assert 0xf8-0xe0==0x18
assert 0xf0-0xe0==0x10

# Core snapshots selected +0x10 coordinate into rich +0x18 as part of the
# 32-byte selected-input block copied to output+0x08.
core=dis(0x1803b8c60,0x1803b8c84)
need(core,
 '1803b8c74:','ldp\tq17, q16, [x8, #0x10]',
 '1803b8c78:','stp\tq17, q16, [x9]')
assert 0x08 + (0x10) == 0x18  # selected +10 maps to rich +18

# runEndOfFrame copies rich+8..+2f to a saved lane.  Therefore rich+18 maps
# to lane+10. BH proves payload has a separate 0x10-byte header.
eof=dis(0x1803bd2e8,0x1803bd320)
need(eof,'1803bd2ec:','mov\tx9, #0x10b8','1803bd2f4:','add\tx9, x5, #0x8',
          '1803bd304:','ldp\tq17, q16, [x9]')
assert (0x18-0x08)==0x10

# Algorithm001 uses PipelineDelay history, converts its configured selector to
# an internal lane, then reads payload + 0x28*lane + 0x20.  With the payload
# header this is exactly saved-lane +0x10.
a1=dis(0x1803fb8f8,0x1803fba38)
need(a1,
 '1803fb8fc:','ldrb\tw1, [x0, #0x8ec]', '1803fb904:','bl\t0x1803d3938',
 '1803fb90c:','ldr\tw0, [x8, #0x1c]', '1803fb914:','bl\t0x180388630',
 '1803fb9c8:','mov\tx23, #0x28', '1803fba2c:','smaddl\tx8, w20, w23, x22',
 '1803fba30:','ldr\ts10, [x8, #0x20]')
assert 0x20-0x10==0x10

# Live AB2 pins the ordinary front selector to internal lane 3, and the already
# proven enum-to-string helper names internal lane 3 S1.
log=AB2.read_text(errors='replace')
need(log,'AB2_TABLE','w20=00000003','s10=               229.675 (0:086:65acdd)',
         '000002c0`268ff3b8  3f800000`4365acdd',
         '000002c0`268ff3c0  01fc4ec3 00000000 00000019 00000000')
name=dis(0x1803885b0,0x180388628)
need(name,'1803885ec:','add\tx0, x8, #0x62c') # internal 3 -> "S1"
# Read the string itself from the pinned image via known rdata mapping.
b=DLL.read_bytes(); off=0xf7c800+((0x1813ad62c-0x180000000)-0xf7e000)
assert b[off:off+3]==b'S1\0'

# Active T681 base is 1.0 * 37516 * correction 1.0 = 37516.
aq=json.loads(AQ.read_text())
k0=aq['decoded_knees'][0]
assert k0=={'increment_priority':1,'gain_f32':1.0,'exposure_time_ns':37516}
assert aq['tuned_blob']['correction_factor_f32']==1.0
base=37516

# Live selected S1 history block: coordinate bits 4365acdd sit at lane+10,
# retained linear exposure 01fc4ec3 sits at lane+18.  Their analytical
# log1.03 relation rounds to the exact live coordinate float.
exposure=0x01fc4ec3
coord_bits=0x4365acdd
one03=from_bits(0x3f83d70a)
analytic=math.log(float(exposure)/float(base))/math.log(float(one03))
assert bits(analytic)==coord_bits,(analytic,hex(bits(analytic)))
assert abs(from_bits(coord_bits)-analytic)<1e-5

print('DLL_SHA256='+DLL_SHA)
print('AB2_SHA256='+AB2_SHA)
print('ALGORITHM001_HISTORY_LANE=3:S1')
print('HISTORY_REFERENCE=F-3 S1 convergence-derived log1.03 exposure coordinate')
print('PROPAGATION=selected+0x10 -> rich+0x18 -> saved-lane+0x10 -> Algorithm001')
print(f'T681_BASE={base}')
print(f'AB2_S1_LINEAR_EXPOSURE={exposure}')
print(f'AB2_S1_COORD_BITS=0x{coord_bits:08x}')
print('AB2_ANALYTIC_LOG103_ROUNDTRIP=PASS')
print('BI_VERIFY=PASS')
