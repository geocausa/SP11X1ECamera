#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,statistics,struct,subprocess,tempfile
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
ARCH={
 'GS':Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gs/attempt1-pass-continuous-shadow-20260911T221117'),
 'GV':Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gv/attempt1-helper-pass-verifier-audit-20260911T222625'),
 'GY':Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gy/attempt1-pass-minimal-changed-sentinel-20260911T224155'),
}
CV=BASE/'cv-native-aec-offline-sensor-control-join'
CU=BASE/'cu-native-aec-raw-stats-request-loop'
CQ=BASE/'cq-aec-output-imx681-control-adapter'
CR=BASE/'cr-native-aec-effective-analyzer-producer'
CT=BASE/'ct-native-aec-bhist-bank4-replay'
DN=BASE/'dn-native-aec-internal-cap'
CF=BASE/'cf-native-aec-final-exposure-si'
CE=BASE/'ce-native-aec-final-target-producer'
CC=BASE/'cc-native-aec-adrc-darkboost-tail'
BY=BASE/'by-native-aec-method11-point-aggregation'
CG=BASE/'cg-native-aec-qword-convergence-input'
CH=BASE/'ch-native-aec-t681-preview-arbitration'
BK=BASE/'bk-native-aec-history-state'
BJ=BASE/'bj-native-aec-log103-coordinate'
CAP_MAX=6133333088
SENTINEL_REL_PCT=(1472/1471-1)*100

def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fbits(s): return struct.unpack('<f',struct.pack('<I',int(s,16)))[0]
manifest={}
for name,a in ARCH.items():
    subprocess.run(['sha256sum','-c','MANIFEST.sha256'],cwd=a,check=True,stdout=subprocess.DEVNULL)
    manifest[name]=sha(a/'MANIFEST.sha256')
gy_attempt=json.loads((ARCH['GY']/'ATTEMPT1-PASS.json').read_text())
need(gy_attempt['status']=='PASS_CAPTURE_GY_MINIMAL_CHANGED_POST_G3_R27','GY pass status')
need(gy_attempt['stream_attempts']==1 and not gy_attempt['same_boot_stream_retry_performed'],'GY one-shot')
need(gy_attempt['new_post_g3_sensor_hardware_transaction_count']==1,'GY one later hardware transaction')
need(gy_attempt['sentinel_native_dgain']==1471 and gy_attempt['sentinel_applied_dgain']==1472,'sentinel tuple')
with tempfile.TemporaryDirectory(prefix='e003i-gz-') as td0:
    td=Path(td0); exe=td/'replay'
    inc=[CV,CU,CQ,CR,CT,DN,CF,CE,CC,BY,CG,CH,BK,BJ]
    src=[CV/'native-raw-control-join.c',CU/'native-raw-aec-loop.c',CU/'native-stats3a.c',CQ/'native-imx681-control.c',CR/'native-effective-analyzers.c',CT/'native-bhist-bank4.c',DN/'native-aec-request-loop.c',DN/'native-internal-cap.c',CF/'native-final-exposure.c',CE/'native-final-target.c',CC/'native-aec-tail.c',BY/'native-target-aggregate.c',CG/'native-convergence.c',CH/'native-t681.c',BK/'native-aec-state.c',BJ/'native-log103.c',HERE/'replay-aec-cap.c']
    cmd=['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-fno-fast-math','-ffp-contract=off']
    for x in inc: cmd += ['-I',str(x)]
    cmd += [str(x) for x in src]+['-lm','-o',str(exe)]
    subprocess.run(cmd,check=True)
    binary_sha=sha(exe)
    txt=subprocess.check_output([str(exe),str(ARCH['GY']/'runtime-output')],text=True)
rx=re.compile(r'G=(\d+) LUMA=([0-9.eE+-]+) LUX_IN=([0-9.eE+-]+) FRAME_TARGET=([0-9.eE+-]+) FRAME_CAND=([0-9.eE+-]+) FRAME_CONF=([0-9.eE+-]+) NEXT_LUX=([0-9.eE+-]+) CONV_SHORT=(\d+) CAP_SHORT=(\d+) T681_GAIN=([0-9.eE+-]+) T681_TIME=(\d+) FLL=(\d+) VB=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) ISP=([0-9.eE+-]+)')
rows=[]
for line in txt.splitlines():
    m=rx.fullmatch(line); need(m,line)
    g,luma,lux,ft,fc,conf,nlux,conv,cap,gain,tim,fll,vb,exp,ag,dg,isp=m.groups()
    rows.append({'g':int(g),'luma':float(luma),'lux_in':float(lux),'frame_target':float(ft),'frame_candidate':float(fc),'frame_confidence':float(conf),'next_lux':float(nlux),'conv_short':int(conv),'cap_short':int(cap),'t681_gain':float(gain),'t681_time':int(tim),'fll':int(fll),'vb':int(vb),'exp':int(exp),'ag':int(ag),'dg':int(dg),'isp':float(isp)})
need([r['g'] for r in rows]==list(range(1,28)),'27 replay rows')
run=(ARCH['GY']/'runtime-output/RUN.txt').read_text(errors='replace')
live={}
for m in re.finditer(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=\d+ FLL=(\d+) VB=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) ISP=0x([0-9a-fA-F]{8})',run):
    g,fll,vb,exp,ag,dg,isp=m.groups(); live[int(g)]=(int(fll),int(vb),int(exp),int(ag),int(dg),int(isp,16))
