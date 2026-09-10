import struct, random, math

def f32(x):
    return struct.unpack('<f', struct.pack('<f', float(x)))[0]
def f32_bits(x):
    return struct.unpack('<I', struct.pack('<f', f32(x)))[0]
def f32_div(a,b): return f32(f32(a)/f32(b))
def f32_mul(a,b): return f32(f32(a)*f32(b))
def u64_from_f32(x):
    x=f32(x)
    if x < 0 or not math.isfinite(x): raise ValueError(x)
    return int(x)

def u64_from_double(x):
    if x < 0 or not math.isfinite(x): raise ValueError(x)
    return int(x)

TABLE681_RAW=bytes.fromhex(
 '010000000000803f8c92000000000000'
 '010000000000864255a0fc0100000000'
 '0100000000008642aa40f90300000000'
 '000000000000b842aa40f90300000000')

def parse_knees(raw):
    out=[]
    assert len(raw)%16==0
    for off in range(0,len(raw),16):
        prio,gain,time=struct.unpack_from('<IfQ',raw,off)
        out.append((prio,f32(gain),time))
    return out
KNEES=parse_knees(TABLE681_RAW)
CORR=f32(1.0)
ONE_NEXT=struct.unpack('<f', bytes.fromhex('0100803f'))[0]
GAIN_EPS=struct.unpack('<d', bytes.fromhex('000000e0e2361a3f'))[0]
FIT_WARN_EPS=struct.unpack('<f', bytes.fromhex('95bfd633'))[0]

def exposure_product(gain,time,corr=CORR):
    return u64_from_double(float(gain)*float(time)*float(corr))

def apply_core_table(target,knees=KNEES,corr=CORR):
    prods=[exposure_product(g,t,corr) for _,g,t in knees]
    if not (prods[0] <= target <= prods[-1]):
        raise ValueError(('target-outside-table',target,prods[0],prods[-1]))
    # Exact end points use the adjacent segment, as the Windows walk stops at first upper product >= target.
    upper=1
    while upper < len(knees) and target > prods[upper]:
        upper += 1
    if upper >= len(knees): upper=len(knees)-1
    p0,g0,t0=knees[upper-1]
    p1,g1,t1=knees[upper]
    base=prods[upper-1]
    ratio=f32_div(f32(target), f32(base))
    gain=f32(g0); time=int(t0)
    if ONE_NEXT < ratio:
        if p1 == 0: # gain first, then time
            gr=f32_div(g1,g0)
            if ratio <= gr:
                leftover=f32(1.0); used=ratio
            else:
                leftover=f32_div(ratio,gr); used=gr
            gain=f32_mul(used,g0)
            if ONE_NEXT < leftover:
                tr=f32_div(f32(t1),f32(t0))
                used_t=leftover if leftover <= tr else tr
                time=u64_from_f32(f32_mul(used_t,f32(t0)))
        else: # nonzero priority: time first, then gain
            tr=f32_div(f32(t1),f32(t0))
            if ratio <= tr:
                leftover=f32(1.0); used=ratio
            else:
                leftover=f32_div(ratio,tr); used=tr
            time=u64_from_f32(f32_mul(used,f32(t0)))
            if 1.0 < leftover:
                gr=f32_div(g1,g0)
                used_g=leftover if leftover <= gr else gr
                gain=f32_mul(used_g,g0)
    desired=exposure_product(gain,time,corr)
    return {'gain':gain,'time':time,'desired':desired,'corr':corr,'upper':upper,'priority':p1}

