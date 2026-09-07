#!/usr/bin/env python3
"""Historical AC2 sequence regression.

The AC2 log did not record request-local lux. The values below are fitted
consistency values and MUST NOT be described as historically observed metadata.
They are used only to prove that the independently reconstructed request-local
pipeline is capable of the exact four published startup CCTs.
"""
from pathlib import Path
import struct
import cct_model as m
ROOT=Path(__file__).resolve().parent
LUX_FITTED=[238.6585693359375,263.858642578125,262.83251953125,374.9688720703125]
EXPECTED=[5652,5915,6019,5733]
def fb(h): return struct.unpack('<f',struct.pack('<I',h))[0]
prev_x,prev_y=fb(0x3f1129ca),fb(0x3f00e486)
print('PROVENANCE FITTED_AC2_REGRESSION')
print('WARNING lux values are fitted consistency values, not historical observations')
ok=True
for i,(lux,exp) in enumerate(zip(LUX_FITTED,EXPECTED),1):
    g=m.agw(ROOT/'fixtures'/f'AC2-R{i}.raw',lux)
    x,y,c=m.temporal(g['x'],g['y'],prev_x,prev_y)
    pub=int(c); match=pub==exp; ok &= match
    print(f'R{i} lux_fit={lux:.9g} p01={g["p01"]} valid={g["valid"]} fresh_cct={float(g["cct"]):.9f} final_cct={float(c):.9f} published={pub} expected={exp} match={match}')
    prev_x,prev_y=x,y
print('ALL_PUBLISHED_MATCH',ok)
raise SystemExit(0 if ok else 1)
