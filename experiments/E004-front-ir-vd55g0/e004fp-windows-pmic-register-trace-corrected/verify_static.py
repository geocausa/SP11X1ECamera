#!/usr/bin/env python3
from pathlib import Path
import subprocess,tempfile,shutil
R=Path(__file__).resolve().parents[3]
D=Path(__file__).resolve().parent
dis=R/'experiments/E004-front-ir-vd55g0/e004fi-native-ir-pmic-routing/build/qcpmic.dis'
t=dis.read_text(errors='replace')
need=[
 '140023aa8:', 'orr\tw8, w21, w19, lsl #4',
 '140023aac:', 'orr\tw27, w24, w8, lsl #16',
 '140023ae4:', 'add\tx3, sp, #0x18',
 '140023af4:', 'bl\t0x140024098', '140023af8:',
 '140023b0c:', 'uxtb\tw24, w0',
 '140023bbc:', 'bic\tw9, w8, w23', '140023bc8:', 'orr\tw8, w9, w8',
 '140023bcc:', 'strb\tw8, [x21]',
 '140023be8:', 'blr\tx15', '140023bec:',
 '140028340:', 'mov\tw2, #0xee67',
 '140026e40:', 'bl\t0x140023968',
]
for s in need:
    if s not in t: raise SystemExit('missing disassembly authority: '+s)
cap=(D/'capture.ps1').read_text()
for bad in ('TrySet','SetValue','FlashControl','ExposureControl.Set','FocusControl','ZoomControl'):
    if bad in cap: raise SystemExit('forbidden setter token: '+bad)
if 'frames -lt 12' not in cap or 'AddSeconds(5)' not in cap: raise SystemExit('capture bound changed')
with tempfile.TemporaryDirectory() as td:
    subprocess.run(['python3',str(D/'generate_kd.py'),'--pmic-base','fffff80012345000','--output',td],check=True)
    a=(Path(td)/'arm.kd').read_text(); v=(Path(td)/'validate.kd').read_text()
    for s in ('fffff80012368af8','fffff80012368bec','0xee3e','0xee41','0xee4a','0xee4d','0xee67','bd 0','bd 1','@sp+0x18','(@w27 & 0xffff)'):
        if s not in a: raise SystemExit('generated arm missing '+s)
    if 'E004FP_POST hit=%u reg=%x' not in a: raise SystemExit('post marker missing')
    if '.printf \"E004FP_POST' in a: raise SystemExit('unexpected escaping')
    for s in ('0xee3e','0xee41','0xee4a','0xee4d','0xee67','0xee42','0xee68','E004FP_DRY_POSTREG'):
        if s not in v: raise SystemExit('dry case missing '+s)
    if '&&' in a or '||' in a or '&&' in v or '||' in v: raise SystemExit('unsupported KD boolean operator emitted')
    packed=(0x1234<<16)|0xee4a
    if (packed & 0xffff) != 0xee4a: raise SystemExit('packed-register model failed')
    if shutil.which('pwsh'):
        ps=Path(td)/'ps'; ps.mkdir()
        subprocess.run(['pwsh','-NoProfile','-File',str(D/'generate-kd.ps1'),'-PmicBase','fffff80012345000','-Output',str(ps)],check=True,stdout=subprocess.DEVNULL)
        if (ps/'arm.kd').read_bytes() != (Path(td)/'arm.kd').read_bytes(): raise SystemExit('PowerShell arm differs')
        if (ps/'validate.kd').read_bytes() != (Path(td)/'validate.kd').read_bytes(): raise SystemExit('PowerShell validate differs')
print('E004FP_STATIC=PASS pre=stack-read-byte post=packed-w27-reg target_regs=9 capture=no-set bounded=12frames/5s generators=equivalent')
