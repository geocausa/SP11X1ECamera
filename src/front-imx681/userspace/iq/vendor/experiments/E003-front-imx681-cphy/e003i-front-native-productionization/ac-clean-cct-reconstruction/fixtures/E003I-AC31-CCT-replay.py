from pathlib import Path
import struct, math, json

ROOT = Path(__file__).resolve().parent
ENGINE = (ROOT / "E003I-AC31-CCTENGINE.bin").read_bytes()
ANCHORS = (ROOT / "E003I-AC31-CCTANCHORS.bin").read_bytes()

def f32(x):
    return struct.unpack('<f', struct.pack('<f', float(x)))[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def rf32(b,o): return struct.unpack_from('<f',b,o)[0]
def bits(x): return struct.unpack('<I',struct.pack('<f',f32(x)))[0]
def frombits(x): return struct.unpack('<f',struct.pack('<I',x))[0]
def add(a,b): return f32(f32(a)+f32(b))
def sub(a,b): return f32(f32(a)-f32(b))
def mul(a,b): return f32(f32(a)*f32(b))
def div(a,b): return f32(f32(a)/f32(b))
def sqrtf(a): return f32(math.sqrt(f32(a))) if f32(a)>=0 else float('nan')

def anchor(i): return rf32(ANCHORS,8*i),rf32(ANCHORS,8*i+4)
def line_rec(i): return tuple(rf32(ENGINE,0x90+16*i+4*j) for j in range(4))
def geom_rec(i): return tuple(rf32(ENGINE,16*(i+1)+4*j) for j in range(4))

def classify(x,y):
    x,y=f32(x),f32(y); idx=4; prev=0; trace=[]
    while True:
        if idx==8: return idx,prev,trace
        A,B,C,flag=line_rec(idx)
        v=add(mul(B,y),mul(A,x)); v=add(v,C)
        if abs(float(flag)-1.0)<1e-12: v=f32(-v)
        s=0 if v==0.0 else (1 if v<0 else 2)
        trace.append((idx,bits(v),s))
        if v<0:
            if prev==2: return idx,1,trace
            prev=1; idx-=1
            if idx==-1: return idx,prev,trace
        elif v>0:
            if prev==1: return idx,2,trace
            prev=2; idx+=1
        else:
            return idx,prev,trace

def primary(x,y,a,b,g):
    x,y=f32(x),f32(y); ax,ay=anchor(a); bx,by=anchor(b)
    A,B,C,flag=geom_rec(g)
    line=add(mul(B,y),mul(A,x)); line=add(line,C); line=mul(line,A)
    ya=sub(y,ay); xa=sub(x,ax); dA=add(mul(ya,ya),mul(xa,xa))
    yb=sub(y,by); xb=sub(x,bx); dB=add(mul(yb,yb),mul(xb,xb))
    L2=rf32(ENGINE,0x110+4*g)
    if line != 0.0:
        r=div(mul(add(sub(dA,dB),L2),0.5),L2)
    else:
        r=sqrtf(div(dA,L2))
    two_r=add(r,r)
    t=mul(two_r,r); t=sub(t,two_r); t=add(t,1.0); t=mul(t,L2)
    perp2=mul(sub(add(dB,dA),t),0.5); perp=sqrtf(perp2)
    if r < 0.0:
        r=f32(0.0); perp=sqrtf(dA)
    signv=line
    if abs(float(line)) < 1e-12:
        signv=sub(y,C)
    elif abs(float(flag)-1.0)<1e-12:
        signv=f32(-line)
    sign=f32(1.0 if signv>0.0 else -1.0)
    metric=mul(sign,perp)
    if math.isnan(metric): metric=f32(0.0)
    return r,metric

def secondary(x,y,a,b):
    x,y=f32(x),f32(y); A=line_rec(a); B=line_rec(b)
    vb=add(add(mul(x,B[0]),B[2]),mul(y,B[1])); vb2=mul(vb,vb)
    va=add(add(mul(x,A[0]),A[2]),mul(y,A[1]))
    nb=add(mul(B[1],B[1]),mul(B[0],B[0])); na=add(mul(A[1],A[1]),mul(A[0],A[0]))
    q=div(div(vb2,nb),div(mul(va,va),na)); q=sqrtf(q); return div(1.0,add(q,1.0))

def blend(r,idx):
    raw_r=f32(r); choose_hi=raw_r>f32(0.5); r=min(f32(1.0),raw_r); r=max(f32(0.0),r); r=f32(r)
    if idx==8:
        return f32(u32(ENGINE,0x150)), u32(ENGINE,0x148+(4 if choose_hi else 0))
    if idx==9:
        return f32(u32(ENGINE,0x1c4)), u32(ENGINE,0x1b8+(4 if choose_hi else 0))
    k0=u32(ENGINE,0x150+16*idx); k1=u32(ENGINE,0x154+16*idx)
    cct=add(mul(f32(k0),sub(1.0,r)),mul(f32(k1),r))
    state=u32(ENGINE,0x148+16*idx+(4 if choose_hi else 0))
    return cct,state

def replay(x,y):
    x,y=f32(x),f32(y); cls,side,trace=classify(x,y)
    if cls==-1:
        ax,ay=anchor(0); dx=sub(x,ax); dy=sub(y,ay); metric=sqrtf(add(mul(dx,dx),mul(dy,dy)))
        return {'classifier':cls,'metric':metric,'ratio':None,'cct':f32(u32(ENGINE,0x150)),'state':u32(ENGINE,0x14c),'trace':trace}
    if cls==8:
        ax,ay=anchor(9); dx=sub(x,ax); dy=sub(y,ay); metric=sqrtf(add(mul(dx,dx),mul(dy,dy)))
        return {'classifier':cls,'metric':metric,'ratio':None,'cct':f32(u32(ENGINE,0x1c4)),'state':u32(ENGINE,0x1b8),'trace':trace}
    if cls==0: r,m=primary(x,y,0,1,0); fr=r; c,s=blend(fr,0)
    elif cls==1: r,m=primary(x,y,1,2,1); fr=r; c,s=blend(fr,1)
    elif cls==2: r,m=primary(x,y,2,3,2); fr=r; c,s=blend(fr,2)
    elif cls==3:
        r,m=primary(x,y,3,5,3); _c,_s=blend(r,3); fr=secondary(x,y,3,4); c,s=blend(fr,3)
    elif cls==4: r,m=primary(x,y,3,5,3); fr=r; c,s=blend(fr,3)
    elif cls==5:
        r,m=primary(x,y,5,7,5); _c,_s=blend(r,5); fr=secondary(x,y,4,5); c,s=blend(fr,5)
    elif cls==6: r,m=primary(x,y,7,8,6); fr=r; c,s=blend(fr,6)
    elif cls==7: r,m=primary(x,y,8,9,7); fr=r; c,s=blend(fr,7)
    else: raise ValueError(cls)
    return {'classifier':cls,'metric':m,'ratio':fr,'cct':c,'state':s,'trace':trace}

CASES=[
 {'name':'activeA','x':0x3f1a37e8,'y':0x3efc1044,'metric':0x3d0b2485,'ratio':0x3e813e8f,'cct':0x45945c8e,'state':3},
 {'name':'activeB','x':0x3f18ef71,'y':0x3f00896d,'metric':0x3cf60e57,'ratio':0x3e27a9d9,'cct':0x45972221,'state':3},
 {'name':'default3','x':0x3f000000,'y':0x3ecccccd,'metric':0xbd9f3b49,'ratio':0x3ec8286e,'cct':0x45900888,'state':3},
 {'name':'default5','x':0x3f19999a,'y':0x3e99999a,'metric':0xbd8d1568,'ratio':0x3e8af2df,'cct':0x45667e88,'state':5},
 {'name':'default3b','x':0x3efebcac,'y':0x3ec7b6ca,'metric':0xbda66f63,'ratio':0x3eeac8d2,'cct':0x458deb7e,'state':3},
 {'name':'default2','x':0x3f000000,'y':0x3f0a3d71,'metric':0xbcf380a8,'ratio':0x3f197d48,'cct':0x45af052f,'state':3},
]
results=[]
for case in CASES:
    out=replay(frombits(case['x']),frombits(case['y']))
    got={'classifier':out['classifier'],'metric':bits(out['metric']),'ratio':None if out['ratio'] is None else bits(out['ratio']),'cct':bits(out['cct']),'state':out['state']}
    exp={k:case[k] for k in ('metric','ratio','cct','state')}
    ok=all(got[k]==exp[k] for k in exp)
    row={'name':case['name'],'ok':ok,'got':{k:(f'{v:08x}' if isinstance(v,int) and k not in ('classifier','state') else v) for k,v in got.items()},'expected':{k:(f'{v:08x}' if isinstance(v,int) and k not in ('state',) else v) for k,v in exp.items()}}
    results.append(row); print(row)
print('ALL_MATCH',all(r['ok'] for r in results))
(ROOT/'E003I-AC31-CCT-replay-results.json').write_text(json.dumps(results,indent=2))
