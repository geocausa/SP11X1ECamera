#!/usr/bin/env python3
from pathlib import Path
import hashlib, struct, subprocess, sys
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

def need(t,*xs):
    for x in xs: assert x in t,x

# Keep the exact method-11 implementation and candidate topology fresh.
fresh('by-native-aec-method11-point-aggregation','verify-by.py','BY_VERIFY=PASS')

obj=qti.parse(TUNING); ids={e['id']:e for e in obj['entries']}
ab=bytes.fromhex(ids[3592]['raw_hex']); assert len(ab)==52*0x8c
recs={}
for i in range(52):
    w=struct.unpack('<35I',ab[i*0x8c:(i+1)*0x8c]); recs[w[0]]=w

def name(aid): return ids[recs[aid][4]]['text']
def ops(aid):
    r=recs[aid]; n,ref=r[31],r[32]
    b=bytes.fromhex(ids[ref]['raw_hex']); assert len(b)==n*208
    return [struct.unpack('<52I',b[i*208:(i+1)*208]) for i in range(n)]

# ArithmeticOperator compact layout is: enabled, operand-count, op-enum,
# four 11-word operand descriptors, then a 5-word output descriptor.
# SafeAgg op2 is the final publication to bank3:data9.
safe=ops(3); assert name(3)=='SafeAggSA' and len(safe)==3
op=safe[2]
assert op[0:3]==(1,2,2),op[0:3]                 # enabled, 2 logical products, MUL
A=op[3:14]; B=op[14:25]; C=op[25:36]; D=op[36:47]; OUT=op[47:52]
# Operand method 1 = database; method 0 = fixed.  DB operand A is bank3:data8.
assert A[0]==1 and A[2:4]==(3,8),A
# Remaining operands are fixed +1.0f.
ONE=0x3f800000
for label,x in [('B',B),('C',C),('D',D)]:
    assert x[0]==0 and x[1]==ONE,(label,x)
assert OUT==(3,9,0,9,3711),OUT
assert ids[3711]['text']=='AdjRatio'

# DLL operation-name table gives the runtime enum identity directly.
pe=pefile.PE(str(DLL)); image=DLL.read_bytes(); imagebase=pe.OPTIONAL_HEADER.ImageBase
def raw_off(va):
    rva=va-imagebase
    for s in pe.sections:
        span=max(s.Misc_VirtualSize,s.SizeOfRawData)
        if s.VirtualAddress <= rva < s.VirtualAddress+span:
            return s.PointerToRawData+(rva-s.VirtualAddress)
    raise AssertionError(hex(va))
def cstr(va):
    off=raw_off(va); end=image.index(b'\0',off); return image[off:end].decode('ascii')
name_table=0x18169dac0
ptrs=struct.unpack_from('<16Q',image,raw_off(name_table))
names=[cstr(p) for p in ptrs]
expected=['ADD::(AxB)+(CxD)','SUB::(AxB)-(CxD)','MUL::(AxB)x(CxD)','DIV::(AxB)/(CxD)',
          'MAX(AXB, CXD)','MIN(AXB, CXD)','Smallest','SecondSmallest','Largest','SecondLargest',
          'FlashHighLuma','LinearInterpolation','CondLarger','CondSmaller','CondEqual','Sqrt']
assert names==expected,names
assert names[op[2]]=='MUL::(AxB)x(CxD)'

# RunOneArithMeticOperator reads enum at runtime +0x08 and dispatches through
# a 16-entry table.  Enum 2 resolves to 0x1803c91cc, where separate float32
# multiplies implement (A*B)*(C*D).
sel=dis(0x1803c9044,0x1803c906c)
need(sel,
     '1803c9048:', 'ldr\tw10, [x8]',
     '1803c9050:', 'cmp\tw10, #0xf',
     '1803c9068:', 'br\tx8')
rels=struct.unpack_from('<16i',image,raw_off(0x1803c9ecc))
assert rels==(-417,-373,-329,-285,-212,-170,-128,-64,0,47,105,152,232,282,332,385),rels
entry=0x1803c96f0+rels[2]*4
assert entry==0x1803c91cc,hex(entry)
mulbody=dis(entry,0x1803c91e0)
need(mulbody,
     '1803c91cc:', 'fmul\ts17, s14, s13',
     '1803c91d4:', 'fmul\ts16, s12, s11',
     '1803c91dc:', 'fmul\ts10, s17, s16')

# UtilGetOperand establishes the operand descriptor semantics used above.
# method 0 loads fixed float at +4; method 1 fetches DB addressing from +8.
getop=dis(0x1803c9f7c,0x1803ca320)
need(getop,
     '1803c9f7c:', 'ldr\tw8, [x19]',
     '1803c9f84:', 'cmp\tw8, #0x1',
     '1803c9f88:', 'b.eq\t0x1803ca164',
     '1803ca164:', 'ldr\tx0, [x20, #0x10]',
     '1803ca170:', 'add\tx1, x19, #0x8',
     '1803ca174:', 'bl\t0x1803d5d30',
     '1803ca2f8:', 'ldr\ts16, [x19, #0x4]',
     '1803ca300:', 'str\ts16, [x22]')

# Multiplication by exact +1.0f is bit-preserving for the finite target domain
# already scoped by BY, so final SafeAgg publication is the method-11 scalar.
print('DLL_SHA256='+DLL_SHA)
print('TUNING_SHA256='+TUNING_SHA)
print('OP_ENUM_2=MUL::(AxB)x(CxD)')
print('SAFEAGG_FINAL_OPERATOR=DB(3:8)*1.0*1.0*1.0 -> 3:9')
print('SAFEAGG_PUBLICATION_IDENTITY=3:9 == method11(3:8)')
print('RUNTIME_MUL_ENTRY=0x1803c91cc')
print('BZ_VERIFY=PASS')
