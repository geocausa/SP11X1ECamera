#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,statistics,subprocess,tempfile
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive')
ARCH={
 'GO':ROOT/'e003i-go/attempt1-pass-twentyseven-frame-20260911T2145',
 'GS':ROOT/'e003i-gs/attempt1-pass-continuous-shadow-20260911T221117',
 'GV':ROOT/'e003i-gv/attempt1-helper-pass-verifier-audit-20260911T222625',
 'GY':ROOT/'e003i-gy/attempt1-pass-minimal-changed-sentinel-20260911T224155',
 'HC':ROOT/'e003i-hc/attempt1-pass-no-cap-release-20260912T060723',
}
DM=BASE/'dm-windows-internal-cap-bounds/RESULT.json'
GZ=BASE/'gz-native-response-threshold-analysis'
HA=BASE/'ha-native-cap-release-one-write-policy'
HB=BASE/'hb-native-cap-release-helper-integration'
CV=BASE/'cv-native-aec-offline-sensor-control-join'; CU=BASE/'cu-native-aec-raw-stats-request-loop'; CQ=BASE/'cq-aec-output-imx681-control-adapter'; CR=BASE/'cr-native-aec-effective-analyzer-producer'; CT=BASE/'ct-native-aec-bhist-bank4-replay'; DN=BASE/'dn-native-aec-internal-cap'; CF=BASE/'cf-native-aec-final-exposure-si'; CE=BASE/'ce-native-aec-final-target-producer'; CC=BASE/'cc-native-aec-adrc-darkboost-tail'; BY=BASE/'by-native-aec-method11-point-aggregation'; CG=BASE/'cg-native-aec-qword-convergence-input'; CH=BASE/'ch-native-aec-t681-preview-arbitration'; BK=BASE/'bk-native-aec-history-state'; BJ=BASE/'bj-native-aec-log103-coordinate'
CAP=6133333088

def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
# Parent authorities and archive immutability.
need(json.loads((GZ/'RESULT.json').read_text())['status']=='PASS_OFFLINE_RESPONSE_THRESHOLD_CENSORED_BY_PREVIEW_CAP','GZ')
need(json.loads((HA/'RESULT.json').read_text())['status']=='PASS_OFFLINE_NATIVE_CAP_RELEASE_ONE_WRITE_POLICY','HA')
need(json.loads((HB/'RESULT.json').read_text())['status']=='PASS_OFFLINE_NATIVE_CAP_RELEASE_HELPER_INTEGRATION','HB')
manifest={}
for name,a in ARCH.items():
    subprocess.run(['sha256sum','-c','MANIFEST.sha256'],cwd=a,check=True,stdout=subprocess.DEVNULL)
    manifest[name]=sha(a/'MANIFEST.sha256')
