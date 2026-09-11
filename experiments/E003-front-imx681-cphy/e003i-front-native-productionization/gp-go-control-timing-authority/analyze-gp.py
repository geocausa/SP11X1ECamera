#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,statistics
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
A=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-go/attempt1-pass-twentyseven-frame-20260911T2145')
RUN=A/'runtime-output/RUN.txt'
ATT=A/'ATTEMPT1-PASS.json'
MAN=A/'MANIFEST.sha256'
SCHED=BASE/'go-twentyseven-frame-live-r5-r27/build/helper/native-db-schedule.h'
SRC=BASE/'en-r5-r9-live-producer-integration/native-db-schedule.c'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
need(A.is_dir() and RUN.is_file() and ATT.is_file() and MAN.is_file(),'GO archive missing')
# Archive is immutable evidence: verify every manifest member before analysis.
import subprocess
subprocess.run(['sha256sum','-c','MANIFEST.sha256'],cwd=A,check=True,stdout=subprocess.DEVNULL)
att=json.loads(ATT.read_text())
need(att['status']=='PASS_CAPTURE_GO_TWENTYSEVEN_FRAME_R5_R27','GO pass authority')
need(att['stream_attempts']==1 and not att['same_boot_stream_retry_performed'],'one-shot authority')
need(att['golden_return'] and att['candidate_retired'],'GO closure')
s=RUN.read_text(errors='replace')
# Static scheduler law from the exact GO build.
h=SCHED.read_text()
for tok in ('#define E003I_DB_FRAME_COUNT 27U','#define E003I_DB_WRITTEN_SOURCE_GENERATIONS 3U','#define E003I_DB_STATS_TO_REQUEST_DELAY 3U','#define E003I_DB_WRITE_AFTER_OFFSET 1U','#define E003I_DB_WRITE_TO_EFFECT_DELAY 2U'):
    need(tok in h,'scheduler header '+tok)
source=SRC.read_text()
need('source = completed_video_generation - E003I_DB_WRITE_AFTER_OFFSET;' in source,'release source law')
need('logical_request_frame =\n        (uint64_t)source + E003I_DB_STATS_TO_REQUEST_DELAY;' in source,'request law')
need('expected_effect_generation =\n        completed_video_generation + E003I_DB_WRITE_TO_EFFECT_DELAY;' in source,'effect law')
# Completed frame boundaries use poll completion as the nearest logged timestamp preceding DQBUF.
bounds=[]
for m in re.finditer(r'POLL(\d+)_START_NS=(\d+) END_NS=(\d+) ELAPSED_NS=(\d+) RC=1 REVENTS=0x1',s):
    bounds.append({'generation':int(m.group(1))+1,'end_ns':int(m.group(3)),'poll_elapsed_ns':int(m.group(4))})
need([x['generation'] for x in bounds]==list(range(1,28)),'27 ordered DQBUF boundaries')
bmap={x['generation']:x['end_ns'] for x in bounds}
intervals=[(bounds[i+1]['end_ns']-bounds[i]['end_ns'])/1e6 for i in range(len(bounds)-1)]
# Directly exercised sensor writes.
pat=r'DB_SENSOR_WRITE_OK SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) START_NS=(\d+) END_NS=(\d+) ELAPSED_NS=(\d+) COMPLETED_G=(\d+)'
writes=[]
for m in re.finditer(pat,s):
    src,after,request,effect,fll,exp,again,dgain,start,end,elapsed,completed=map(int,m.groups())
    need(src in (1,2,3) and after==src+1 and request==src+3 and effect==src+3,'write mapping')
    need(completed==after and end-start==elapsed,'write timing identity')
    need(after+1 in bmap,'next boundary')
    row={'source_generation':src,'write_after_generation':after,'logical_request_generation':request,'expected_effect_generation':effect,
         'start_after_boundary_ms':(start-bmap[after])/1e6,'write_elapsed_ms':elapsed/1e6,'end_before_next_boundary_ms':(bmap[after+1]-end)/1e6,
         'controls':{'fll':fll,'exposure':exp,'analogue_gain':again,'digital_gain':dgain}}
    need(0 <= row['start_after_boundary_ms'] < 1.0,'write did not start tightly after gate')
    need(row['end_before_next_boundary_ms'] > 0,'write crossed next DQBUF')
    writes.append(row)
need([x['source_generation'] for x in writes]==[1,2,3],'exact three live writes')
need('DB_AEC_SCHEDULE_PASS ACCEPTED_G=1..27 WRITES=3 RELEASE=G1@G2,G2@G3,G3@G4 EFFECT=G4,G5,G6' in s,'schedule pass marker')
# A finite 27-frame continuous replay can only claim effects for sources through G24.
finite_sources=list(range(1,25))
finite_releases=[g+1 for g in finite_sources]
finite_effects=[g+3 for g in finite_sources]
need(finite_effects[-1]==27 and finite_releases[-1]==25,'finite horizon algebra')
result={
 'schema':'sp11-e003i-gp-go-control-timing-authority-v1',
 'status':'PASS_OFFLINE_GO_CONTROL_TIMING_AUTHORITY',
 'source_archive':str(A),'source_archive_manifest_sha256':sha(MAN),'source_archive_manifest_entries':sum(1 for _ in MAN.open()),
 'go_attempt_status':att['status'],'live_frames':27,'live_sensor_write_sources':[1,2,3],
 'stats_to_request_delay_generations':3,'write_after_source_offset_generations':1,'write_to_effect_delay_generations':2,
 'live_write_observations':writes,
 'frame_boundary_interval_ms':{'minimum':min(intervals),'median':statistics.median(intervals),'maximum':max(intervals),
                               'first_six':intervals[:6],'post_g6_minimum':min(intervals[5:])},
 'observed_write_elapsed_ms':{'minimum':min(x['write_elapsed_ms'] for x in writes),'maximum':max(x['write_elapsed_ms'] for x in writes)},
 'observed_end_before_next_boundary_ms':{'minimum':min(x['end_before_next_boundary_ms'] for x in writes),'maximum':max(x['end_before_next_boundary_ms'] for x in writes)},
 'finite_r27_continuous_replay_design':{'queue_generations':list(range(1,28)),'release_source_generations':finite_sources,'release_after_completed_generations':finite_releases,'effects_inside_capture_generations':finite_effects},
 'continuous_physical_writes_proven':False,
 'safe_next_step':'offline scheduler extension and deterministic replay only',
 'camera_runtime_performed':False,
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('GP_GO_ARCHIVE_MANIFEST=PASS')
print('GP_LIVE_WRITE_TIMING=3/3 PASS')
print(f"GP_MIN_WRITE_MARGIN_MS={result['observed_end_before_next_boundary_ms']['minimum']:.6f}")
print('GP_R27_FINITE_SCHEDULER_TARGET=G1_G24_WRITES_EFFECT_G4_G27')
print('GP_VERIFY=PASS')
