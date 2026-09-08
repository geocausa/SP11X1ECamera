#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, struct, subprocess, sys
import pefile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
TUNING=Path('/tmp/sp11-aec-oracle/com.surface.tuned.ffc_imx681.bin')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
TUNING_SHA='2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d'
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
assert TUNING.is_file() and hashlib.sha256(TUNING.read_bytes()).hexdigest()==TUNING_SHA
sys.path.insert(0,str(REPO/'tools'))
import qti_parameter_bin as qti

def fresh(rel,script,marker):
    p=BASE/rel/script
    cp=subprocess.run([sys.executable,str(p)],cwd=p.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode:
        raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,(rel,marker,cp.stdout)

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True,stderr=subprocess.DEVNULL)

def line_has(t,addr,*parts):
    key=f'{addr:x}:'
    ls=[x for x in t.splitlines() if key in x]
    assert len(ls)==1,(hex(addr),ls)
    for p in parts: assert p in ls[0],(hex(addr),p,ls[0])

def fbits(x): return struct.unpack('<I',struct.pack('<f',x))[0]

# Retain the exact method-11 implementation and all of BY's transitive
# default-candidate/topology checks fresh.
fresh('by-native-aec-method11-point-aggregation','verify-by.py','BY_VERIFY=PASS')

obj=qti.parse(TUNING); ids={e['id']:e for e in obj['entries']}
ab=bytes.fromhex(ids[3592]['raw_hex']); assert len(ab)==52*0x8c
recs={}
for i in range(52):
    w=struct.unpack('<35I',ab[i*0x8c:(i+1)*0x8c]); recs[w[0]]=w

def name(aid): return ids[recs[aid][4]]['text']
def comp(aid,off): return recs[aid][off:off+8]
def ops(aid):
    r=recs[aid]; n,ref=r[31],r[32]
    b=bytes.fromhex(ids[ref]['raw_hex']); assert len(b)==n*0xd0
    return [struct.unpack('<52I',b[i*0xd0:(i+1)*0xd0]) for i in range(n)]
def operand(o,k): return o[3+11*k:3+11*(k+1)]
def out(o): return o[47:52]
def desc(o):
    e=ids[o[51]]; assert e['name']=='description' and e['payload_size']==o[50]
    return e['text']

def fixed1(x):
    return x[0]==0 and x[1]==0x3f800000
def db(x,bank,data,fallback=None):
    ok=x[0]==1 and (x[2],x[3])==(bank,data)
    if fallback is not None: ok = ok and x[1]==fbits(fallback)
    return ok

# Serialized arithmetic layout is exactly 0xd0:
# 3 u32 header + 4 * 11-u32 operands + 5-u32 output descriptor.
# All 964 operand records use only the three runtime input methods 0/1/2,
# and each operand's symbol-reference field points to trigger1Data.
method_counts={0:0,1:0,2:0}; op_count=0
for aid,r in recs.items():
    for o in ops(aid):
        op_count += 1
        assert len(o)==52 and o[0] in (0,1) and o[2] <= 15
        for k in range(4):
            x=operand(o,k); assert len(x)==11 and x[0] in method_counts
            method_counts[x[0]] += 1
            assert x[9] in ids and ids[x[9]]['name']=='trigger1Data'
        assert len(out(o))==5
        assert out(o)[4] in ids and ids[out(o)[4]]['name']=='description'
assert op_count==241,op_count
assert method_counts=={0:438,1:434,2:92},method_counts
assert 3*4 + 4*(11*4) + 5*4 == 0xd0
# Runtime expansion is 0x108: aligned 16-byte header, four 0x38 operands,
# and a 0x18 output.  A compact 32-bit symbol reference expands to a pointer.
assert 0x10 + 4*0x38 + 0x18 == 0x108

# Exact scoped records.  The Frame record is an independent semantic anchor:
# target component is bank3:data5, luma component is bank3:data4, and its
# phase-2 DIV publishes AdjRatio at bank3:data7.
frame=ops(2)[0]
assert name(2)=='FrameSA' and frame[:3]==(1,2,3) and desc(frame)=='AdjRatio'
assert comp(2,15)[3:5]==(3,5) and comp(2,7)[3:5]==(3,4)
assert fixed1(operand(frame,0)) and db(operand(frame,1),3,5,0.0)
assert fixed1(operand(frame,2)) and db(operand(frame,3),3,4,0.0)
assert out(frame)[:3]==(3,7,0)

safe=ops(3)[2]
assert name(3)=='SafeAggSA' and safe[:3]==(1,2,2) and desc(safe)=='AdjRatio'
assert db(operand(safe,0),3,8,0.0)
assert all(fixed1(operand(safe,k)) for k in (1,2,3))
assert out(safe)[:3]==(3,9,0)

