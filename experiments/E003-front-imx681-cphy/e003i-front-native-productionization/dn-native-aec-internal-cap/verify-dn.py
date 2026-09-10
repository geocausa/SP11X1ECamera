#!/usr/bin/env python3
"""Offline DN verification against live DM pairs and pinned ARM64 cap arithmetic."""
from pathlib import Path
import ctypes as C
import hashlib, importlib.util, json, random, struct, subprocess, tempfile
from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm64_const import *

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=BASE.parents[2]
ARCHIVE=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive')
DLL=ARCHIVE/'sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll'
DM=ARCHIVE/'e003i-dm/windows-internal-cap-20260910'
DB=ARCHIVE/'e003i-db/attempt4-live-g4-fail-20260910T181907'
FLAGS=['-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
class CapIn(C.Structure):
    _fields_=[('linear',C.c_uint64*7),('minimum',C.c_uint64*7),('maximum',C.c_uint64*7),
              ('history1_short',C.c_uint64),('pred_gain',C.c_float),('compact_98',C.c_float),
              ('snap_steps',C.c_float),('rescale_disabled',C.c_uint32),('history1_valid',C.c_uint32)]
class CapOut(C.Structure):
    _fields_=[('linear',C.c_uint64*7),('pred_gain',C.c_float),
              ('rescaled',C.c_uint32),('history_snapped',C.c_uint32)]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fbits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def f32(f):return struct.unpack('<f',struct.pack('<f',f))[0]
def inp(values):
    p=CapIn()
    p.linear[:]=values;p.minimum[:]=[37516]*7;p.maximum[:]=[6133333088]*7
    p.pred_gain=1;p.compact_98=0;p.snap_steps=0.5
    return p
def read_module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
assert sha(DLL)=='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
dm=read_module('dm',BASE/'dm-windows-internal-cap-bounds/parse-dm.py').parse(DM)
assert dm==json.loads((BASE/'dm-windows-internal-cap-bounds/RESULT.json').read_text())
b=DLL.read_bytes();pe=struct.unpack_from('<I',b,60)[0];n=struct.unpack_from('<H',b,pe+6)[0]
opt=struct.unpack_from('<H',b,pe+20)[0];sections=[]
for i in range(n):
    vs,va,sz,raw=struct.unpack_from('<IIII',b,pe+24+opt+40*i+8);sections.append((va,sz,raw))
def pebytes(a,size):
    for va,sz,raw in sections:
        if va<=a and a+size<=va+sz:return b[raw+a-va:raw+a-va+size]
    raise AssertionError(hex(a))
# Runtime-initialized reciprocal log1.03 scale, already pinned by CG.
LOG103_SCALE=struct.pack('<I',0x429bcc0c)
assert struct.unpack('<I',pebytes(0x3d3934,4))[0]==0x3f800001
libm=C.CDLL('libm.so.6');libm.log10f.argtypes=[C.c_float];libm.log10f.restype=C.c_float
def emulate(p):
    u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
    u.mem_map(0x3d3000,0x1000);u.mem_write(0x3d3000,pebytes(0x3d3000,0x1000))
    u.mem_map(0x1795000,0x1000);u.mem_write(0x1795b34,LOG103_SCALE)
    u.mem_map(0x2000000,0x10000)
    conv,out,bounds,config,history,obj=[0x2000000+i*0x1000 for i in range(6)]
    def qw(a,v):u.mem_write(a,struct.pack('<Q',v))
    def fw(a,v):u.mem_write(a,struct.pack('<f',v))
    qw(conv+0x98,bounds);qw(conv+0x138,config);qw(conv,obj);qw(obj+8,history)
    fw(conv+0xd8,p.pred_gain);fw(config+0x2c,p.snap_steps);fw(out+0x98,p.compact_98)
    for i in range(7):
        qw(out+i*8,p.linear[i]);qw(bounds+0x18+0x50*i,p.minimum[i]);qw(bounds+0x40+0x50*i,p.maximum[i])
    qw(history+0x28,p.history1_short)
    u.reg_write(UC_ARM64_REG_X19,out);u.reg_write(UC_ARM64_REG_X20,conv);u.reg_write(UC_ARM64_REG_X12,p.rescale_disabled)
    # Execute original cap arithmetic. External logging and the already-proven
    # history selector/log10f primitives are modeled at their call boundaries.
    def hook(uc,addr,size,user):
        if addr==0x3d3638:
            uc.reg_write(UC_ARM64_REG_X0,history if p.history1_valid else 0)
            uc.reg_write(UC_ARM64_REG_PC,0x3d363c)
        elif addr==0x3d3664:
            arg=struct.unpack('<f',struct.pack('<I',uc.reg_read(UC_ARM64_REG_S0)))[0]
            uc.reg_write(UC_ARM64_REG_S0,fbits(libm.log10f(arg)))
            uc.reg_write(UC_ARM64_REG_PC,0x3d3668)
        elif addr==0x3d36d8:
            uc.reg_write(UC_ARM64_REG_PC,0x3d3760)
    u.hook_add(UC_HOOK_CODE,hook)
    u.emu_start(0x3d35e4,0x3d3908,count=1000)
    assert u.reg_read(UC_ARM64_REG_PC)==0x3d3908
    return list(struct.unpack('<7Q',u.mem_read(out,56))),struct.unpack('<I',u.mem_read(conv+0xd8,4))[0]

with tempfile.TemporaryDirectory(prefix='e003i-dn-') as td:
    td=Path(td);so=td/'cap.so'
    subprocess.run(['cc',*FLAGS,'-shared','-fPIC',str(HERE/'native-internal-cap.c'),'-lm','-o',str(so)],check=True)
    cap=C.CDLL(str(so));cap.e003i_internal_cap.argtypes=[C.POINTER(CapIn),C.POINTER(CapOut)]
    cap.e003i_internal_cap_preview_observed.argtypes=[C.POINTER(C.c_uint64),C.c_float,C.POINTER(CapOut)]
    cases=[]
    for sample in dm['samples']:
        p=inp(sample['pre']);r=CapOut()
        assert cap.e003i_internal_cap(C.byref(p),C.byref(r))==0
        assert list(r.linear)==sample['post'] and fbits(r.pred_gain)==sample['pred_gain_bits']
        assert cap.e003i_internal_cap_preview_observed(p.linear,p.pred_gain,C.byref(r))==0
        assert list(r.linear)==sample['post'];cases.append(p)
    rng=random.Random(0xD003)
    # Boundary values and deliberately eligible preludes with/without history snap.
    for trigger in [0,1]:
        for history in [0,1]:
            for snap in [0.0,0.5,50.0]:
                p=inp([4000000000,9000000000,8000000000,5000000000,4500000000,4200000000,4100000000])
                p.rescale_disabled=trigger;p.history1_valid=history
                p.history1_short=3066666544;p.snap_steps=snap;p.pred_gain=8
                cases.append(p)
    for history_value in [3066666000,3066666496,3066666544]:
        p=inp([4000000000,9000000000,8000000000,5000000000,4500000000,4200000000,4100000000])
        p.history1_valid=1;p.history1_short=history_value;p.snap_steps=0.5
        cases.append(p)
    boundary=[1,37515,37516,37517,2**24-1,2**24+1,6133333087,6133333088,6133333089,2**35]
    for x in boundary:
        for flag in [0.0,1.0,f32(1+2**-23),2.0]:
            p=inp([x,8000000000,6000000000,37516,2**24+1,2**24-1,37516]);p.compact_98=flag;p.pred_gain=12
            cases.append(p)
    for _ in range(350):
        p=inp([rng.randrange(37516,60000000000) for _ in range(7)])
        p.rescale_disabled=rng.randrange(2);p.history1_valid=rng.randrange(2)
        p.history1_short=rng.randrange(37516,6133333089)
        p.pred_gain=f32(rng.uniform(0.5,16));p.compact_98=rng.choice([0.0,1.0,2.0])
        p.snap_steps=rng.choice([0.0,0.5,50.0]);cases.append(p)
    rescaled=snapped=0
    for index,p in enumerate(cases):
        r=CapOut();assert cap.e003i_internal_cap(C.byref(p),C.byref(r))==0
        expected,pg=emulate(p)
        assert (list(r.linear),fbits(r.pred_gain))==(expected,pg),(index,list(r.linear),expected,fbits(r.pred_gain),pg)
        rescaled+=bool(r.rescaled);snapped+=bool(r.history_snapped)
    print("COVERAGE",len(cases),rescaled,snapped)
    assert rescaled>10 and snapped>2
    # Missing branch binding fails before any output mutation.
    p=cases[18];r=CapOut();C.memset(C.byref(r),0xa5,C.sizeof(r));before=bytes(r)
    assert cap.e003i_internal_cap_preview_observed(p.linear,p.pred_gain,C.byref(r))==-2 and bytes(r)==before
    p.minimum[0]=0
    assert cap.e003i_internal_cap(C.byref(p),C.byref(r))==-1 and bytes(r)==before
    mp=json.loads((HERE/'SOURCE-MAP.json').read_text())
    for sub,f in mp:
        if sub==HERE.name:continue
        paths_to_pin=[BASE/sub/f,*sorted((BASE/sub).glob('*.h'))]
        for source in paths_to_pin:
            original=subprocess.check_output(['git','show','8bc6598:'+str(source.relative_to(REPO))],cwd=REPO)
            assert hashlib.sha256(original).hexdigest()==sha(source),str(source)

    exe=td/'g4';cmd=['cc',*FLAGS]
    for sub,_ in mp:cmd+=['-I',str(BASE/sub)]
    cmd += [str(HERE/'replay-g4-cap.c')]+[str(BASE/sub/f) for sub,f in mp]+['-lm','-o',str(exe)]
    subprocess.run(cmd,check=True)
    pins=json.loads((BASE/'dl-native-aec-g4-failure-replay/RESULT.json').read_text())['pairs']
    paths=[DB/('producer/STATS3A-G%d.bin'%g if g<4 else 'STATS3A-FAIL-G4.bin') for g in range(1,5)]
    for p,pin in zip(paths,pins):assert sha(p)==pin['stats3a_sha256']
    replay=subprocess.check_output([str(exe),*map(str,paths)],text=True)
    assert 'G4_CAP_REPLAY=PASS STATE_ADVANCES_ON_SUCCESS=PASS' in replay
    assert 'G4_CAPPED_CONTROL FLL=7116 EXP=7108 AG=960 DG=1471 retained=6133332579' in replay
    (HERE/'REPLAY.txt').write_text(replay)
result=dict(status='PASS_OFFLINE_SCOPED_CAP',windows_live_pairs=18,windows_changed_pairs=11,
            instruction_differential_cases=len(cases),rescaled_cases=rescaled,history_snapped_cases=snapped,
            g1_g3_controls_unchanged=True,g4_rc=0,g4_cap=6133333088,g4_retained=6133332579,
            g4_controls=dict(fll=7116,exposure=7108,analogue_gain=960,digital_gain=1471),
            error_output_atomic=True,table_rejection_unchanged=True,hardware_runs=0,
            limitations=['Preview adapter rejects conditional-prelude-eligible requests until bank9:data10 is bound.',
                         'Compact +0x98=0 and fixed limits cover the observed ordinary preview domain.',
                         'ARM64 differential models external history lookup, log10f and the proven runtime log scale; it executes original cap arithmetic.',
                         'Sensor write-to-statistics timing remains unproven; no delay change or live success claimed.'])
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
