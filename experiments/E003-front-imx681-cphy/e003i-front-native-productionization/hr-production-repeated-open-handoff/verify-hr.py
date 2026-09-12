#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,re,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent; BASE=HERE.parent; REPO=HERE.parents[3]
FRONT=REPO/'src/front-imx681'; HQ=BASE/'hq-four-stream-shadow-r27'; HN=BASE/'hn-snapshot-generation-reset-package'
HC_MEDIA=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-hc/attempt1-pass-no-cap-release-20260912T060723/runtime-output/MEDIA.txt')
KERNEL_BUILD=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(cmd,**kw): return subprocess.run(cmd,text=True,capture_output=True,check=True,**kw)
hq=json.loads((HQ/'RESULT.json').read_text()); hn=json.loads((HN/'RESULT.json').read_text())
need(hq['status']=='PASS_CAPTURE_HQ_FOUR_STREAM_SHADOW_R27_GOLDEN_RESTORED_RETIRED','HQ parent')
need(hq['streams_completed']==4 and hq['total_frames']==108 and hq['post_g3_native_write_count_total']==0,'HQ authority')
need(hq['archive_manifest_sha256']=='a1358953c9dc545c5b5125f4ea4f71d35402391c00c52fe163f98d81822ef545','HQ manifest')
need(hn['status']=='PASS_OFFLINE_SNAPSHOT_GENERATION_RESET_PACKAGE','HN package')
launcher=FRONT/'bin/front-imx681-launcher.py'; source=launcher.read_text()
for marker in ("DEFAULT_OUTPUT_ROOT=Path('/var/tmp/sp11-front-imx681')","return DEFAULT_OUTPUT_ROOT/f'session-{stamp}-{os.getpid()}'","if a.output_dir is None:a.output_dir=default_output_dir()","need(not a.output_dir.exists(),'output-dir already exists; choose a fresh session directory')","a.output_dir.mkdir(parents=True,exist_ok=False)"):
    need(marker in source,'launcher session isolation '+marker)
# Four independent source dry-runs get fresh, non-created default output paths.
plans=[]
for _ in range(4): plans.append(json.loads(run([str(launcher),'--topology-file',str(HC_MEDIA)]).stdout))
outs=[p['output_dir'] for p in plans]
need(len(set(outs))==4,'source default output paths not unique')
need(all(not Path(x).exists() for x in outs),'source dry-run created output')
need(all(p['post_g3_write_policy']=='shadow' and p['execute'] is False for p in plans),'source dry-run policy')
with tempfile.TemporaryDirectory(prefix='e003i-hr-explicit-') as td:
    out=Path(td)/'explicit-session'
    p=json.loads(run([str(launcher),'--topology-file',str(HC_MEDIA),'--output-dir',str(out)]).stdout)
    need(p['output_dir']==str(out) and not out.exists(),'explicit dry-run output contract')
