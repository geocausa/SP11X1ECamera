#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
D=Path(__file__).resolve().parent; R=D.parents[3]; B=R/'experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate'; m=json.loads((D/'MANIFEST.json').read_text()); sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
for n,w in m['assets_sha256'].items():
 p=B/'imx681.ko' if n=='imx681.ko' else B/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb' if n=='dtb' else B/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin' if n=='r4' else B/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE_R5.bin' if n=='r5' else B/'firmware/sp11/e003h/E003H_PIX_ORACLE_CAPSULE_R6.bin' if n=='r6' else D/n
 if sha(p)!=w: raise SystemExit(f'hash drift {n}')
s=(D/'e003i-u-six-frame-tlbg.c').read_text(); assert '#define TLBG_RAW_BYTES 0xF000U' in s and '#define TLBG_BYTES (TLBG_HEADER_BYTES + TLBG_RAW_BYTES)' in s and 'last_generation != FRAME_COUNT' in s
entry=(D/'99za_sp11_camera_e003i_u_tlbg').read_text(); assert 'clk_ignore_unused' in entry and 'pd_ignore_unused' in entry and 'sp11_camera_e003i_u_tlbg=1' in entry
print('PASS: E003i-U immutable corrected-ABI package')
