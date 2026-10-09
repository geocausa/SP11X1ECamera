#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fresh ordinary libcamera rear-request transport qualification build, no install."""
import hashlib,json,os,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ORIG=HERE.parent/"rear-libcamera"
ROOT=HERE.parents[2];PROJECT=ROOT.parents[1]
SOURCE=PROJECT/"06-camera/reference/libcamera-v0.7.0-native-ir"
OUT=PROJECT/"06-camera/reference/libcamera-native-rgb-rear-v4l2-20261010-21"
BUILD=PROJECT/"02-kernel/libcamera-native-rgb-rear-v4l2-20261010-21"
HEAD="8186b59b8e4bb23ce28489ac31f8e9e5babdb4d1"
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def run(args,name):
 with (BUILD/name).open("x") as log:subprocess.run([str(x) for x in args],stdout=log,stderr=subprocess.STDOUT,check=True)
def replace(path,a,b):
 t=path.read_text();assert t.count(a)==1;path.write_text(t.replace(a,b,1))
def main():
 os.umask(0o077)
 subprocess.run(["bash",ROOT/"tools/camera-overlap-guard.sh","--require-golden","--require-no-camera-process","--ignore-parent-builder","--expect-head",HEAD,"--expect-origin",HEAD],check=True)
 assert not OUT.exists() and not BUILD.exists()
 manifest=json.loads((HERE.parent/"libcamera/sources.json").read_text())
 assert subprocess.check_output(["git","-C",SOURCE,"rev-parse","HEAD"],text=True).strip()==manifest["libcamera_commit"]
 BUILD.mkdir()
 run(["git","clone","--no-local","--no-hardlinks",SOURCE,OUT],"clone.log")
 for group in ["libcamera_inputs","pipeline_inputs"]:
  for name,digest in manifest[group].items():assert sha(OUT/name)==digest,name
 p=OUT/"src/libcamera/pipeline/camss-x1e-rear";p.mkdir()
 (p/"camss-x1e-rear.cpp").write_bytes((HERE/"camss-x1e-rear-compact66.cpp").read_bytes())
 (p/"rear-manual-controls.h").write_bytes((ORIG/"rear-manual-controls.h").read_bytes())
 (p/"meson.build").write_text("# SPDX-License-Identifier: CC0-1.0\nlibcamera_internal_sources += files('camss-x1e-rear.cpp')\n")
 replace(OUT/"meson_options.txt","            'all',","            'camss-x1e-rear',\n            'all',")
 replace(OUT/"meson.build","pipelines_support = {","pipelines_support = {\n    'camss-x1e-rear': ['aarch64'],")

 (p/"rear-ae-controller.h").write_bytes((ORIG/"rear-ae-controller.h").read_bytes())
 (p/"native-rear-stats.h").write_bytes((HERE/"native-rear-aec-v2.h").read_bytes())
 replace(OUT/"meson_options.txt","choices : ['ipu3',","choices : ['camss-x1e-rear', 'ipu3',")
 (OUT/"include/libcamera/ipa/camss_x1e_rear.mojom").write_bytes((ORIG/"camss_x1e_rear-ae.mojom").read_bytes())
 replace(OUT/"include/libcamera/ipa/meson.build","pipeline_ipa_mojom_mapping = {","pipeline_ipa_mojom_mapping = {\n    'camss-x1e-rear': 'camss_x1e_rear.mojom',")
 ipa=OUT/"src/ipa/camss-x1e-rear";ipa.mkdir()
 for source,dest in [("camss-x1e-rear-ae-ipa.cpp","camss-x1e-rear.cpp"),("rear-statistics-receiver.h","rear-statistics-receiver.h"),("rear-ipa-meson.build","meson.build")]:
  (ipa/dest).write_bytes((ORIG/source).read_bytes())
 for name in ["rear-aec-statistics.h","rear-ae-controller.h"]:(ipa/name).write_bytes((HERE/"rear-aec-v2-decoder.h" if name=="rear-aec-statistics.h" else ORIG/name).read_bytes())
 (ipa/"native-rear-stats.h").write_bytes((HERE/"native-rear-aec-v2.h").read_bytes())
 (OUT/"test/ipa/libipa/camss-x1e-rear-ipa-test.cpp").write_bytes((ORIG/"camss-x1e-rear-ae-ipa-test.cpp").read_bytes())
 replace(OUT/"test/ipa/libipa/meson.build","libipa_test = [","libipa_test = [\n {'name': 'camss-x1e-rear-ipa', 'sources': ['camss-x1e-rear-ipa-test.cpp']},")
 options=["-Ddebug=false","-Dpipelines=camss-x1e-rear","-Dipas=camss-x1e-rear","-Dcam=enabled","-Dtest=true","-Ddocumentation=disabled","-Dgstreamer=disabled","-Dqcam=disabled","-Dv4l2=disabled","-Dpycamera=disabled","-Dlibunwind=disabled","-Dtracing=disabled","-Dlc-compliance=disabled","-Dwerror=true"]
 paths=["meson.build","meson_options.txt","src/libcamera/pipeline/camss-x1e-rear/camss-x1e-rear.cpp","src/libcamera/pipeline/camss-x1e-rear/meson.build","src/libcamera/pipeline/camss-x1e-rear/rear-manual-controls.h"]
 paths += ["include/libcamera/ipa/camss_x1e_rear.mojom","include/libcamera/ipa/meson.build","test/ipa/libipa/camss-x1e-rear-ipa-test.cpp","test/ipa/libipa/meson.build"]
 paths += [str(x.relative_to(OUT)) for x in ipa.iterdir() if x.is_file()]
 paths += ["src/libcamera/pipeline/camss-x1e-rear/native-rear-stats.h","src/libcamera/pipeline/camss-x1e-rear/rear-ae-controller.h"]
 result={"status":"BUILDING_REAR_PUBLIC_LIBCAMERA_TRANSPORT","libcamera_commit":manifest["libcamera_commit"],"base_camera_commit":HEAD,"staged_sources":{n:sha(OUT/n) for n in paths},"capture_source_sha256":sha(HERE/"capture-optical-v11.cpp"),"capture_ae_source_sha256":sha(HERE/"capture-ae66.cpp"),"capture_optical_header_sha256":sha(HERE/"rear-private-optical-v11.h"),"capture_timing_header_sha256":sha(ORIG/"rear-completion-cadence.h"),"capture_manual_header_sha256":sha(ORIG/"rear-manual-controls.h"),"capture_live_luma_header_sha256":sha(ORIG/"rear-live-luma.h"),"installed":False,"hardware_access":False,"continuous_capture_implemented":True,"IPA_implemented":True,"qualification_frames":400,"software_pixel_ISP":False,"optical_analyzer_sha256":sha(HERE/"analyze-private-optical-v11.py"),"private_optical_identity":66,"private_optical_frames_per_session":3,"diagnostic_pixel_bytes_read_per_session":37324800,"pipeline_transport_policy_unchanged_from06":False,"statistics_transport":True,"statistics_wire_format":"QXA2","statistics_wire_bytes":82016,"decoded_photometry":False,"automatic_exposure":False,"opt_in_AE_implemented":True,"AE_engineering_raw_target":12000,"AE_gain_ceiling":2048,"AE_quality_calibrated":False,"manual_request_controls_implemented":True,"per_frame_exposure_metadata_association_proven":False}
 report=BUILD/"build-result.json"
 try:
  run(["meson","setup",BUILD,OUT,*options],"setup.log")
  run(["meson","compile","-C",BUILD,"-j","4"],"compile.log")
  tests=["control_info","control_value","fixedpoint","histogram","interpolator","pwl","camss-x1e-rear-ipa"]
  run(["meson","test","-C",BUILD,"--no-rebuild","--print-errorlogs",*tests],"tests.log")
  values=[json.loads(l) for l in (BUILD/"meson-logs/testlog.json").read_text().splitlines()]
  assert len(values)==7 and all(t["result"]=="OK" for t in values)
  assert not any("warning:" in l.lower() for l in (BUILD/"compile.log").read_text().splitlines())
  run(["g++","-std=c++17","-Wall","-Wextra","-Werror","-O2","-pthread","-I"+str(ORIG),"-I"+str(OUT/"include"),"-I"+str(BUILD/"include"),HERE/"capture-optical-v11.cpp","-L"+str(BUILD/"src/libcamera"),"-L"+str(BUILD/"src/libcamera/base"),"-Wl,-rpath,"+str(BUILD/"src/libcamera")+":"+str(BUILD/"src/libcamera/base"),"-lcamera","-lcamera-base","-o",BUILD/"capture"],"capture-compile.log")
  run([BUILD/"capture","--help"],"capture-help.log")
  run([BUILD/"capture","--identity-check"],"capture-identity.log")
  assert json.loads((BUILD/"capture-identity.log").read_text())==dict(status="PASS_PRIVATE_OPTICAL_COMPILE_BOUND_IDENTITY",candidate_identity=66,hardware_access=False)
  run(["g++","-std=c++17","-Wall","-Wextra","-Werror","-O2","-pthread","-I"+str(ORIG),"-I"+str(OUT/"include"),"-I"+str(BUILD/"include"),HERE/"capture-ae66.cpp","-L"+str(BUILD/"src/libcamera"),"-L"+str(BUILD/"src/libcamera/base"),"-Wl,-rpath,"+str(BUILD/"src/libcamera")+":"+str(BUILD/"src/libcamera/base"),"-lcamera","-lcamera-base","-o",BUILD/"capture-ae"],"capture-ae-compile.log")
  run([BUILD/"capture-ae","--identity-check"],"capture-ae-identity.log")
  assert json.loads((BUILD/"capture-ae-identity.log").read_text())==dict(status="PASS_PRIVATE_OPTICAL_COMPILE_BOUND_IDENTITY",candidate_identity=66,hardware_access=False)
  assert all(sha(OUT/n)==h for n,h in result["staged_sources"].items())
  names=["src/ipa/camss-x1e-rear/ipa_camss_x1e_rear.so","src/ipa/camss-x1e-rear/ipa_camss_x1e_rear.so.sign","src/libcamera/proxy/worker/camss_x1e_rear_ipa_proxy","src/libcamera/libcamera.so.0.7.0","src/libcamera/base/libcamera-base.so.0.7.0","src/apps/cam/cam","capture","capture-ae"]
  result.update(status="PASS_REAR_PUBLIC_LIBCAMERA_TRANSPORT_BUILD_NOT_INSTALLED",tests=[{"name":t["name"],"result":t["result"]} for t in values],built_outputs={n:sha(BUILD/n) for n in names},compiler_warnings=0)
 except Exception as exc:
  result.update(status="FAIL_REAR_PUBLIC_LIBCAMERA_TRANSPORT_BUILD",error=str(exc));raise
 finally:report.write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({k:result[k] for k in ["status","tests","installed","hardware_access","qualification_frames"]}))
if __name__=="__main__":main()
