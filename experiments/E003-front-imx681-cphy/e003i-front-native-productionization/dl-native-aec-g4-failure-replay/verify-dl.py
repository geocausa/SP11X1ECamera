#!/usr/bin/env python3
"""Replay the exact archived DB attempt4 without any camera or boot access."""
from pathlib import Path
import hashlib, json, re, struct, subprocess, tempfile

HERE = Path(__file__).resolve().parent
BASE = HERE.parent
REPO = HERE.parents[3]
ARCHIVE = Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-db/attempt4-live-g4-fail-20260910T181907')
PINS = {
 'producer/STATS3A-G1.bin': '630551efdaf54c18909caab9cff7d252ce2c59e3eb9638a37a06520291504f76',
 'producer/STATS3A-G2.bin': 'cb5c776e6467c5891a0c5e4266a65cf446048e7f89da78e245a0a849e145204a',
 'producer/STATS3A-G3.bin': 'aa0aeae802fae4a3bf1a8246f3bca83546c593fdb4ec271c9a583ddaaa109c59',
 'STATS3A-FAIL-G4.bin': 'f9ac87f147edd0272f2f8f107383aa5ed25a0caff6b7bc143eed40fdaa1160a9',
 'TLBG-FAIL-G4.bin': 'd1328aa789806b770dd6e4bba0ce0ffdb3b0967ff4f94680083329f24875c7fa',
}
SOURCE_MAP = [
 ('dj-native-aec-request4-warmup-rebase','native-aec-request-loop.c'),
 ('cv-native-aec-offline-sensor-control-join','native-raw-control-join.c'),
 ('cu-native-aec-raw-stats-request-loop','native-raw-aec-loop.c'),
 ('cq-aec-output-imx681-control-adapter','native-imx681-control.c'),
 ('cr-native-aec-effective-analyzer-producer','native-effective-analyzers.c'),
 ('ct-native-aec-bhist-bank4-replay','native-bhist-bank4.c'),
 ('cf-native-aec-final-exposure-si','native-final-exposure.c'),
 ('ce-native-aec-final-target-producer','native-final-target.c'),
 ('cc-native-aec-adrc-darkboost-tail','native-aec-tail.c'),
 ('by-native-aec-method11-point-aggregation','native-target-aggregate.c'),
 ('cg-native-aec-qword-convergence-input','native-convergence.c'),
 ('ch-native-aec-t681-preview-arbitration','native-t681.c'),
 ('bk-native-aec-history-state','native-aec-state.c'),
 ('bj-native-aec-log103-coordinate','native-log103.c'),
]
def need(ok, message):
    if not ok:
        raise AssertionError(message)
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

for name, expected in PINS.items():
    need(sha(ARCHIVE / name) == expected, 'fixture hash: '+name)
paths = [ARCHIVE / name for name in list(PINS)[:4]]
pairs = []
for g, stats_path in enumerate(paths,1):
    tlbg_path = ARCHIVE / ('producer/TLBG-G%d.bin'%g if g<4 else 'TLBG-FAIL-G4.bin')
    s, t = stats_path.read_bytes(), tlbg_path.read_bytes()
    need(len(s)==331840 and len(t)==61472, 'pair sizes')
    need(struct.unpack_from('<IHH',s)==(0x54534133,1,64), 'stats header')
    need(struct.unpack_from('<HH',t,4)==(1,32), 'tlbg header')
    sg, ss, slot = struct.unpack_from('<QII',s,8)
    tg, ts, tslot = struct.unpack_from('<QII',t,8)
    need((sg,ss,slot)==(tg,ts,tslot) and sg==g and ss==g and slot<2, 'pair identity')
    pairs.append({'generation':g,'source_seq':ss,'slot':slot,'stats3a_sha256':sha(stats_path),'tlbg_sha256':sha(tlbg_path)})
sources=[BASE/d/f for d,f in SOURCE_MAP]+[BASE/SOURCE_MAP[2][0]/'native-stats3a.c']
# Exact source baseline, including every dependency header, prevents silently
# claiming this is a replay of the consumed runtime after later edits.
for directory, _ in SOURCE_MAP:
    for source in sorted((BASE/directory).glob('*.h')):
        sources.append(source)
for source in sources:
    rel=source.relative_to(REPO)
    original=subprocess.check_output(['git','show','8bc6598:'+str(rel)],cwd=REPO)
    need(hashlib.sha256(original).hexdigest()==sha(source),'runtime source changed: '+str(rel))

