#!/usr/bin/env python3
import hashlib, json, pathlib, re, shutil, subprocess, tempfile

D = pathlib.Path(__file__).resolve().parent
REPO = D.parents[2]
SRC = pathlib.Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src')
CAMSS = SRC/'drivers/media/platform/qcom/camss/camss.c'
PATCH = D/'0056-x1e-front-ife1-camnoc-300mhz.patch'
MODULE = D/'qcom-camss.ko'
BASE_SHA = 'c5e01fbf9b4e9ae6c687e1adbbb64e1450a9a677ac2ae15d2b5779ffc3a6a24c'
NEW_SHA = '945a5765667ab6a2bada9395079cd519e7afc038afaa8d57d99926dd38c50795'
PATCH_SHA = '73ad65c3a95ea151d2174ab411ff6c49a423d6cd496bab186fff60c021acc7bf'
MODULE_SHA = '072aae4359a77e3eb41847cda2f34a9355bc1a9e68e8c0fd2a0a422bf4e18f05'
WIN_KD_SHA = '237e5c7ba0eeef73e0b7452a61778003d3364471ec1560e2649fdd35ac2e15f3'
LINUX_0055_SHA = '9fdba6fad49d493d8eafb4a97a658323e70e09b20f2a110a06457bb9496d96b0'
VERMAGIC = '7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def need(c,m):
    if not c: raise SystemExit('FAIL: '+m)

def run(*args, **kw):
    return subprocess.run(args, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kw)

need(sha(CAMSS)==NEW_SHA, 'current camss.c hash')
need(sha(PATCH)==PATCH_SHA, 'patch hash')
need(sha(MODULE)==MODULE_SHA, 'module hash')
need((REPO/'experiments/E003-front-imx681-cphy/e003h-camnoc-rate-0055-candidate/WINDOWS-E003H-CAMNOC-RATE-20260831.log').is_file(), 'Windows KD evidence absent')
need(sha(REPO/'experiments/E003-front-imx681-cphy/e003h-camnoc-rate-0055-candidate/WINDOWS-E003H-CAMNOC-RATE-20260831.log')==WIN_KD_SHA, 'Windows KD hash')
need(sha(REPO/'experiments/E003-front-imx681-cphy/e003h-camnoc-rate-0055-candidate/runtime-0055-analysis.json')==LINUX_0055_SHA, '0055 analysis hash')

patch = PATCH.read_text()
need(patch.count('--- a/drivers/media/platform/qcom/camss/camss.c')==1, 'patch old path')
need(patch.count('+++ b/drivers/media/platform/qcom/camss/camss.c')==1, 'patch new path')
need('CAMSS_X1E_FRONT_CAMNOC_RT_RATE 300000000UL' in patch, '300 MHz constant')
need('vfe->camss->res->version != CAMSS_X1E80100 || vfe->id != 1' in patch, 'X1E/IFE1 scope')
need('strcmp(clock->name, "camnoc_rt_axi")' in patch, 'clock name scope')
need(patch.count('+\t\trounded = clk_round_rate(')==1, 'round-rate call count')
need(patch.count('+\t\treturn clk_set_rate(clock->clk, rounded);')==1, 'set-rate call count')
added='\n'.join(l[1:] for l in patch.splitlines() if l.startswith('+') and not l.startswith('+++'))
for forbidden in ('writel(', 'writel_relaxed(', 'readl(', 'readl_relaxed(', 'regmap_write(', 'iowrite', 'MODE_SELECT', 'csid680_', 'vfe680_x1e_pix_runtime_bus_prepare('):
    need(forbidden not in added, 'forbidden added hardware programming: '+forbidden)

s = CAMSS.read_text()
validate = s.index('ret = camss_x1e_pix_runner_validate(camss, req);')
pm = s.index('ret = v4l2_pipeline_pm_get(video_entity);', validate)
rate = s.index('ret = camss_x1e_front_camnoc_rt_set_rate(vfe);', pm)
alloc = s.index('ret = vfe680_x1e_pix_runtime_alloc(', rate)
rtcdm = s.index('ret = camss_x1e_pix_rtcdm_open_start(camss);', alloc)
need(validate < pm < rate < alloc < rtcdm, 'runner ordering')
need(s.count('camss_x1e_front_camnoc_rt_set_rate(vfe);')==1, 'rate callsite count')
need(s.count('CAMSS_X1E_FRONT_CAMNOC_RT_RATE')==3, 'rate constant use count')

# Reverse the patch from the current source and require the exact frozen 0055/0054 source.
with tempfile.TemporaryDirectory() as td:
    td=pathlib.Path(td)
    target=td/'drivers/media/platform/qcom/camss/camss.c'
    target.parent.mkdir(parents=True)
    shutil.copy2(CAMSS,target)
    subprocess.run(['patch','-R','-p1','-i',str(PATCH)],cwd=td,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    need(sha(target)==BASE_SHA, 'reverse patch baseline hash')
    subprocess.run(['patch','-p1','-i',str(PATCH)],cwd=td,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    need(sha(target)==NEW_SHA, 'forward patch new hash')

vermagic = subprocess.check_output(['modinfo','-F','vermagic',str(MODULE)],text=True).strip()
need(vermagic==VERMAGIC, 'module vermagic')
build=(D/'CAMSS-0056-BUILD.raw.txt').read_text()
need('error:' not in build.lower() and 'warning:' not in build.lower(), 'build warning/error')
check=(D/'CHECKPATCH.raw.txt').read_text()
need('total: 0 errors, 0 warnings, 0 checks' in check, 'checkpatch')

analysis={
  'schema':'sp11-e003h-camnoc-rate-parity-0056-static-inspection-v1',
  'accepted':True,
  'base_camss_sha256':BASE_SHA,
  'camss_sha256':NEW_SHA,
  'patch_sha256':PATCH_SHA,
  'module_sha256':MODULE_SHA,
  'vermagic':VERMAGIC,
  'scope':{'soc':'CAMSS_X1E80100','vfe_id':1,'clock':'camnoc_rt_axi','rate_hz':300000000,'call_path':'validated E003h PIX one-shot runner only'},
  'ordering':'front validate -> pipeline PM/power -> CAMNOC CCF set-rate -> PIX alloc -> RT-CDM/startup',
  'new_direct_mmio_reads':0,
  'new_direct_mmio_writes':0,
  'new_sensor_register_values':0,
  'new_csid_register_values':0,
  'new_vfe_register_values':0,
  'new_clock_rate_requests':1,
  'clock_api':['clk_round_rate','clk_set_rate'],
  'windows_rate_evidence_sha256':WIN_KD_SHA,
  'linux_0055_analysis_sha256':LINUX_0055_SHA,
  'reverse_patch_exact':True,
  'forward_patch_exact':True,
  'runtime_authorized':False,
}
out=D/'0056-static-inspection.json'
out.write_text(json.dumps(analysis,indent=2,sort_keys=True)+'\n')
print(json.dumps(analysis,indent=2,sort_keys=True))