def make_table_exposure_fit(v, min_gain, min_time, max_gain, max_time):
    # Direct transcription of QcDeviceMFT8380.dll RVA 0x3c31f8 for positive normal-preview values.
    gain=f32(v['gain']); time=int(v['time']); desired=int(v['desired']); corr=f32(v['corr'])
    min_gain=f32(min_gain); max_gain=f32(max_gain); min_time=int(min_time); max_time=int(max_time)
    old_gain=gain
    if min_gain <= old_gain:
        if max_gain < old_gain:
            gain=max_gain
            if float(max_gain)+GAIN_EPS <= float(old_gain):
                time=u64_from_double((float(desired)/float(max_gain))/float(corr))
                if max_time < time and time <= max_time+1:
                    time=max_time
    else:
        gain=min_gain
        if float(old_gain) <= float(min_gain)-GAIN_EPS:
            time=u64_from_double((float(desired)/float(min_gain))/float(corr))
            if time < min_time and min_time-1 <= time:
                time=min_time
    if time < min_time:
        old_time=time; time=min_time
        if not (min_time-1 <= old_time):
            gain=f32((float(desired)/float(min_time))/float(corr))
            if not (min_gain <= gain or float(gain) < float(min_gain)-GAIN_EPS):
                gain=min_gain
    else:
        maxg=max_gain
        if time > max_time:
            old_time=time; time=max_time
            if not (old_time <= max_time+1):
                gain=f32((float(desired)/float(max_time))/float(corr))
                if not (gain <= maxg or float(maxg)+GAIN_EPS < float(gain)):
                    gain=maxg
    ok=not (time < min_time or max_time < time or gain < f32(min_gain-FIT_WARN_EPS))
    return {'gain':gain,'time':time,'desired':desired,'corr':corr,'ok':ok}

def check():
    assert KNEES == [(1,1.0,37516),(1,67.0,33333333),(1,67.0,66666666),(0,92.0,66666666)], KNEES
    print('TABLE681',KNEES)
    prods=[exposure_product(g,t) for _,g,t in KNEES]
    print('KNEE_PRODUCTS',prods)
    tests=set()
    for p in prods:
        for d in (-2,-1,0,1,2):
            if prods[0] <= p+d <= prods[-1]: tests.add(p+d)
    # deterministic midpoints and the observed-gain neighborhood
    tests.update([241_379_190,241_379_203,241_379_204,241_379_210])
    rng=random.Random(0x681)
    for _ in range(100000): tests.add(rng.randrange(prods[0],prods[-1]+1))
    last_by_target=[]
    seg={1:0,2:0,3:0}
    for target in sorted(tests):
        out=apply_core_table(target)
        seg[out['upper']]+=1
        assert math.isfinite(out['gain']) and out['gain']>0 and out['time']>0
        # The table output stays inside the bracketing knee bounds, allowing f32/time truncation by <=1 at exact caps.
        _,g0,t0=KNEES[out['upper']-1]; _,g1,t1=KNEES[out['upper']]
        assert min(g0,g1)-1e-5 <= out['gain'] <= max(g0,g1)+1e-5
        assert min(t0,t1)-1 <= out['time'] <= max(t0,t1)+1
        full=make_table_exposure_fit(out,1.0,37516,92.0,66666666)
        assert full['ok'] and 37516 <= full['time'] <= 66666666 and 1.0-1e-6 <= full['gain'] <= 92.0+1e-6
        preview=make_table_exposure_fit(out,1.0,37516,92.0,66666664)
        assert preview['ok'] and 37516 <= preview['time'] <= 66666664 and 1.0-1e-6 <= preview['gain'] <= 92.0+1e-6
    print('FUZZ_CASES',len(tests),'SEGMENTS',seg,'PASS')
    for t in [prods[0],33333333,241379204,prods[1],prods[2],prods[3]]:
        if prods[0] <= t <= prods[-1]:
            o=apply_core_table(t); p=make_table_exposure_fit(o,1.0,37516,92.0,66666664)
            print('FIX',t,'table',hex(f32_bits(o['gain'])),o['gain'],o['time'],o['desired'],'preview',hex(f32_bits(p['gain'])),p['gain'],p['time'],p['desired'])
    # Corroborative Windows live pair seen in active controller memory.
    o=apply_core_table(241379204); p=make_table_exposure_fit(o,1.0,37516,92.0,66666664)
    print('OBSERVED_PAIR_CHECK',hex(f32_bits(p['gain'])),p['time'])
    assert f32_bits(p['gain'])==0x40e7b95b and p['time']==33333332
    print('AQ_REPLAY_SELFTEST=PASS')
if __name__=='__main__': check()
