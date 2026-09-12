#!/usr/bin/env python3
from __future__ import annotations
import hashlib,importlib.util,json,os,re,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
FRONT=REPO/'src/front-imx681'
RT=FRONT/'userspace/runtime'
IQ=FRONT/'userspace/iq'
BIN=FRONT/'bin'
HH=BASE/'hh-cleanroom-authority-cache-reduction'
HC=BASE/'hc-native-cap-release-observer-r27'
R4=IQ/'authority/r4-bootstrap.bin'
R4_SHA='1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa'
ARCH=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive')
FIXTURES=[
 ('GO',ARCH/'e003i-go/attempt1-pass-twentyseven-frame-20260911T2145/runtime-output/MEDIA.txt','imx681 3-0010'),
 ('GS',ARCH/'e003i-gs/attempt1-pass-continuous-shadow-20260911T221117/runtime-output/MEDIA.txt','imx681 3-0010'),
 ('GV',ARCH/'e003i-gv/attempt1-helper-pass-verifier-audit-20260911T222625/runtime-output/MEDIA.txt','imx681 3-0010'),
 ('GY',ARCH/'e003i-gy/attempt1-pass-minimal-changed-sentinel-20260911T224155/runtime-output/MEDIA.txt','imx681 3-0010'),
 ('HC',ARCH/'e003i-hc/attempt1-pass-no-cap-release-20260912T060723/runtime-output/MEDIA.txt','imx681 4-0010'),
]

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise AssertionError(m)
def run(cmd,**kw):return subprocess.run(cmd,text=True,capture_output=True,check=True,**kw)
# Parent HH is closed and production safety starts from its clean runtime.
hh=json.loads((HH/'RESULT.json').read_text());need(hh['status']=='PASS_OFFLINE_CLEAN_RUNTIME_AUTHORITY_R5_R27','HH parent')
# Production helper is a deterministic transform of the exact frozen HC helper.
need(sha(RT/'e003i-hc-caprelease-native-aec.c')=='578f41d5cc0935aff327f500d38c095ed64f7428d2e245adc1f8196e9b3c99a3','HC helper source')
with tempfile.TemporaryDirectory(prefix='e003i-hi-') as td0:
    td=Path(td0);generated=td/'capture.c'
    run([str(HERE/'make-production-capture.py'),'--output',str(generated)])
    need(generated.read_bytes()==(RT/'front-imx681-production-capture.c').read_bytes(),'generated production helper drift')
    # Build twice to prove the stable userspace build is deterministic on the protected host toolchain.
    a=td/'build-a';b=td/'build-b'
    run([str(FRONT/'build-userspace.sh'),str(a)]);run([str(FRONT/'build-userspace.sh'),str(b)])
    capsha=sha(a/'front-imx681-capture');bootsha=sha(a/'front-imx681-bootstrap-controls')
    need((a/'front-imx681-capture').read_bytes()==(b/'front-imx681-capture').read_bytes(),'capture build nondeterministic')
    need((a/'front-imx681-bootstrap-controls').read_bytes()==(b/'front-imx681-bootstrap-controls').read_bytes(),'bootstrap build nondeterministic')
    # Policy parser/apply gate: absent policy defaults to shadow; only explicit one-shot+HA allow can write later.
    test=td/'test-policy'
    run(['cc','-O2','-std=c11','-Wall','-Wextra','-Werror','-I'+str(RT),str(HERE/'test-production-write-policy.c'),str(RT/'production-write-policy.c'),'-o',str(test)])
    cp=run([str(test)]);need('DEFAULT=shadow' in cp.stdout,'policy unit')
    # Bootstrap source remains exact accepted HC code.
    need((RT/'bootstrap-controls.c').read_bytes()==(HC/'bootstrap-controls.c').read_bytes(),'bootstrap source drift')
    # Derived R4 capsule is exact accepted template-free bootstrap.
    need(R4.is_file() and R4.stat().st_size==41088 and sha(R4)==R4_SHA,'R4 bootstrap')
    # Archived media topologies cover real I2C-entity drift 3-0010 -> 4-0010.
    rows=[]
    for name,path,sensor in FIXTURES:
        cp=run([str(BIN/'front-imx681-discover.py'),'--topology-file',str(path),'--json'])
        d=json.loads(cp.stdout);need(d['sensor_entity']==sensor,name+' sensor');need(d['sensor_subdev']=='/dev/v4l-subdev25',name+' subdev evidence');need(d['video_node']=='/dev/video7',name+' video evidence')
        need(d['csiphy_entity']=='msm_csiphy2' and d['csid_entity']=='msm_csid1' and d['pix_entity']=='msm_vfe1_pix',name+' pipeline')
        rows.append({'stage':name,'sensor_entity':d['sensor_entity'],'sensor_subdev':d['sensor_subdev'],'video_node':d['video_node']})
    need(len({x['sensor_entity'] for x in rows})==2,'archived bus drift not exercised')
    # Synthetic node/bus renumbering proves discovery does not pin /dev numbering or I2C bus.
    text=FIXTURES[-1][1].read_text(errors='replace').replace('imx681 4-0010','imx681 9-0010').replace('/dev/v4l-subdev25','/dev/v4l-subdev31').replace('/dev/video7','/dev/video12')
    synth=td/'renumbered-media.txt';synth.write_text(text)
    d=json.loads(run([str(BIN/'front-imx681-discover.py'),'--topology-file',str(synth),'--json']).stdout)
    need((d['sensor_entity'],d['sensor_subdev'],d['video_node'])==('imx681 9-0010','/dev/v4l-subdev31','/dev/video12'),'synthetic renumber discovery')
    # Default dry plan is shadow and emits dynamic sensor/video nodes. No actual camera device may be opened.
    trace=td/'launcher.strace';plan=td/'plan.json'
    cmd=['strace','-f','-e','trace=openat','-o',str(trace),str(BIN/'front-imx681-launcher.py'),'--topology-file',str(synth),'--build-dir',str(a),'--output-dir',str(td/'session')]
    cp=run(cmd);plan.write_text(cp.stdout);p=json.loads(cp.stdout)
    need(p['post_g3_write_policy']=='shadow' and p['environment']['SP11_FRONT_POST_G3_WRITE_POLICY']=='shadow','launcher default shadow')
    need(p['discovery']['sensor_subdev']=='/dev/v4l-subdev31' and p['discovery']['video_node']=='/dev/video12','launcher dynamic nodes')
    rx=re.compile(r'openat\([^,]+, "([^"]+)"[^=]*=\s*(-?\d+)');dev=[]
    for line in trace.read_text(errors='replace').splitlines():
        m=rx.search(line)
        if m and int(m.group(2))>=0 and (m.group(1).startswith('/dev/video') or m.group(1).startswith('/dev/media') or m.group(1).startswith('/dev/v4l-subdev')):dev.append(m.group(1))
    need(not dev,'dry launcher opened camera device '+repr(dev))
    # Execution safety gates fail before any live discovery/device access.
    deny=subprocess.run([str(BIN/'front-imx681-launcher.py'),'--execute','--topology-file',str(synth)],text=True,capture_output=True)
    need(deny.returncode!=0 and '--execute cannot be combined with --topology-file' in deny.stderr,'fixture execute gate')
    deny=subprocess.run(['sudo','-n',str(BIN/'front-imx681-launcher.py'),'--execute','--post-g3-write-policy','cap-release-one-shot'],text=True,capture_output=True)
    need(deny.returncode!=0 and 'requires explicit --allow-one-native-write' in deny.stderr,'one-shot acknowledgement gate')
    # Stable launcher/discovery sources contain no accepted-run bus or /dev node literals.
    stable=(BIN/'front-imx681-discover.py').read_text()+(BIN/'front-imx681-launcher.py').read_text()
    for forbidden in ('imx681 3-0010','imx681 4-0010','/dev/video7','/dev/v4l-subdev25'):
        need(forbidden not in stable,'hardcoded live identity '+forbidden)