# Production artifacts remain byte-identical to HN; only staged runtime metadata/scripts may change.
with tempfile.TemporaryDirectory(prefix='e003i-hr-') as td0:
    td=Path(td0); a=td/'build-a'; b=td/'build-b'; env=os.environ.copy(); env['KERNEL_BUILD']=str(KERNEL_BUILD)
    run([str(FRONT/'build-production.sh'),str(a)],env=env); run([str(FRONT/'build-production.sh'),str(b)],env=env)
    artifacts=['front-imx681-capture','front-imx681-bootstrap-controls','qcom-camss.ko','imx681.ko']; hashes={}
    for f in artifacts:
        need((a/f).read_bytes()==(b/f).read_bytes(),f+' nondeterministic'); hashes[f]=sha(a/f); need(hashes[f]==hn['build']['hashes'][f],f+' changed from HN')
    for f in ('qcom-camss.ko','imx681.ko'): need(run(['modinfo','-F','vermagic',str(a/f)]).stdout.strip()==VERMAGIC,f+' vermagic')
    sa=td/'stage-a'; sb=td/'stage-b'; penv=env.copy(); penv['BUILD_DIR']=str(a)
    run([str(FRONT/'stage-package.sh'),str(sa)],env=penv); run([str(FRONT/'stage-package.sh'),str(sb)],env=penv)
    ma=sa/'PACKAGE-MANIFEST.sha256'; mb=sb/'PACKAGE-MANIFEST.sha256'; need(ma.read_bytes()==mb.read_bytes(),'package nondeterministic'); run(['sha256sum','-c','PACKAGE-MANIFEST.sha256'],cwd=sa)
    package_sha=sha(ma); need(package_sha!=hn['package']['manifest_sha256'],'package manifest did not change after launcher safety fix')
    prefix=sa/'usr/lib/sp11-front-imx681'; staged=prefix/'bin/front-imx681-launcher.py'; wrapper=sa/'usr/bin/sp11-front-imx681'
    need(wrapper.is_file() and os.access(wrapper,os.X_OK),'wrapper missing')
    need('exec /usr/lib/sp11-front-imx681/bin/front-imx681-launcher.py "$@"' in wrapper.read_text(),'wrapper target')
    staged_plans=[]
    for _ in range(4): staged_plans.append(json.loads(run([str(staged),'--topology-file',str(HC_MEDIA),'--build-dir',str(prefix/'build')]).stdout))
    staged_out=[p['output_dir'] for p in staged_plans]
    need(len(set(staged_out))==4,'staged default output paths not unique')
    need(all(not Path(x).exists() for x in staged_out),'staged dry-run created output')
    need(all(p['post_g3_write_policy']=='shadow' for p in staged_plans),'staged shadow default')
    trace=td/'launcher.strace'
    run(['strace','-f','-e','trace=openat','-o',str(trace),str(staged),'--topology-file',str(HC_MEDIA),'--build-dir',str(prefix/'build')])
    rx=re.compile(r'openat\([^,]+, "([^"]+)"[^=]*=\s*(-?\d+)'); repo_escape=[]; dev=[]
    for line in trace.read_text(errors='replace').splitlines():
        m=rx.search(line)
        if not m or int(m.group(2))<0: continue
        path=m.group(1)
        if path.startswith(str(REPO)): repo_escape.append(path)
        if path.startswith('/dev/video') or path.startswith('/dev/media') or path.startswith('/dev/v4l-subdev'): dev.append(path)
    need(not repo_escape,'staged launcher escaped source repo '+repr(sorted(set(repo_escape))))
    need(not dev,'staged dry-run opened camera nodes')
result={
 'schema':'sp11-e003i-hr-production-repeated-open-handoff-v1',
 'status':'PASS_OFFLINE_PRODUCTION_REPEATED_OPEN_HANDOFF',
 'parent':'HQ four-stream shadow live PASS',
 'camera_runtime_performed':False,
 'bounded_repeated_open_live_proven_streams':4,
 'bounded_repeated_open_live_proven_frames':108,
 'post_g3_policy':'shadow',
 'post_g3_native_writes_authorized':0,
 'launcher':{'default_session_paths_unique_dry_runs':4,'dry_run_output_directories_created':0,'execute_existing_output_dir_fail_closed':True,'explicit_output_dir_preserved_in_plan':True},
 'build':{'artifacts_byte_identical_across_two_builds':True,'hashes':hashes,'all_artifacts_unchanged_from_HN':True,'module_vermagic':VERMAGIC},
 'package':{'manifest_sha256':package_sha,'two_stages_identical':True,'manifest_verify':True,'manifest_changed_from_HN_for_launcher_safety':True,'staged_unique_default_sessions':4,'staged_source_repo_opens':0,'staged_camera_device_opens':0},
 'production_contract':{'one_launcher_invocation_one_fresh_output_directory':True,'default_post_g3_policy':'shadow','bounded_repeated_open_close_proven':True,'indefinite_soak_proven':False,'production_native_changed_post_g3_feedback_proven':False},
 'next_gate':'HS production install-image transaction and rollback contract offline'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HR_SESSION_ISOLATION=PASS SOURCE=4/4 STAGED=4/4')
print('HR_BUILD_ARTIFACTS=UNCHANGED_FROM_HN')
print('HR_PACKAGE_MANIFEST='+package_sha)
print('HR_REPEATED_OPEN_HANDOFF=PASS LIVE_PARENT_STREAMS=4 FRAMES=108')
print('HR_CAMERA_RUNTIME=NO')
print('HR_VERIFY=PASS')
