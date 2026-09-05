#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,subprocess
D=Path(__file__).resolve().parent; R=D.parents[3]; B=R/'experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate'; m=json.loads((D/'MANIFEST.json').read_text()); sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for n,w in m['assets_sha256'].items():
 p=B/'imx681.ko' if n=='imx681.ko' else B/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb' if n=='dtb' else B/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin' if n=='r4' else B/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE_R5.bin' if n=='r5' else B/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE_R6.bin' if n=='r6' else D/n
 if sha(p)!=w: raise SystemExit(f'hash drift {n}')
s=(D/'e003i-z-six-frame-stats.c').read_text()
for x in ('#define TLBG_RAW_BYTES 0xF000U','#define STATS3A_RAW_BYTES 0x51000U','#define STATS3A_BYTES (STATS3A_HEADER_BYTES + STATS3A_RAW_BYTES)','TL_BG/3A source identity mismatch','last_generation != FRAME_COUNT || last_3a_generation != FRAME_COUNT'):
 if x not in s: raise SystemExit(f'helper contract drift: {x}')
entry=(D/'99za_sp11_camera_e003i_z_3a').read_text()
for x in ('clk_ignore_unused','pd_ignore_unused','sp11_camera_e003i_z_3a=1','sp11-camera-e003i-z-3a-one-shot'):
 if x not in entry: raise SystemExit(f'boot contract drift: {x}')
vm=subprocess.check_output(['modinfo','-F','vermagic',D/'qcom-camss-e003i-y.ko'],text=True).strip()
if vm!='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64': raise SystemExit('vermagic drift')
print('PASS: E003i-Z immutable paired TLBG/3A package')
