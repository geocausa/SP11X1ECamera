#!/usr/bin/env python3
from pathlib import Path
import hashlib, importlib.util, subprocess, sys, struct

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert DLL.is_file()
assert hashlib.sha256(DLL.read_bytes()).hexdigest()==SHA

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True)
def req(t,*ss):
    for s in ss: assert s in t,s

def load_model():
    p=HERE/'windows-single-exposure-output.py'
    spec=importlib.util.spec_from_file_location('bcmodel',p); m=importlib.util.module_from_spec(spec)
    sys.modules[spec.name]=m; spec.loader.exec_module(m); return m

# ConvergeSensorExposures entry and count=1 setup.
c=dis(0x1803d13f0,0x1803d1898)
req(c,
 '1803d141c:', 'ldr\td20, [x19, #0xa0]',
 '1803d142c:', 'mov\tw20, #0x1',
 '1803d1448:', 'str\td20, [x19, #0x100]',
 '1803d144c:', 'ldr\tw8, [x19, #0x4b4]',
 '1803d1468:', 'cmp\tw8, #0x4',
 '1803d146c:', 'csel\tw9, w8, w25, lo',
 '1803d1470:', 'cmp\tw20, w9',
 '1803d1474:', 'b.hs\t0x1803d14f8')
# For active count=1: min(count,4)=1 and w20 starts at 1, so the multi-exposure loop is skipped.
assert min(1,4)==1 and 1>=min(1,4)
# The count=1 fill path uses +0x100 as source and replicates to +108,+110,+118.
req(c,
 '1803d1574:', 'add\tw8, w20, #0x3',
 '1803d1580:', 'add\tx11, x10, #0x1c',
 '1803d1584:', 'ldr\td16, [x19, x11, lsl #3]',
 '1803d1598:', 'str\td16, [x19, x10, lsl #3]')
# With w20=1: source index (1+3)+0x1c = 0x20 => +0x100;
# destinations are +0x108,+0x110,+0x118 for the remaining 3 slots.
assert (1+3+0x1c)*8==0x100
assert tuple((0x21+i)*8 for i in range(3))==(0x108,0x110,0x118)
# Final internal s1-s4 are copied into normal output-lane slots and converted for x1 output.
req(c,
 '1803d1788:', 'ldr\td1, [x19, #0x100]', '1803d1790:', 'str\td1, [x19, #0xb8]',
 '1803d17a4:', 'ldr\td1, [x19, #0x108]', '1803d17a8:', 'str\td1, [x19, #0xc0]',
 '1803d17bc:', 'ldr\td1, [x19, #0x110]', '1803d17c0:', 'str\td1, [x19, #0xc8]',
 '1803d17d4:', 'ldr\td1, [x19, #0x118]', '1803d17d8:', 'str\td1, [x19, #0xd0]')
for a in ('1803d1794:','1803d17ac:','1803d17c4:','1803d17dc:'):
    assert a in c
for off in ('#0x18]','#0x20]','#0x28]','#0x30]'):
    assert off in c

# RunConvProcesss calls ConvergeSensorExposures then back-edges to common output path.
r=dis(0x1803b66c0,0x1803b6810)
req(r,
 '1803b67d4:', 'bl\t0x1803d2150',
 '1803b67e4:', 'bl\t0x1803d13f0',
 '1803b67e8:', 'mov\tw8, #0x1',
 '1803b67ec:', 'str\tw8, [x23, #0x88]',
 '1803b67f0:', 'b\t0x1803b6080')
outblock=dis(0x1803b6080,0x1803b6408)
req(outblock,'1803b63e8:','ldr\tx1, [sp, #0xd8]','1803b63ec:','mov\tx0, x22',
    '1803b63f0:','bl\t0x1803cdf50')

# PopulateOutput converts all 7 final log lanes, in Short/Long/Safe/s1/s2/s3/s4 order.
p=dis(0x1803cdf50,0x1803ce040)
loads=[0xa0,0xa8,0xb0,0xb8,0xc0,0xc8,0xd0]
stores=[None,0x8,0x10,0x18,0x20,0x28,0x30]
for off in loads: assert f'ldr\td1, [x19, #0x{off:x}]' in p
for off in stores:
    if off is None: assert 'str\tx8, [x20]' in p
    else: assert f'str\tx8, [x20, #0x{off:x}]' in p
assert p.count('bl\t0x180cee718')>=7
assert p.count('fcvtzu\tx8, d0')>=7
# Exact base literal used by both ConvergeSensorExposures and PopulateOutput.
raw=subprocess.check_output(['llvm-objdump','-s','--start-address=0x1803ce3f8','--stop-address=0x1803ce400',str(DLL)],text=True)
# Direct PE read verifies the literal value, avoiding formatting dependence.
b=DLL.read_bytes(); e=struct.unpack_from('<I',b,0x3c)[0]; coff=e+4; ns=struct.unpack_from('<H',b,coff+2)[0]; os=struct.unpack_from('<H',b,coff+16)[0]; opt=coff+20; image=struct.unpack_from('<Q',b,opt+24)[0]; sb=opt+os
lit=None
for i in range(ns):
    o=sb+i*40; vs,rva,rs,rp=struct.unpack_from('<IIII',b,o+8); va=image+rva
    if va<=0x1803ce3f8<va+max(vs,rs):
        q=b[rp+(0x1803ce3f8-va):rp+(0x1803ce3f8-va)+8]; lit=struct.unpack('<d',q)[0]; break
assert lit==1.0299999713897705,lit

# Offline semantic model.
m=load_model()
x=m.SevenLogLanes(100.0,105.0,102.0,11.0,22.0,33.0,44.0)
y=m.converge_single_exposure(x)
assert y.tuple()==(100.0,105.0,102.0,100.0,100.0,100.0,100.0)
z=m.populate_output(y)
assert len(z)==7 and z[0]==z[3]==z[4]==z[5]==z[6]
assert z[1]!=z[0] and z[2]!=z[0]

# Mechanical join to already-closed downstream stages. These are static/offline/evidence verifiers only.
def run(rel, script, marker):
    q=BASE/rel/script
    cp=subprocess.run([sys.executable,str(q)],cwd=q.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode!=0: raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,(rel,cp.stdout)

run('ax-windows-aec-convergence-history-loop','verify-ax.py','AX_VERIFY=PASS')
run('aq-windows-aec-arbitration-table','verify-aq.py','AQ_VERIFY=PASS')
run('av-windows-imx681-sensor-delay','verify-av.py','AV_VERIFY=PASS')
run('aw-windows-sensor-request-submit','verify-aw.py','AW_VERIFY=PASS')
run('ap-bounded-imx681-control-runtime','verify.py','AP_VERIFY=PASS')

print('DLL_SHA256='+SHA)
print('FUNCTION=CAECXConvergence::ConvergeSensorExposures@0x1803d13f0')
print('ACTIVE_EXPOSURE_COUNT=1')
print('COUNT1_INTERNAL_LOGS=Short,Long,Safe,Short,Short,Short,Short')
print('POPULATE_OUTPUT=CAECXConvergence::PopulateOutput@0x1803cdf50')
print('LINEARIZATION=FCVTZU(pow(1.0299999713897705,logExposure))')
print('RUNCONV_BACKEDGE=ConvergeSensorExposures->0x1803b6080->PopulateOutput')
print('DOWNSTREAM_JOIN=AX+Aq+AV+AW+AP PASS'.replace('Aq','AQ'))
print('BC_VERIFY=PASS')
