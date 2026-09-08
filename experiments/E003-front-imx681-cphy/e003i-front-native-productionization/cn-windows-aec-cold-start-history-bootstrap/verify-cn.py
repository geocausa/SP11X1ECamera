#!/usr/bin/env python3
from pathlib import Path
import hashlib, re, subprocess

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[3]
DLL=Path('/tmp/sp11-aec-oracle/QcDeviceMFT8380.dll')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
START_SHA='7d703a37b02a99fe7e2915d14e9a63ddc805d1985681a1f89831556f0d2a1d5f'
assert DLL.is_file() and hashlib.sha256(DLL.read_bytes()).hexdigest()==DLL_SHA
assert subprocess.run(['git','merge-base','--is-ancestor','2b09272','HEAD'],cwd=REPO).returncode==0

def dis(a,b):
    cp=subprocess.run(['llvm-objdump','-d',f'--start-address={a}',f'--stop-address={b}',str(DLL)],text=True,capture_output=True,check=True)
    return cp.stdout

def need(s,*xs):
    for x in xs: assert x in s,x

h=dis('0x1803ae6f8','0x1803ae958')
need(h,
 '1803ae74c:', 'ldr\tw9, [x19, #0xc]',
 '1803ae754:', 'ldr\tw9, [x19, #0x1c0]',
 '1803ae7c4:', 'add\tx10, x19, #0x10',
 '1803ae7d4:', 'ldr\tx8, [x19, #0x1d0]',
 '1803ae7f4:', 'ldr\tx12, [x8, #0x10]',
 '1803ae7f8:', 'add\tx10, x8, #0x10',
 '1803ae7fc:', 'add\tx12, x27, x12',
 '1803ae800:', 'cmp\tx12, x11')

c=dis('0x1803b46fc','0x1803b47b0')
need(c,
 '1803b4700:', 'mov\tw1, #0x1',
 '1803b4718:', 'fmov\ts16, #1.00000000',
 '1803b471c:', 'str\twzr, [x22, #0xdc]',
 '1803b4720:', 'str\ts16, [x22, #0xd8]',
 '1803b479c:', 'ldr\ts16, [x24, #0x178]',
 '1803b47a0:', 'str\ts16, [x22, #0xd8]',
 '1803b47a4:', 'ldr\ts16, [x24, #0x17c]')

z=dis('0x180371130','0x180371170')
need(z,'180371150:', 'str\twzr, [x19, #0x970]')
p=dis('0x180376ec8','0x180376ef0')
need(p,'180376ed4:', 'ldr\tw8, [x19, #0x970]', '180376edc:', 'str\tw8, [x9, #0x178]')

ev=(HERE/'ORACLE-EVIDENCE.txt').read_text()
need(ev,
 f'START_RECORD_SHA256={START_SHA}',
 'START_RECORD_FRAME=0','START_RECORD_MARKER=1',
 'START_RECORD_LANES=33333332,33333332,33333332,33333332,33333332,33333332,33333332',
 'START_RECORD_F17C=0x00000000',
 'ACTIVE_HISTORY_FIELD=history+0x1d0',
 'ACTIVE_HISTORY_CAPACITY_OBSERVED=10',
 'ACTIVE_REAL_RECORD_MARKER=0',
 'START_DISTINCT_FROM_SAMPLED_REAL_NODES=PASS')
assert ev.count('sha='+START_SHA)>=4
assert ev.count('eq_start=False')>=2

# Re-check raw oracle provenance when the read-only Windows volume is available.
raw=Path('/mnt/sp11-win-oracle/Users/Geoca/Documents')
expected={
'E003I-CN2-probe.log':'f002016b98470e9a5030f214f9856f567cea5cdcf9d30977b9f7f1cc7cb9d68a',
'E003I-CN3-probe.log':'33ccc88f20a681653260e9d582cc1feb53bd8600899f4cf34fab8fb5de098558',
}
for n,sha in expected.items():
    q=raw/n
    if q.exists(): assert hashlib.sha256(q.read_bytes()).hexdigest()==sha,(n,hashlib.sha256(q.read_bytes()).hexdigest())

# Model the mechanically observed ordinary lookup: newest -> oldest; keep the
# oldest inspected node when the requested depth has not yet matured.
def lookup(current,offset,newest_to_oldest,start='START'):
    selected=start
    for f in newest_to_oldest:
        selected=f
        if f+offset <= current: break
    return selected
assert lookup(0,3,[])=='START'
assert lookup(1,3,[0])==0
assert lookup(2,3,[1,0])==0
assert lookup(3,3,[2,1,0])==0
assert lookup(4,3,[3,2,1,0])==1
assert lookup(2,1,[1,0])==1
assert lookup(2,2,[1,0])==0

print('DLL_SHA256='+DLL_SHA)
print('START_RECORD_SHA256='+START_SHA)
print('START_RECORD=frame0 marker1 seven_lanes_33333332')
print('ACTIVE_HISTORY=history+0x1d0 capacity10 marker0')
print('WARMUP_LOOKUP=start -> oldest_available -> exact requested depth')
print('NULL_CONVERGENCE=PredGain1 previous_delta0')
print('CN_VERIFY=PASS')
