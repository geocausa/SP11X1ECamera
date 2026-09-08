#!/usr/bin/env python3
from pathlib import Path
import hashlib, pefile, re, struct, subprocess, sys

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = BASE.parents[2]
CAMERA_ROOT = REPO.parent
DLL = Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
ASM = Path('/tmp/sp11-aec-oracle/full.asm')
CAMX = CAMERA_ROOT / 'reference/comprehensive9-study/Camera/camx/src/swl/stats/camxaecengine.cpp'
DLL_SHA = 'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'

assert DLL.is_file() and ASM.is_file() and CAMX.is_file()
assert hashlib.sha256(DLL.read_bytes()).hexdigest() == DLL_SHA

pe = pefile.PE(str(DLL), fast_load=True)
image = DLL.read_bytes()
IB = pe.OPTIONAL_HEADER.ImageBase

def va_bytes(va, n):
    return image[pe.get_offset_from_rva(va - IB):][:n]

def qword(va):
    return struct.unpack('<Q', va_bytes(va, 8))[0]

def i32(va):
    return struct.unpack('<i', va_bytes(va, 4))[0]

def dis(a, b):
    return subprocess.check_output(
        ['llvm-objdump', '-d', f'--start-address={hex(a)}', f'--stop-address={hex(b)}', str(DLL)],
        text=True)

def req(text, *needles):
    for n in needles:
        assert n in text, n

