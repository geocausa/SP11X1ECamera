#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess
D=Path(__file__).resolve().parent;E=D/'evidence'
def need(v,m):
    if not v:raise AssertionError(m)
r=json.loads((D/'RESULT.json').read_text());a=json.loads((E/'FAILURE-ANALYSIS.json').read_text());f=json.loads((E/'ATTEMPT1-FAILURE.json').read_text())
need(r['status']==a['status']=='FAIL_VERIFIER_PRIVILEGE_AFTER_REAR_RUNTIME_BEHAVIOR_PASS_GOLDEN_RETURN_RETIRED','status')
need(f['status']=='FAIL_BOUNDED_NO_RETRY' and f['same_boot_retry_performed'] is False,'attempt failure')
need(a['formal_attempt_result']=='FAIL' and a['camera_behavior_retry_performed'] is False,'formal fail')
need(a['candidate_boot_id']=='1b72a2d4-4c5b-427d-b47f-8534d5fd24da' and a['golden_return_boot_id']=='49c8b928-46a3-43be-9acb-cb568e463f16','boots')
# copied raw evidence hashes
for manifest in ('RAW-TOPLEVEL.sha256','RAW-RUNTIME.sha256'):
 cp=subprocess.run(['sha256sum','-c',manifest],cwd=E,text=True,capture_output=True);need(cp.returncode==0,manifest+' '+cp.stdout+cp.stderr)
need((E/'REAR-COLORBAR.sha256').read_text().split()[0]=='6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346','colorbar record')
t=(E/'REAR-NORMAL8.txt').read_text();seq=[int(x) for x in re.findall(r'seq:\s*(\d+)\s+bytesused:\s*14321824',t)];need(seq==list(range(8)),'seq')
ts=[float(x) for x in re.findall(r'ts:\s*([0-9]+\.[0-9]+)',t)];need(len(ts)==8,'timestamps');fps=1/(sum(b-a for a,b in zip(ts,ts[1:]))/7);need(28.5<=fps<=31.5,'fps')
for ff,prefix in ((E/'PRE-STREAM-SUSPEND.txt','PRE_STREAM'),(E/'POST-STREAM-SUSPEND.txt','POST_STREAM')):
 s=ff.read_text()
 for x in ('IR','REAR','FRONT'):need(f'{x}_{prefix}_SUSPEND=PASS' in s,x+' suspend')
cp=subprocess.run([str(D/'route-state.py'),str(E/'FINAL-NEUTRAL.txt'),'--expect','neutral'],text=True,capture_output=True);need(cp.returncode==0,'final route')
log=(E/'DMESG.txt').read_text(errors='replace')
need('SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596' in log,'IR bind')
for bad in ('E004J_CSIPHY0_DPHY_WINDOWS_PARITY','E004T_','MODE_SELECT=1 front transmission started','SP11_VD55G0_NATIVE_STREAM_BLOCK','ILLUMINATION_ON','WARNING:','Call trace:','Kernel panic','Unhandled fault'):
 need(bad.lower() not in log.lower(),'bad marker '+bad)
need('Path.read_text()' in a['failure_cause'] and '0400' in a['failure_cause'],'root cause')
need('status=PASS_GOLDEN_RETURN' in (E/'GOLDEN-RETURN.txt').read_text(),'Golden');need('status=PASS_CANDIDATE_RETIRED' in (E/'RETIRE.txt').read_text(),'retire')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'current Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'GRUB')
need(not Path('/boot/sp11-7.1.5-camera-e004dq-unified-rgb-ir-rear').exists(),'candidate boot');need(not Path('/etc/grub.d/99zzzzzz_sp11_camera_e004dq_unified_rgb_ir_rear').exists(),'candidate entry')
print('E004dq FAILURE CLOSE VERIFY: PASS (runtime behavior evidence preserved; formal verifier failure; no retry; Golden retired)')
