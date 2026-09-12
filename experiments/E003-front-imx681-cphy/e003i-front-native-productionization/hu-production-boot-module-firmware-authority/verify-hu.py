#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,os,re,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent; BASE=HERE.parent; REPO=HERE.parents[3]
FRONT=REPO/'src/front-imx681'; HT=BASE/'ht-production-deployment-smoke-boundary'; HN=BASE/'hn-snapshot-generation-reset-package'; HQ=BASE/'hq-four-stream-shadow-r27'
GOLDEN_DTB=Path('/boot/sp11-7.1.5-audio-fullio-v19c/x1e80100-microsoft-denali-sp11-fullio-v19c.dtb')
FRONT_DTB=REPO/'experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'
FRONT_BUILDER=REPO/'experiments/E003-front-imx681-cphy/e003h-bounded-vfe1-pix-runtime-candidate/build-pix-frontonly-dtb.py'
KERNEL_BUILD=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
GOLDEN_SHA='2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00'
FRONT_SHA='019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f'
OLD_CAMERA_BASE_SHA='333e3c81c8a490f1b8b444e9a8d8005539799c438f2d03ebc6acfc366074b14e'
CAMSS_SHA='7afe6ed0bd0b945092256c53d111601c44cf33c174c1988945c05d8ef2697e95'
IMX_SHA='ef57ed06941a8c9c3ce6b811268767944affce409936be4eb7f4db09806f63d6'
VERMAGIC='7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'
EXPECTED_ADDED={
'/soc@0/cci@ac15000','/soc@0/cci@ac15000/i2c-bus@0','/soc@0/cci@ac15000/i2c-bus@1','/soc@0/cci@ac15000/i2c-bus@1/camera@10',
'/soc@0/cci@ac16000','/soc@0/cci@ac16000/i2c-bus@0','/soc@0/cci@ac16000/i2c-bus@1','/soc@0/cci@ac16000/i2c-bus@1/camera@10','/soc@0/cci@ac16000/i2c-bus@1/camera@10/port','/soc@0/cci@ac16000/i2c-bus@1/camera@10/port/endpoint',
'/soc@0/clock-controller@ade0000','/soc@0/isp@acb7000','/soc@0/isp@acb7000/ports','/soc@0/isp@acb7000/ports/port@2','/soc@0/isp@acb7000/ports/port@2/endpoint',
'/soc@0/pinctrl@f100000/cci0-default-state','/soc@0/pinctrl@f100000/cci0-default-state/cci0-i2c1-pins','/soc@0/pinctrl@f100000/cci0-sleep-state','/soc@0/pinctrl@f100000/cci0-sleep-state/cci0-i2c1-pins',
'/soc@0/pinctrl@f100000/cci1-master1-default-state','/soc@0/pinctrl@f100000/cci1-master1-sleep-state','/soc@0/pinctrl@f100000/front-imx681-default-state','/soc@0/pinctrl@f100000/front-imx681-default-state/mclk-pins','/soc@0/pinctrl@f100000/front-imx681-default-state/reset-pins','/soc@0/pinctrl@f100000/rear-mclk1-default-state',
'/soc@0/rsc@17500000/regulators-0/ldo7','/soc@0/rsc@17500000/regulators-8','/soc@0/rsc@17500000/regulators-8/ldo1','/soc@0/rsc@17500000/regulators-8/ldo3','/soc@0/rsc@17500000/regulators-8/ldo5','/soc@0/rsc@17500000/regulators-8/ldo6'}
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(cmd,check=True,**kw): return subprocess.run(cmd,text=True,capture_output=True,check=check,**kw)
def fdtget(dt,node,prop,typ='x'):
    return run(['fdtget','-t',typ,str(dt),node,prop]).stdout.strip().split()
def node_paths(dt:Path)->set[str]:
    cp=run(['dtc','-q','-s','-I','dtb','-O','dts',str(dt)])
    stack=[]; out=set()
    for raw in cp.stdout.splitlines():
        s=raw.strip()
        if not s or s.startswith('/dts-') or s.startswith('/memreserve/'): continue
        if s.endswith('{'):
            name=s[:-1].strip()
            if ':' in name: name=name.split(':',1)[1].strip()
            if name=='/': stack=['']
            else: stack.append(name)
            out.add('/'+'/'.join(x for x in stack if x)); continue
        if s in ('};','}') and stack: stack.pop()
    return out
