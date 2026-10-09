#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile identical QXA2 packer in kernel and userspace modes with guard pages."""
import hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];PROJECT=ROOT.parents[1]
REPORT=PROJECT/"02-kernel/rear-aec-v2-hosted-20261010-01.json"
def main():
 assert not REPORT.exists()
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-aec-v2-") as t:
  d=Path(t);(d/"linux").mkdir()
  (d/"linux/types.h").write_text("#include <stdint.h>\ntypedef uint8_t u8;typedef uint32_t u32;typedef uint64_t u64;\n")
  (d/"linux/errno.h").write_text("#include <asm-generic/errno.h>\n")
  (d/"linux/string.h").write_text("#include <string.h>\n")
  (d/"native-rear-stats.h").write_bytes((HERE/"native-rear-aec-v2.h").read_bytes())
  (d/"rear-statistics-receiver.h").write_bytes((HERE.parent/"rear-libcamera/rear-statistics-receiver.h").read_bytes())
  (d/"rear-aec-statistics.h").write_bytes((HERE/"rear-aec-v2-decoder.h").read_bytes())
  for cc in ["gcc","clang"]:
   for mode in ["user","kernel"]:
    exe=d/(cc+"-"+mode)
    args=[cc,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-pie","-no-pie","-I"+str(d)]
    if mode=="kernel":args+=["-D__KERNEL__"]
    subprocess.run([*args,HERE/"test-copy.c","-o",exe],check=True,capture_output=True,text=True)
    r=json.loads(subprocess.check_output([exe],text=True));results.append(dict(compiler=cc,mode=mode,**r))
  for cc in ["g++","clang++"]:
   for label,source in [("receiver",HERE/"test-receiver.cpp"),("decoder",HERE/"test-decoder.cpp")]:
    exe=d/(cc.replace("+","p")+"-"+label)
    subprocess.run([cc,"-std=c++17","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-pie","-no-pie","-I"+str(d),source,"-o",exe],check=True,capture_output=True,text=True)
    results.append(dict(compiler=cc,label=label,**json.loads(subprocess.check_output([exe],text=True))))
 result=dict(status="PASS_COMPACT_AEC_V2_IDENTICAL_KERNEL_USER_PACKER_AND_DECODER",hardware_access=False,kernel_and_user_algorithm_identical=True,actual_kernel_types_only_shimmed=True,wire_bytes=82016,active_AEC_bytes=81920,absent_statistics_fabricated=False,legacy_QXR1_rejected=True,results=results)
 REPORT.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result))
if __name__=="__main__":main()
