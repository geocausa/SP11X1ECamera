#!/usr/bin/env python3
from __future__ import annotations
import struct

def f32(v): return struct.unpack('<f',struct.pack('<f',float(v)))[0]
def rf32(u,a): return struct.unpack('<f',bytes(u.mem_read(a,4)))[0]
def wf32(u,a,v): u.mem_write(a,struct.pack('<f',f32(v)))

def mode2_cubic_map(u,source_knots,target_knots,coeffs,domain,out,count_minus_one):
    """Clean-room active GTM mode-2 cubic mapper (native RVA 0x9a4f38)."""
    first=rf32(u,source_knots+4)
    low_ratio=f32(rf32(u,target_knots+4)/first)
    count=(int(count_minus_one)+1)&0xffffffff
    for i in range(count):
        x=rf32(u,domain+i*4)
        y=f32(0.0)
        if first < x:
            seg=2
            while seg < 7:
                if x <= rf32(u,source_knots+seg*4):
                    ci=(seg-2)*3
                    dx=f32(x-rf32(u,source_knots+(seg-1)*4))
                    t=f32(f32(rf32(u,coeffs+(ci+2)*4)*dx)+rf32(u,coeffs+(ci+1)*4))
                    t=f32(f32(t*dx)+rf32(u,coeffs+ci*4))
                    y=f32(f32(t*dx)+rf32(u,target_knots+(seg-1)*4))
                    break
                seg+=1
        else:
            y=f32(x*low_ratio)
        top=f32(1.0) if f32(1.0) < y else y
        clamped=f32(0.0) if not (f32(0.0) < y) else top
        denom=x if x != f32(0.0) else f32(1.0)
        ratio=f32(clamped/denom)
        limited=ratio if ratio <= low_ratio else low_ratio
        result=limited if f32(1.0) < ratio else f32(1.0)
        wf32(u,out+i*4,result)
    if count >= 2:
        u.mem_write(out,bytes(u.mem_read(out+4,4)))
    return 1

def tmc_domain_map_zero_blend(u,domain,io,tmc,scale_shift,count_minus_one,power=1.0):
    """Clean-room active GTM TMC-domain mapper for the validated v5/0x60800 path.

    Both native TMC blend scalars are zero on R4/R5/R6, making the large tone
    domain algebraically inactive. The active power is exactly 1.0.
    """
    if struct.pack('<f',f32(power)) != struct.pack('<f',f32(1.0)):
        raise ValueError('unsupported active GTM power')
    if bytes(u.mem_read(tmc+0x109c,8)) != b'\0'*8:
        raise ValueError('unsupported nonzero GTM TMC blend')
    count=(int(count_minus_one)+1)&0xffffffff
    scale=float(1 << (int(scale_shift)&0x1f))
    for i in range(count):
        x=rf32(u,domain+i*4)
        ratio=rf32(u,io+i*4)
        y=f32(ratio*x)
        top=f32(1.0) if f32(1.0) < y else y
        clamped=f32(0.0) if not (f32(0.0) < y) else top
        # Native powf(clamped/x,1.0) is bit-identical to its float32 input.
        q=f32(clamped/x)
        wf32(u,io+i*4,f32(q*scale))

def rf64(u,a): return struct.unpack('<d',bytes(u.mem_read(a,8)))[0]
def wf64(u,a,v): u.mem_write(a,struct.pack('<d',float(v)))

def final_adaptive_map_power1(u,curve,enabled,low_bits,high_bits,domain,power=1.0,strength=0.8500000238418579):
    """Clean-room active final GTM mapper (native RVA 0x9aa3a8) for s0=1.0.

    With exact power 1.0 the native B-spline domain-warp factor collapses to 1,
    so the selected coordinate is simply clamp(domain,0,1). The 0.85 branch is
    algebraically inactive on this validated call, but is kept as a guard.
    """
    if int(enabled) != 1: return 1
    if struct.pack('<f',f32(power)) != struct.pack('<f',f32(1.0)):
        raise ValueError('unsupported GTM final adaptive power')
    if struct.pack('<f',f32(strength)) != struct.pack('<f',f32(0.8500000238418579)):
        raise ValueError('unsupported GTM final adaptive strength')
    src=[rf64(u,curve+i*8) for i in range(257)]
    dom=[rf32(u,domain+i*4) for i in range(257)]
    limit=float(f32(float(1 << ((int(low_bits)+int(high_bits))&0x1f))-f32(1.0)))
    out=[]
    one=f32(1.0); zero=f32(0.0)
    for i in range(257):
        x=dom[i]
        coord=one if one < x else x
        if not (zero < x): coord=zero
        d=src[i]
        j=1
        while j < 257:
            if coord < dom[j]:
                x1=dom[j]; x0=dom[j-1]
                a=f32(x1-coord); b=f32(coord-x0); den=f32(x1-x0)
                num=(src[j-1]*float(x0)*float(a)) + (src[j]*float(x1)*float(b))
                q=(num/float(den))/float(coord)
                d=float(f32(q))
                break
            j+=1
        if d > limit: d=limit
        if not (0.0 < d): d=0.0
        out.append(d)
    # Native triple loop is equivalent to a sequential minimum for 1..255.
    for i in range(1,256):
        if out[i-1] <= out[i]: out[i]=out[i-1]
    for i,v in enumerate(out): wf64(u,curve+i*8,v)
    return 1
