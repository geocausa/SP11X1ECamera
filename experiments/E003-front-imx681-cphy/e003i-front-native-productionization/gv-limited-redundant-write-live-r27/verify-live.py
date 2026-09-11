#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,math,re,struct
D=Path(__file__).resolve().parent; O=D/'runtime-output'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def frombits(u): return struct.unpack('<f',struct.pack('<I',u))[0]
run=(O/'RUN.txt').read_text(errors='replace'); dmesg=(D/'DMESG.txt').read_text(errors='replace'); tx=(O/'CONTROL-TRANSACTION.txt').read_text(errors='replace')
need('HELPER_RC=0' in run,'helper rc'); need('STREAMON_OK_ASYNC' in run and 'STREAMOFF_OK' in run,'stream lifecycle'); need('E003I_GM_PRODUCER=PASS' in run,'GM producer')
for bad in ('PINNED_FOR_REBOOT:','DB_AEC_FAIL','DB_AEC_OWNERSHIP_FAIL','DB_SCHEDULE_QUEUE_FAIL','GU_BOUNDARY_RELEASE_FAIL','DB_SENSOR_WRITE_FAIL','EN_GAIN_FEED_FAIL','E003I_GM_PRODUCER=FAIL','GN_DQBUF_MISMATCH'):
    need(bad not in run,bad)
cycle=[0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2]
for i in range(27):
    need(re.search(rf'DQBUF{i}_INDEX={cycle[i]} BYTESUSED=7778304 SEQUENCE={i}\b',run),f'dqbuf{i}')
    need(f'DB_VIDEO_COMPLETION_PUBLISH G={i+1}' in run,f'completion G{i+1}')
for req in range(7,28): need(f'E003I_ES_IQ_CONSUMED R={req} FRAME={req} SLOT={(req-7)&1}' in dmesg,f'kernel IQ R{req}')
need('X1E front PIX completed provider-owned bounded twenty-seven-frame live requeue' in dmesg,'kernel completion')
# Exact AEC tuples determine whether G4..G6 were allowed to write.
pat=r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+) FLL=(\d+) VB=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) ISP=0x([0-9a-fA-F]{8}) RELEASED_AT_G=(\d+) RELEASE_SOURCE=(\d+) EFFECT=(\d+)'
acc=[]
for m in re.finditer(pat,run):
    x=list(m.groups()); x[7]=int(x[7],16); acc.append(tuple(int(v) for v in x))
need(len(acc)==27,'27 AEC accepts')
def key(r): return r[2:8]
for r in acc:
    g,req,fll,vb,exp,ag,dg,isp,rel,src,effect=r
    need(req==g+3 and math.isfinite(frombits(isp)) and frombits(isp)>0,f'AEC G{g}')
    if g==1: need((rel,src,effect)==(0,0,0),'G1 release')
    else: need((rel,src,effect)==(g,g-1,g+2),f'release G{g}')
expected_redundant=[]; expected_changed=[]; last=acc[2]
for source in range(4,7):
    if key(acc[source-1])==key(last): expected_redundant.append(source); last=acc[source-1]
    else: expected_changed.append(source)
# Parse successful userspace control-ioctl path calls and branch logs.
# DB_SENSOR_WRITE_OK means the helper called VIDIOC_S_EXT_CTRLS successfully;
# the V4L2 core may still dedupe an unchanged cluster before driver .s_ctrl.
wpat=r'DB_SENSOR_WRITE_OK SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) START_NS=(\d+) END_NS=(\d+) ELAPSED_NS=(\d+) COMPLETED_G=(\d+)'
writes=[tuple(map(int,m.groups())) for m in re.finditer(wpat,run)]
write_sources=[r[0] for r in writes]
need(write_sources[:3]==[1,2,3],'startup write sources'); need(write_sources[3:]==expected_redundant,'conditional write sources'); need(3<=len(writes)<=6,'write count bound')
allows=[int(m.group(1)) for m in re.finditer(r'GU_REDUNDANT_WRITE_ALLOW SOURCE=(\d+) AFTER_G=',run)]
need(allows==expected_redundant,'redundant allow logs')
changed=[int(m.group(1)) for m in re.finditer(r'GU_SENSOR_WRITE_SHADOW_CHANGED SOURCE=(\d+) AFTER_G=',run)]
need(changed==expected_changed,'changed shadow logs')
bounded=[int(m.group(1)) for m in re.finditer(r'GU_SENSOR_WRITE_SHADOW_BOUND SOURCE=(\d+) AFTER_G=',run)]
need(bounded==list(range(7,27)),'bounded shadow G7..G26')
# No changed conditional source may reach the real ioctl path.
need(not (set(expected_changed)&set(write_sources)),'changed control reached ioctl path')
marker=re.search(r'GU_LIMITED_SCHEDULE_PASS ACCEPTED_G=1\.\.27 RELEASED_SOURCES=G1\.\.G26 PHYSICAL_WRITES=(\d+) REDUNDANT=(\d+) CHANGED_SHADOW=(\d+) BOUND_SHADOW=(\d+) PENDING=G27 EFFECT_RANGE=G4\.\.G29',run)
need(marker,'final schedule marker'); pw,red,ch,bnd=map(int,marker.groups()); need((pw,red,ch,bnd)==(len(writes),len(expected_redundant),len(expected_changed),20),'final accounting')
# V4L2 core explicitly suppresses .s_ctrl for an unchanged cluster. The GV
# G4..G6 tuples are exact equals of the already-current G3 tuple, so those
# successful S_EXT_CTRLS calls must *not* become driver/hardware transactions.
core=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src/drivers/media/v4l2-core/v4l2-ctrls-core.c').read_text(errors='replace')
need('if (ret || !set || !cluster_changed(master))\n\t\treturn ret;' in core,'V4L2 unchanged-cluster dedupe authority')
need(core.index('if (ret || !set || !cluster_changed(master))') < core.index('ret = call_op(master, s_ctrl);'),'V4L2 dedupe before s_ctrl')
txlines=[x for x in tx.splitlines() if 'AM request controls:' in x]
need(len(txlines)==4,'bootstrap + G1..G3 hardware transactions only')
need('FLL=3562 exposure=3554 again=0x000 dgain=0x0100 ret=0' in txlines[0],'bootstrap tx')
for r in writes[:3]:
    src,after,req,effect,fll,exp,ag,dg,*_=r
    needle=f'FLL={fll} exposure={exp} again=0x{ag:03x} dgain=0x{dg:04x} ret=0'
    need(any(needle in x for x in txlines[1:]),f'hardware tx G{src}')
