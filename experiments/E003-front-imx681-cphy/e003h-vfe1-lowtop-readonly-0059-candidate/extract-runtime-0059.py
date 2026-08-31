#!/usr/bin/env python3
import hashlib, json, re, subprocess
from pathlib import Path

REPO=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
NEW=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-lowtop-readonly-0059-candidate'
STATIC=REPO/'experiments/E003-front-imx681-cphy/e003h-vfe1-lowtop-readonly-0059-static'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)

expected_hash={
 'RUN':'2ba3a9f3031109f5740990e1b98261aaf693c5209be4ec1d734ca78c83a1e36f',
 'POST':'8a347b53523adea35865f4517b7d360d1974d71a9215151001bef2c0b789c12f',
 'DMESG':'3c86d58173cc4518a3aed1b1d47e8c83bac7ab3189cf9d2807346fba162f3898',
 'STAGES':'3f04c8fe3ae8216455f2bfd03318282bbad8fd0460f0c9009af14e4c10933ae0',
 'AUTH':'c6cd7e067fefeeaac332cb6a2af2ab7a4e41df424eaf24a0a3806a66276357b1',
}
files={
 'RUN':NEW/'RUNTIME-VFELOWTOP-0059-RUN.txt',
 'POST':NEW/'RUNTIME-VFELOWTOP-0059-POST.txt',
 'DMESG':NEW/'RUNTIME-VFELOWTOP-0059-DMESG.txt',
 'STAGES':NEW/'RUNTIME-VFELOWTOP-0059-RTCDM-STAGES.txt',
 'AUTH':NEW/'AUTHORIZATION.json',
}
for k,p in files.items():
 if not p.exists(): die(f'missing {k}')
 if sha(p)!=expected_hash[k]: die(f'{k} hash drift {sha(p)}')

run=files['RUN'].read_text(); post=files['POST'].read_text(); dm=files['DMESG'].read_text(); stages=files['STAGES'].read_text()
if run.count('HELPER_INVOCATION_COUNT=1')!=1 or 'RUN_RC=1' not in run: die('single-run contract')
if 'CAMERA_PROGRAMMING_DELTA=NONE_VS_0057' not in run or 'TELEMETRY=IN_DRIVER_VFE1_LOWTOP_0059' not in run: die('telemetry identity')
if 'fifo_seq=25' not in post or 'faulted=0' not in post or 'QC10C_OUTPUT=absent' not in post: die('post boundary')
if 'fifo_seq=25' not in stages or 'faulted=1' in stages: die('RT-CDM boundary')
if 'E003h VFE1 epoch0-timeout top=00000000/00030003' not in dm or 'bus=00000000/00000000' not in dm: die('VFE timeout boundary')
if 'ipp-seq[3]=00000ee8/08700f00' not in dm or 'line-error=00000000/00000000/00000000' not in dm: die('healthy CSID boundary')

oracle=json.loads((STATIC/'0059-static-oracle.json').read_text())
exp={k.lower():v.lower() for k,v in oracle['windows_live1_lowtop'].items()}
actual={}
m=re.search(r'VFE1 epoch0-timeout cfg=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8}) diag=([0-9a-f]{8}) core3=([0-9a-f]{8}) throttle=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})',dm)
if not m: die('lowtop line 1 missing')
for off,val in zip(['0x0024','0x0028','0x002c','0x0050','0x0068','0x0070','0x0074','0x0078'],m.groups()): actual[off]='0x'+val
m=re.search(r'VFE1 epoch0-timeout core456=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8}) period=([0-9a-f]{8}) epoch_height=([0-9a-f]{8})',dm)
if not m: die('lowtop line 2 missing')
for off,val in zip(['0x0080','0x0084','0x0088','0x008c','0x009c'],m.groups()): actual[off]='0x'+val
m=re.search(r'VFE1 epoch0-timeout viol=.* marker=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})',dm)
if not m: die('marker line missing')
for off,val in zip(['0x0090','0x0094','0x0098'],m.groups()): actual[off]='0x'+val
if set(actual)!=set(exp): die(f'offset set mismatch {set(exp)-set(actual)} {set(actual)-set(exp)}')
mismatches={k:{'windows':exp[k],'linux':actual[k]} for k in exp if exp[k]!=actual[k]}
if mismatches: die('Windows/Linux low-TOP mismatch '+json.dumps(mismatches,sort_keys=True))

