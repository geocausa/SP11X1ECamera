#!/usr/bin/env python3
from pathlib import Path
import hashlib
D=Path(__file__).resolve().parent/'windows-sync-oracle'
W,H=644,604; Y=W*H
src=(D/'input-644x604-nv12.bin').read_bytes()
win=(D/'windows-trustlet-sync-swabf-644x604.bin').read_bytes()
stable=(D/'windows-trustlet-sync-swasf-644x604-stable.bin').read_bytes()
race_a=(D/'windows-trustlet-sync-swasf-644x604-race-a.bin').read_bytes()
race_b=(D/'windows-trustlet-sync-swasf-644x604-race-b.bin').read_bytes()
weights=[2000,1990,1960,1911,1846,1670,1452,1213,973,750,556,395,270,177,142,112]
dx=(1,-1,0,1,-1,0,1,-1); dy=(1,1,1,-1,-1,-1,0,0)
out=bytearray(src)
for y in range(H):
    for x in range(W):
        c=src[y*W+x]; acc=0
        for xx,yy in zip(dx,dy):
            d=src[((y+yy)%H)*W+((x+xx)%W)]-c; m=abs(d)
            if m<128: acc += weights[min(15,m>>1)]*d
        out[y*W+x]=(c+(acc>>14))&255
assert bytes(out)==win, 'scalar SWABF differs from synchronized Windows trustlet output'
def h(b): return hashlib.sha256(b).hexdigest()
def diff(a,b):
    ix=[i for i,(x,y) in enumerate(zip(a,b)) if x!=y]
    ys=[i//W for i in ix if i<Y]; xs=[i%W for i in ix if i<Y]
    return {'bytes':len(ix),'y_bytes':sum(i<Y for i in ix),'uv_bytes':sum(i>=Y for i in ix),
            'row_min':min(ys) if ys else None,'row_max':max(ys) if ys else None,
            'rows':sorted(set(ys)),'col_min':min(xs) if xs else None,'col_max':max(xs) if xs else None}
print('SWABF_BYTE_EXACT=YES')
print('SWABF_SHA256='+h(win))
print('SWASF_STABLE_SHA256='+h(stable))
for name,b in [('race_a',race_a),('race_b',race_b)]:
    d=diff(stable,b)
    print(name.upper()+'_SHA256='+h(b))
    print(name.upper()+'_DIFF_BYTES='+str(d['bytes']))
    print(name.upper()+'_DIFF_ROWS='+','.join(map(str,d['rows'])))
    print(name.upper()+'_UV_DIFF_BYTES='+str(d['uv_bytes']))
