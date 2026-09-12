#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,os,subprocess,tempfile
HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
BUNDLE=REPO/'src/front-imx681'
HE=BASE/'he-production-integration-inventory'; HC=BASE/'hc-native-cap-release-observer-r27'
K=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
EXPECTED_HELPER='578f41d5cc0935aff327f500d38c095ed64f7428d2e245adc1f8196e9b3c99a3'
EXPECTED_HELPER_BIN='fc305c89c9d7ff62fa85c58d987b5738c5ad53ee850e2c74903aa822180adb67'
EXPECTED_CAMSS='117136b2c624de5ef3f4c081cdcf9c363cda9f6db5c752b7ade5f5e11b1b3e95'
EXPECTED_IMX='6e14f6d345759eb61a2a54129437e04f747e64d59d3bfc264069a0ecddeeb78e'
EXPECTED_PRODUCER='fa2f6f8c912a5ea5ab031ab149d1da45809ef24b79a111a5a64e3784c4af6ed1'
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v: raise AssertionError(m)
need(json.loads((HE/'RESULT.json').read_text())['status']=='PASS_OFFLINE_PRODUCTION_INTEGRATION_INVENTORY','HE authority')
need(BUNDLE.is_dir(),'bundle root')
# Regenerate final authorities from the experiment chain for byte comparison.
subprocess.run(['python3',str(HC/'verify.py')],check=True,stdout=subprocess.DEVNULL)
generated_helper=HC/'build/helper/e003i-hc-caprelease-native-aec.c'
generated_camss=HC/'build/camss/camss.c'
need(sha(generated_helper)==EXPECTED_HELPER,'generated helper authority')
need(sha(generated_camss)==EXPECTED_CAMSS,'generated CAMSS authority')
need(sha(BUNDLE/'userspace/runtime/e003i-hc-caprelease-native-aec.c')==EXPECTED_HELPER,'bundled helper')
need(sha(BUNDLE/'kernel/camss/camss.c')==EXPECTED_CAMSS,'bundled CAMSS')
need(sha(BUNDLE/'kernel/imx681/imx681.c')==EXPECTED_IMX,'bundled IMX681')
need(sha(BUNDLE/'userspace/iq/live-iq-producer.py')==EXPECTED_PRODUCER,'bundled producer')
# Provenance is complete for copied authority files and still matches origins.
prov=json.loads((BUNDLE/'PROVENANCE.json').read_text())
need(prov['schema']=='sp11-front-imx681-stable-source-provenance-v1','provenance schema')
entries=prov['files']; need(len(entries)==82,'82 authority files')
need(len({e['bundle_path'] for e in entries})==len(entries),'unique provenance paths')
external_root=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src/drivers/media/platform/qcom/camss')
for e in entries:
    bp=BUNDLE/e['bundle_path']; need(bp.is_file(),e['bundle_path']); need(sha(bp)==e['sha256'],'bundle hash '+e['bundle_path'])
    origin=e['origin']
    if origin=='HC build-camss final generated authority': need(bp.read_bytes()==generated_camss.read_bytes(),'generated CAMSS bytes')
    elif origin=='HC build-helper final generated authority': need(bp.read_bytes()==generated_helper.read_bytes(),'generated helper bytes')
    elif origin.startswith('/home/geoca/Documents/SP11-PROJECT/02-kernel/'):
        op=Path(origin); need(op.is_file(),'external origin '+origin); need(bp.read_bytes()==op.read_bytes(),'external byte copy '+origin)
    else:
        op=REPO/origin; need(op.is_file(),'repo origin '+origin); need(bp.read_bytes()==op.read_bytes(),'repo byte copy '+origin)
# Stable source/build surface must not depend on this user's absolute workspace path.
for p in BUNDLE.rglob('*'):
    if not p.is_file() or p.name=='PROVENANCE.json' or p.suffix.lower() in {'.md'}: continue
    data=p.read_bytes()
    need(b'/home/geoca/Documents/SP11-PROJECT' not in data,'absolute workspace coupling '+str(p.relative_to(BUNDLE)))
# Offline build from the consolidated bundle. No /dev node is opened.
with tempfile.TemporaryDirectory(prefix='e003i-hf-build-') as td0:
    out=Path(td0)/'out'; env=os.environ.copy(); env['KERNEL_BUILD']=str(K)
    subprocess.run([str(BUNDLE/'build-offline.sh'),str(out)],check=True,stdout=subprocess.DEVNULL,env=env)
    helper=out/'front-imx681-capture-helper'; cam=out/'qcom-camss.ko'; imx=out/'imx681.ko'
    need(sha(helper)==EXPECTED_HELPER_BIN,'helper binary exact authority')
    cam_ver=subprocess.check_output(['modinfo','-F','vermagic',str(cam)],text=True).strip()
    imx_ver=subprocess.check_output(['modinfo','-F','vermagic',str(imx)],text=True).strip()
    need(cam_ver==VERMAGIC,'CAMSS vermagic'); need(imx_ver==VERMAGIC,'IMX681 vermagic')
    build={'helper_sha256':sha(helper),'camss_module_sha256':sha(cam),'imx681_module_sha256':sha(imx),'vermagic':VERMAGIC}
result={
 'schema':'sp11-e003i-hf-stable-front-imx681-source-bundle-v1',
 'status':'PASS_OFFLINE_STABLE_FRONT_IMX681_SOURCE_BUNDLE',
 'bundle_root':'src/front-imx681',
 'provenance_authority_files':len(entries),
 'authority':{'camss_source_sha256':EXPECTED_CAMSS,'capture_helper_source_sha256':EXPECTED_HELPER,'capture_helper_binary_sha256':EXPECTED_HELPER_BIN,'imx681_source_sha256':EXPECTED_IMX,'iq_producer_sha256':EXPECTED_PRODUCER},
 'offline_build':build,
 'properties':{
   'final_camss_source_directly_tracked_in_bundle':True,
   'final_helper_source_directly_tracked_in_bundle':True,
   'native_aec_sources_consolidated':True,
   'kernel_camss_base_consolidated':True,
   'imx681_driver_consolidated':True,
   'runtime_c_helper_buildable_from_bundle':True,
   'kernel_modules_buildable_from_bundle':True,
   'absolute_workspace_path_coupling_in_build_sources':False,
   'iq_producer_source_frozen_byte_exact':True,
   'iq_producer_hermetic':False,
   'camera_runtime_performed':False,
   'post_g3_native_feedback_proven':False,
 },
 'next_gate':'HG hermetic IQ producer dependency relocation and byte-exact R5..R27 regression from the stable bundle',
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HF_PROVENANCE=82_FILES_PASS')
print('HF_CAMSS_SOURCE='+EXPECTED_CAMSS)
print('HF_HELPER_SOURCE='+EXPECTED_HELPER)
print('HF_HELPER_BINARY_EXACT='+EXPECTED_HELPER_BIN)
print('HF_IMX681_SOURCE='+EXPECTED_IMX)
print('HF_KERNEL_BUILD=PASS VERMAGIC='+VERMAGIC)
print('HF_IQ_PRODUCER_HERMETIC=NO_NEXT_HG')
print('HF_VERIFY=PASS')
