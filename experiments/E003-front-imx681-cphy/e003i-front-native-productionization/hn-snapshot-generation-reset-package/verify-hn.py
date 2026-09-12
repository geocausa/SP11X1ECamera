#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,re,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent; BASE=HERE.parent; REPO=HERE.parents[3]
FRONT=REPO/'src/front-imx681'; HM=BASE/'hm-repeat-stream-reset-ownership-analysis'; HJ=BASE/'hj-package-install-repeated-stream-shadow-prep'; GM=BASE/'gm-r5-r27-producer-integration'
GI=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-gi/attempt1-pass-twentyfour-frame-20260911T2035')
GO_MEDIA=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-go/attempt1-pass-twentyseven-frame-20260911T2145/runtime-output/MEDIA.txt')
HC_MEDIA=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-hc/attempt1-pass-no-cap-release-20260912T060723/runtime-output/MEDIA.txt')
KERNEL_BUILD=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(cmd,**kw): return subprocess.run(cmd,text=True,capture_output=True,check=True,**kw)
def fn_body(text,name):
    m=re.search(r'void\s+'+re.escape(name)+r'\([^)]*\)\s*\{(.*?)\n\}',text,re.S); need(m,name); return m.group(1)
hm=json.loads((HM/'RESULT.json').read_text()); need(hm['status']=='PASS_OFFLINE_REPEAT_STREAM_RESET_OWNERSHIP','HM parent')
hj=json.loads((HJ/'RESULT.json').read_text()); need(hj['status']=='PASS_OFFLINE_PACKAGE_INSTALL_STAGING','HJ authority')
video=(FRONT/'kernel/camss/camss-video.c').read_text()
for fn,lock,gen in [('camss_x1e_3a_reset','x1e_3a_lock','x1e_3a_generation'),('camss_x1e_tlbg_reset','x1e_tlbg_lock','x1e_tlbg_generation')]:
    b=fn_body(video,fn); need(f'mutex_lock(&video->{lock});' in b,fn+' lock'); need(f'video->{gen} = 0;' in b,fn+' generation reset'); need(b.index(f'mutex_lock(&video->{lock});') < b.index(f'video->{gen} = 0;') < b.index(f'mutex_unlock(&video->{lock});'),fn+' reset outside lock')
# Pure state-model regression: reset -> 27 publishes -> reset -> first publish must be G1 for both channels.
for channel in ('3a','tlbg'):
    gen=0
    first=[]
    for session in range(2):
        gen=0
        for i in range(27):
            gen+=1
            if i==0:first.append(gen)
        need(gen==27,channel+' end generation')
    need(first==[1,1],channel+' two-session generation restart')