with tempfile.TemporaryDirectory(prefix='e003i-dl-') as td:
    exe=Path(td)/'replay-g4'
    command=['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
    for d,_ in SOURCE_MAP:
        command += ['-I',str(BASE/d)]
    command += [str(HERE/'replay-g4.c')]+[str(p) for p in sources if p.suffix=='.c']+['-lm','-o',str(exe)]
    subprocess.run(command,check=True)
    replay=subprocess.check_output([str(exe),*map(str,paths)],text=True)
need('G4_FAILURE_REPRODUCED=PASS STATE_AND_CONTROL_OUTPUT_UNCHANGED=PASS' in replay,'replay')
(HERE/'REPLAY.txt').write_text(replay)

run=(ARCHIVE/'RUN.txt').read_text()
need('DB_AEC_FAIL G=4 RC=-142 WRITES=3' in run,'live failure')
need('DB_FAIL_PAIR_SAVED G=4' in run and 'PINNED_FOR_REBOOT' in run,'live disposition')
need('DB_AEC_ACCEPT G=4' not in run,'G4 must not be accepted')
writes=[]
for m in re.finditer(r'DB_SENSOR_WRITE_OK SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) START_NS=(\d+) END_NS=(\d+) ELAPSED_NS=(\d+) COMPLETED_G=(\d+)',run):
    keys=['source','after_generation','request','claimed_effect_generation','fll','exposure','again','dgain','start_ns','end_ns','elapsed_ns','completed_generation']
    row=dict(zip(keys,map(int,m.groups())))
    need(row['end_ns']-row['start_ns']==row['elapsed_ns'],'write time')
    need(row['after_generation']==row['completed_generation'],'DQBUF gate')
    writes.append(row)
need(len(writes)==3,'exactly three writes')
need([[w['fll'],w['exposure'],w['again'],w['dgain']] for w in writes]==[[3562,3554,851,256],[3562,3554,960,556],[7116,7108,960,1111]],'live tuples match replay')
golden=(ARCHIVE/'GOLDEN-RETURN.txt').read_text()
need('status=PASS' in golden and 'camera_modules=absent' in golden and 'saved_entry=sp11-audio-fullio-v19c' in golden,'archived Golden return')
cy=json.loads((BASE/'cy-bounded-imx681-latch-runtime/RESULT.json').read_text())
means=[float(m.group(1)) for m in re.finditer(r'BHIST G=\d total=2073600 mean=([^\n]+)',replay)]
need(len(means)==4,'bhist rows')
source_manifest={str(p.relative_to(REPO)):sha(p) for p in sources}
result={
 'schema':'sp11-e003i-dl-exact-g4-failure-replay-v1',
 'status':'PASS_OFFLINE_FAILURE_LOCALIZATION',
 'runtime_base_commit':'8bc6598440f5ddeb36587e140bf64f48eaee38bf',
 'archive':str(ARCHIVE),
 'pairs':pairs,
 'live_sensor_writes':writes,
 'g4':{'cu_rc':-132,'cv_rc':-142,'short_convergence_target':24819566146,
       'table_maximum':6133333272,'target_over_table_maximum':24819566146/6133333272,
       'delayed_s1_request':4,'delayed_s1_retained_exposure':197553039,
       'short_metering_target':32233622719,'safe_metering_target':45127069396,
       'caller_state_unchanged_on_error':True,'caller_control_output_unchanged_on_error':True},
 'measurement':{'frame_luma':[0.898956835,0.886852384,0.886802614,0.883978605],
                'bhist_means':means,'bhist_g4_over_g1':means[3]/means[0],
                'g4_brightness_increase_observed':False},
 'timing_comparison':{'cy_single_exposure_step_elapsed_ns':cy['runtime']['step_ioctl_elapsed_ns'],
                      'db_first_full_tuple_elapsed_ns':writes[0]['elapsed_ns'],
                      'db_over_cy_duration':writes[0]['elapsed_ns']/cy['runtime']['step_ioctl_elapsed_ns'],
                      'exact_group_hold_release_time_observed':False,
                      'exact_optical_latch_frame_proven_by_db':False},
 'golden_return':'PASS',
 'candidate_retired':True,
 'aec_math_changed':False,'hardware_tests_started_by_dl':0,
 'missing_windows_stage':'PopulateOutput -> CapExposure; see CAP-STAGE-RESULT.json',
 'next_gate':'Recover and replay the omitted Windows internal CapExposure stage, including exact request-local bounds and branch inputs, before CH arbitration. Sensor-control-to-statistics timing remains a separate unresolved association.',
 'limitations':['G5/G6 raw pairs were not retained by the consumed helper after G4 failure.',
                'Near-constant luma and a slower ioctl are evidence of an unresolved feedback association, not proof of an exact replacement delay.',
                'T681 regular policy-0 rejection remains authoritative; no clamp is introduced.'],
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
(HERE/'SOURCE-HASHES.json').write_text(json.dumps(source_manifest,indent=2)+'\n')
summary='\n'.join([
 'FIXTURE_HASHES=PASS','PAIRED_IDENTITIES_G1_G4=PASS','RUNTIME_BASE_SOURCES=UNCHANGED',
 'STRICT_BUILD=PASS','EXACT_LIVE_G1_G3_TUPLES=PASS','EXACT_G4_MINUS142=PASS',
 'G4_ERROR_STATE_AND_OUTPUT_ATOMICITY=PASS','GOLDEN_RETURN=PASS',
 'BHIST_G4_OVER_G1='+str(means[3]/means[0]),
 'DB_FIRST_IOCTL_OVER_CY='+str(writes[0]['elapsed_ns']/cy['runtime']['step_ioctl_elapsed_ns']),
 'AEC_PARITY=NOT_CLOSED','DL_VERIFY=PASS'])+'\n'
(HERE/'VERIFY-RESULT.txt').write_text(summary)
print(summary)
