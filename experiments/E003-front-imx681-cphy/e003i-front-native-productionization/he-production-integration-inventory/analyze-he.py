#!/usr/bin/env python3
from pathlib import Path
import ast,hashlib,json,re,subprocess,tempfile
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
HD=BASE/'hd-real-scene-cap-release-envelope'; HC=BASE/'hc-native-cap-release-observer-r27'
GM=BASE/'gm-r5-r27-producer-integration'; GL=BASE/'gl-twentyfour-generation-gain-feed-publisher'; GQ=BASE/'gq-continuous-control-ring-scheduler'; HA=BASE/'ha-native-cap-release-one-write-policy'; CW=BASE/'cw-imx681-atomic-dynamic-control-cluster'; GN=BASE/'gn-twentyseven-frame-r27-transport'
CV=BASE/'cv-native-aec-offline-sensor-control-join'; CU=BASE/'cu-native-aec-raw-stats-request-loop'; CQ=BASE/'cq-aec-output-imx681-control-adapter'; CR=BASE/'cr-native-aec-effective-analyzer-producer'; CT=BASE/'ct-native-aec-bhist-bank4-replay'; DN=BASE/'dn-native-aec-internal-cap'; CF=BASE/'cf-native-aec-final-exposure-si'; CE=BASE/'ce-native-aec-final-target-producer'; CC=BASE/'cc-native-aec-adrc-darkboost-tail'; BY=BASE/'by-native-aec-method11-point-aggregation'; CG=BASE/'cg-native-aec-qword-convergence-input'; CH=BASE/'ch-native-aec-t681-preview-arbitration'; BK=BASE/'bk-native-aec-history-state'; BJ=BASE/'bj-native-aec-log103-coordinate'

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
def status(path): return json.loads(path.read_text())['status']
need(status(HD/'RESULT.json')=='PASS_OFFLINE_REAL_SCENE_CAP_RELEASE_STRATEGY','HD')
need(json.loads((HC/'ATTEMPT1-PASS.json').read_text())['status']=='PASS_CAPTURE_HC_NO_CAP_RELEASE_R27','HC')
need(status(GM/'RESULT.json')=='PASS_OFFLINE_R5_R27_AUTHORIZED_INTEGRATION','GM')
need(status(GL/'RESULT.json')=='PASS_OFFLINE_G1_G24_C_PUBLISHER','GL')
need(status(HA/'RESULT.json')=='PASS_OFFLINE_NATIVE_CAP_RELEASE_ONE_WRITE_POLICY','HA')
# Reproduce the final bounded helper and CAMSS source without opening any camera device.
with tempfile.TemporaryDirectory(prefix='e003i-he-') as td0:
    td=Path(td0); helper=td/'helper'; cam=td/'cam.ko'
    subprocess.run([str(HC/'build-helper.sh'),str(helper)],check=True,stdout=subprocess.DEVNULL)
    subprocess.run([str(HC/'build-camss.sh'),str(cam)],check=True,stdout=subprocess.DEVNULL)
    generated_helper=HC/'build/helper/e003i-hc-caprelease-native-aec.c'
    generated_camss=HC/'build/camss/camss.c'
    helper_source_sha=sha(generated_helper); camss_source_sha=sha(generated_camss)
    helper_binary_sha=sha(helper); camss_module_sha=sha(cam)
need(helper_source_sha=='578f41d5cc0935aff327f500d38c095ed64f7428d2e245adc1f8196e9b3c99a3','helper authority')
need(camss_source_sha=='117136b2c624de5ef3f4c081cdcf9c363cda9f6db5c752b7ade5f5e11b1b3e95','CAMSS authority')
# Canonical native AEC source closure.
native_sources=[
 CV/'native-raw-control-join.c',CV/'native-raw-control-join.h',CU/'native-raw-aec-loop.c',CU/'native-raw-aec-loop.h',CU/'native-stats3a.c',CU/'native-stats3a.h',CQ/'native-imx681-control.c',CQ/'native-imx681-control.h',CR/'native-effective-analyzers.c',CR/'native-effective-analyzers.h',CT/'native-bhist-bank4.c',CT/'native-bhist-bank4.h',DN/'native-aec-request-loop.c',DN/'native-aec-request-loop.h',DN/'native-internal-cap.c',DN/'native-internal-cap.h',CF/'native-final-exposure.c',CF/'native-final-exposure.h',CE/'native-final-target.c',CE/'native-final-target.h',CC/'native-aec-tail.c',CC/'native-aec-tail.h',BY/'native-target-aggregate.c',BY/'native-target-aggregate.h',CG/'native-convergence.c',CG/'native-convergence.h',CH/'native-t681.c',CH/'native-t681.h',BK/'native-aec-state.c',BK/'native-aec-state.h',BJ/'native-log103.c',BJ/'native-log103.h']
for p in native_sources: need(p.is_file(),str(p))
native_manifest={str(p.relative_to(REPO)):sha(p) for p in native_sources}
# GM producer is tracked but dynamically imports many experiment-local modules.
producer=GM/'live-iq-producer.py'; text=producer.read_text(); producer_sha=sha(producer)
dep_names=[]
for m in re.finditer(r"(?:=BASE/'([^']+)'|=BASE/\"([^\"]+)\")",text): dep_names.append(m.group(1) or m.group(2))
dep_names=sorted(set(dep_names))
# Some dependencies are direct files under a stage; preserve exact literal path declarations too.
file_literals=[]
for line in text.splitlines()[:60]:
    if 'FILE=' in line or re.match(r'^[A-Z]+=',line):
        if "BASE/'" in line: file_literals.append(line.strip())
