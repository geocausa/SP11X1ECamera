#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile the actual mapped-SG kernel adapter with explicit VB2/SG models."""
from pathlib import Path
import argparse,json,subprocess,tempfile,shutil
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args()
 assert not a.report.exists()
 with tempfile.TemporaryDirectory(prefix="native-rear-vb2-dma-") as name:
  d=Path(name)
  for n in ["native-rear-video-dma.h","native-rear-video-dma.inc","native-rear-nv12-layout.h"]:
   shutil.copyfile(a.staged/n,d/n)
  shutil.copyfile(HERE/"test-video-dma.c",d/"test.c")
  results=[]
  for cc in ["gcc","clang"]:
   binary=d/cc
   subprocess.run([cc,"-std=gnu11","-Wall","-Wextra","-Werror","-g","-O1","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie",str(d/"test.c"),"-o",str(binary)],check=True)
   r=subprocess.run([str(binary)],capture_output=True,text=True,check=True)
   results.append(dict(compiler=cc,ASAN_UBSAN_Werror=True,result=json.loads(r.stdout),stderr=r.stderr))
 report=dict(status="PASS_ACTUAL_REAR_VB2_MAPPED_SG_APERTURE_ADMISSION",actual_staged_adapter_and_arithmetic=True,VB2_SG_types_mapping_descriptors_and_target_predicate_are_host_models=True,hardware_access=False,buffer_ownership_or_completion_authority_granted=False,results=results)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