def fresh(rel, script, marker):
    p = BASE / rel / script
    cp = subprocess.run([sys.executable, str(p)], cwd=p.parent, text=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if cp.returncode:
        raise AssertionError(f'{rel} failed\n{cp.stdout}\n{cp.stderr}')
    assert marker in cp.stdout, (rel, marker, cp.stdout)

# Fresh prerequisite: BP is the generic fixed-tuning wrapper whose four runtime
# scalar controls BQ projects for the ordinary unlocked streaming profile.
fresh('bp-native-aec-fixed-preview-profile', 'verify-bp.py', 'BP_VERIFY=PASS')

# Final core +8 interface vtable. Slot +0x18 is the exact context-bit test.
assert qword(0x1813383b8 + 0x18) == 0x1803ae9b0
helper = dis(0x1803ae9b0, 0x1803ae9cc)
req(helper,
    '1803ae9b0:', 'mov\tx8, #0x1',
    '1803ae9b4:', 'lsl\tx9, x8, x1',
    '1803ae9b8:', 'ldr\tx8, [x0, #0xb8]',
    '1803ae9bc:', 'and\tx8, x9, x8',
    '1803ae9c4:', 'cset\tw0, hi')

# Constructor installs that vtable on the core +8 subobject.
ctor_iface = dis(0x1803af9f0, 0x1803afa14)
req(ctor_iface,
    '1803af9fc:', 'adrp\tx8, 0x181338000',
    '1803afa00:', 'add\tx8, x8, #0x3b8',
    '1803afa04:', 'add\tx0, x21, #0x8',
    '1803afa08:', 'str\tx8, [x21, #0x8]')

# BasicSafe calls this bit-test with context index 3.
basic = dis(0x1803ceaf0, 0x1803ceb1c)
req(basic,
    '1803ceaf0:', 'ldr\tx0, [x19]',
    '1803ceaf4:', 'mov\tw1, #0x3',
    '1803ceafc:', 'ldr\tx8, [x8, #0x18]',
    '1803ceb14:', 'cmp\tw0, #0x1')

# ContextManager operation-mode jump table: opMode 1 -> OR 0x4 (bit 2),
# opMode 2 -> OR 0x8 (bit 3). Thus normal Streaming (mode 1) does not activate
# BasicSafe's context-3 exemption.
ctx_base = 0x1803c870c
ctx_tbl = 0x1803c8c44
ctx_targets = [ctx_base + i32(ctx_tbl + 4*i) * 4 for i in range(6)]
assert ctx_targets[1] == 0x1803c86d4
assert ctx_targets[2] == 0x1803c86f0
ctx = dis(0x1803c868c, 0x1803c870c)
req(ctx,
    '1803c8690:', 'ldr\tw10, [x19, #0x220]',
    '1803c86d4:', 'orr\tx8, x11, #0x4',
    '1803c86f0:', 'orr\tx8, x11, #0x8')

# This exact DLL's CAECXControl::SetControlOpMode switch maps enum value 1 to
# the streaming branch. The branch contains both Streaming-to-Streaming and
# entering-streaming diagnostics.
op_base = 0x18037fd2c
op_tbl = 0x18038025c
op_targets = [op_base + i32(op_tbl + 4*i) * 4 for i in range(6)]
assert op_targets[1] == 0x18037febc
stream_case = dis(0x18037febc, 0x18037ffcc)
req(stream_case,
    '18037febc:',
    '18037ff1c:', 'add\tx5, x8, #0x6a8',
    '18037ff94:', 'add\tx5, x8, #0x680')
assert b'Streaming to Streaming' in image
assert b'entering streaming op mode' in image

# Same-tree CamX source independently maps normal streaming to the Streaming
# algorithm operation mode, and maps HAL AELock off to AECAlgoLockOFF.
src = CAMX.read_text(errors='ignore')
for n in [
    'case StatsOperationModeNormal:',
    'aeOperationMode = AECAlgoOperationModeStreaming;',
    'SetOperationModeToAlgo(aeOperationMode)',
    'if (ControlAELockOn == pHALParam->AELock)',
    '*pLock = AECAlgoLockOn;',
    '*pLock = AECAlgoLockOFF;',
    'setParamType      = AECAlgoSetParamAECLock;'
]:
    assert n in src, n

# The metering-lock bookkeeping routine calls the same context-bit test with
# index 38. w1=0x26 is established before x0=core+8 and remains live until the
# virtual slot +0x18 call.
lock_gate = dis(0x1803b3020, 0x1803b30e8)
req(lock_gate,
    '1803b302c:', 'mov\tw1, #0x26',
    '1803b3030:', 'add\tx0, x23, #0x8',
    '1803b30c4:', 'ldr\tx8, [x23, #0x8]',
    '1803b30cc:', 'ldr\tx8, [x8, #0x18]',
    '1803b30e4:', 'ldr\ts14')

# The control path explicitly sets/clears context 38 around the temporary
# metering-lock request context. This is dynamic mode bookkeeping and is not
# folded into the ordinary unlocked wrapper.
set38 = dis(0x1803777cc, 0x180377800)
req(set38,
    '1803777cc:', 'ldr\tw8, [x20, #0x4]',
    '1803777d0:', 'cmp\tw8, #0x1',
    '1803777dc:', 'mov\tw2, #0x1',
    '1803777e0:', 'mov\tw1, #0x26',
    '1803777e4:', 'ldr\tx8, [x0, #0xf0]')
clr38 = dis(0x180378274, 0x180378298)
req(clr38,
    '180378274:', 'ldr\tx0, [x19, #0x8]',
    '180378278:', 'mov\tw2, #0x0',
    '18037827c:', 'mov\tw1, #0x26',
    '180378280:', 'ldr\tx8, [x0, #0xf0]')

# Convergence constructor/reset state.
ctor = dis(0x1803cd5e4, 0x1803cd604)
req(ctor,
    '1803cd5f4:', 'str\txzr, [x19, #0x2b0]',
    '1803cd5f8:', 'str\twzr, [x19, #0x2ac]')
reset = dis(0x1803bad78, 0x1803bad94)
req(reset,
    '1803bad84:', 'str\twzr, [x19, #0x2ac]',
    '1803bad88:', 'str\txzr, [x19, #0x2b0]')

# Whole AEC-code census of stores to the three consumed offsets. +0x2b4 has no
# independent store: it is the upper word of the qword rooted at +0x2b0.
asm_lines = ASM.read_text(errors='ignore').splitlines()
def addr(line):
    try: return int(line.split(':',1)[0],16)
    except Exception: return None

def stores(off):
    out=[]
    needle=f'#0x{off:x}]'
    for l in asm_lines:
        a=addr(l)
        if a is None or not (0x180360000 <= a < 0x180400000): continue
        if needle in l and re.search(r'\bstr\w*\b', l): out.append((a,l))
    return out

s2ac=stores(0x2ac); s2b0=stores(0x2b0); s2b4=stores(0x2b4)
assert [a for a,_ in s2ac] == [0x1803b316c,0x1803b3190,0x1803b31ac,0x1803b31d0,0x1803bad84,0x1803cd5f8]
assert [a for a,_ in s2b0] == [0x1803b3168,0x1803b318c,0x1803b31b0,0x1803bad88,0x1803cd5f4]
assert s2b4 == []
# All nonzero writes are inside the lock-bookkeeping block.
for a,l in s2ac:
    if a not in (0x1803bad84,0x1803cd5f8): assert 0x1803b3100 <= a < 0x1803b3200
for a,l in s2b0:
    if a not in (0x1803bad88,0x1803cd5f4): assert 0x1803b3100 <= a < 0x1803b3200

# Explicit ordinary profile projection: Streaming -> context3 false; unlocked
# wrapper -> context38 false; constructor/reset lock bookkeeping remains zero.
projection = {
    'small_delta_exemption': 0,
    'state_flag_short': 0,
    'state_flag_long': 0,
    'word_0x2b4': 0,
}
assert all(v == 0 for v in projection.values())

print('DLL_SHA256='+DLL_SHA)
print('STREAMING_OPERATION_MODE=1 context_bit=2')
print('BASICSAFE_CONTEXT_QUERY=3 active=0')
print('METERING_LOCK_CONTEXT_QUERY=38 ordinary_unlocked_active=0')
print('STORE_CENSUS_2AC='+','.join(hex(a) for a,_ in s2ac))
print('STORE_CENSUS_2B0='+','.join(hex(a) for a,_ in s2b0))
print('INDEPENDENT_STORE_2B4=0')
print('NORMAL_UNLOCKED_RUNTIME_CONTROLS=0,0,0,0')
print('BQ_VERIFY=PASS')