# Current repo has no stable consolidated production tree/package surface.
production_roots=['src','production','packaging','systemd','udev']
root_presence={x:(REPO/x).exists() for x in production_roots}
# Direct tracked authority sources.
authority={
 'kernel_camss':{'source_sha256':camss_source_sha,'direct_tracked_final_source':False,'reproducer':'HC build-camss.sh -> GN R27 transport chain'},
 'sensor_imx681':{'path':str((CW/'imx681.c').relative_to(REPO)),'sha256':sha(CW/'imx681.c'),'direct_tracked_final_source':True},
 'capture_helper':{'source_sha256':helper_source_sha,'binary_sha256':helper_binary_sha,'direct_tracked_final_source':False,'reproducer':'HC build-helper.sh multi-stage transform chain'},
 'iq_producer':{'path':str(producer.relative_to(REPO)),'sha256':producer_sha,'direct_tracked_final_source':True,'experiment_local_dependency_count':len(dep_names)},
 'gain_feed':{'c_sha256':sha(GL/'gain-feed.c'),'h_sha256':sha(GL/'gain-feed.h'),'direct_tracked_final_source':True},
 'continuous_scheduler':{'c_sha256':sha(GQ/'continuous-db-schedule.c'),'h_sha256':sha(GQ/'continuous-db-schedule.h'),'direct_tracked_final_source':True},
 'cap_release_policy':{'c_sha256':sha(HA/'native-cap-release-policy.c'),'h_sha256':sha(HA/'native-cap-release-policy.h'),'direct_tracked_final_source':True},
 'native_aec_sources':{'count':len(native_sources),'manifest':native_manifest,'direct_tracked_final_sources':True},
}
# Count transform depth / absolute-path coupling in current final build route.
build_text=(HC/'build-helper.sh').read_text()
transform_calls=len(re.findall(r'python3 \"\$[^\"]+/make-[^\"]+helper\.py\"',build_text)) + len(re.findall(r'python3 \"\$D/make-hc-helper\.py\"',build_text))
absolute_refs={
 'hc_build_helper':build_text.count('/home/geoca/Documents/SP11-PROJECT'),
 'hc_build_camss':(HC/'build-camss.sh').read_text().count('/home/geoca/Documents/SP11-PROJECT'),
 'gm_producer':text.count('/home/geoca/Documents/SP11-PROJECT'),
}
result={
 'schema':'sp11-e003i-he-production-integration-inventory-v1',
 'status':'PASS_OFFLINE_PRODUCTION_INTEGRATION_INVENTORY',
 'camera_runtime_performed':False,
 'authority':authority,
 'generated_build_products':{'camss_module_sha256':camss_module_sha,'helper_binary_sha256':helper_binary_sha},
 'producer_experiment_dependencies':dep_names,
 'producer_dependency_declarations':file_literals,
 'current_build_coupling':{'helper_transform_steps':transform_calls,'absolute_repo_path_references':absolute_refs,'final_camss_source_tracked_directly':False,'final_helper_source_tracked_directly':False},
 'production_root_presence':root_presence,
 'readiness':{
   'bounded_r27_linux_capture':True,
   'windows_awb_lsc_authority_r27':True,
   'native_aec_control_path':True,
   'changed_post_g3_transport':True,
   'production_native_changed_post_g3_feedback':False,
   'production_native_feedback_blocker':'real scene remains preview-cap-censored; HD requires brighter diffuse scene',
   'consolidated_source_tree':False,
   'hermetic_userspace_build':False,
   'kernel_tree_integration':False,
   'stable_device_discovery':False,
   'service_or_package':False,
   'repeated_stream_live_robustness':False,
   'long_duration_soak':False,
 },
 'integration_risks':[
   'final CAMSS and capture-helper sources are generated through experiment transforms instead of living in a stable production tree',
   'GM producer dynamically imports many experiment-local modules and fixtures',
   'candidate scripts contain machine-specific absolute workspace paths',
   'device/media discovery and lifecycle remain candidate-script responsibilities rather than a production launcher/service',
   'post-G3 native writes must stay fail-closed until the brighter-real-scene cap-release gate is proven',
 ],
 'recommended_order':[
   'HF: create a stable front-IMX681 source bundle by byte-copying proven authorities plus provenance manifest; no behavior change and no runtime',
   'HG: make the bundle hermetic/buildable without experiment-directory imports or absolute workspace paths and prove byte-equivalent outputs',
   'HH: integrate kernel/user-space install and stable media-device discovery with post-G3 writes defaulting fail-closed',
   'HI+: perform fresh bounded repeated-stream and reboot/module recovery validation before any production enablement',
   'separately resume the native-feedback live gate only under the HD-required brighter diffuse real scene',
 ],
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HE_FINAL_CAMSS_SOURCE='+camss_source_sha)
print('HE_FINAL_HELPER_SOURCE='+helper_source_sha)
print('HE_IMX681_SOURCE='+authority['sensor_imx681']['sha256'])
print('HE_GM_PRODUCER='+producer_sha)
print('HE_NATIVE_AEC_FILES='+str(len(native_sources)))
print('HE_PRODUCER_EXPERIMENT_DEPS='+str(len(dep_names)))
print('HE_HELPER_TRANSFORM_STEPS='+str(transform_calls))
print('HE_PRODUCTION_ROOTS_PRESENT='+','.join(k for k,v in root_presence.items() if v) if any(root_presence.values()) else 'none')
print('HE_VERIFY=PASS')
