#!/usr/bin/env python3
from pathlib import Path
import hashlib, subprocess

DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert DLL.is_file()
assert hashlib.sha256(DLL.read_bytes()).hexdigest()==SHA

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True)

def req(txt,*ss):
    for s in ss:
        assert s in txt,s

# F-1 history lookup and seven current-exposure seeds.
c=dis(0x1803b46f0,0x1803b49c0)
req(c,
 '1803b4700:', 'mov\tw1, #0x1', 'bl\t0x1803d3938',
 'ldr\tx8, [x24, #0x28]', 'ldr\tx8, [x24, #0x50]',
 'ldr\tx8, [x24, #0x78]', 'ldr\tx8, [x24, #0xa0]',
 'ldr\tx8, [x24, #0xc8]', 'ldr\tx8, [x24, #0xf0]',
 'ldr\tx8, [x24, #0x118]')
# Current arbitration-derived target qwords are the other side of convergence.
for off in (0x10,0x18,0x20,0x28,0x30,0x38,0x40):
    assert f'ldr\tx8, [x23, #0x{off:x}]' in c

# PopulateOutput converts seven internal converged log exposures to seven compact qwords.
p=dis(0x1803cdf50,0x1803ce180)
for off in (0xa0,0xa8,0xb0,0xb8,0xc0,0xc8,0xd0):
    assert f'[x19, #0x{off:x}]' in p
for off in (0x0,0x8,0x10,0x18,0x20,0x28,0x30):
    # first slot can be [x20] rather than +0
    if off==0: assert '[x20]' in p
    else: assert f'[x20, #0x{off:x}]' in p

# runConvergence: pre-convergence arbitration bridge populates target lanes,
# then external +0xb0 RunConvProcesss writes compact result at +14cf8.
rc=dis(0x180374e90,0x180375180)
req(rc,
 '180374ef0:', 'add\tx2, x9, #0x660', '180374efc:', 'bl\t0x180389dd0',
 '180375150:', 'add\tx1, x8, #0xca0', '180375154:', 'add\tx2, x9, #0xcf8',
 '180375158:', 'ldr\tx8, [x0, #0xb0]')

# Bridge helper itself is a pre-convergence RunControlArbitration(w4=1),
# followed by seven 0x50 copies into child+688..868.
b=dis(0x180389dd0,0x180389f14)
req(b,'mov\tw4, #0x1','bl\t0x180388910')
for off in (0x688,0x6d8,0x728,0x778,0x7c8,0x818,0x868):
    assert f'#0x{off:x}' in b

# Main normal frame ordering: runConvergence, then post-convergence
# RunControlArbitration(w4=0) with x1=controller+14cf8; copy its 0x3c0 rich
# result into controller+14da8.
o=dis(0x1803722c0,0x180372400)
req(o,
 '1803722d4:', 'bl\t0x180374ab8',
 '1803723c4:', 'mov\tw4, #0x0',
 '1803723c8:', 'add\tx1, x22, #0xcf8',
 '1803723d0:', 'bl\t0x180388910',
 '1803723d8:', 'mov\tw2, #0x3c0',
 '1803723e0:', 'add\tx0, x8, #0xda8')

# Post-convergence RunControlArbitration: x1 is retained at child+668;
# selected compact lane qword becomes selected 0x28 record+0x18, and its
# log1.03 coordinate becomes selected record+0x10.
a=dis(0x180388938,0x18038a210)
req(a,
 '180388970:', 'stp\tx9, x1, [x8]',
 '18038a174:', 'ldr\tx8, [x19, #0x668]',
 '18038a17c:', 'ldr\tx8, [x8, x10, lsl #3]',
 '18038a180:', 'str\tx8, [x9, #0xf8]',
 '18038a1b4:', 'ldr\tx8, [x8, #0xf8]',
 '18038a1bc:', 'fdiv\ts16, s16, s8',
 '18038a1d4:', 'bl\t0x180cc2e98',
 '18038a1e0:', 'fmul\td16, d0, d16',
 '18038a1f4:', 'str\ts16, [x8, x19]')
# Geometry: child+e0 is array base; +f8 is record+18; (lane+6)*28 is +f0 = record+10.
assert 0xe0 + 0x18 == 0xf8
assert 6*0x28 == 0xf0
assert 0xf0 - 0xe0 == 0x10
assert 0x1f8 - 0xe0 == 7*0x28