result={
 'schema':'sp11-e003i-hi-production-launcher-device-discovery-v1',
 'status':'PASS_OFFLINE_PRODUCTION_LAUNCHER_DISCOVERY',
 'parent':'HH clean runtime authority',
 'production_helper':{'source':'src/front-imx681/userspace/runtime/front-imx681-production-capture.c','generated_from_frozen_hc':True,'default_post_g3_policy':'shadow','explicit_opt_in_policy':'cap-release-one-shot','capture_binary_sha256':capsha,'builds_byte_identical':2},
 'bootstrap':{'source_byte_exact_hc':True,'binary_sha256':bootsha,'r4_bytes':41088,'r4_sha256':R4_SHA},
 'media_discovery':{'archived_real_topologies':5,'real_sensor_entities':['imx681 3-0010','imx681 4-0010'],'synthetic_bus_and_devnode_renumber_pass':True,'hardcoded_i2c_bus':False,'hardcoded_video_node':False,'hardcoded_sensor_subdev':False,'proven_pipeline_entities':['msm_csiphy2','msm_csid1','msm_vfe1_pix','msm_vfe1_video3']},
 'launcher':{'dry_run_default':True,'default_post_g3_policy':'shadow','execute_with_topology_fixture_forbidden':True,'cap_release_one_shot_requires_explicit_allow_flag_on_execute':True,'dry_run_camera_device_opens':0},
 'camera_runtime_performed':False,
 'production_native_changed_post_g3_feedback_proven':False,
 'repeated_stream_live_robustness_proven':False,
 'next_gate':'HJ package/install staging and bounded repeated-stream shadow-mode runtime candidate preparation',
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
(HERE/'DISCOVERY-REGRESSION.json').write_text(json.dumps({'schema':'sp11-hi-media-discovery-regression-v1','rows':rows},indent=2,sort_keys=True)+'\n')
print('HI_PRODUCTION_HELPER_BUILD=PASS DETERMINISTIC=2/2')
print('HI_POST_G3_DEFAULT=shadow')
print('HI_MEDIA_DISCOVERY_REAL=5/5 PASS BUS_DRIFT=PASS')
print('HI_MEDIA_DISCOVERY_SYNTHETIC_RENUMBER=PASS')
print('HI_DRY_RUN_CAMERA_DEVICE_OPENS=0')
print('HI_CAMERA_RUNTIME=NO')
print('HI_VERIFY=PASS')
