#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,re,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
FRONT=REPO/'src/front-imx681'
HI=BASE/'hi-production-launcher-device-discovery'
GM=BASE/'gm-r5-r27-producer-integration'
GI=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gi/attempt1-pass-twentyfour-frame-20260911T2035')
GO_MEDIA=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-go/attempt1-pass-twentyseven-frame-20260911T2145/runtime-output/MEDIA.txt')
HC_MEDIA=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-hc/attempt1-pass-no-cap-release-20260912T060723/runtime-output/MEDIA.txt')
KERNEL_BUILD=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise AssertionError(m)
def run(cmd,**kw):return subprocess.run(cmd,text=True,capture_output=True,check=True,**kw)
hi=json.loads((HI/'RESULT.json').read_text());need(hi['status']=='PASS_OFFLINE_PRODUCTION_LAUNCHER_DISCOVERY','HI parent')
expected=json.loads((GM/'RESULT.json').read_text())['all_capsule_sha256']
with tempfile.TemporaryDirectory(prefix='e003i-hj-') as td0:
    td=Path(td0);a=td/'build-a';b=td/'build-b';env=os.environ.copy();env['KERNEL_BUILD']=str(KERNEL_BUILD)
    run([str(FRONT/'build-production.sh'),str(a)],env=env);run([str(FRONT/'build-production.sh'),str(b)],env=env)
    artifacts=['front-imx681-capture','front-imx681-bootstrap-controls','qcom-camss.ko','imx681.ko']
    hashes={}
    for f in artifacts:
        need((a/f).read_bytes()==(b/f).read_bytes(),f+' nondeterministic');hashes[f]=sha(a/f)
    for f in ('qcom-camss.ko','imx681.ko'):
        vm=run(['modinfo','-F','vermagic',str(a/f)]).stdout.strip();need(vm==VERMAGIC,f+' vermagic '+vm)
        strings=run(['strings',str(a/f)]).stdout;need('/tmp/sp11-front-imx681-kbuild' not in strings,f+' temp path leak')
    # Stage twice; the install image is content deterministic and contains committed runtime files only.
    sa=td/'stage-a';sb=td/'stage-b';penv=env.copy();penv['BUILD_DIR']=str(a)
    run([str(FRONT/'stage-package.sh'),str(sa)],env=penv);run([str(FRONT/'stage-package.sh'),str(sb)],env=penv)
    ma=sa/'PACKAGE-MANIFEST.sha256';mb=sb/'PACKAGE-MANIFEST.sha256';need(ma.read_bytes()==mb.read_bytes(),'package manifest nondeterministic')
    run(['sha256sum','-c','PACKAGE-MANIFEST.sha256'],cwd=sa)
    package_manifest_sha=sha(ma)
    prefix=sa/'usr/lib/sp11-front-imx681'
    need(not any(prefix.glob('kernel/**')),'kernel sources entered runtime package')
    need(not any(prefix.glob('userspace/runtime/**')),'runtime C sources entered runtime package')
    need(not any(prefix.glob('**/local-authority/**')),'HG local authority cache entered package')
    # Installed launcher works from staged prefix and remains shadow by default on two real topologies.
    launcher=prefix/'bin/front-imx681-launcher.py';build=prefix/'build'
    for media,sensor in ((GO_MEDIA,'imx681 3-0010'),(HC_MEDIA,'imx681 4-0010')):
        p=json.loads(run([str(launcher),'--topology-file',str(media),'--build-dir',str(build),'--output-dir',str(td/'dry')]).stdout)
        need(p['post_g3_write_policy']=='shadow','staged launcher default')
        need(p['discovery']['sensor_entity']==sensor,'staged discovery '+sensor)
        need(str(prefix) in p['capture_command'][0] and str(prefix) in p['capture_command'][2],'staged path relocation')
    # Staged IQ runtime reproduces accepted R5..R27 outside the source workspace.
    snap=td/'snapshot';snap.mkdir();out=td/'producer-out';out.mkdir()
    for gen in range(1,25):
        for pre in ('STATS3A','TLBG'):
            src=GI/'runtime-output'/f'{pre}-{gen-1}.bin';dst=snap/src.name
            with dst.open('wb') as f:subprocess.run(['sudo','-n','cat',str(src)],check=True,stdout=f)
    gains={}
    for m in re.finditer(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+).*?ISP=0x([0-9a-fA-F]{8})',(GI/'runtime-output/RUN.txt').read_text()):
        gen,req,bits=m.groups();gen=int(gen);req=int(req)
        if gen<=24:need(req==gen+3,'gain identity');gains[str(gen)]=f'0x{bits.lower()}'
    gain=td/'gain.json';gain.write_text(json.dumps({'cq_gain_bits':gains})+'\n')
    trace=td/'producer.strace';producer=prefix/'userspace/iq/live-iq-producer.py'
    cp=run(['strace','-f','-e','trace=openat','-o',str(trace),str(producer),'--mode','offline','--snapshot-dir',str(snap),'--gain-manifest',str(gain),'--output-dir',str(out),'--manifest',str(td/'producer.json')])
    need('E003I_GM_PRODUCER=PASS' in cp.stdout,'staged producer marker')
    for req in range(5,28):need(sha(out/f'R{req}-dynamic.bin')==expected[str(req)],f'R{req} staged package authority')
    rx=re.compile(r'openat\([^,]+, "([^"]+)"[^=]*=\s*(-?\d+)');repo_escape=[];dev=[]
    for line in trace.read_text(errors='replace').splitlines():
        m=rx.search(line)
        if not m or int(m.group(2))<0:continue
        p=m.group(1)
        if p.startswith(str(REPO)):repo_escape.append(p)
        if p.startswith('/dev/video') or p.startswith('/dev/media') or p.startswith('/dev/v4l-subdev'):dev.append(p)
    need(not repo_escape,'staged runtime escaped into source repo '+repr(sorted(set(repo_escape))))
    need(not dev,'staged offline runtime opened camera nodes')
result={
 'schema':'sp11-e003i-hj-package-install-staging-v1',
 'status':'PASS_OFFLINE_PACKAGE_INSTALL_STAGING',
 'parent':'HI production launcher/device discovery',
 'build':{'artifacts_byte_identical_across_two_builds':True,'hashes':hashes,'module_vermagic':VERMAGIC,'temporary_kbuild_path_embedded':False},
 'package':{'layout':'/usr/lib/sp11-front-imx681','manifest_sha256':package_manifest_sha,'two_stages_identical':True,'manifest_verify':True,'ignored_local_authority_packaged':False,'kernel_source_packaged':False,'runtime_c_source_packaged':False},
 'staged_runtime':{'launcher_real_topologies_passed':2,'default_post_g3_policy':'shadow','R5_R27_capsules_byte_exact':23,'source_repo_runtime_opens':0,'camera_device_opens':0},
 'camera_runtime_performed':False,
 'repeated_stream_live_robustness_proven':False,
 'production_native_changed_post_g3_feedback_proven':False,
 'next_gate':'HK fresh bounded repeated-stream shadow-mode candidate preparation',
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HJ_PRODUCTION_BUILD=PASS BYTE_IDENTICAL=2/2')
print('HJ_MODULE_VERMAGIC=PASS')
print('HJ_PACKAGE_STAGE=PASS DETERMINISTIC=2/2')
print('HJ_STAGED_R5_R27=23/23_BYTE_EXACT_PASS')
print('HJ_SOURCE_REPO_RUNTIME_OPENS=0')
print('HJ_CAMERA_RUNTIME=NO')
print('HJ_VERIFY=PASS')