# Core RunArbitration snapshots selected input record+0x18 into rich output+0x20.
ra=dis(0x1803b89f0,0x1803ba630)
req(ra,
 '1803b8af4:', 'stp\tx23, x26, [x19, #0x18]',
 '1803b8c60:', 'ldp\tx10, x9, [x19, #0x18]',
 '1803b8c70:', 'smaddl\tx8, w8, w22, x10',
 '1803b8c74:', 'ldp\tq17, q16, [x8, #0x10]',
 '1803b8c78:', 'stp\tq17, q16, [x9]',
 '1803b8c80:', 'str\tx8, [x9, #0x20]')
# Active BankIDArbitrationTable type 5 direct table path.
req(ra,'cmp\tw9, #0x5','b.eq\t0x1803ba5a4','1803ba5c0:','bl\t0x1803c35f8')
# ApplyCoreTable result scratch +0x18 is copied to rich output +0x20 by the
# 32-byte scratch+0..+0x1f -> rich+0x08..+0x27 block copy.
req(ra,'1803ba5d0:','ldp\tq17, q16, [sp, #0xa0]',
       '1803ba5d4:','add\tx9, x8, #0x8',
       '1803ba5d8:','stp\tq17, q16, [x9]')
assert 0xa0 + 0x18 == 0xb8
assert 0x08 + 0x18 == 0x20

# ApplyCoreTable normal table path reloads selected 0x28 record coordinate/exposure,
# and its final retained exposure quantity is FRINTA(gain*time*correction) at output+18.
t=dis(0x1803c3bd0,0x1803c4210)
req(t,
 '1803c3c20:', 'ldr\ts8, [x8, #0x10]',
 '1803c3c24:', 'ldr\tx25, [x8, #0x18]',
 '1803c4184:', 'fmul\td13, d16, d14',
 '1803c41c0:', 'str\ts8, [x20]',
 '1803c41c4:', 'str\tx25, [x20, #0x8]',
 '1803c41d4:', 'ldr\ts16, [x8, #0x24]',
 '1803c41e0:', 'fmul\td0, d16, d13',
 '1803c41e4:', 'bl\t0x1800014b0',
 '1803c41f0:', 'str\tx8, [x20, #0x18]')

# External runEndOfFrame callback gets compact result (+14cf8) and rich post-arb
# block (+14da8); x5 is the rich block.
e=dis(0x1803772e0,0x180377340)
req(e,
 '180377308:', 'add\tx5, x10, #0xda8',
 '18037730c:', 'add\tx4, x9, #0xcf8',
 '18037731c:', 'ldr\tx8, [x0, #0x48]')
# Adapter +0x48 ultimately forwards wrapper vtable +0xc0 = runEndOfFrame.
ad=dis(0x1803a7e90,0x1803a7ec8)
req(ad,'ldr\tx8, [x8, #0xc0]')

# runEndOfFrame converts seven rich 0x88 records to seven 0x28 history records.
reof=dis(0x1803bd2e0,0x1803bd3e8)
req(reof,
 '1803bd2f4:', 'add\tx9, x5, #0x8',
 '1803bd31c:', 'ldp\tq17, q16, [x5, #0x90]',
 '1803bd344:', 'add\tx9, x5, #0x118',
 '1803bd360:', 'ldp\tq17, q16, [x5, #0x1a0]',
 '1803bd388:', 'add\tx9, x5, #0x228',
 '1803bd3a4:', 'ldp\tq17, q16, [x5, #0x2b0]',
 '1803bd3cc:', 'add\tx9, x5, #0x338')
# The copied third qword is always source-block +0x20 -> history-block +0x20.
for a in ('1803bd30c:','1803bd32c:','1803bd350:','1803bd370:',
          '1803bd394:','1803bd3b4:','1803bd3d8:'):
    assert a in reof
# mechanical relation: history read field = rich record +20.
for i in range(7):
    rich=0x20+i*0x88
    hist=0x28+i*0x28
    assert hist == 0x10+i*0x28+0x18
    assert rich == 0x8+i*0x88+0x18

print('DLL_SHA256='+SHA)
print('HISTORY_LOOKBACK=F-1')
print('LANES=7')
print('PRECONV_ARBITRATION=RunControlArbitration(w4=1)')
print('CONVERGENCE_OUTPUT=controller+0x14cf8')
print('POSTCONV_ARBITRATION=RunControlArbitration(w4=0)')
print('POSTCONV_RICH_OUTPUT=controller+0x14da8')
print('SELECTED_COMPACT_EXPOSURE_TO_RECORD_PLUS18=PASS')
print('SELECTED_LOG1P03_COORDINATE_TO_RECORD_PLUS10=PASS')
print('TYPE5_TABLE_CONSUMES_SELECTED_RECORD=PASS')
print('HISTORY_RETAINED_EXPOSURE=richRecord+0x20')
print('RECURRENCE=history(F-1)->convergence(F)->table/arbitration(F)->history(F)')
print('AX_VERIFY=PASS')
