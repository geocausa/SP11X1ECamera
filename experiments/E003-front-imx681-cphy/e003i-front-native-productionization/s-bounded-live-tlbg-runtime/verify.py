#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,sys
D=Path(__file__).resolve().parent
R=D.parents[3]
B=R/'experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate'
m=json.loads((D/'MANIFEST.json').read_text())
sha=lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
for name,want in m['assets_sha256'].items():
    if name=='imx681.ko': p=B/'imx681.ko'
    elif name=='dtb': p=B/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'
    elif name=='r4': p=B/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin'
    elif name=='r5': p=B/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE_R5.bin'
    elif name=='r6': p=B/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE_R6.bin'
    else: p=D/name
    got=sha(p)
    if got!=want: raise SystemExit(f'hash drift {name}: {got} != {want}')
src=(D/'e003i-s-six-frame-tlbg.c').read_text()
for needle in ['IQ_R4_SUBMITTED_PRE_STREAMON','IQ_R5_SUBMITTED_AFTER_DQBUF0','IQ_R6_SUBMITTED_AFTER_DQBUF1','VIDIOC_G_EXT_CTRLS','last_generation != FRAME_COUNT','PINNED_FOR_REBOOT']:
    if needle not in src: raise SystemExit(f'missing helper contract: {needle}')
entry=(D/'99z_sp11_camera_e003i_s_live_tlbg').read_text()
for needle in ['clk_ignore_unused','pd_ignore_unused','modprobe.blacklist=qcom_camss,imx681,ov13858','sp11_camera_e003i_s_live_tlbg=1']:
    if needle not in entry: raise SystemExit(f'missing boot contract: {needle}')
if 'e003h_pix_runtime_arm' in ''.join(p.read_text(errors='ignore') for p in D.glob('*.sh')):
    raise SystemExit('stale runtime arm parameter present')
print('PASS: E003i-S immutable package hashes and contracts')