ht=json.loads((HT/'RESULT.json').read_text()); hn=json.loads((HN/'RESULT.json').read_text()); hq=json.loads((HQ/'RESULT.json').read_text())
need(ht['status']=='PASS_OFFLINE_PRODUCTION_DEPLOYMENT_BOUNDARY','HT parent')
need(hn['status']=='PASS_OFFLINE_SNAPSHOT_GENERATION_RESET_PACKAGE','HN parent')
need(hq['status']=='PASS_CAPTURE_HQ_FOUR_STREAM_SHADOW_R27_GOLDEN_RESTORED_RETIRED','HQ live parent')
need(sha(GOLDEN_DTB)==GOLDEN_SHA,'Golden DTB identity')
need(sha(FRONT_DTB)==FRONT_SHA,'front-only DTB identity')
builder=FRONT_BUILDER.read_text(); m=re.search(r"EXPECTED_BASE_SHA256 = '([0-9a-f]{64})'",builder); need(m and m.group(1)==OLD_CAMERA_BASE_SHA,'front-only builder base identity')
need(GOLDEN_SHA!=OLD_CAMERA_BASE_SHA,'front-only candidate unexpectedly derived from current Golden')
ng=node_paths(GOLDEN_DTB); nc=node_paths(FRONT_DTB)
need(len(ng)==1402 and len(nc)==1433,'DT node counts')
need(ng <= nc,'front-only DT not structural superset of Golden node paths')
need(nc-ng==EXPECTED_ADDED,'candidate-only node set drift '+repr(sorted(nc-ng)))
need(not (ng-nc),'Golden-only node paths exist '+repr(sorted(ng-nc)))
# Exact proven front route / resources.
need(run(['fdtget','-l',str(FRONT_DTB),'/soc@0/isp@acb7000/ports']).stdout.split()==['port@2'],'front-only CAMSS ports')
need(fdtget(FRONT_DTB,'/soc@0/isp@acb7000','iommus')==['3d','800','60','3d','820','60','3d','840','60','3d','860','60','3d','18a0','0'],'CAMSS IOMMU authority')
front_sensor='/soc@0/cci@ac16000/i2c-bus@1/camera@10'; front_ep=front_sensor+'/port/endpoint'; cam_ep='/soc@0/isp@acb7000/ports/port@2/endpoint'; rear='/soc@0/cci@ac15000/i2c-bus@1/camera@10'
need(fdtget(FRONT_DTB,front_sensor,'compatible','s')==['sony,imx681'],'front sensor identity')
need(fdtget(FRONT_DTB,front_sensor,'reg')==['10'],'front sensor address')
need(fdtget(FRONT_DTB,rear,'status','s')==['disabled'],'rear not disabled in front-only DT')
for ep in (front_ep,cam_ep):
    need(fdtget(FRONT_DTB,ep,'bus-type')==['1'],ep+' bus-type')
    need(fdtget(FRONT_DTB,ep,'data-lanes')==['0'],ep+' data-lanes')
# Current modules: exact HN hashes/vermagic/dependency order authority and no firmware loader/token coupling.
with tempfile.TemporaryDirectory(prefix='e003i-hu-build-') as td0:
    td=Path(td0); env=os.environ.copy(); env['KERNEL_BUILD']=str(KERNEL_BUILD)
    run([str(FRONT/'build-production.sh'),str(td)],env=env)
    cam=td/'qcom-camss.ko'; sensor=td/'imx681.ko'
    need(sha(cam)==CAMSS_SHA and sha(sensor)==IMX_SHA,'module identity')
    for mod in (cam,sensor):
        need(run(['modinfo','-F','vermagic',str(mod)]).stdout.strip()==VERMAGIC,'vermagic '+mod.name)
        need(run(['modinfo','-F','firmware',str(mod)]).stdout.strip()=='','firmware metadata '+mod.name)
        nm=run(['nm','-u',str(mod)],check=False).stdout.lower(); need('firmware' not in nm,'firmware unresolved symbol '+mod.name)
        strings=run(['strings',str(mod)]).stdout
        need('sp11_camera_e003i' not in strings,'candidate token embedded '+mod.name)
    cam_dep=run(['modinfo','-F','depends',str(cam)]).stdout.strip().split(',')
    imx_dep=run(['modinfo','-F','depends',str(sensor)]).stdout.strip().split(',')
    need(cam_dep==['videobuf2-v4l2','videobuf2-dma-sg','videodev','mc','v4l2-async','videobuf2-common','v4l2-fwnode'],'CAMSS dependency set')
    need(imx_dep==['v4l2-async','videodev','v4l2-cci','mc','v4l2-fwnode'],'IMX dependency set')
