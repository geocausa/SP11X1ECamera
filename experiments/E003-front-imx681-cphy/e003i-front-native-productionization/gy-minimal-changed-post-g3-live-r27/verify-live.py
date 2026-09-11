#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,math,re,struct
D=Path(__file__).resolve().parent; O=D/'runtime-output'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def frombits(u): return struct.unpack('<f',struct.pack('<I',u))[0]
run=(O/'RUN.txt').read_text(errors='replace'); dmesg=(D/'DMESG.txt').read_text(errors='replace'); tx=(O/'CONTROL-TRANSACTION.txt').read_text(errors='replace')
need('HELPER_RC=0' in run,'helper rc'); need('STREAMON_OK_ASYNC' in run and 'STREAMOFF_OK' in run,'stream lifecycle'); need('E003I_GM_PRODUCER=PASS' in run,'producer marker')
for bad in ('PINNED_FOR_REBOOT:','DB_AEC_FAIL','DB_AEC_OWNERSHIP_FAIL','DB_SCHEDULE_QUEUE_FAIL','GX_BOUNDARY_RELEASE_FAIL','DB_SENSOR_WRITE_FAIL','EN_GAIN_FEED_FAIL','E003I_GM_PRODUCER=FAIL','GN_DQBUF_MISMATCH'):
    need(bad not in run,bad)
cycle=[0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2]
for i in range(27):
    need(re.search(rf'DQBUF{i}_INDEX={cycle[i]} BYTESUSED=7778304 SEQUENCE={i}\b',run),f'dqbuf{i}')
    need(f'DB_VIDEO_COMPLETION_PUBLISH G={i+1}' in run,f'completion G{i+1}')
    need(re.search(rf'TLBG_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=61472\b',run),f'tlbg{i}')
    need(re.search(rf'STATS3A_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=331840\b',run),f'stats{i}')
for req in range(7,28): need(f'E003I_ES_IQ_CONSUMED R={req} FRAME={req} SLOT={(req-7)&1}' in dmesg,f'kernel IQ R{req}')
need('X1E front PIX completed provider-owned bounded twenty-seven-frame live requeue' in dmesg,'kernel 27-frame completion')
# Native AEC controls and delayed-release ownership.
pat=r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+) FLL=(\d+) VB=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) ISP=0x([0-9a-fA-F]{8}) RELEASED_AT_G=(\d+) RELEASE_SOURCE=(\d+) EFFECT=(\d+)'
acc=[]
for m in re.finditer(pat,run):
    x=list(m.groups()); x[7]=int(x[7],16); acc.append(tuple(int(v) for v in x))
need(len(acc)==27,'27 AEC accepts')
def key(r): return r[2:8]
for r in acc:
    g,req,fll,vb,exp,ag,dg,isp,rel,src,effect=r
    need(req==g+3 and vb==fll-2160 and exp<=((fll-4)&~1),f'geometry G{g}')
    need(math.isfinite(frombits(isp)) and frombits(isp)>0,f'ISP G{g}')
    if g==1: need((rel,src,effect)==(0,0,0),'G1 release')
    else: need((rel,src,effect)==(g,g-1,g+2),f'release G{g}')
need(key(acc[2])==key(acc[3]),'native G4 must equal last-applied native G3 for sentinel authority')
need(acc[3][6]==1471,'native G4 dgain authority')
# Sentinel must apply exactly once and never be suppressed.
allow=re.findall(r'GX_SENTINEL_WRITE_ALLOW SOURCE=4 AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) NATIVE_DGAIN=(\d+) SENTINEL_DGAIN=(\d+)',run)
need(allow==[('5','7','7','1471','1472')],'exact G4 sentinel allow')
need('GX_SENTINEL_SUPPRESSED SOURCE=4' not in run,'sentinel suppressed')
# Successful real-path control ioctls: native G1..G3 plus changed sentinel G4 only.
wpat=r'DB_SENSOR_WRITE_OK SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) START_NS=(\d+) END_NS=(\d+) ELAPSED_NS=(\d+) COMPLETED_G=(\d+)'
writes=[tuple(map(int,m.groups())) for m in re.finditer(wpat,run)]
need([r[0] for r in writes]==[1,2,3,4],'control ioctl sources G1..G4')
for r in writes:
    src,after,req,effect,fll,exp,ag,dg,start,end,elapsed,completed=r
    need(after==src+1 and req==src+3 and effect==src+3 and completed==after and end-start==elapsed,f'write mapping G{src}')
