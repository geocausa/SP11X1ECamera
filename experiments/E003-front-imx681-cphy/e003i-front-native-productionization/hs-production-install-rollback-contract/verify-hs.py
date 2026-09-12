#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent; BASE=HERE.parent; REPO=HERE.parents[3]
FRONT=REPO/'src/front-imx681'; HR=BASE/'hr-production-repeated-open-handoff'; INSTALL=FRONT/'install-package.sh'
KERNEL_BUILD=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(cmd,check=True,**kw): return subprocess.run(cmd,text=True,capture_output=True,check=check,**kw)
def tree_digest(root:Path)->dict:
    out={}
    if not root.exists(): return out
    for p in sorted(x for x in root.rglob('*') if x.is_file() or x.is_symlink()):
        rel=str(p.relative_to(root))
        out[rel]=('L:'+os.readlink(p)) if p.is_symlink() else sha(p)
    return out
hr=json.loads((HR/'RESULT.json').read_text()); need(hr['status']=='PASS_OFFLINE_PRODUCTION_REPEATED_OPEN_HANDOFF','HR parent')
need(hr['package']['manifest_sha256']=='57aa9cc2ad85131881416d7795603ab777a70e7c5877828986ff279266a5a757','HR package')
text=INSTALL.read_text()
for marker in ("TARGET_ROOT=/ requires --allow-real-root","package manifest verification failed","another install transaction holds the lock","restore_backup","FRONT_IMX681_INSTALL=PASS","FRONT_IMX681_ROLLBACK=PASS"):
    need(marker in text,'installer marker '+marker)
need(run(['bash','-n',str(INSTALL)]).returncode==0,'installer syntax')
need(run(['shellcheck','-x','-S','warning',str(INSTALL)]).returncode==0,'installer shellcheck')
with tempfile.TemporaryDirectory(prefix='e003i-hs-') as td0:
    td=Path(td0); build=td/'build'; env=os.environ.copy(); env['KERNEL_BUILD']=str(KERNEL_BUILD)
    run([str(FRONT/'build-production.sh'),str(build)],env=env)
    stage=td/'stage'; penv=env.copy(); penv['BUILD_DIR']=str(build); run([str(FRONT/'stage-package.sh'),str(stage)],env=penv)
    run(['sha256sum','-c','PACKAGE-MANIFEST.sha256'],cwd=stage)
    package_sha=sha(stage/'PACKAGE-MANIFEST.sha256'); need(package_sha==hr['package']['manifest_sha256'],'runtime package drift')
    # Real-root mutation requires explicit opt-in and is rejected before any action.
    cp=run([str(INSTALL),'install',str(stage),'/'],check=False)
    need(cp.returncode!=0 and 'TARGET_ROOT=/ requires --allow-real-root' in cp.stderr,'real root guard')
    # Existing installation -> install -> one-step rollback restores byte-exact prior tree.
    root=td/'root-existing'; (root/'usr/lib/sp11-front-imx681').mkdir(parents=True); (root/'usr/bin').mkdir(parents=True)
    (root/'usr/lib/sp11-front-imx681/legacy.txt').write_text('legacy-prefix\n')
    (root/'usr/bin/sp11-front-imx681').write_text('legacy-launcher\n'); (root/'usr/bin/sp11-front-imx681-discover').write_text('legacy-discover\n')
    before=tree_digest(root/'usr')
    cp=run([str(INSTALL),'install',str(stage),str(root)])
    need('FRONT_IMX681_INSTALL=PASS' in cp.stdout,'existing install')
    receipt=root/'var/lib/sp11-front-imx681/current-install.env'; need(receipt.is_file(),'receipt missing')
    need(f'PACKAGE_MANIFEST_SHA256={package_sha}' in receipt.read_text(),'receipt package sha')
    need(tree_digest(root/'usr/lib/sp11-front-imx681')==tree_digest(stage/'usr/lib/sp11-front-imx681'),'installed prefix mismatch')
    need(sha(root/'usr/bin/sp11-front-imx681')==sha(stage/'usr/bin/sp11-front-imx681'),'installed wrapper mismatch')
    cp=run([str(INSTALL),'rollback','-',str(root)])
    need('FRONT_IMX681_ROLLBACK=PASS' in cp.stdout,'existing rollback')
    need(tree_digest(root/'usr')==before,'rollback did not restore existing install byte-exact')
    # Fresh root install -> rollback returns to no installed package/wrappers.
    fresh=td/'root-fresh'; fresh.mkdir()
    cp=run([str(INSTALL),'install',str(stage),str(fresh)]); need(cp.returncode==0,'fresh install')
    need((fresh/'usr/lib/sp11-front-imx681').is_dir(),'fresh prefix')
    cp=run([str(INSTALL),'rollback','-',str(fresh)]); need(cp.returncode==0,'fresh rollback')
    need(not (fresh/'usr/lib/sp11-front-imx681').exists(),'fresh prefix survived rollback')
    need(not (fresh/'usr/bin/sp11-front-imx681').exists() and not (fresh/'usr/bin/sp11-front-imx681-discover').exists(),'fresh wrappers survived rollback')
    # Corrupt source package is rejected before target mutation, including install-state creation.
    corrupt=td/'stage-corrupt'; shutil.copytree(stage,corrupt,symlinks=True)
    with (corrupt/'usr/lib/sp11-front-imx681/README.md').open('a') as f: f.write('corrupt\n')
    target=td/'root-corrupt'; (target/'sentinel').mkdir(parents=True); (target/'sentinel/keep').write_text('keep\n'); target_before=tree_digest(target)
    cp=run([str(INSTALL),'install',str(corrupt),str(target)],check=False)
    need(cp.returncode!=0 and 'package manifest verification failed' in cp.stderr,'corrupt package accepted')
    need(tree_digest(target)==target_before,'corrupt-package rejection mutated target')
    # Offline transaction must not touch camera devices.
    trace=td/'install.strace'; traced=td/'root-trace'; traced.mkdir()
    run(['strace','-f','-e','trace=openat','-o',str(trace),str(INSTALL),'install',str(stage),str(traced)])
    t=trace.read_text(errors='replace'); need('/dev/video' not in t and '/dev/media' not in t and '/dev/v4l-subdev' not in t,'installer opened camera device')
    run([str(INSTALL),'rollback','-',str(traced)])
result={
 'schema':'sp11-e003i-hs-production-install-rollback-contract-v1',
 'status':'PASS_OFFLINE_PRODUCTION_INSTALL_ROLLBACK_CONTRACT',
 'parent':'HR production repeated-open handoff',
 'camera_runtime_performed':False,
 'runtime_package_manifest_sha256':package_sha,
 'real_root_requires_explicit_allow':True,
 'manifest_verified_before_target_mutation':True,
 'existing_install_roundtrip_byte_exact':True,
 'fresh_install_rollback_removes_package':True,
 'corrupt_package_rejected_before_target_mutation':True,
 'install_receipt_records_package_manifest':True,
 'one_step_rollback_supported':True,
 'installer_camera_device_opens':0,
 'production_runtime_package_changed_from_HR':False,
 'next_gate':'HT production deployment smoke-plan and distro integration boundary offline'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HS_INSTALL_ROLLBACK=PASS EXISTING_BYTE_EXACT=YES FRESH_REMOVE=YES')
print('HS_CORRUPT_PACKAGE=REJECT_BEFORE_TARGET_MUTATION')
print('HS_REAL_ROOT_GUARD=PASS')
print('HS_RUNTIME_PACKAGE_UNCHANGED='+package_sha)
print('HS_CAMERA_RUNTIME=NO')
print('HS_VERIFY=PASS')
