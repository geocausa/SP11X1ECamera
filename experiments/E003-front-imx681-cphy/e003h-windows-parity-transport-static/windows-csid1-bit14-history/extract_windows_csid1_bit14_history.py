#!/usr/bin/env python3
import hashlib,json,re
from pathlib import Path
from datetime import datetime
H=Path(__file__).resolve().parent
R=H.parents[1]/'e003h-csid1-line-error-frame-0049-candidate'/'runtime-0049-analysis.json'
F={'kd':H/'E003H_CSID1_BIT14_HISTORY_20260830_2334.log','cycles':H/'E003H_CSID1_BIT14_WINDOWS_CYCLES_20260830.txt','linux0049':R,'static':H.parent/'windows-csid1-line-count-error'/'windows-csid1-line-count-error-oracle.json'}
E={'kd':'7ba4a32a14a3a1ae44ca13425de6115b00ce7a35cf0d65bdb4fed43f6c43fdec','cycles':'45fd5b2d70581d0822c0dd5c965b0c35c09b440a442a575b0f638c2b914aa628','linux0049':'dd7860df3b63a78ca9af13b871a5b5e44d2e3aaef12da64f791094257fc4eac4','static':'2081159e5a28a02fa79a933c83fe0838a6efe778f1ccdd85a804c6f3d8ec9b3e'}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def need(c,m):
 if not c: raise SystemExit('FAIL: '+m)
for k,p in F.items(): need(p.is_file(),f'missing {p}'); need(sha(p)==E[k],f'{k} hash drift')
kd=F['kd'].read_text(errors='replace'); cy=F['cycles'].read_text(errors='replace'); l=json.loads(R.read_text())
need(kd.count('Breakpoint 0 hit')==0,'IPP error breakpoint fired')
need(kd.count('Breakpoint 1 hit')==1,'selector proof breakpoint count drift')
need('EV ENABLE_ENTRY' in kd and 'x1=5 x3=5' in kd,'IPP selector5 proof absent')
need(re.search(r'ffff\w+`\w+\s+ffffe700`d1a32000',kd,re.I),'CSID1 MMIO pointer proof absent')
need(re.search(r'ffff\w+`\w+\s+00000001',kd,re.I),'CSID1 index proof absent')
need('ffffe700`d1a32300  802b2000' in kd,'CFG0 drift')
need('ffffe700`d1a3235c  0eff0000 086f0000' in kd,'crop drift')
need('EV BIT14_NEGATIVE_BOUND THREE_LIVE_STARTS_COMPLETED' in kd,'bounded marker absent')
need('ffffe700`d1a32388  08700f00 08700f00 03b203ad 00ffffff' in kd,'end format-measure drift')
need('ffffe700`d1a320ac  00e11ff8' in kd,'end IPP status drift')
# Breakpoint must still be armed at bounded end.
post=kd.split('EV BIT14_NEGATIVE_BOUND THREE_LIVE_STARTS_COMPLETED',1)[1]
need('qccamisp8380+0x1ba04' in post,'error breakpoint not armed at bound')
for n in (2,3):
 for s in (f'CYCLE{n}_STOP_BEGIN',f'CYCLE{n}_START_BEGIN',f'CYCLE{n}_LIVE PID=',f'CYCLE{n}_UI_CONTROLS=Change camera,Switch to photo mode,Take video'): need(s in cy,f'missing {s}')
 m0=re.search(rf'([0-9T:+.\-]+) CYCLE{n}_START_BEGIN',cy); m1=re.search(rf'([0-9T:+.\-]+) CYCLE{n}_LIVE PID=',cy); need(m0 and m1,f'cycle{n} timestamps')
 need((datetime.fromisoformat(m1.group(1))-datetime.fromisoformat(m0.group(1))).total_seconds()>=12,f'cycle{n} live bound <12s')
need('TEST_END CAMERA_STOPPED' in cy,'camera stop evidence absent')
need(l['csid1']['error_time_actual_frame']=='0x0a500f00' and l['csid1']['programmed_expected_frame']=='0x08700f00','0049 geometry drift')
out={'schema':'sp11-e003h-windows-csid1-bit14-history-v1','accepted':True,'date':'2026-08-30','evidence_sha256':E,'qccamisp_error_branch_rva':'0x1ba04','tested_front_starts':3,'selector_proven_start':{'selector':5,'csid_index':1,'mmio_va':'ffffe700d1a32000'},'pre_enable':{'cfg0':'0x802b2000','hcrop':'0x0eff0000','vcrop':'0x086f0000','expected_frame':'0x08700f00','actual_frame':'0x00000000'},'bounded_end':{'expected_frame':'0x08700f00','actual_frame':'0x08700f00','width':3840,'height':2160,'hbi':'0x03b203ad','vbi':'0x00ffffff','ipp_status':'0x00e11ff8','ipp_bit14':False},'qccamisp_ipp_error_branch_hits':0,'bounded_windows_result':'Across one selector-proven CSID1 IPP start plus two timestamped/UI-confirmed Camera restarts, qccamisp never entered its IPP error branch while the breakpoint remained armed.','linux_0049_comparison':{'expected':'0x08700f00','error_time_actual':'0x0a500f00','actual_height':2640,'extra_lines':480,'bit14_seen':True},'classification':{'windows_bit14_absent_in_bounded_normal_sample':True,'universal_windows_bit14_absence_proven':False,'linux_0049_line_count_error_is_normal_windows_startup_transient':False,'linux_0049_line_count_error_is_concrete_parity_fault':True,'sensor_mode_change_justified':False,'causal_link_to_missing_vfe_epoch0_proven':False},'next_gate':'Statically close CSID680 vertical-crop active/shadow/update semantics: Linux readback matches Windows but error-time actual remains 3840x2640, while bounded Windows reaches actual=expected 3840x2160 without qccamisp IPP error. No Linux runtime or programming delta is authorized by this oracle.'}
t=json.dumps(out,indent=2,sort_keys=True)+'\n'; (H/'windows-csid1-bit14-history-oracle.json').write_text(t); (H/'EXTRACT.txt').write_text(t); print(t,end='')
