#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build libcamera lib19 + capture-pattern61 for the rear pattern calibration run.

Starts from the qualified lib18 staged source tree, changes only:
 * the private statistics directory root (pattern-61 run directory);
 * logs the raw IPA meter for every frame when AE is disabled.
"""
import hashlib,json,os,shutil,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2];PROJECT=ROOT.parents[1]
SRC18=PROJECT/"06-camera/reference/libcamera-native-rgb-rear-v4l2-20261009-18"
OUT=PROJECT/"06-camera/reference/libcamera-rear-pattern61-19"
BUILD=PROJECT/"02-kernel/libcamera-rear-pattern61-19"
PIPE="src/libcamera/pipeline/camss-x1e-rear/camss-x1e-rear.cpp"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(args,name):
 with (BUILD/name).open("w") as log:subprocess.run([str(x) for x in args],stdout=log,stderr=subprocess.STDOUT,check=True)
def replace(path,a,b):
 t=path.read_text();assert t.count(a)==1,a;path.write_text(t.replace(a,b,1))
def main():
 assert SRC18.is_dir()
 if OUT.exists():shutil.rmtree(OUT)
 if BUILD.exists():shutil.rmtree(BUILD)
 shutil.copytree(SRC18,OUT,symlinks=True,ignore=shutil.ignore_patterns(".git"))
 BUILD.mkdir(parents=True)
 p=OUT/PIPE
 replace(p,'"/var/lib/sp11-camera-native-rear-generation-20261007-60/private-statistics/session-"','"/var/lib/sp11-camera-rear-pattern-61/private-statistics/session-"')
 replace(p," meterDecoded_++;\n"," meterDecoded_++;\n if(!aeEnabled_)LOG(CAMSSX1ERear,Info)<<\"NATIVE_REAR_METER sequence=\"<<sequence<<\" timestamp=\"<<timestamp<<\" meter=\"<<meter;\n")
 options=["-Ddebug=false","-Dpipelines=camss-x1e-rear","-Dipas=camss-x1e-rear","-Dcam=enabled","-Dtest=true","-Ddocumentation=disabled","-Dgstreamer=disabled","-Dqcam=disabled","-Dv4l2=disabled","-Dpycamera=disabled","-Dlibunwind=disabled","-Dtracing=disabled","-Dlc-compliance=disabled","-Dwerror=true"]
 result={"status":"BUILDING","base":str(SRC18),"pipeline_sha256":sha(p)}
 try:
  run(["meson","setup",BUILD,OUT,*options],"setup.log")
  run(["meson","compile","-C",BUILD,"-j","8"],"compile.log")
  run(["meson","test","-C",BUILD,"--no-rebuild","--print-errorlogs","camss-x1e-rear-ipa"],"tests.log")
  run(["g++","-std=c++17","-Wall","-Wextra","-Werror","-O2","-pthread","-I"+str(OUT/"include"),"-I"+str(BUILD/"include"),HERE/"capture-pattern61.cpp","-L"+str(BUILD/"src/libcamera"),"-L"+str(BUILD/"src/libcamera/base"),"-lcamera","-lcamera-base","-o",BUILD/"capture-pattern"],"capture-compile.log")
  names=["src/ipa/camss-x1e-rear/ipa_camss_x1e_rear.so","src/ipa/camss-x1e-rear/ipa_camss_x1e_rear.so.sign","src/libcamera/proxy/worker/camss_x1e_rear_ipa_proxy","src/libcamera/libcamera.so.0.7.0","src/libcamera/base/libcamera-base.so.0.7.0","capture-pattern"]
  result.update(status="PASS_BUILD",outputs={n:sha(BUILD/n) for n in names})
 except Exception as exc:
  result.update(status="FAIL_BUILD",error=str(exc));raise
 finally:(BUILD/"build-result.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps(result))
if __name__=="__main__":main()