short_ops=ops(4); short=short_ops[4]
assert name(4)=='ShortAggSA' and short[:3]==(1,2,3) and desc(short)=='AdjRatio'
assert desc(short_ops[1])=='ADRCGain' and out(short_ops[1])[:2]==(3,67)
assert db(operand(short,0),3,9,0.0) and fixed1(operand(short,1))
assert db(operand(short,2),3,67,1.0) and fixed1(operand(short,3))
assert out(short)[:3]==(3,11,0)

long_ops=ops(5); long=long_ops[6]
assert name(5)=='LongAggSA' and long[:3]==(1,2,2) and desc(long)=='AdjRatio'
assert desc(long_ops[2])=='DarkBoostGain' and out(long_ops[2])[:2]==(3,69)
assert db(operand(long,0),3,9,0.0) and fixed1(operand(long,1))
assert db(operand(long,2),3,69,1.0) and fixed1(operand(long,3))
assert out(long)[:3]==(3,13,0)

# DLL operation-name table.  The AEC context constructor stores its base at
# +0x118; enum indices 0..15 are therefore mechanically named.
pe=pefile.PE(str(DLL),fast_load=True); image=DLL.read_bytes(); image_base=pe.OPTIONAL_HEADER.ImageBase
def off_va(va): return pe.get_offset_from_rva(va-image_base)
def qword(va): return struct.unpack_from('<Q',image,off_va(va))[0]
def cstr(va):
    o=off_va(va); e=image.index(b'\0',o); return image[o:e].decode('ascii')
expected_names=[
 'ADD::(AxB)+(CxD)','SUB::(AxB)-(CxD)','MUL::(AxB)x(CxD)','DIV::(AxB)/(CxD)',
 'MAX(AXB, CXD)','MIN(AXB, CXD)','Smallest','SecondSmallest','Largest','SecondLargest',
 'FlashHighLuma','LinearInterpolation','CondLarger','CondSmaller','CondEqual','Sqrt']
assert [cstr(qword(0x18169dac0+i*8)) for i in range(16)]==expected_names
ctor=dis(0x1803a9700,0x1803a9718)
line_has(ctor,0x1803a9708,'adrp','0x18169d000')
line_has(ctor,0x1803a970c,'add','0xac0')
line_has(ctor,0x1803a9710,'str','[x21, #0x118]')

# The analyzer's context object gets vtable 0x1813383b8.  Slot +0x58 is the
# exact arithmetic executor 0x1803c8e10.
vctor=dis(0x1803a9420,0x1803a9434)
line_has(vctor,0x1803a9424,'adrp','0x181338000')
line_has(vctor,0x1803a9428,'add','0x3b8')
line_has(vctor,0x1803a9430,'str','[x21]')
assert qword(0x1813383b8+0x58)==0x1803c8e10

# CAnalyzer phase helper walks the parsed arithmetic array at tuning +0xb8,
# checks enabled (+0) and phase (+4), advances exactly 0x108, and invokes
# context virtual slot +0x58 with the record pointer as x1.
run=dis(0x1803f0d08,0x1803f0da4)
line_has(run,0x1803f0d10,'ldr','[x8, #0xb0]')
line_has(run,0x1803f0d20,'ldr','[x8, #0xb8]')
line_has(run,0x1803f0d24,'add','x1, x8, x22')
line_has(run,0x1803f0d28,'ldr','[x8, x22]')
line_has(run,0x1803f0d30,'ldr','[x1, #0x4]')
line_has(run,0x1803f0d70,'ldr','[x19, #0x30]')
line_has(run,0x1803f0d7c,'ldr','[x8, #0x58]')
line_has(run,0x1803f0d9c,'add','x22, x22, #0x108')

# Executor shape: four 0x38 operands at +10/+48/+80/+b8; each selector is
# operand+0x30.  Same record's enum is read at +8.  Runtime output descriptor
# is bank +f0, dataID +f4, mode +f8, description pointer +100.
exe=dis(0x1803c8e44,0x1803c8f20)
for a,off in [(0x1803c8e6c,0x10),(0x1803c8e88,0x48),(0x1803c8ea4,0x80),(0x1803c8ec0,0xb8)]:
    line_has(exe,a,'add',f'#{hex(off)}')
for a,off in [(0x1803c8e58,0x40),(0x1803c8e78,0x78),(0x1803c8e94,0xb0),(0x1803c8eb0,0xe8)]:
    line_has(exe,a,'ldr',f'#{hex(off)}')
line_has(exe,0x1803c8ecc,'ldr','[x20, #0xf0]')
line_has(exe,0x1803c8f10,'ldr','[x20, #0xf4]')
enumdis=dis(0x1803c8f80,0x1803c905c)
line_has(enumdis,0x1803c8f8c,'ldrb','[x20, #0x8]')
line_has(enumdis,0x1803c9048,'ldr','[x8]')
line_has(enumdis,0x1803c9050,'cmp','#0xf')
outdis=dis(0x1803c9e28,0x1803c9e48)
line_has(outdis,0x1803c9e30,'ldr','[x20, #0xf8]')
line_has(outdis,0x1803c9e38,'ldr','[x20, #0x100]')
line_has(outdis,0x1803c9e3c,'ldp','[x20, #0xf0]')

