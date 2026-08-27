#!/usr/bin/env python3
import argparse,csv,re
from pathlib import Path
p=argparse.ArgumentParser(); p.add_argument('--source',required=True); p.add_argument('--table',required=True); p.add_argument('--oracle',required=True); p.add_argument('--header',required=True); a=p.parse_args()
s=Path(a.source).read_text()
# Exact X1E C-PHY source table.
m=re.search(r'lane_regs_x1e80100_3ph\[\]\s*=\s*\{(.*?)\n\};',s,re.S)
if not m: raise SystemExit('X1E C-PHY table not found')
rows=[]
for x in re.finditer(r'\{\s*(0x[0-9a-fA-F]+)\s*,\s*(0x[0-9a-fA-F]+)\s*,\s*([0-9]+)\s*,\s*CSIPHY_DEFAULT_PARAMS\s*\}',m.group(1)):
    rows.append((int(x.group(1),16),int(x.group(2),16),int(x.group(3))))
with open(a.table) as f:
    wr=list(csv.DictReader(f))
expected_order=[(int(r['reg_offset'],16),int(r['value'],16),int(r['aux'])//1000) for r in wr]
if rows != expected_order:
    raise SystemExit(f'Linux ordered table differs from Windows: linux={len(rows)} windows={len(expected_order)}')
final={}
for off,val,delay in rows: final[off]=val
with open(a.oracle) as f:
    kd={int(r['offset'],16):(int(r['live1'],16),int(r['live2'],16),int(r['post'],16)) for r in csv.DictReader(f)}
for off,val in final.items():
    if off not in kd or kd[off][0]!=val or kd[off][1]!=val:
        raise SystemExit(f'table/live mismatch off=0x{off:04x}')
# Common values written outside the table by lanes_enable and independently stable in Windows.
common={0x1014:0x02,0x1018:0x01,0x101c:0x7a}
for off,val in common.items():
    if kd.get(off,(None,None,None))[:2] != (val,val):
        raise SystemExit(f'common/live mismatch off=0x{off:04x}')
# Model the old generic clobber: table followed by common CTRL11..21 zeroing.
pre=dict(final); pre.update(common)
for i in range(11,22): pre[0x1000+i*4]=0
pre_bad=[off for off,val in {**final,**common}.items() if pre.get(off)!=val]
if pre_bad != list(range(0x102c,0x1055,4)):
    raise SystemExit(f'unexpected pre-fix mismatch set: {[hex(x) for x in pre_bad]}')
# Source must gate generic mask-zeroing away from X1E C-PHY.
required=[
 'const bool x1e_cphy = csiphy->camss->res->version == CAMSS_X1E80100 &&',
 'if (!x1e_cphy) {',
 'common CTRL11..CTRL21 (0x102c..0x1054)',
]
for x in required:
    if x not in s: raise SystemExit('missing source guard: '+x)
post={**final,**common}
post_bad=[off for off,val in post.items() if kd.get(off,(None,None,None))[0]!=val or kd[off][1]!=val]
if post_bad: raise SystemExit('post-fix Windows mismatch')
# Generate compact exact runtime expected register header.
h=Path(a.header)
lines=['/* Generated from same-machine Windows KD + validated 121-record table. */',
       'struct e003f_expected_reg { u32 off; u32 val; };',
       'static const struct e003f_expected_reg e003f_windows_expected[] = {']
for off in sorted(post): lines.append(f'\t{{ 0x{off:04x}, 0x{post[off]:08x} }},')
lines += ['};','']
h.write_text('\n'.join(lines))
print(f'ordered_records={len(rows)}')
print(f'table_unique_offsets={len(final)}')
print(f'pre_fix_mismatches={len(pre_bad)}')
print('pre_fix_offsets='+','.join(f'0x{x:04x}' for x in pre_bad))
print(f'post_fix_expected_offsets={len(post)}')
print(f'post_fix_mismatches={len(post_bad)}')
print('E003F_STATIC_FINAL_STATE=PASS')
