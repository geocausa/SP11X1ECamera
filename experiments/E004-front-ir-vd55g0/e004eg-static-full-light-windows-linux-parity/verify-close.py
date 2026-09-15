#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,struct,subprocess
D=Path(__file__).resolve().parent; E=D/'evidence'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
expected={
 'windows/E004EG-STATIC-FULLLIGHT-DM-oracle.log':'3623b813cbfa79633e9919a2dd7725405242ad23e35e6d070637d001237e381b',
 'windows/E004EG-STATIC-BANK4-ALL.log':'d9a72e44f71b0a04ae5581770f6ab5c2e2f9cf152dff0c5f6b73f5d3e6f9c347',
 'windows/E004EG-STATIC-SCENEANALYZER-SETTER.log':'fe6b6568788e5130bf211537e0acef53a21b1e04a14aeec3505a27f70ba74839',
 'windows/E004EG-STATIC-FULLLIGHT-WINDOWS-CLOSURE.txt':'9ff1b40910d732195c22c655ee9fc1fefc8da88ce9c5a4068071108f4413355d',
 'linux/OFFLINE-AEC-REPLAY.txt':'5302b52b88a812815d402b33262672f204c3ba91336295e278850d0baa52ebca'}
for n,h in expected.items(): need(sha(E/n)==h,'hash '+n)
dm=(E/'windows/E004EG-STATIC-FULLLIGHT-DM-oracle.log').read_text(errors='replace')
req=re.findall(r'DM_REQUEST .*?capflag=(\d+)',dm); need(len(req)==12 and set(req)=={'0'},'Windows capflag')
sa=(E/'windows/E004EG-STATIC-SCENEANALYZER-SETTER.log').read_text(errors='replace')
rows=[]
for m in re.finditer(r'E004EG_SET hit=\d+ id=(\d+) bits0=([0-9a-fA-F]{8}) bits1=([0-9a-fA-F]{8})',sa):
    i=int(m.group(1)); b=int(m.group(2),16); b1=int(m.group(3),16)
    if 7 <= i <= 13: need(b==b1,'final point publication mismatch id '+str(i))
    rows.append((i,struct.unpack('<f',struct.pack('<I',b))[0]))
def vals(i): return [f for j,f in rows if j==i]
luma,target,adj=vals(4),vals(5),vals(7); need(len(luma)==len(target)==len(adj)==4,'FrameSA count')
for l,t,a in zip(luma,target,adj): need(abs(t/l-a)<1e-6,'FrameSA arithmetic')
for i in range(8,14):
    v=vals(i); need(len(v)>=3,'id count '+str(i)); need(all(abs(a-b)<1e-6 for a,b in zip(adj[:len(v)],v)),'id parity '+str(i))
obs=json.loads((E/'linux/ATTEMPT1-OBSERVATION.json').read_text()); need(obs['cap_active_shadow_count']==21 and obs['apply_one_native_sources']==[] and obs['later_native_writes']==0,'Linux shadow')
rep=(E/'linux/OFFLINE-AEC-REPLAY.txt').read_text(); g24=next(x for x in rep.splitlines() if x.startswith('G=24 '))
for tok in ('LUMA=83.6211014','FRAME_TARGET=40','FRAME_ADJ=0.478348166','TARGET_SAFE=6.95884275','TARGET_SHORT=0.774501204','PUB_SHORT=30486355401','CONV=11133280747','CAP=6133333088'):
    need(tok in g24,'G24 '+tok)
r=json.loads((D/'RESULT.json').read_text()); need(r['lighting_hypothesis']=='DISPROVEN','lighting'); need(r['production_code_changed'] is False,'production changed')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True); need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
for p in ('/usr/lib/sp11-front-imx681','/usr/lib/sp11-camera-stack','/var/lib/sp11-camera-stack'): need(not Path(p).exists(),'package '+p)
print('E004eg CLOSE VERIFY: PASS (lighting disproven; first observable parity divergence at FrameSA; Golden clean)')