# Current production source has no functional firmware-loader coupling; only historical retention comments mention firmware.
source='\n'.join(p.read_text(errors='replace') for p in (FRONT/'kernel').rglob('*') if p.is_file() and p.suffix in ('.c','.h'))
functional=[line for line in source.splitlines() if re.search(r'\b(?:request_firmware|firmware_request_nowarn|request_firmware_direct)\s*\(',line) and not line.lstrip().startswith(('/*','*','//'))]
need(not functional,'functional firmware loader calls '+repr(functional))
launcher=(FRONT/'bin/front-imx681-launcher.py').read_text(); need("R4=IQ/'authority/r4-bootstrap.bin'" in launcher and "PRODUCER=IQ/'live-iq-producer.py'" in launcher,'packaged IQ authority')
menu=(HQ/'99zzzzzz_sp11_camera_e003i_hq_four_stream_shadow_r27').read_text(); need('firmware_class.path=' in menu,'historical firmware cmdline absent')
load=(HQ/'load.sh').read_text()
for dep in ('mc','videodev','v4l2_async','v4l2_fwnode','videobuf2_common','videobuf2_memops','videobuf2_v4l2','videobuf2_dma_sg','v4l2_cci'): need('modprobe "$m"' in load,'dependency loop absent')
need('insmod "$P/build/qcom-camss.ko"' in load and 'insmod "$P/build/imx681.ko"' in load,'proven module load order')
pre=(HQ/'runtime-preflight.sh').read_text(); need('sp11_camera_e003i_hq_four_stream_shadow_r27=1' in pre,'HQ fail-closed boot token gate')
result={
 'schema':'sp11-e003i-hu-production-boot-module-firmware-authority-v1',
 'status':'PASS_OFFLINE_PRODUCTION_BOOT_MODULE_FIRMWARE_AUTHORITY',
 'parent':'HT production deployment boundary',
 'camera_runtime_performed':False,'golden_system_modified':False,
 'dtb':{
   'golden_sha256':GOLDEN_SHA,'proven_front_only_sha256':FRONT_SHA,'proven_front_only_builder_base_sha256':OLD_CAMERA_BASE_SHA,
   'proven_front_only_derived_from_current_golden':False,'golden_node_paths':len(ng),'front_only_node_paths':len(nc),'common_node_paths':len(ng&nc),'candidate_only_node_paths':len(nc-ng),'golden_only_node_paths':len(ng-nc),
   'candidate_only_nodes':sorted(EXPECTED_ADDED),'structural_superset_only':True,'direct_reuse_on_protected_golden_authorized':False,
   'front_camss_ports':['port@2'],'front_iommus':['0x800/0x60','0x820/0x60','0x840/0x60','0x860/0x60','0x18a0/0'],'front_sensor':'sony,imx681@0x10','rear_sensor_status':'disabled','cphy_bus_type':1,'data_lanes':[0]
 },
 'modules':{
   'qcom_camss_sha256':CAMSS_SHA,'imx681_sha256':IMX_SHA,'vermagic':VERMAGIC,
   'qcom_camss_depends':['videobuf2-v4l2','videobuf2-dma-sg','videodev','mc','v4l2-async','videobuf2-common','v4l2-fwnode'],
   'imx681_depends':['v4l2-async','videodev','v4l2-cci','mc','v4l2-fwnode'],
   'proven_load_order':['dependency modules','qcom-camss.ko','imx681.ko'],'candidate_boot_token_enforced_by_modules':False
 },
 'firmware':{
   'historical_candidate_firmware_class_path_present':True,'current_module_firmware_metadata_entries':0,'current_module_firmware_unresolved_symbols':0,'current_source_functional_firmware_loader_calls':0,
   'historical_firmware_class_path_required_by_current_production_runtime':False,'current_iq_authority':'packaged r4-bootstrap.bin + live-iq-producer.py'
 },
 'activation':{
   'hq_boot_token_fail_closed_preflight_proven':True,'module_internal_boot_token_gate':False,'production_equivalent_fail_closed_activation_gate_required':True
 },
 'conclusion':'do not overwrite or directly reuse the historical front-only DTB on Golden; construct a new camera-capable DTB from the exact current Golden DTB plus proven camera additions, then regress all Golden common-node semantics before runtime',
 'next_gate':'HV current-Golden camera-DTB merge construction and semantic regression offline'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HU_DTB_AUTHORITY=PASS GOLDEN_NODES=1402 FRONT_NODES=1433 ADDED=31 REMOVED=0')
print('HU_DIRECT_FRONT_DTB_REUSE=BLOCKED OLD_BASE='+OLD_CAMERA_BASE_SHA[:12]+' CURRENT_GOLDEN='+GOLDEN_SHA[:12])
print('HU_MODULE_AUTHORITY=PASS CAMSS='+CAMSS_SHA[:12]+' IMX='+IMX_SHA[:12]+' VERMAGIC=PASS')
print('HU_FIRMWARE_LOADER=NONE HISTORICAL_FIRMWARE_PATH_REQUIRED=NO')
print('HU_ACTIVATION_GATE=REQUIRED MODULE_INTERNAL_GATE=NO')
print('HU_CAMERA_RUNTIME=NO GOLDEN_MODIFIED=NO')
print('HU_VERIFY=PASS')
