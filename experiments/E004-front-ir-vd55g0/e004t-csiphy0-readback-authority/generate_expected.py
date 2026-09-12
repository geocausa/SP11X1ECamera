#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
J=REPO/'experiments/E004-front-ir-vd55g0/e004j-csiphy0-dphy-authority'
CSIPHY=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003c-dtb-build/source/drivers/media/platform/qcom/camss/camss-csiphy-3ph-1-0.c')
WIN=J/'WINDOWS-CSIPHY0-LIVE2.normalized.txt'
OUT=HERE/'csiphy0-windows-expected.generated.h'

WIN_SHA='fc3994ea2a2d607d8028ed0881b8056e510287d5831fe22b5ea635f1ec109a26'
CSIPHY_SHA='418fe18845e1d57e2de5f2c9ece4bdd78d817d59ca71b25b00eb4259581464a8'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

if sha(WIN)!=WIN_SHA: raise SystemExit('Windows normalized snapshot drift')
if sha(CSIPHY)!=CSIPHY_SHA: raise SystemExit('CSIPHY source drift')

w={}
for line in WIN.read_text().splitlines():
    off,val=line.split(); w[int(off,16)]=int(val,16)

s=CSIPHY.read_text()
blk=s.split('csiphy_lane_regs lane_regs_x1e80100[] = {',1)[1].split('};',1)[0]
rows=[]
for m in re.finditer(r'\{\s*(0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+),\s*(0x[0-9A-Fa-f]+),\s*([A-Z0-9_]+)\s*\}',blk):
    rows.append((int(m.group(1),16),int(m.group(2),16),m.group(4)))

current={0x1014:0x81,0x1018:0x01,0x101c:0x02}
for off,val,typ in rows:
    if typ in ('CSIPHY_SKEW_CAL','CSIPHY_DNP_PARAMS'):
        continue
    if typ=='CSIPHY_SETTLE_CNT_LOWER_BYTE':
        val=0x12
    current[off]=val
for i in range(11,22):
    current[0x1000+4*i]=0

proposed=dict(current)
for off in (0x0008,0x0408,0x0808,0x0c08,0x0e08):
    proposed[off]=0x10
proposed[0x1014]=0x81
for off in range(0x102c,0x1058,4):
    proposed[off]=w[off]

if len(proposed)!=96:
    raise SystemExit(f'expected 96 modeled registers, got {len(proposed)}')
bad=[(o,v,w.get(o)) for o,v in sorted(proposed.items()) if w.get(o)!=v]
if bad:
    raise SystemExit('proposed map is not 96/96 Windows: '+repr(bad))

lines=[
'/* SPDX-License-Identifier: GPL-2.0 */',
'/* Generated mechanically from E004j same-machine Windows CSIPHY0 authority. */',
'#ifndef SP11_E004T_CSIPHY0_WINDOWS_EXPECTED_H',
'#define SP11_E004T_CSIPHY0_WINDOWS_EXPECTED_H',
'',
'#define E004T_WINDOWS_CSIPHY0_NORMALIZED_SHA256 "'+WIN_SHA+'"',
'#define E004T_EXPECTED_REGISTER_COUNT 96',
'',
'struct e004t_reg_expect { u16 offset; u32 value; };',
'',
'static const struct e004t_reg_expect e004t_windows_csiphy0_expected[] = {',
]
for off,val in sorted(proposed.items()):
    lines.append(f'\t{{ 0x{off:04x}, 0x{val:08x} }},')
lines += ['};','','#endif','']
OUT.write_text('\n'.join(lines))
print('E004T_EXPECTED_GENERATE=PASS COUNT=96 WINDOWS_MATCH=96/96')
print('OUTPUT_SHA256='+sha(OUT))