# Redundant G4..G6 ioctls are expected to return quickly without driver .s_ctrl.
need(expected_redundant==[4,5,6] and not expected_changed,'GV observed redundant branch')
for r in writes[3:]:
    need(r[10] < 1_000_000,f'redundant ioctl G{r[0]} unexpectedly slow')
# Producer coverage and deadline.
prod=json.loads((O/'producer/RESULT.json').read_text()); need(prod['status']=='PASS' and len(prod['rows'])==24,'producer')
deadline={}; caps={}
for row in prod['rows'][1:]:
    req=row['request_target']; need(row.get('submitted_live') is True,f'R{req} submit'); cap=O/'producer'/f'R{req}-dynamic.bin'; need(cap.is_file() and cap.stat().st_size==41088 and sha(cap)==row['capsule_sha256'],f'R{req} capsule'); p=float(row['gain_wait_ms'])+float(row['total_process_ms'])+float(row.get('submit_ms',0)); need(p<33.333333,f'R{req} deadline'); deadline[str(req)]=p; caps[str(req)]=sha(cap)
for bad in ('TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup','Kernel panic'): need(bad.lower() not in dmesg.lower(),'kernel '+bad)
# Capture files.
hashes={'qc10c':[],'tlbg':[],'stats3a':[]}
for i in range(27):
    for k,pfx,size in [('qc10c','QC10C',7778304),('tlbg','TLBG',61472),('stats3a','STATS3A',331840)]:
        p=O/f'{pfx}-{i}.bin'; need(p.is_file() and p.stat().st_size==size,f'{pfx}-{i}'); hashes[k].append(sha(p))
result={'schema':'sp11-e003i-gv-redundant-ioctl-dedupe-live-r27-v1','status':'PASS_CAPTURE_GV_REDUNDANT_IOCTL_DEDUPE_R27','runtime_performed':True,'same_boot_retry_performed':False,'frames':27,'stats_generations':27,'producer_generations':24,'requests':list(range(5,28)),'successful_control_ioctl_calls':len(writes),'control_ioctl_sources':write_sources,'startup_sensor_hardware_sources':[1,2,3],'stream_sensor_hardware_transactions':3,'sensor_hardware_transactions_including_bootstrap':len(txlines),'redundant_ioctl_sources':expected_redundant,'redundant_ioctl_v4l2_deduped_before_driver_s_ctrl':True,'changed_shadow_sources':expected_changed,'bounded_shadow_sources':bounded,'post_g3_sensor_hardware_write_performed':False,'continuous_scheduler_release_sources':list(range(1,27)),'pending_source_at_end':27,'streamoff':True,'kernel_health':'PASS','deadline_ms':deadline,'capsules':caps,'capture_sha256':hashes,'changed_post_g3_controls_proven':False,'redundant_post_g3_ioctl_lifecycle_proven':len(expected_redundant)>0,'new_post_g3_sensor_hardware_write_count':0,'golden_return_required':True}
(O/'LIVE-RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print(f'GV_LIVE_FRAMES=27 CONTROL_IOCTLS={len(writes)} REDUNDANT_DEDUPED={len(expected_redundant)} CHANGED_SHADOW={len(expected_changed)}')
print('GV_POST_G3_SENSOR_HW_WRITES=0 V4L2_REDUNDANT_DEDUPE=PASS')
print('GV_STREAMOFF=PASS KERNEL_HEALTH=PASS')
print('GV_MAX_PIPELINE_MS=%.6f'%max(deadline.values()))
print('GV_CAPTURE_VERIFY=PASS')
