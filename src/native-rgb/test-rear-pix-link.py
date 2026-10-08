#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import argparse,json,os,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--report",type=Path,required=True);a=p.parse_args()
 assert not a.report.exists();results=[]
 with tempfile.TemporaryDirectory(prefix="rear-pix-link-") as tmp:
  for compiler in ["gcc","clang"]:
   binary=Path(tmp)/compiler
   subprocess.run([compiler,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined",
    "-fno-omit-frame-pointer","-I"+str(HERE),HERE/"test-rear-pix-link.c","-o",binary],check=True)
   r=subprocess.run([binary],text=True,capture_output=True,check=True,
    env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   assert not r.stderr;results.append({"compiler":compiler,"result":json.loads(r.stdout),"ASAN_UBSAN_Werror":True})
 result={"status":"PASS_EXACT_IMMUTABLE_PIX_VIDEO_LINK_WITH_STATS_FANOUT",
 "actual_helper_body":True,"media_graph_lookup_host_model":True,"hardware_access":False,"results":results}
 a.report.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result))
if __name__=="__main__":main()
