#!/usr/bin/env python3
from pathlib import Path
import hashlib, subprocess

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert DLL.is_file()
assert hashlib.sha256(DLL.read_bytes()).hexdigest()==SHA

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True)
def req(t,*ss):
    for s in ss:
        assert s in t,s

# Re-run CI so this checkpoint stays joined to the current native recurrence.
ci=BASE/'ci-native-aec-default-request-recurrence'/'verify-ci.py'
cp=subprocess.run([str(ci)],cwd=ci.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
assert cp.returncode==0,(cp.stdout,cp.stderr)
assert 'CI_VERIFY=PASS' in cp.stdout

# Manager per-request update obtains the retained-history record through the
# mode-selected history offset byte at ModeInfo+0x8ec.
u=dis(0x1803e3998,0x1803e3f30)
req(u,
 '1803e3a54:', 'ldrb\tw21, [x0, #0x8ec]',
 '1803e3a98:', 'bl\t0x1803d3938',
 '1803e3b94:', 'ldr\tx8, [x19, #0x28]',
 '1803e3b9c:', 'ldr\tx27, [x19, #0x50]',
 '1803e3ba8:', 'ldr\tx26, [x19, #0x78]',
 '1803e3bb0:', 'ldr\tx25, [x19, #0xa0]',
 '1803e3bbc:', 'ldr\tx23, [x19, #0xc8]',
 '1803e3bc8:', 'ldr\tx24, [x19, #0xf0]',
 '1803e3bd4:', 'ldr\tx21, [x19, #0x118]')

# Exact retained-history lane -> AnalyzerManager source-vector materialization.
req(u,
 '1803e3e8c:', 'ldr\tx9, [x20, #0x18]',
 '1803e3e90:', 'ucvtf\td17, x8',
 '1803e3ea0:', 'stp\td17, d16, [x9, #0x20]',
 '1803e3ea4:', 'ucvtf\td17, x26',
 '1803e3ea8:', 'ucvtf\td16, x25',
 '1803e3eac:', 'stp\td17, d16, [x9, #0x30]',
 '1803e3eb4:', 'ucvtf\td17, x23',
 '1803e3eb8:', 'stp\td17, d16, [x9, #0x40]',
 '1803e3ec0:', 'str\td16, [x9, #0x50]')
# Mechanical lane geometry: +20 Short,+28 Long,+30 Safe,+38 S1,+40 S2,+48 S3,+50 S4.
assert [0x20+8*i for i in range(7)] == [0x20,0x28,0x30,0x38,0x40,0x48,0x50]
assert [0x28+0x28*i for i in range(7)] == [0x28,0x50,0x78,0xa0,0xc8,0xf0,0x118]

# Manager hands state+0x20 straight to CAnalyzer::RunAnalyzer.
m=dis(0x1803b25e0,0x1803b2680)
req(m,'1803b2660:', 'add\tx1, x19, #0x20',
      '1803b2668:', 'bl\t0x1803f0ef8')

# RunAnalyzer maps sourceType and selects lane*8. Ordinary final analyzers use
# sourceType S1=3 (BD); lane 3 from vector+0x20 is state+0x38 above.
r=dis(0x1803f15d8,0x1803f1620)
req(r,
 '1803f15e0:', 'ldr\tw0, [x19, #0x2c]',
 '1803f15f0:', 'bl\t0x180388630',
 '1803f15f4:', 'add\tx20, x20, w0, sxtw #3',
 '1803f15fc:', 'ldr\td8, [x20]')
assert 0x20 + 3*8 == 0x38

# AX independently identifies the same retained-history lane geometry used by
# convergence and runEndOfFrame. Fresh-run it as the persistence cross-check.
ax=BASE/'ax-windows-aec-convergence-history-loop'/'verify-ax.py'
cp=subprocess.run([str(ax)],cwd=ax.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
assert cp.returncode==0,(cp.stdout,cp.stderr)
assert 'AX_VERIFY=PASS' in cp.stdout

print('DLL_SHA256='+SHA)
print('HISTORY_SELECTOR=ModeInfo+0x8ec (constant value deferred)')
print('HISTORY_LANES=Short@28,Long@50,Safe@78,S1@a0,S2@c8,S3@f0,S4@118')
print('MANAGER_SOURCE_VECTOR=state+20..50 as f64 uint64 conversions')
print('SOURCE_TYPE_S1=lane3 -> state+0x38 -> retained history S1@+0xa0')
print('SOURCE_S1_NOT_INDEPENDENT_REQUEST_INPUT=PASS')
print('CJ_VERIFY=PASS')
