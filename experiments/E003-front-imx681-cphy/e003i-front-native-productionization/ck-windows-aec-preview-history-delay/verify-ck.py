#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, struct, subprocess
import pefile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ROOT=HERE.parents[3]
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
assert DLL.is_file()
assert hashlib.sha256(DLL.read_bytes()).hexdigest()==SHA

def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(DLL)],text=True)
def req(t,*ss):
    for s in ss:
        assert s in t,s

# Fresh-run CJ so the temporal selector is joined to the proven retained-S1 source path.
cj=BASE/'cj-windows-aec-source-s1-history-provenance'/'verify-cj.py'
cp=subprocess.run([str(cj)],cwd=cj.parent,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
assert cp.returncode==0,(cp.stdout,cp.stderr)
assert 'CJ_VERIFY=PASS' in cp.stdout

# Same-machine front transport oracle pins the ordinary front session to camera useCase 2.
front=ROOT/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-ife-start-804-oracle.json'
raw=ROOT/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/E003H_IFE_START804_VALUES_20260830.log'
o=json.loads(front.read_text())
assert o['accepted'] is True
assert o['dynamic_same_machine']['camera_use_case']==2
assert o['dynamic_same_machine']['ife1_marker']=='EV IFE_START804 id=1 usecase=2 skip=0'
assert hashlib.sha256(raw.read_bytes()).hexdigest()==o['dynamic_same_machine']['sha256']

# CapturePipe lifecycle state +0x162e58 is zero at construction. The only
# effective scalar writers in this class transition it to 2 (stop path) or 1
# after a successful Start/resume. Thus first ordinary Configure is state 0.
ctor=dis(0x1802abcbc,0x1802abd00)
req(ctor,
    '1802abcc8:', 'add\tx8, x19, #0x162, lsl #12',
    '1802abcd8:', 'str\twzr, [x8, #0xe58]')
stop=dis(0x1802acfd0,0x1802ad108)
req(stop,
    '1802acff0:', 'ldr\tw8, [x19, #0xe58]',
    '1802acff4:', 'cmp\tw8, #0x2',
    '1802ad0e8:', 'mov\tw8, #0x2',
    '1802ad0ec:', 'str\tw8, [x19, #0xe58]')
start=dis(0x1802ae8e0,0x1802ae9f8)
req(start,
    '1802ae988:', 'cbnz\tw0, 0x1802ae9ac',
    '1802ae9b4:', 'add\tx9, x19, #0x162, lsl #12',
    '1802ae9b8:', 'mov\tw8, #0x1',
    '1802ae9bc:', 'str\tw8, [x9, #0xe58]')

# CapturePipe chooses exactly 3 for non-AutoHDR and 4 for AutoHDR, stores the
# choice in the global pipeline-delay halfword, then useCase 2 routes through
# the normal refresh branch. That branch is taken at initial state 0 and writes
# the selected global delay to the stats/pipeline object +0x2478.
cfg=dis(0x1802b3c30,0x1802b3d38)
req(cfg,
    '1802b3c50:', 'add\tx2, x8, #0xa78',
    '1802b3c58:', 'mov\tw5, #0x4',
    '1802b3c5c:', 'mov\tw9, #0x4',
    '1802b3c68:', 'add\tx2, x8, #0xb20',
    '1802b3c70:', 'mov\tw5, #0x3',
    '1802b3c74:', 'mov\tw9, #0x3',
    '1802b3c84:', 'strh\tw9, [x8, #0x88]',
    '1802b3cac:', 'ldr\tw8, [x22, #0x480]',
    '1802b3cd4:', 'ldr\tw8, [x8, #0xe58]',
    '1802b3cd8:', 'cmp\tw8, #0x1',
    '1802b3ce4:', 'ldrh\tw8, [x8, #0x88]',
    '1802b3cf0:', 'str\tw8, [x9, #0x2478]')

# Decode CapturePipe's 15-way useCase switch mechanically: useCase 2 -> 0x1802b3cd0.
data=DLL.read_bytes(); pe=pefile.PE(str(DLL),fast_load=True); image=pe.OPTIONAL_HEADER.ImageBase
def va2off(va):
    r=va-image
    for s in pe.sections:
        if s.VirtualAddress <= r < s.VirtualAddress+max(s.Misc_VirtualSize,s.SizeOfRawData):
            return s.PointerToRawData+(r-s.VirtualAddress)
    raise AssertionError(hex(va))
tab=0x1802b53b8; base=0x1802b3d38; off=va2off(tab)
def capture_target(usecase):
    assert 1 <= usecase <= 15
    rel=struct.unpack_from('<i',data,off+4*(usecase-1))[0]
    return base+rel*4
assert capture_target(2)==0x1802b3cd0

# +0x480 is exactly the helper's useCase argument; its diagnostic prints the
# helper result as pickModeUseCase and this original argument as useCase.
uc=dis(0x1802baaac,0x1802baae4)
req(uc,
    '1802baac4:', 'ldr\tw1, [x21, #0x480]',
    '1802baad0:', 'bl\t0x1802b9da0')
pick=dis(0x1802b9da0,0x1802b9e48)
req(pick,
    '1802b9db8:', 'mov\tw20, w1',
    '1802b9e20:', 'mov\tw6, w20',
    '1802b9e24:', 'mov\tw5, w19')

# Stats processing publishes input ID15 from the exact +0x2478 byte.
st=dis(0x180833ea4,0x180833ed0)
req(st,
    '180833eb8:', 'mov\tw1, #0xf',
    '180833ec0:', 'ldr\tw8, [x8, #0x2478]',
    '180833ec4:', 'strb\tw8, [x26, #0x6b8]',
    '180833ec8:', 'bl\t0x18084db88')

# Input ID15 is translated to one-byte public/internal set-param 25.
tr=dis(0x18084e0c0,0x18084e0e8)
req(tr,
    '18084e0d0:', 'ldrb\tw8, [x22]',
    '18084e0d4:', 'mov\tw3, #0x1',
    '18084e0d8:', 'mov\tx2, x22',
    '18084e0dc:', 'mov\tw1, #0x19')

# CAECX set-param dispatch preserves x0 as x22, and type25 routes to 0x1803c6f2c.
sp=dis(0x1803c5010,0x1803c50a0)
req(sp,
    '1803c503c:', 'ldr\tx19, [x1, #0x8]',
    '1803c5040:', 'mov\tx22, x0',
    '1803c5050:', 'ldr\tw10, [x19, #0xc]',
    '1803c5070:', 'sub\tw10, w10, #0x1',
    '1803c5080:', 'adr\tx9, 0x1803c82b0',
    '1803c5088:', 'adr\tx9, 0x1803c69c8')
sp_tab=0x1803c82b0; sp_base=0x1803c69c8; off=va2off(sp_tab)
def setparam_target(t):
    assert 1 <= t <= 50
    rel=struct.unpack_from('<i',data,off+4*(t-1))[0]
    return sp_base+rel*4
assert setparam_target(25)==0x1803c6f2c

# Type25 requires a one-byte payload and stores its byte into x22+0xb0c.
set25=dis(0x1803c6f2c,0x1803c7068)
req(set25,
    '1803c6f38:', 'ldr\tw8, [x19, #0x8]',
    '1803c6f88:', 'mov\tw8, #0x1',
    '1803c6fd4:', 'ldr\tx8, [x19]',
    '1803c6fd8:', 'ldrb\tw8, [x8]',
    '1803c6fdc:', 'strb\tw8, [x22, #0xb0c]',
    '1803c7028:', 'ldrb\tw8, [x22, #0xb0c]')

# Concrete CAECX interface slot0 returns this+0x220. AnalyzerManager later reads
# +0x8ec from that returned object, so x22+0xb0c is exactly the same byte:
# 0x220 + 0x8ec = 0xb0c.
ctx=dis(0x1803ae960,0x1803ae968)
req(ctx,'1803ae960:','add\tx0, x0, #0x220','1803ae964:','ret')
assert 0x220+0x8ec==0xb0c
mgr=dis(0x1803e3a34,0x1803e3aa0)
req(mgr,
    '1803e3a3c:', 'ldr\tx8, [x0]',
    '1803e3a54:', 'ldrb\tw21, [x0, #0x8ec]',
    '1803e3a94:', 'mov\tw1, w21',
    '1803e3a98:', 'bl\t0x1803d3938')

print('DLL_SHA256='+SHA)
print('FRONT_ORDINARY_USECASE=2')
print('CAPTUREPIPE_LIFECYCLE=constructor:0 start/resume:1 stop:2')
print('NON_AUTOHDR_PIPELINE_DELAY=3')
print('AEC_INPUT15_SOURCE=stats+0x2478')
print('AEC_SET_PARAM=25 one-byte pipeline delay')
print('CAECX_SELECTOR_DEST=(core+8)+0xb0c = context+0x8ec')
print('ANALYZER_HISTORY_OFFSET=3')
print('CK_VERIFY=PASS')