# Compile the same native replay used by GZ.
with tempfile.TemporaryDirectory(prefix='e003i-hd-') as td0:
    td=Path(td0); exe=td/'replay'
    inc=[CV,CU,CQ,CR,CT,DN,CF,CE,CC,BY,CG,CH,BK,BJ]
    src=[CV/'native-raw-control-join.c',CU/'native-raw-aec-loop.c',CU/'native-stats3a.c',CQ/'native-imx681-control.c',CR/'native-effective-analyzers.c',CT/'native-bhist-bank4.c',DN/'native-aec-request-loop.c',DN/'native-internal-cap.c',CF/'native-final-exposure.c',CE/'native-final-target.c',CC/'native-aec-tail.c',BY/'native-target-aggregate.c',CG/'native-convergence.c',CH/'native-t681.c',BK/'native-aec-state.c',BJ/'native-log103.c',GZ/'replay-aec-cap.c']
    cmd=['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
    for x in inc: cmd += ['-I',str(x)]
    cmd += [str(x) for x in src]+['-lm','-o',str(exe)]
    subprocess.run(cmd,check=True)
    replay_sha=sha(exe)
    rx=re.compile(r'G=(\d+) LUMA=([0-9.eE+-]+).*? CONV_SHORT=(\d+) CAP_SHORT=(\d+).*? FLL=(\d+) VB=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) ISP=([0-9.eE+-]+)')
    runs={}
    for name,a in ARCH.items():
        out=subprocess.check_output([str(exe),str(a/'runtime-output')],text=True)
        rows=[]
        for line in out.splitlines():
            m=rx.fullmatch(line); need(m,f'{name}: {line}')
            g,luma,conv,capv,fll,vb,exp,ag,dg,isp=m.groups()
            rows.append({'generation':int(g),'request':int(g)+3,'luma':float(luma),'convergence':int(conv),'cap_output':int(capv),'ratio_to_cap':int(conv)/CAP,'fll':int(fll),'vblank':int(vb),'exposure':int(exp),'again':int(ag),'dgain':int(dg),'isp':float(isp)})
        need([r['generation'] for r in rows]==list(range(1,28)),name+' rows')
        runs[name]=rows
# All five Linux R27 captures stayed capped after G3; HC gate must have made no later write.
linux_summary={}
for name,rows in runs.items():
    post=rows[2:]
    need(all(r['convergence']>CAP and r['cap_output']==CAP for r in post),name+' G3..G27 cap')
    steady=rows[7:24]
    linux_summary[name]={
      'g3_ratio_to_cap':rows[2]['ratio_to_cap'],
      'g4_ratio_to_cap':rows[3]['ratio_to_cap'],
      'g5_ratio_to_cap':rows[4]['ratio_to_cap'],
      'g27_ratio_to_cap':rows[26]['ratio_to_cap'],
      'minimum_ratio_g3_g27':min(r['ratio_to_cap'] for r in post),
      'maximum_ratio_g3_g27':max(r['ratio_to_cap'] for r in post),
      'steady_luma_mean_g8_g24':statistics.mean(r['luma'] for r in steady),
      'steady_luma_cv_percent_g8_g24':statistics.stdev(r['luma'] for r in steady)/statistics.mean(r['luma'] for r in steady)*100,
      'cap_release_observed':False,
    }
hc_attempt=json.loads((ARCH['HC']/'ATTEMPT1-PASS.json').read_text())
need(hc_attempt['status']=='PASS_CAPTURE_HC_NO_CAP_RELEASE_R27','HC result')
need(hc_attempt['post_g3_native_write_count']==0,'HC later writes')
# Windows DM proves an ordinary preview can legitimately live below this cap.
dm=json.loads(DM.read_text()); need(dm['status']=='PASS','DM')
samples=dm['samples']; need([s['request'] for s in samples]==list(range(1,19)),'DM requests')
win=[]
for s in samples:
    pre=s['pre'][0]; post=s['post'][0]
    win.append({'request':s['request'],'pre_short':pre,'post_short':post,'pre_ratio_to_cap':pre/CAP,'clamped':pre>CAP and post==CAP})
unclamped=[x for x in win if not x['clamped']]
clamped=[x for x in win if x['clamped']]
need(unclamped[-1]['request']==7 and clamped[0]['request']==8,'DM transition R7/R8')
# Direct request-number comparisons are not same-scene calibration; they only bound how far apart the captured regimes are.
hc_by_req={r['request']:r for r in runs['HC']}
comparisons=[]
for req in range(4,19):
    h=hc_by_req[req]; w=win[req-1]
    comparisons.append({'request':req,'hc_generation':req-3,'hc_convergence':h['convergence'],'hc_ratio_to_cap':h['ratio_to_cap'],'windows_dm_pre_short':w['pre_short'],'windows_dm_ratio_to_cap':w['pre_ratio_to_cap'],'hc_to_windows_pre_ratio':h['convergence']/w['pre_short']})
# Stability evidence: after startup all five actual Linux captures end far above cap, so simply waiting longer in the same static scene has no evidence-based rationale.
final_ratios={name:rows[-1]['ratio_to_cap'] for name,rows in runs.items()}
need(min(final_ratios.values())>8.0,'steady end remains deeply capped')
result={
 'schema':'sp11-e003i-hd-real-scene-cap-release-envelope-v1',
 'status':'PASS_OFFLINE_REAL_SCENE_CAP_RELEASE_STRATEGY',
 'archive_manifest_sha256':manifest,
 'native_replay_binary_sha256':replay_sha,
 'linux_r27_runs':linux_summary,
 'linux_observation':{
   'runs':list(ARCH.keys()),'all_runs_cap_active_g3_g27':True,
   'all_runs_final_ratio_above_8x_cap':True,'final_ratio_to_cap':final_ratios,
   'hc_eligible_g4_g24_cap_active':True,'hc_post_g3_native_write_count':0,
 },
 'windows_dm':{
   'status':'PASS','last_unclamped_request':7,'request7_pre_short':unclamped[-1]['pre_short'],
   'request7_ratio_to_cap':unclamped[-1]['pre_ratio_to_cap'],'first_clamped_request':8,
   'request8_pre_short':clamped[0]['pre_short'],'request8_ratio_to_cap':clamped[0]['pre_ratio_to_cap'],
   'ordinary_preview_below_cap_state_proven':True,
 },
 'request_number_comparison_hc_vs_windows_dm':comparisons,
 'interpretation':{
   'numeric_scene_brightness_threshold_identifiable':False,
   'why_not_numeric':'HC and DM are different live captures with different scene and history; exposure convergence is recurrent and not linearly invertible to illuminance from these records alone',
   'same_static_scene_longer_observation_supported':False,
   'why_not_just_wait':'all five real Linux R27 runs end more than 8x above cap and are steady/censored; no run trends toward release by G27',
   'synthetic_sensor_control_delta_authorized':False,
   'real_scene_change_required_for_next_feedback_proof':True,
   'windows_proves_cap_release_reachable':True,
 },
 'next_live_acceptance':{
   'fresh_identity_required':True,
   'reuse_hc_identity_forbidden':True,
   'base_policy':'HA/HB one-native-write gate, exact DQBUF boundary',
   'synthetic_control_delta':'none',
   'scene_precondition':'front RGB camera aimed at a substantially brighter diffuse real scene before the one-shot; avoid direct sun/laser into the sensor',
   'eligible_native_write_sources':'G4..G24 for a 27-frame stream',
   'horizon_shadow_sources':['G25','G26'],
   'valid_outcomes':['PASS_NO_CAP_RELEASE','PASS_CAP_RELEASE_ONE_NATIVE_WRITE'],
   'physical_user_or_environment_action_needed':True,
 },
 'camera_runtime_performed':False,
 'safe_parallel_work':'while waiting for a brighter real scene, continue repeated-stream/production-integration work that does not require post-G3 native cap release',
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HD_ARCHIVES=GO_GS_GV_GY_HC_MANIFEST_PASS')
for name,s in linux_summary.items(): print(f'HD_{name}_G3={s["g3_ratio_to_cap"]:.6f}x G4={s["g4_ratio_to_cap"]:.6f}x G27={s["g27_ratio_to_cap"]:.6f}x')
print(f'HD_WINDOWS_DM_R7={unclamped[-1]["pre_ratio_to_cap"]:.6f}x_UNCLAMPED R8={clamped[0]["pre_ratio_to_cap"]:.6f}x_CLAMPED')
print('HD_LONGER_SAME_SCENE=NOT_SUPPORTED')
print('HD_SYNTHETIC_SENSOR_DELTA=NOT_AUTHORIZED')
print('HD_REAL_SCENE_CHANGE_REQUIRED=YES')
print('HD_VERIFY=PASS')
