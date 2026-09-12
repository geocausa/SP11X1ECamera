#!/usr/bin/env python3
from __future__ import annotations
import json,os,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent; BASE=HERE.parent; REPO=HERE.parents[3]
FRONT=REPO/'src/front-imx681'; HS=BASE/'hs-production-install-rollback-contract'; HR=BASE/'hr-production-repeated-open-handoff'; HQ=BASE/'hq-four-stream-shadow-r27'
KERNEL_BUILD=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
def need(v,m):
    if not v: raise AssertionError(m)
def run(cmd,check=True,**kw): return subprocess.run(cmd,text=True,capture_output=True,check=check,**kw)
def sha(p):
    import hashlib
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
hs=json.loads((HS/'RESULT.json').read_text()); hr=json.loads((HR/'RESULT.json').read_text())
need(hs['status']=='PASS_OFFLINE_PRODUCTION_INSTALL_ROLLBACK_CONTRACT','HS parent')
need(hr['status']=='PASS_OFFLINE_PRODUCTION_REPEATED_OPEN_HANDOFF','HR parent')
need(hs['runtime_package_manifest_sha256']==hr['package']['manifest_sha256'],'package continuity')
# Current protected Golden is intentionally not camera-enabled.
need(run(['uname','-r']).stdout.strip()=='7.1.5-sp11-render-parity-v4+','Golden kernel')
cmdline=Path('/proc/cmdline').read_text()
need('sp11_camera_e003i_' not in cmdline,'candidate token on Golden')
env=run(['sudo','-n','grub-editenv','/boot/grub/grubenv','list']).stdout
need('saved_entry=sp11-audio-fullio-v19c' in env,'Golden saved entry')
need(not any(x.startswith('next_entry=') and x!='next_entry=' for x in env.splitlines()),'pending one-shot')
for m in ('qcom_camss','imx681','ov13858'): need(not Path('/sys/module',m).exists(),'camera module loaded '+m)
for pat in ('media*','video*','v4l-subdev*'): need(not list(Path('/dev').glob(pat)),'camera node present '+pat)
for p in ('/usr/lib/sp11-front-imx681','/usr/bin/sp11-front-imx681','/usr/bin/sp11-front-imx681-discover'): need(not Path(p).exists(),'production install already present '+p)
# Live discovery on Golden fails closed without creating camera state.
disc=FRONT/'bin/front-imx681-discover.py'; cp=run([str(disc),'--json'],check=False)
need(cp.returncode!=0 and 'front IMX681 media discovery failed: matches=0' in cp.stderr,'Golden discovery did not fail closed')
for pat in ('media*','video*','v4l-subdev*'): need(not list(Path('/dev').glob(pat)),'discovery created node '+pat)
# Userspace package/deployer do not own boot/module activation.
launcher=(FRONT/'bin/front-imx681-launcher.py').read_text(); installer=(FRONT/'install-package.sh').read_text()
for forbidden in ('modprobe','insmod','depmod','update-grub','grub-reboot','systemctl'):
    need(forbidden not in launcher,'launcher unexpectedly owns '+forbidden)
for forbidden in ('modprobe','insmod','depmod','update-grub','grub-reboot','systemctl'):
    need(forbidden not in installer,'installer unexpectedly owns '+forbidden)
# Package layout is userspace/private modules only: no boot, /etc, systemd, or /lib/modules integration.
with tempfile.TemporaryDirectory(prefix='e003i-ht-') as td0:
    td=Path(td0); build=td/'build'; envb=os.environ.copy(); envb['KERNEL_BUILD']=str(KERNEL_BUILD)
    run([str(FRONT/'build-production.sh'),str(build)],env=envb)
    stage=td/'stage'; penv=envb.copy(); penv['BUILD_DIR']=str(build); run([str(FRONT/'stage-package.sh'),str(stage)],env=penv)
    need(sha(stage/'PACKAGE-MANIFEST.sha256')==hs['runtime_package_manifest_sha256'],'runtime package drift')
    need((stage/'usr/lib/sp11-front-imx681/build/qcom-camss.ko').is_file(),'private CAMSS module absent')
    need((stage/'usr/lib/sp11-front-imx681/build/imx681.ko').is_file(),'private sensor module absent')
    for p in ('boot','etc','lib/modules','usr/lib/systemd','etc/systemd'): need(not (stage/p).exists(),'package unexpectedly owns '+p)
# Proven live candidate explicitly supplies boot graph/firmware and manually loads modules; these are separate deployment authorities.
menu=(HQ/'99zzzzzz_sp11_camera_e003i_hq_four_stream_shadow_r27').read_text(); load=(HQ/'load.sh').read_text(); preflight=(HQ/'runtime-preflight.sh').read_text()
need('devicetree /boot/sp11-7.1.5-camera-e003i-hq-four-stream-shadow-r27/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb' in menu,'front-only DTB authority absent')
need('firmware_class.path=' in menu,'firmware-path authority absent')
need('modprobe.blacklist=qcom_camss,imx681,ov13858' in menu,'candidate module blacklist absent')
need('insmod "$P/build/qcom-camss.ko"' in load and 'insmod "$P/build/imx681.ko"' in load,'manual module-load authority absent')
need('sp11_camera_e003i_hq_four_stream_shadow_r27=1' in preflight,'candidate boot-token gate absent')
result={
 'schema':'sp11-e003i-ht-production-deployment-smoke-boundary-v1',
 'status':'PASS_OFFLINE_PRODUCTION_DEPLOYMENT_BOUNDARY',
 'parent':'HS production install/rollback contract',
 'camera_runtime_performed':False,
 'golden_system_modified':False,
 'golden':{'kernel':'7.1.5-sp11-render-parity-v4+','saved_entry':'sp11-audio-fullio-v19c','next_entry_empty':True,'camera_modules_loaded':0,'camera_nodes':0,'production_install_present':False,'live_discovery_fail_closed':True},
 'runtime_package_manifest_sha256':hs['runtime_package_manifest_sha256'],
 'runtime_package_owns_boot_integration':False,
 'runtime_package_owns_module_install_or_activation':False,
 'runtime_package_owns_systemd_integration':False,
 'installer_owns_boot_or_module_activation':False,
 'proven_live_environment_requires':[
   'front-only proven camera DTB/graph authority',
   'stable camera firmware search-path authority',
   'exact Golden-vermagic qcom-camss and imx681 module load policy',
   'candidate/production boot-token or equivalent fail-closed runtime gate',
 ],
 'real_root_package_install_ready':False,
 'blocker':'boot graph + firmware + module activation remain separate from the userspace/runtime install transaction',
 'next_gate':'HU production boot/module/firmware integration authority offline'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('HT_GOLDEN_DEPLOYMENT_BOUNDARY=PASS CAMERA_NODES=0 MODULES=0 INSTALL=ABSENT')
print('HT_GOLDEN_DISCOVERY=FAIL_CLOSED_EXPECTED')
print('HT_RUNTIME_PACKAGE_BOOT_INTEGRATION=NO MODULE_ACTIVATION=NO')
print('HT_REAL_ROOT_INSTALL_READY=NO')
print('HT_CAMERA_RUNTIME=NO GOLDEN_MODIFIED=NO')
print('HT_VERIFY=PASS')