need(writes[3][4:8]==(7116,7108,960,1472),'G4 sentinel physical tuple')
shadow=[int(m.group(1)) for m in re.finditer(r'GX_SENSOR_WRITE_SHADOW SOURCE=(\d+) AFTER_G=',run)]
need(shadow==list(range(5,27)),'G5..G26 shadow-only')
marker=re.search(r'GX_SENTINEL_SCHEDULE_PASS ACCEPTED_G=1\.\.27 RELEASED_SOURCES=G1\.\.G26 CONTROL_IOCTLS=(\d+) SENTINEL_WRITES=(\d+) SENTINEL_SUPPRESSED=(\d+) BOUND_SHADOW=(\d+) PENDING=G27 EFFECT_RANGE=G4\.\.G29',run)
need(marker and tuple(map(int,marker.groups()))==(4,1,0,22),'final sentinel accounting')
# Driver transaction evidence: bootstrap + G1..G3 + changed G4 sentinel = exactly five.
txlines=[x for x in tx.splitlines() if 'AM request controls:' in x]
need(len(txlines)==5,'exactly five driver/hardware transactions including bootstrap')
need('FLL=3562 exposure=3554 again=0x000 dgain=0x0100 ret=0' in txlines[0],'bootstrap transaction')
for r in writes[:3]:
    src,after,req,effect,fll,exp,ag,dg,*_=r; needle=f'FLL={fll} exposure={exp} again=0x{ag:03x} dgain=0x{dg:04x} ret=0'; need(any(needle in x for x in txlines[1:]),f'native hardware G{src}')
need(any('FLL=7116 exposure=7108 again=0x3c0 dgain=0x05c0 ret=0' in x for x in txlines),'sentinel hardware transaction')
# With all later sensor writes suppressed, the sentinel remains the current hardware tuple.
post=(O/'CONTROLS-POST-AEC.txt').read_text(errors='replace')
for x in ('vertical_blanking: 4956','exposure: 7108','analogue_gain: 960','digital_gain: 1472'): need(x in post,'post '+x)
# Producer coverage/deadline.
prod=json.loads((O/'producer/RESULT.json').read_text()); need(prod['status']=='PASS' and len(prod['rows'])==24,'producer manifest')
deadline={}; caps={}
for row in prod['rows'][1:]:
    req=row['request_target']; need(row.get('submitted_live') is True,f'R{req} submit'); cap=O/'producer'/f'R{req}-dynamic.bin'; need(cap.is_file() and cap.stat().st_size==41088 and sha(cap)==row['capsule_sha256'],f'R{req} capsule'); p=float(row['gain_wait_ms'])+float(row['total_process_ms'])+float(row.get('submit_ms',0)); need(p<33.333333,f'R{req} deadline'); deadline[str(req)]=p; caps[str(req)]=sha(cap)
for bad in ('TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup','Kernel panic'): need(bad.lower() not in dmesg.lower(),'kernel '+bad)
hashes={'qc10c':[],'tlbg':[],'stats3a':[]}
for i in range(27):
    for k,pfx,size in [('qc10c','QC10C',7778304),('tlbg','TLBG',61472),('stats3a','STATS3A',331840)]:
        p=O/f'{pfx}-{i}.bin'; need(p.is_file() and p.stat().st_size==size,f'{pfx}-{i}'); hashes[k].append(sha(p))
result={'schema':'sp11-e003i-gy-minimal-changed-post-g3-live-r27-v1','status':'PASS_CAPTURE_GY_MINIMAL_CHANGED_POST_G3_R27','runtime_performed':True,'same_boot_retry_performed':False,'frames':27,'stats_generations':27,'producer_generations':24,'continuous_scheduler_release_sources':list(range(1,27)),'control_ioctl_sources':[1,2,3,4],'startup_native_sensor_sources':[1,2,3],'sentinel_source':4,'sentinel_write_after_generation':5,'sentinel_expected_effect_generation':7,'sentinel_native_digital_gain_code':1471,'sentinel_applied_digital_gain_code':1472,'sentinel_relative_gain_delta_percent':0.06798096532971698,'new_post_g3_sensor_hardware_transaction_count':1,'new_post_g3_sensor_hardware_sources':[4],'g5_g26_shadow_sources':list(range(5,27)),'sensor_hardware_transactions_including_bootstrap':5,'post_controls':{'fll':7116,'vertical_blanking':4956,'exposure':7108,'analogue_gain_code':960,'digital_gain_code':1472},'streamoff':True,'kernel_health':'PASS','deadline_ms':deadline,'capsules':caps,'capture_sha256':hashes,'changed_post_g3_sensor_transport_proven':True,'production_native_changed_post_g3_feedback_proven':False,'synthetic_transport_sentinel':True,'golden_return_required':True}
(O/'LIVE-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('GY_LIVE_FRAMES=27 SENTINEL_HW_TRANSACTION=1 SOURCE=G4 EFFECT=G7')
print('GY_DGAIN_SENTINEL=1471_TO_1472 G5_G26_SHADOW=PASS')
print('GY_STREAMOFF=PASS KERNEL_HEALTH=PASS')
print('GY_MAX_PIPELINE_MS=%.6f'%max(deadline.values()))
print('GY_CAPTURE_VERIFY=PASS')
