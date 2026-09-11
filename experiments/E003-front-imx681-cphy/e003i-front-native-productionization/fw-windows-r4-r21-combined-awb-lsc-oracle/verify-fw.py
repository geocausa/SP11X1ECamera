#!/usr/bin/env python3
from pathlib import Path
import hashlib,re

H=Path(__file__).resolve().parent
DLL=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll')
DLL_SHA='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
HOOKS={
  0x6bfa68:(48,'24eaf82d9f264c8e0363f1042e75b124bf5a679262191cf724bcf3a1386de5fe'),
  0x68fa00:(200,'12f2f1f9fe26e02eb5397325ae37c61bd4b43fe2f6560e6c1beeae12fa92c1eb'),
  0x88e1e8:(64,'c1d02234593a0ef0c7dc4af28392051d481d618257c3f12c4872817a2c6cf01c'),
  0xa03b34:(64,'04e1b598ffcd0488e8f221e73e8ebb89084faafad9a8f653e59ff25f4b433f14'),
}

def need(v,m):
    if not v:
        raise AssertionError(m)

def sha(b):
    return hashlib.sha256(bytes(b)).hexdigest()

need(sha(DLL.read_bytes())==DLL_SHA,'pinned DLL SHA')
import pefile
pe=pefile.PE(str(DLL))
for rva,(n,h) in HOOKS.items():
    need(sha(pe.get_data(rva,n))==h,f'hook bytes {rva:x}')

holder=(H/'holder.ps1').read_text()
oracle=(H/'oracle.cmd').read_text()
ga=(H/'ga.cmd').read_text()
pub=(H/'pub.cmd').read_text()
entry=(H/'entry.cmd').read_text()
post=(H/'post.cmd').read_text()

need('Surface Camera Front' in holder and 'WAIT_START' in holder,'holder front gate')
need('E003I-FW' in holder and 'FW_HOLDER_BEGIN' in holder and 'FW_HOLDER_END' in holder,'holder identity')
need(holder.count('START_BEGIN')==1 and holder.count('StartAsync')==1 and holder.count('StopAsync')==1,'one holder stream')
need('Remove-Item $go,$ready,$done' in holder,'stale trigger cleanup')

for token in (
    'QcDeviceMFT8380+0x6bfa68',
    'QcDeviceMFT8380+0x68fa00',
    'QcDeviceMFT8380+0x88e1e8',
    'QcDeviceMFT8380+0xa03b34',
    'FW_BREAKPOINTS_ARMED R4_R21 COMBINED_AWB_LSC',
):
    need(token in oracle,'oracle '+token)
need(oracle.count('bp QcDeviceMFT8380+')==4,'four breakpoint contract')
need('r @$t17=0' in oracle and 'r @$t18=0' in oracle and 'r @$t19=0' in oracle,'pseudo-register init')

ga_regs=set(re.findall(r'@\$(t\d+)',ga))
need(ga_regs=={f't{i}' for i in range(18)},f'GA register ownership {sorted(ga_regs)}')

entry_regs=set(re.findall(r'@\$(t\d+)',entry))
post_regs=set(re.findall(r'@\$(t\d+)',post))
need(entry_regs <= {'t18','t19'},f'entry clobbers AWB regs {entry_regs}')
need(post_regs <= {'t18','t19'},f'post clobbers AWB regs {post_regs}')
need('@$t17' not in entry and '@$t17' not in post,'LSC scripts touch AWB valid flag')

for token in ('dwo(@x19+0xa4)','dwo(@x19+0xa8)','dwo(@x19+0x78)',
              'dwo(poi(@x19+0x88)+0xf49)','dwo(@x19+0x14)','dwo(@x19+0x1c)'):
    need(token in ga,'GA map '+token)
for token in ('qwo(@x23+0x128)','dwo(@x13+8)','dwo(@x13+0xc)',
              'dwo(@x13+0x10)','dwo(@x13+0x14)','FW_GA req=','FW_PUB req='):
    need(token in pub,'PUB map '+token)

need('qwo(@x1+0x1ff8)' in entry and 'poi(@x0+0xa0)' in entry and '@x1+0x2080' in entry,'entry direct expressions')
need('dwo(poi(@x0+0xa0)+4) != 0x300' in entry,'stats record fail closed')
need('(dwo(poi(@x0+0xa0))&2) == 0' in entry,'stats layout fail closed')
need('qwo(@x20+0x1ff8)' in post and '@x19+0xac' in post and '@x19+0x194b' in post,'post direct expressions')

for r in range(4,22):
    q=f'{r:02d}'
    need(f'R{q}_TINTLESS_STATS.bin' in entry,f'R{r} stats file')
    need(f'R{q}_TRIGGER.bin' in entry,f'R{r} trigger file')
    need(f'R{q}_LSC_STAGING.bin' in post,f'R{r} staging file')

need('r @$t18=(@$t18&0x100)|qwo(@x1+0x1ff8)' in entry,'entry low-byte request state')
need('r @$t18=@$t18|0x100' in pub,'AWB completion bit')
need('@$t19 == 0n21' in pub,'PUB waits for LSC R21')
need('r @$t19=0n21' in post,'LSC R21 completion state')
need('(@$t18 & 0x100) != 0' in post,'LSC waits for AWB R21')
need(pub.count('FW_CAPTURE_COMPLETE R=21 AWB=YES LSC=YES')==1,'PUB terminal marker')
need(post.count('FW_CAPTURE_COMPLETE R=21 AWB=YES LSC=YES')==1,'POST terminal marker')
need(pub.count('.detach; q')==2 and post.count('.detach; q')==1,'fail-closed plus two-sided terminal detach')

for f,s in [('oracle',oracle),('ga',ga),('pub',pub),('entry',entry),('post',post)]:
    need(max(map(len,s.splitlines()))<512,f'{f} command line too long')

print('FW_DLL_AND_FOUR_HOOKS_PINNED=PASS')
print('FW_PSEUDO_REGISTER_OWNERSHIP=PASS AWB=t0..t17 LSC=t18..t19')
print('FW_R4_R21_AWB_SCOPE=PASS')
print('FW_R4_R21_TINTLESS_LSC_SCOPE=PASS')
print('FW_TWO_SIDED_R21_COMPLETION_HANDSHAKE=PASS')
print('FW_ONE_STREAM_HOLDER_GATE=PASS')
print('FW_VERIFY=PASS')