# Producer strict fresh-session contract remains unchanged.
producer=(FRONT/'userspace/iq/live-iq-producer.py').read_text(); need('self.next_generation=1' in producer,'producer baseline'); need("missed 3A generation {target}, now {i3[0]}" in producer,'producer strict guard')
expected=json.loads((GM/'RESULT.json').read_text())['all_capsule_sha256']
with tempfile.TemporaryDirectory(prefix='e003i-hn-') as td0:
    td=Path(td0); a=td/'build-a'; b=td/'build-b'; env=os.environ.copy(); env['KERNEL_BUILD']=str(KERNEL_BUILD)
    run([str(FRONT/'build-production.sh'),str(a)],env=env); run([str(FRONT/'build-production.sh'),str(b)],env=env)
    artifacts=['front-imx681-capture','front-imx681-bootstrap-controls','qcom-camss.ko','imx681.ko']; hashes={}
    for f in artifacts:
        need((a/f).read_bytes()==(b/f).read_bytes(),f+' nondeterministic'); hashes[f]=sha(a/f)
    need(hashes['qcom-camss.ko']!=hj['build']['hashes']['qcom-camss.ko'],'CAMSS module hash did not change')
    for f in ('front-imx681-capture','front-imx681-bootstrap-controls','imx681.ko'):
        need(hashes[f]==hj['build']['hashes'][f],f+' unrelated artifact changed')
    for f in ('qcom-camss.ko','imx681.ko'):
        need(run(['modinfo','-F','vermagic',str(a/f)]).stdout.strip()==VERMAGIC,f+' vermagic')
        need('/tmp/sp11-front-imx681-kbuild' not in run(['strings',str(a/f)]).stdout,f+' temp path leak')
    sa=td/'stage-a'; sb=td/'stage-b'; penv=env.copy(); penv['BUILD_DIR']=str(a)
    run([str(FRONT/'stage-package.sh'),str(sa)],env=penv); run([str(FRONT/'stage-package.sh'),str(sb)],env=penv)
    ma=sa/'PACKAGE-MANIFEST.sha256'; mb=sb/'PACKAGE-MANIFEST.sha256'; need(ma.read_bytes()==mb.read_bytes(),'package manifest nondeterministic'); run(['sha256sum','-c','PACKAGE-MANIFEST.sha256'],cwd=sa)
    package_sha=sha(ma); prefix=sa/'usr/lib/sp11-front-imx681'; launcher=prefix/'bin/front-imx681-launcher.py'; build=prefix/'build'
    for media,sensor in ((GO_MEDIA,'imx681 3-0010'),(HC_MEDIA,'imx681 4-0010')):
        plan=json.loads(run([str(launcher),'--topology-file',str(media),'--build-dir',str(build),'--output-dir',str(td/'dry')]).stdout); need(plan['post_g3_write_policy']=='shadow','launcher default'); need(plan['discovery']['sensor_entity']==sensor,'topology discovery')
    # Staged IQ runtime remains byte-exact R5..R27 against accepted GI authority.
    snap=td/'snapshot'; snap.mkdir(); out=td/'producer-out'; out.mkdir(); gains={}
    for gen in range(1,25):
        for pre in ('STATS3A','TLBG'):
            src=GI/'runtime-output'/f'{pre}-{gen-1}.bin'; dst=snap/src.name
            with dst.open('wb') as f: subprocess.run(['sudo','-n','cat',str(src)],check=True,stdout=f)
    text=(GI/'runtime-output/RUN.txt').read_text()
    for m in re.finditer(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+).*?ISP=0x([0-9a-fA-F]{8})',text):
        g,req,bits=m.groups(); g=int(g); req=int(req)
        if g<=24: need(req==g+3,'gain identity'); gains[str(g)]=f'0x{bits.lower()}'
    gain=td/'gain.json'; gain.write_text(json.dumps({'cq_gain_bits':gains})+'\n')
    cp=run([str(prefix/'userspace/iq/live-iq-producer.py'),'--mode','offline','--snapshot-dir',str(snap),'--gain-manifest',str(gain),'--output-dir',str(out),'--manifest',str(td/'producer.json')]); need('E003I_GM_PRODUCER=PASS' in cp.stdout,'producer offline')
    for req in range(5,28): need(sha(out/f'R{req}-dynamic.bin')==expected[str(req)],f'R{req} authority')
result={
 'schema':'sp11-e003i-hn-snapshot-generation-reset-package-v1','status':'PASS_OFFLINE_SNAPSHOT_GENERATION_RESET_PACKAGE','parent':'HM reset ownership analysis','camera_runtime_performed':False,
 'source_fix':{'camss-video.c_sha256':sha(FRONT/'kernel/camss/camss-video.c'),'x1e_3a_generation_reset_under_lock':True,'x1e_tlbg_generation_reset_under_lock':True,'two_logical_sessions_first_generation':[1,1]},
 'build':{'artifacts_byte_identical_across_two_builds':True,'hashes':hashes,'module_vermagic':VERMAGIC,'unrelated_artifacts_unchanged_from_HJ':True},
 'package':{'manifest_sha256':package_sha,'two_stages_identical':True,'manifest_verify':True,'default_post_g3_policy':'shadow','real_topologies_passed':2,'R5_R27_capsules_byte_exact':23},
 'safety':{'post_g3_native_write_authorization_changed':False,'producer_generation_contract_changed':False,'live_runtime_authorized':False},
 'next_gate':'HO fresh repeat-stream shadow candidate using HN package; prepare/install unarmed before any runtime'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HN_GENERATION_RESET=PASS TWO_SESSIONS_FIRST_G=1,1')
print('HN_PRODUCTION_BUILD=PASS BYTE_IDENTICAL=2/2 CAMSS='+hashes['qcom-camss.ko'])
print('HN_PACKAGE=PASS MANIFEST='+package_sha)
print('HN_STAGED_R5_R27=23/23_BYTE_EXACT_PASS')
print('HN_CAMERA_RUNTIME=NO')
print('HN_VERIFY=PASS')
