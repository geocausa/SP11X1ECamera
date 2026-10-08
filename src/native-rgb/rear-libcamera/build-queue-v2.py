#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fresh ordinary libcamera rear-request transport qualification build, no install."""
import hashlib,json,os,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2];PROJECT=ROOT.parents[1]
SOURCE=PROJECT/"06-camera/reference/libcamera-v0.7.0-native-ir"
OUT=PROJECT/"06-camera/reference/libcamera-native-rgb-rear-v4l2-20261008-04"
BUILD=PROJECT/"02-kernel/libcamera-native-rgb-rear-v4l2-20261008-04"
HEAD="e6864b797946723fc293dbcf7079511d03a9f740"
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
 (p/"camss-x1e-rear.cpp").write_bytes((HERE/"camss-x1e-rear-queue.cpp").read_bytes())
 (p/"meson.build").write_text("# SPDX-License-Identifier: CC0-1.0\nlibcamera_internal_sources += files('camss-x1e-rear.cpp')\n")
 replace(OUT/"meson_options.txt","            'all',","            'camss-x1e-rear',\n            'all',")
 replace(OUT/"meson.build","pipelines_support = {","pipelines_support = {\n    'camss-x1e-rear': ['aarch64'],")
 options=["-Dpipelines=camss-x1e-rear","-Dipas=[]","-Dcam=enabled","-Dtest=true","-Ddocumentation=disabled","-Dgstreamer=disabled","-Dqcam=disabled","-Dv4l2=disabled","-Dpycamera=disabled","-Dlibunwind=disabled","-Dtracing=disabled","-Dlc-compliance=disabled","-Dwerror=true"]
 paths=["meson.build","meson_options.txt","src/libcamera/pipeline/camss-x1e-rear/camss-x1e-rear.cpp","src/libcamera/pipeline/camss-x1e-rear/meson.build"]
 result={"status":"BUILDING_REAR_PUBLIC_LIBCAMERA_TRANSPORT","libcamera_commit":manifest["libcamera_commit"],"base_camera_commit":HEAD,"staged_sources":{n:sha(OUT/n) for n in paths},"capture_source_sha256":sha(HERE/"capture-queue.cpp"),"installed":False,"hardware_access":False,"continuous_capture_implemented":True,"IPA_implemented":False,"qualification_frames":80,"software_pixel_ISP":False}
 report=BUILD/"build-result.json"
 try:
  run(["meson","setup",BUILD,OUT,*options],"setup.log")
  run(["meson","compile","-C",BUILD,"-j","4"],"compile.log")
  tests=["control_info","control_value","fixedpoint","histogram","interpolator","pwl"]
  run(["meson","test","-C",BUILD,"--no-rebuild","--print-errorlogs",*tests],"tests.log")
  values=[json.loads(l) for l in (BUILD/"meson-logs/testlog.json").read_text().splitlines()]
  assert len(values)==6 and all(t["result"]=="OK" for t in values)
  assert not any("warning:" in l.lower() for l in (BUILD/"compile.log").read_text().splitlines())
  run(["g++","-std=c++17","-Wall","-Wextra","-Werror","-O2","-pthread","-I"+str(OUT/"include"),"-I"+str(BUILD/"include"),HERE/"capture-queue.cpp","-L"+str(BUILD/"src/libcamera"),"-L"+str(BUILD/"src/libcamera/base"),"-Wl,-rpath,"+str(BUILD/"src/libcamera")+":"+str(BUILD/"src/libcamera/base"),"-lcamera","-lcamera-base","-o",BUILD/"capture"],"capture-compile.log")
  run([BUILD/"capture","--help"],"capture-help.log")
  assert all(sha(OUT/n)==h for n,h in result["staged_sources"].items())
  names=["src/libcamera/libcamera.so.0.7.0","src/libcamera/base/libcamera-base.so.0.7.0","src/apps/cam/cam","capture"]
  result.update(status="PASS_REAR_PUBLIC_LIBCAMERA_TRANSPORT_BUILD_NOT_INSTALLED",tests=[{"name":t["name"],"result":t["result"]} for t in values],built_outputs={n:sha(BUILD/n) for n in names},compiler_warnings=0)
 except Exception as exc:
  result.update(status="FAIL_REAR_PUBLIC_LIBCAMERA_TRANSPORT_BUILD",error=str(exc));raise
 finally:report.write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({k:result[k] for k in ["status","tests","installed","hardware_access","qualification_frames"]}))
if __name__=="__main__":main()
