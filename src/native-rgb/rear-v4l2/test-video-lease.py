#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Exercise the actual lease code; DMA-BUF calls/VB2 descriptors are models."""
from pathlib import Path
import argparse,json,subprocess,tempfile,shutil
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 fixture=(HERE/"test-video-dma.c").read_text().split("int main(void){",1)[0]
 fixture=fixture.replace("assertions,negatives,partitions", "assertions,negatives")
 fixture=fixture.replace("struct vb2_buffer {", "struct dma_buf;struct vb2_buffer;\nstruct vb2_mem_ops {struct dma_buf *(*get_dmabuf)(struct vb2_buffer *,void *,unsigned long);};\nextern const struct vb2_mem_ops vb2_dma_sg_memops;\nstruct vb2_queue {const struct vb2_mem_ops *mem_ops;int dma_dir;};\nstruct vb2_buffer {unsigned int memory;struct vb2_queue *vb2_queue;")
 fixture=fixture.replace("unsigned int data_offset;} planes[1]", "unsigned int data_offset;void *mem_priv;struct dma_buf *dbuf;} planes[1]")
 fixture=fixture.replace("struct camss_video {", "struct camss_video {struct vb2_queue vb2_q;")
 fixture=fixture.replace("struct camss {struct vfe_device", "struct camss {void *dev;struct vfe_device")
 with tempfile.TemporaryDirectory(prefix="native-rear-lease-") as name:
  d=Path(name)
  for n in ["native-rear-video-dma.h","native-rear-video-dma.inc","native-rear-video-lease.inc","native-rear-nv12-layout.h"]:shutil.copyfile(a.staged/n,d/n)
  (d/"test.c").write_text(fixture+(HERE/"test-video-lease.c").read_text())
  results=[]
  for cc in ["gcc","clang"]:
   binary=d/cc
   subprocess.run([cc,"-std=gnu11","-Wall","-Wextra","-Werror","-Wno-misleading-indentation","-g","-O1","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie",str(d/"test.c"),"-o",str(binary)],check=True)
   r=subprocess.run([str(binary)],capture_output=True,text=True,check=True)
   results.append(dict(compiler=cc,ASAN_UBSAN_Werror=True,result=json.loads(r.stdout),stderr=r.stderr))
 report=dict(status="PASS_ACTUAL_REAR_RETAINED_DMABUF_MAPPING_LEASE",actual_staged_lease_and_DMA_admission=True,DMA_BUF_API_and_VB2_types_are_explicit_host_models=True,hardware_access=False,results=results)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
