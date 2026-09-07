#!/usr/bin/env python3
from pathlib import Path
import hashlib, subprocess, sys

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert DLL.is_file(), DLL
assert hashlib.sha256(DLL.read_bytes()).hexdigest()==SHA

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True)
def need(text,*ss):
    for s in ss: assert s in text,s

def run_verify(rel,script,marker):
    p=BASE/rel/script
    cp=subprocess.run([sys.executable,str(p)],cwd=p.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    if cp.returncode:
        raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout,(rel,marker,cp.stdout)

# runMetering: external callback +0x30 receives output object controller+0x14b38.
# RunMeteringPostprocess logs/uses seven outputs at x2+0x38..+0x68 => controller+0x14b70..+0x14ba0.
meter=dis(0x180374700,0x180374748)
need(meter,
    '180374714:', 'add\tx2, x26, #0xb38',
    '180374720:', 'ldr\tx8, [x0, #0x30]',
    '180374734:', 'blr\tx15')
assert 0x14B38+0x38==0x14B70
assert 0x14B70+6*8==0x14BA0

# True CAECXControl::runConvergence is 0x180374ab8; the normal path constructs
# controller+0x14ca0 and calls the pre-convergence arbitration bridge.
conv=dis(0x180374E8C,0x180375180)
need(conv,
    '180374e98:', 'add\tx22, x19, #0x14, lsl #12',
    '180374e9c:', 'add\tx8, x22, #0xca0',
    '180374ee8:', 'add\tx24, x8, #0xb70',
    '180374ef0:', 'add\tx2, x9, #0x660',
    '180374ef8:', 'mov\tx1, x24',
    '180374efc:', 'bl\t0x180389dd0',
    '180374f04:', 'str\tx0, [x8, #0xca8]',
    '180374f0c:', 'ldr\tx8, [x8, #0x5d0]',
    '180374f10:', 'str\tx8, [x22, #0xca0]',
    '180374f18:', 'add\tx9, x8, #0xcb0',
    '180374f24:', 'ldp\tq17, q16, [x24]',
    '180374f28:', 'stp\tq17, q16, [x9]',
    '180374f2c:', 'ldr\tq16, [x24, #0x20]',
    '180374f30:', 'str\tq16, [x9, #0x20]',
    '180374f34:', 'ldr\tx8, [x24, #0x30]',
    '180374f38:', 'str\tx8, [x9, #0x30]',
    '180375150:', 'add\tx1, x8, #0xca0',
    '180375154:', 'add\tx2, x9, #0xcf8',
    '180375158:', 'ldr\tx8, [x0, #0xb0]')
assert 0x14000+0xCA0==0x14CA0
assert 0x14000+0xCA8==0x14CA8
assert 0x14000+0xCB0==0x14CB0
assert 0x14000+0xCF8==0x14CF8
assert 0x14CB0+6*8==0x14CE0

# Pre-convergence bridge: RunControlArbitration(w4=1), copy seven 0x50 target
# records, return child+0x688. That returned pointer is controller+0x14ca8.
bridge=dis(0x180389DD0,0x180389F14)
need(bridge,
    '180389de0:', 'mov\tw4, #0x1',
    '180389dec:', 'bl\t0x180388910',
    '180389df4:', 'add\tx8, x19, #0x688',
    '180389e14:', 'ldp\tq17, q16, [x8]',
    '180389ea8:', 'ldp\tq17, q16, [x0, #0x360]',
    '180389efc:', 'add\tx0, x19, #0x688')
assert [0x688+0x50*i for i in range(7)] == [0x688,0x6D8,0x728,0x778,0x7C8,0x818,0x868]

# Core RunConvProcesss consumes x1 as a real structure and x2 as output.
core=dis(0x1803B38C0,0x1803B3F20)
need(core,
    '1803b3904:', 'str\tx2, [sp, #0xd8]',
    '1803b3908:', 'mov\tx23, x1',
    '1803b3ddc:', 'ldp\tx8, x9, [x23, #0x18]',
    '1803b3e60:', 'ldr\tx8, [x23, #0x20]')

# The caller executes post-convergence RunControlArbitration(w4=0) using the exact
# compact output controller+0x14cf8.
post=dis(0x180372390,0x1803723E8)
need(post,
    '1803723c0:', 'mov\tw4, #0x0',
    '1803723c8:', 'add\tx1, x22, #0xcf8',
    '1803723d0:', 'bl\t0x180388910',
    '1803723d8:', 'mov\tw2, #0x3c0',
    '1803723e0:', 'add\tx0, x8, #0xda8')
assert 0x14000+0xDA8==0x14DA8

# AR's exact RunArbitration layout identity: input child+0xd0, base at input+0x198,
# coordinates at input+0x138/+0x160. AQ consumes the resulting desired exposure.
assert 0xD0+0x198==0x268
assert 0xD0+0x138==0x208
assert 0xD0+0x160==0x230

# Fresh joins: upstream measured-luma->SI + no-op metering modifier; temporal
# convergence/history; T681 coordinate/table; final linear output; sensor submit/runtime.
for rel,script,marker in [
 ('be-windows-aec-antibanding-noop','verify-be.py','BE_VERIFY=PASS'),
 ('bd-windows-aec-target-analyzer-si','verify-bd.py','BD_VERIFY=PASS'),
 ('ax-windows-aec-convergence-history-loop','verify-ax.py','AX_VERIFY=PASS'),
 ('ar-windows-aec-exposure-coordinate','verify-ar.py','AR_VERIFY=PASS'),
 ('aq-windows-aec-arbitration-table','verify-aq.py','AQ_VERIFY=PASS'),
 ('bc-windows-aec-single-exposure-output','verify-bc.py','BC_VERIFY=PASS'),
 ('aw-windows-sensor-request-submit','verify-aw.py','AW_VERIFY=PASS'),
 ('ap-bounded-imx681-control-runtime','verify.py','AP_VERIFY=PASS'),
]: run_verify(rel,script,marker)

print('DLL_SHA256='+SHA)
print('METERING_OUTPUT=controller+0x14b70..0x14ba0 (7 qwords)')
print('CONV_INPUT_OBJECT=controller+0x14ca0')
print('CONV_INPUT_FRAMEID=+0x00')
print('CONV_INPUT_PREARB_RECORDS=+0x08 -> child+0x688 (7x0x50)')
print('CONV_INPUT_TARGETS=+0x10..+0x40 <- controller+0x14b70..0x14ba0')
print('RUNCONV_OUTPUT=controller+0x14cf8')
print('POSTCONV_ARBITRATION=RunControlArbitration(w4=0)')
print('T681_BASE_FIELD=RunArbitrationInput+0x198=child+0x268')
print('END_TO_END_STATIC_JOIN=BD+BE+AX+AR+AQ+BC+AW+AP PASS')
print('OPTICAL_FRAME_MAPPING=NOT_EXTENDED_BEYOND_AW_SCOPE')
print('BF_VERIFY=PASS')