cmdline=Path('/proc/cmdline').read_text()
if 'sp11_entry=7.1.5-sp11-fullio-v19c' not in cmdline: die('not Golden')
head=subprocess.check_output(['git','-C',str(REPO),'rev-parse','HEAD'],text=True).strip()
origin=subprocess.check_output(['git','-C',str(REPO),'rev-parse','origin/experiment/e003-front-imx681-cphy'],text=True).strip()
if head!=origin: die('git/origin divergence')
mods=[m for m in ['qcom_camss','imx681','ov13858'] if Path('/sys/module',m).exists()]
if mods: die('camera module remains '+','.join(mods))

env=subprocess.run(['grub-editenv','list'],text=True,capture_output=True).stdout
if 'saved_entry=sp11-audio-fullio-v19c' not in env or re.search(r'^next_entry=.+',env,re.M): die('GRUB return drift')

out={
 'schema':'sp11-e003h-runtime-0059-vfe-lowtop-v1',
 'accepted':True,
 'authorization_consumed':True,
 'execution':{'helper_invocations':1,'run_rc':1,'same_boot_retry':False,'golden_return_verified':True},
 'camera':{'csid_geometry':'3840x2160','csid_line_error':False,'rtcdm_fifo_final':25,'rtcdm_faulted':False,'vfe1_raw_epoch0':False,'qc10c_output':False},
 'vfe1_lowtop':{'windows_linux_exact_match':True,'matched_registers':len(exp),'mismatches':{},'linux':dict(sorted(actual.items())),'windows':dict(sorted(exp.items()))},
 'classification':{
   'lowtop_config_cluster_causal':False,
   'new_programming_write_justified':False,
   'closed_boundary':'VFE1 low-TOP configuration values match successful Windows 16/16 while raw Epoch0 remains absent',
   'next_focus':'VFE1 ingress/event-generation state outside the now-closed low-TOP configuration cluster'
 },
 'evidence_sha256':{k:sha(p) for k,p in files.items()},
}
(NEW/'runtime-0059-analysis.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
(NEW/'RESULT.md').write_text('# E003h 0059 result\n\nPASS as a read-only diagnostic. Linux VFE1 low-TOP configuration matches successful Windows exactly at all 16 pinned offsets, while VFE1 raw Epoch0 remains absent. The low-TOP configuration cluster is therefore closed as the remaining stall cause; no new write is justified.\n')
(NEW/'GOLDEN-RETURN-0059.txt').write_text('Golden return verified after the single 0059 helper invocation.\n'+env)
auth=json.loads(files['AUTH'].read_text()); auth_consumed={'schema':'sp11-e003h-vfelowtop-0059-authorization-consumed-v1','accepted':True,'authorization_sha256':sha(files['AUTH']),'consumed':True,'helper_invocations':1,'same_boot_retry':False,'analysis_sha256':sha(NEW/'runtime-0059-analysis.json')}
(NEW/'AUTHORIZATION-CONSUMED.json').write_text(json.dumps(auth_consumed,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
print('ANALYSIS_SHA256='+sha(NEW/'runtime-0059-analysis.json'))
print('RESULT_SHA256='+sha(NEW/'RESULT.md'))
print('GOLDEN_SHA256='+sha(NEW/'GOLDEN-RETURN-0059.txt'))
print('AUTH_CONSUMED_SHA256='+sha(NEW/'AUTHORIZATION-CONSUMED.json'))