need(len(live)==27,'27 live tuples')
for r in rows:
    ib=struct.unpack('<I',struct.pack('<f',r['isp']))[0]
    need((r['fll'],r['vb'],r['exp'],r['ag'],r['dg'],ib)==live[r['g']],f'exact replay G{r["g"]}')
plateau=rows[2:]
need(all(r['cap_short']==CAP_MAX for r in plateau),'G3..G27 cap max')
need(all(r['conv_short']>CAP_MAX for r in plateau),'G3..G27 unconstrained above cap')
need(all((r['fll'],r['exp'],r['ag'],r['dg'])==(7116,7108,960,1471) for r in plateau),'G3..G27 native output plateau')
ratios=[r['conv_short']/CAP_MAX for r in plateau]
g7=rows[6]
luma_runs={}
for name,a in ARCH.items():
    pr=json.loads((a/'runtime-output/producer/RESULT.json').read_text())
    d={int(x['generation']):fbits(x['measured_luma_bits']) for x in pr['rows'] if x.get('generation') is not None}
    need(all(g in d for g in range(3,24)),name+' luma coverage')
    luma_runs[name]=d
steady_cv={}
for name,d in luma_runs.items():
    vals=[d[g] for g in range(8,24)]
    steady_cv[name]=statistics.stdev(vals)/statistics.mean(vals)*100
g7_vs_gv_pct=(luma_runs['GY'][7]/luma_runs['GV'][7]-1)*100
g7_vs_gs_pct=(luma_runs['GY'][7]/luma_runs['GS'][7]-1)*100
gy_g7_local_mid=(luma_runs['GY'][7]/((luma_runs['GY'][6]+luma_runs['GY'][8])/2)-1)*100
noise_floor_min=min(steady_cv.values())
signal_to_noise=noise_floor_min/SENTINEL_REL_PCT
gy_late=[luma_runs['GY'][g] for g in range(7,24)]
gy_late_pp=(max(gy_late)/min(gy_late)-1)*100
result={
 'schema':'sp11-e003i-gz-native-response-threshold-analysis-v1',
 'status':'PASS_OFFLINE_RESPONSE_THRESHOLD_CENSORED_BY_PREVIEW_CAP',
 'archive_manifest_sha256':manifest,
 'native_replay':{'rows':27,'live_control_tuples_exact':'27/27','binary_sha256':binary_sha,'camera_runtime_performed':False},
 'sentinel':{'source_generation':4,'expected_effect_generation':7,'digital_gain_code':[1471,1472],'relative_gain_delta_percent':SENTINEL_REL_PCT},
 'effect_observation':{
   'gy_g7_frame_luma':luma_runs['GY'][7],
   'gv_g7_frame_luma':luma_runs['GV'][7],
   'gs_g7_frame_luma':luma_runs['GS'][7],
   'gy_vs_gv_g7_percent':g7_vs_gv_pct,
   'gy_vs_gs_g7_percent':g7_vs_gs_pct,
   'gy_g7_vs_local_g6_g8_midpoint_percent':gy_g7_local_mid,
   'steady_luma_cv_percent_g8_g23':steady_cv,
   'minimum_baseline_cv_percent':noise_floor_min,
   'minimum_cv_to_sentinel_step_ratio':signal_to_noise,
   'single_run_signal_resolved':False,
   'reason':'0.06798% sentinel is far below ordinary frame-luma variability and cross-run pre-effect trajectories differ'
 },
 'native_control_censoring':{
   'preview_cap_max':CAP_MAX,
   'cap_active_generations':'G3..G27',
   'unconstrained_convergence_above_cap_generations':'G3..G27',
   'g7_unconstrained_short':g7['conv_short'],
   'g7_unconstrained_to_cap_ratio':g7['conv_short']/CAP_MAX,
   'minimum_unconstrained_to_cap_ratio_g3_g27':min(ratios),
   'maximum_unconstrained_to_cap_ratio_g3_g27':max(ratios),
   'native_sensor_tuple_g3_g27':{'fll':7116,'exposure':7108,'analogue_gain_code':960,'digital_gain_code':1471},
   'gy_luma_peak_to_peak_percent_g7_g23':gy_late_pp,
   'interpretation':'output is hard-censored by the Windows-derived preview cap, not demonstrably held by a small deadband/quantizer'
 },
 'threshold_conclusion':{
   'production_native_control_change_threshold_identifiable_from_GY':False,
   'larger_synthetic_gain_step_authorized':False,
   'why':'the controller is already cap-saturated; GY cannot reveal the uncapped response threshold, and the tiny photometric perturbation is below observed luma variability',
   'safe_next_step':'design an offline controlled cap-release/bright-scene acceptance plan that detects when native convergence falls below E003I_PREVIEW_CAP_MAX; do not guess a larger live sentinel'
 }
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('GZ_ARCHIVES=PASS GS_GV_GY')
print('GZ_NATIVE_REPLAY=27/27_EXACT')
print(f'GZ_SENTINEL_STEP_PERCENT={SENTINEL_REL_PCT:.6f}')
print(f'GZ_G7_GY_VS_GV_PERCENT={g7_vs_gv_pct:.6f}')
print(f'GZ_MIN_STEADY_CV_PERCENT={noise_floor_min:.6f} STEP_BELOW_CV_X={signal_to_noise:.2f}')
print(f'GZ_G7_CONV_TO_CAP_X={g7["conv_short"]/CAP_MAX:.6f} CAP_ACTIVE=G3..G27')
print('GZ_THRESHOLD=NOT_IDENTIFIABLE_CAP_CENSORED')
print('GZ_LARGER_SENTINEL_AUTHORIZED=NO')
print('GZ_VERIFY=PASS')
