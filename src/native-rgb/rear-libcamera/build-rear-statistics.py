#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Quarantined rear statistics source qualification. NEVER installs or arms.
The kernel stage disables rear runtime authorization and has no valid profile.
Hosted tests, ARM64 kernel compilation, and real generated libcamera IPA build.
"""
import json,hashlib,shutil,subprocess,importlib.util,os,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;N=HERE.parent;ROOT=HERE.parents[2];PROJECT=ROOT.parents[1]
BASE=PROJECT/'02-kernel/native-rgb-rear-generation-20261007-69/camss'
OUT=PROJECT/'02-kernel/native-rgb-rear-statistics-source-20261009-04'
SOURCE=PROJECT/'06-camera/reference/libcamera-v0.7.0-native-ir'
LIBSOURCE=PROJECT/'06-camera/reference/libcamera-native-rgb-rear-statistics-source-20261009-04'
LIBBUILD=OUT/'libcamera'
HEAD='4f25547d1c24063080e17db08972327bf9d7e840'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def once(p,a,b):
 t=p.read_text();assert t.count(a)==1,(p,a);p.write_text(t.replace(a,b,1))
def run(args,log):
 with (OUT/log).open('x') as f:subprocess.run([str(x) for x in args],stdout=f,stderr=subprocess.STDOUT,check=True,cwd=ROOT)
def main():
 os.umask(0o077)
 subprocess.run(['bash',ROOT/'tools/camera-overlap-guard.sh','--require-golden','--require-no-camera-process','--ignore-parent-builder','--expect-head',HEAD,'--expect-origin',HEAD],check=True)
 assert not OUT.exists() and not LIBSOURCE.exists()
 assert BASE.is_dir()
 OUT.mkdir();camss=OUT/'camss';camss.mkdir()
 # Copy SOURCE files only; never alter or hardlink the retired build69.
 for p in BASE.iterdir():
  if p.is_file() and (p.suffix in ('.c','.h','.inc') or p.name in ('Makefile','Kconfig')) and p.name!='qcom-camss.mod.c':
   shutil.copyfile(p,camss/p.name)
 spec=importlib.util.spec_from_file_location('stats_overlay',N/'rear-v4l2/apply-rear-statistics.py')
 overlay=importlib.util.module_from_spec(spec);spec.loader.exec_module(overlay)
 contract=overlay.apply(camss)
 p=camss/'native-rear-generation-hook.inc'
 once(p,' return native_rear_generation_trial &&',' return false && native_rear_generation_trial &&')
 ident=camss/'native-rear-generation-identity.h'
 text=ident.read_text();match=re.search(r'#define NATIVE_REAR_GENERATION_INPUT_BYTES (\d+)U',text);assert match
 ident.write_text('#define NATIVE_REAR_GENERATION_FIRMWARE "qcom/sp11/rear-statistics-SOURCE-ONLY-NO-FIRMWARE.bin"\n#define NATIVE_REAR_GENERATION_INPUT_BYTES '+match[1]+'U\nstatic const u8 native_rear_generation_input_sha256[32]={0};\n')
 report=dict(status='BUILDING_REAR_STATISTICS_SOURCE_ONLY',base_head=HEAD,
   base_hardware='E-NATIVE-REAR-GENERATION-56',installed=False,armed=False,
   hardware_access=False,runtime_authorization=False,valid_profile=False,
   automatic_exposure=False,decoded_photometry=False,contract=contract,hosted=[])
 try:
  # Execute the actual shared producer/admission and actual kernel copy hook.
  for compiler,language,source in [
   ('gcc','c',N/'rear-v4l2/test-rear-statistics-copy.c'),
   ('clang','c',N/'rear-v4l2/test-rear-statistics-copy.c'),
   ('g++','c++',HERE/'test-rear-statistics.cpp'),
   ('clang++','c++',HERE/'test-rear-statistics.cpp')]:
   label=compiler.replace('+','p')+'-'+source.stem
   binary=OUT/label
   run([compiler,'-std=gnu11' if language=='c' else '-std=c++17','-Wall','-Wextra','-Werror',
    '-O1','-g','-fsanitize=address,undefined','-fno-omit-frame-pointer',
    '-I'+str(camss),'-I'+str(HERE),source,'-o',binary],label+'-compile.log')
   run([binary],label+'-run.json')
   proof=json.loads((OUT/(label+'-run.json')).read_text());assert proof['status'].startswith('PASS')
   report['hosted'].append(dict(compiler=compiler,**proof))
  # Check integration against the actual staged path, not just a model.
  aux=(camss/'native-rear-live-aux-retire.inc').read_text()
  assert aux.index('native_rear_live_replacement_read(vfe')<aux.index('native_rear_statistics_before_aux_release(vfe')<aux.index('e008d_rear_aux_release(vfe')
  base_aux=(BASE/'native-rear-live-aux-retire.inc').read_text()
  original=aux.replace('\n#include "native-rear-stats.h"\n#include "native-rear-statistics-copy.inc"','').replace(' ret = native_rear_statistics_before_aux_release(vfe,pair,result,cursor);\n if (ret)\n  return ret;\n','')
  assert original==base_aux
  run(['make','-C',PROJECT/'02-kernel/e003i-front-production-src','O='+str(PROJECT/'02-kernel/build-runtime-v4-headers-20260826'),'M='+str(camss),'CONFIG_VIDEO_QCOM_CAMSS=m','W=1','KCFLAGS=-Werror','-j4','modules'],'kernel-compile.log')
  assert not re.search(r'warning:|error:',(OUT/'kernel-compile.log').read_text(),re.I)
  print('PASS_ARM64_KERNEL_STATISTICS_SOURCE_BUILD',flush=True)
  manifest=json.loads((N/'libcamera/sources.json').read_text())
  assert subprocess.check_output(['git','-C',SOURCE,'rev-parse','HEAD'],text=True).strip()==manifest['libcamera_commit']
  run(['git','clone','--no-local','--no-hardlinks',SOURCE,LIBSOURCE],'libcamera-clone.log')
  for group in ['libcamera_inputs','pipeline_inputs']:
   for name,digest in manifest[group].items():assert sha(LIBSOURCE/name)==digest,name
  pipeline=LIBSOURCE/'src/libcamera/pipeline/camss-x1e-rear';pipeline.mkdir()
  for name in ['rear-manual-controls.h','camss-x1e-rear-statistics.cpp']:
   shutil.copyfile(HERE/name,pipeline/('camss-x1e-rear.cpp' if name.endswith('.cpp') else name))
  shutil.copyfile(N/'rear-v4l2/native-rear-stats.h',pipeline/'native-rear-stats.h')
  (pipeline/'meson.build').write_text("# SPDX-License-Identifier: CC0-1.0\nlibcamera_internal_sources += files('camss-x1e-rear.cpp')\n")
  once(LIBSOURCE/'meson_options.txt',"            'all',","            'camss-x1e-rear',\n            'all',")
  once(LIBSOURCE/'meson_options.txt',"choices : ['ipu3',","choices : ['camss-x1e-rear', 'ipu3',")
  once(LIBSOURCE/'meson.build','pipelines_support = {',"pipelines_support = {\n    'camss-x1e-rear': ['aarch64'],")
  shutil.copyfile(HERE/'camss_x1e_rear.mojom',LIBSOURCE/'include/libcamera/ipa/camss_x1e_rear.mojom')
  once(LIBSOURCE/'include/libcamera/ipa/meson.build','pipeline_ipa_mojom_mapping = {',"pipeline_ipa_mojom_mapping = {\n    'camss-x1e-rear': 'camss_x1e_rear.mojom',")
  ipa=LIBSOURCE/'src/ipa/camss-x1e-rear';ipa.mkdir()
  for name,dest in [('camss-x1e-rear-ipa.cpp','camss-x1e-rear.cpp'),('rear-statistics-receiver.h','rear-statistics-receiver.h'),('rear-ipa-meson.build','meson.build')]:
   shutil.copyfile(HERE/name,ipa/dest)
  shutil.copyfile(N/'rear-v4l2/native-rear-stats.h',ipa/'native-rear-stats.h')
  shutil.copyfile(HERE/'camss-x1e-rear-ipa-test.cpp',LIBSOURCE/'test/ipa/libipa/camss-x1e-rear-ipa-test.cpp')
  once(LIBSOURCE/'test/ipa/libipa/meson.build','libipa_test = [',"libipa_test = [\n {'name': 'camss-x1e-rear-ipa', 'sources': ['camss-x1e-rear-ipa-test.cpp']},")
  options=['-Dpipelines=camss-x1e-rear','-Dipas=camss-x1e-rear','-Dcam=enabled','-Dtest=true','-Ddocumentation=disabled','-Dgstreamer=disabled','-Dqcam=disabled','-Dv4l2=disabled','-Dpycamera=disabled','-Dlibunwind=disabled','-Dtracing=disabled','-Dlc-compliance=disabled','-Dwerror=true']
  run(['meson','setup',LIBBUILD,LIBSOURCE,*options],'libcamera-setup.log')
  run(['meson','compile','-C',LIBBUILD,'-j4'],'libcamera-compile.log')
  assert not re.search(r'warning:',(OUT/'libcamera-compile.log').read_text(),re.I)
  tests=['control_info','control_value','fixedpoint','histogram','interpolator','pwl','camss-x1e-rear-ipa']
  run(['meson','test','-C',LIBBUILD,'--no-rebuild','--print-errorlogs',*tests],'libcamera-tests.log')
  values=[json.loads(l) for l in (LIBBUILD/'meson-logs/testlog.json').read_text().splitlines()]
  assert len(values)==7 and all(v['result']=='OK' for v in values)
  report.update(status='PASS_REAR_STATISTICS_SOURCE_BUILD_NOT_INSTALLED',compiler_warnings=0,
   tests=[dict(name=v['name'],result=v['result']) for v in values],
   kernel_module=str(camss/'qcom-camss.ko'),libcamera_build=str(LIBBUILD),library_source=str(LIBSOURCE),
   generated_IPA_proxy_built=True,private_raw_statistics_transport=True,
   next='Fresh candidate57 kernel/profile/runtime builder and metadata/IPA fault qualification before one-shot. Then verify payload format and actual stats response before automatic exposure.')
 except Exception as exc:
  report.update(status='FAIL_REAR_STATISTICS_SOURCE_BUILD',error=str(exc));raise
 finally:(OUT/'build-result.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report),flush=True)
if __name__=='__main__':main()