# UtilGetOperand: method u32 at +0, method 0 returns fixed float +4; method 1
# performs a DB read using descriptor +8; method 2 has its own trigger path.
getop=dis(0x1803c9f70,0x1803ca310)
line_has(getop,0x1803c9f7c,'ldr','[x19]')
line_has(getop,0x1803c9f80,'cbz','0x1803ca2f4')
line_has(getop,0x1803c9f84,'cmp','#0x1')
line_has(getop,0x1803c9f88,'b.eq','0x1803ca164')
line_has(getop,0x1803c9f8c,'cmp','#0x2')
line_has(getop,0x1803c9f90,'b.eq','0x1803ca020')
line_has(getop,0x1803ca170,'add','x1, x19, #0x8')
line_has(getop,0x1803ca174,'bl','0x1803d5d30')
line_has(getop,0x1803ca2e4,'cmp','w25, #0x2')
line_has(getop,0x1803ca2e8,'fcsel')
line_has(getop,0x1803ca2f8,'ldr','[x19, #0x4]')

# Arithmetic dispatch verifies the first four operation names against actual
# f32 instruction bodies; method 2 is multiply, method 3 is division.
sw=dis(0x1803c906c,0x1803c92a4)
line_has(sw,0x1803c906c,'fmul'); line_has(sw,0x1803c9074,'fmul'); line_has(sw,0x1803c907c,'fadd')
line_has(sw,0x1803c911c,'fmul'); line_has(sw,0x1803c9124,'fmul'); line_has(sw,0x1803c912c,'fsub')
line_has(sw,0x1803c91cc,'fmul'); line_has(sw,0x1803c91d4,'fmul'); line_has(sw,0x1803c91dc,'fmul')
line_has(sw,0x1803c927c,'fmul'); line_has(sw,0x1803c9288,'fmul'); line_has(sw,0x1803c929c,'fdiv')

# Critical terminology correction.  CAnalyzer searches for enabled phase-2
# arithmetic output, reads that float, and if positive uses it directly as the
# adjustment ratio.  Only if absent/nonpositive does it fall back to target/luma.
# It then multiplies the ratio by the source exposure (d8) and FCVTZU to qword.
si=dis(0x1803f1608,0x1803f16c0)
line_has(si,0x1803f1614,'ldr','[x13, #0xb0]')
line_has(si,0x1803f161c,'ldr','[x13, #0xb8]')
line_has(si,0x1803f1620,'mov','x11, #0x108')
line_has(si,0x1803f1628,'ldr','[x15]')
line_has(si,0x1803f1634,'ldr','[x15, #0x4]')
line_has(si,0x1803f1638,'cmp','#0x2')
line_has(si,0x1803f1668,'ldp','[x8, #0xf0]')
line_has(si,0x1803f1680,'fcmpe','s9, #0.0')
line_has(si,0x1803f1688,'fmov','s16, s9')
line_has(si,0x1803f1694,'ldr','[x19, #0x10]')
line_has(si,0x1803f16a4,'ldr','[x19, #0x18]')
line_has(si,0x1803f16a8,'fdiv')
line_has(si,0x1803f16b4,'fmul','d16, d16, d8')
line_has(si,0x1803f16b8,'fcvtzu')

print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('SERIAL_ARITH_LAYOUT=0xd0=header12+4*operand44+output20')
print('RUNTIME_ARITH_LAYOUT=0x108=header16+4*operand56+output24')
print('OPERAND_METHOD_COUNTS=0:438,1:434,2:92')
print('OPERATION_ENUM=0:ADD,1:SUB,2:MUL,3:DIV,4:MAX,5:MIN,6:Smallest,7:SecondSmallest,8:Largest,9:SecondLargest,10:FlashHighLuma,11:LinearInterpolation,12:CondLarger,13:CondSmaller,14:CondEqual,15:Sqrt')
print('FRAME_ADJRATIO=3:7=(3:5)/(3:4)')
print('SAFE_ADJRATIO=3:9=3:8')
print('SHORT_ADJRATIO=3:11=(3:9)/(3:67 ADRCGain)')
print('LONG_ADJRATIO=3:13=(3:9)*(3:69 DarkBoostGain)')
print('BANK3_7_9_11_13_SEMANTIC=AdjRatio-float-publication-not-qword-SI')
print('CAnalyzer_QWORD_SI=sourceExposure*AdjRatio then FCVTZU')
print('BZ_VERIFY=PASS')
