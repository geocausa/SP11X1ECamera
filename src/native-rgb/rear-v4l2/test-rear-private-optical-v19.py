#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual private snapshot helpers, DMA fault models, source flow and decoder vectors."""
from pathlib import Path
import argparse,json,re,runpy,subprocess,tempfile,os
import numpy as np
UNDO_STATS=runpy.run_path(str(Path(__file__).resolve().parent/"rear-statistics-source-proof.py"))["undo_queue_timestamp"]
HERE=Path(__file__).resolve().parent;LIB=HERE.parent/"rear-libcamera"
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 s=(LIB/"capture-optical-v9.cpp").read_text();base=(LIB/"capture-soak.cpp").read_text()

 for added in ['#include "rear-manual-controls.h"\n','#include "rear-live-luma.h"\n']:
  assert s.count(added)==1;s=s.replace(added,"",1)
 start=s.index('  const char *folder=getenv(');end=s.index(' running_ = true;',start)+len(' running_ = true;')
 s=s[:start]+'  need(!camera_->start(), "start"); running_ = true;'+s[end:]
 start=s.index('   if (RearManual::sampleSequence(');end=s.index('\n  } catch',start)
 s=s[:start]+s[end:]
 for line in list(s.splitlines(True)):
  if line.startswith('   if (completed_==') and 'request->controls().set' in line:s=s.replace(line,"",1)
 start=s.index(' struct Sample {');end=s.index(' std::string colorSpace_;',start);s=s[:start]+s[end:]
 start=s.index('  need(samples_.size()==96');end=s.index('  std::cout << "\\\"status',start)
 s=s[:start]+s[end:]
 s=s.replace('  std::cout << "\\\"status','  std::cout << "{\\\"status',1)
 s=re.sub(r" /\* OPTICAL_IDENTITY_PREFLIGHT_BEGIN \*/\n.*? /\* OPTICAL_IDENTITY_PREFLIGHT_END \*/\n","",s,flags=re.S)
 s=s.replace('#include "rear-private-optical-v9.h"','#include "rear-private-optical.h"')
 clean=s.replace('/* Real public libcamera Requests with3 finite SAME-SP11 private snapshots. */','/* Real public libcamera requests; no pixel mapping, reading or file output. */')
 for added in ['#include "rear-private-optical.h"\n','  colorSpace_ = cfg.colorSpace ? cfg.colorSpace->toString() : "unspecified";\n','  privateFrames_.saveAfterRelease();\n',' RearOptical::PrivateFrames privateFrames_;\n',' std::string colorSpace_;\n']:
  assert clean.count(added)==1,added;clean=clean.replace(added,"",1)
 start=clean.index('  try {\n   const auto &planes=buffer->planes();')
 end=clean.index('  const auto now =',start);clean=clean[:start]+clean[end:]
 added='            << ",\\\"color_space\\\":\\\"" << colorSpace_ << "\\\""\n'
 assert clean.count(added)==1;clean=clean.replace(added,"",1)
 clean=clean.replace('\\\"pixel_bytes_read\\\":37324800,\\\"private_nv12_frames_saved\\\":3,\\\"optical_diagnostic_copy\\\":true,','\\\"pixel_bytes_read\\\":0,')
 clean=clean.replace('SP11 private optical snapshots; pixels remain SAME SP11; normal Request reuse','SP11 real public-libcamera rear continuous reused-request qualification; no pixels read')
 clean=clean.replace("std::chrono::seconds(35)","std::chrono::seconds(20)") # Sole declared deadline extension.
 assert clean==base,"optical additions changed existing Request/metadata/stop flow"
 assert s.index('buffer->metadata().planes()[1].bytesused')<s.index('privateFrames_.capture(')<s.index('request->reuse(Request::ReuseBuffers)')
 assert s.index('camera_->release()')<s.index('privateFrames_.saveAfterRelease()')
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-optical-source-") as tmp:
  d=Path(tmp)
  for cc in ["g++","clang++"]:
   exe=d/cc
   subprocess.run([cc,"-std=c++17","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie","-I"+str(LIB),str(LIB/"test-private-optical-model-v9.cpp"),"-o",str(exe)],check=True,capture_output=True,text=True)
   out=subprocess.check_output(["sudo","-n","env","ASAN_OPTIONS=detect_leaks=1:halt_on_error=1","UBSAN_OPTIONS=halt_on_error=1",str(exe)],text=True)
   m=re.search(r"PRIVATE_OPTICAL_MODEL_PASS assertions=(\d+) negatives=(\d+)",out);assert m,out
   results.append(dict(compiler=cc,ASAN_UBSAN_Werror=True,assertions=int(m[1]),negative_cases=int(m[2])))
 analyzer=runpy.run_path(str(LIB/"analyze-private-optical-v9.py"));decode=analyzer["decode"]
 assert str(analyzer["ROOT"])=="/var/lib/sp11-camera-native-rear-generation-20261007-59/private-optical"
 cases=0
 for matrix in ["bt601-limited","bt709-limited","bt709-full"]:
  for y,expected in [(16,0),(235,255)] if matrix.endswith("limited") else [(0,0),(255,255)]:
   rgb=decode(np.full((2,2),y,np.uint8),np.full((1,1),128,np.uint8),np.full((1,1),128,np.uint8),matrix)
   assert np.all(rgb==expected);cases+=1
  y=np.full((2,2),128,np.uint8);u=np.full((1,1),128,np.uint8);v=np.full((1,1),200,np.uint8)
  rgb=decode(y,u,v,matrix);assert np.all(rgb[:,:,0]>rgb[:,:,1]);cases+=1
 # Run the actual analyzer on tiny synthetic NV12 files, with real sealed
 # files/PNG writes. No camera or user pixel data exists in this test.
 code="""import importlib.util,tempfile,os,json
from pathlib import Path
s=importlib.util.spec_from_file_location('a',PATH);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
m.W=4;m.H=2;m.YBYTES=8;m.TOTAL=12
with tempfile.TemporaryDirectory(prefix='sp11-optical-analyzer-model-') as temp:
 d=Path(temp);d.chmod(0o700)
 for seq in [15,79,199]:
  p=d/('frame-'+str(seq)+'.nv12');p.write_bytes(bytes([16]*8+[128]*4));p.chmod(0o600)
 r=m.analyze(d);assert r['native_frames']==3 and r['private_previews_saved']==9 and r['degenerate_frame_count']==3
 assert 'constant_luma' in r['frames'][0]['diagnostic_flags']
 assert 'identical_to_previous_selected_frame' in r['frames'][1]['diagnostic_flags']
 assert r['frames'][0]['preview_interpretations']['bt709-limited']['all_channels_black_fraction']==1
 assert len(list(d.glob('*.png')))==9
 for p in d.glob('*.png'):assert p.stat().st_mode&0o777==0o600
 p=d/'frame-15.nv12';p.chmod(0o644)
 try:m.analyze(d,False)
 except RuntimeError:pass
 else:raise AssertionError('unsealed optical file admitted')
 p.chmod(0o600);p.write_bytes(b'x')
 try:m.analyze(d,False)
 except RuntimeError:pass
 else:raise AssertionError('short NV12 admitted')
print('PRIVATE_ANALYZER_SYNTHETIC_SEALED_DECODER_FLAG_PASS')
""".replace("PATH",repr(str(LIB/"analyze-private-optical-v9.py")))
 assert "PRIVATE_ANALYZER_SYNTHETIC_SEALED_DECODER_FLAG_PASS" in subprocess.check_output(["sudo","-n","python3","-c",code],text=True)
 # Actual strict parser rejects stale no-pixel success and incorrect read counts.
 runtime=runpy.run_path(str(HERE/"run-rear-cadence-v19.py"));validate=runtime["validate_optical_probe"]
 good=dict(pixel_bytes_read=37324800,private_nv12_frames_saved=3,optical_diagnostic_copy=True,color_space="unspecified")
 assert validate(good);neg=0
 for key,values in {"pixel_bytes_read":[0,12441600,37324799,37324801,True],"private_nv12_frames_saved":[0,2,4],"optical_diagnostic_copy":[False,None],"color_space":["Rec709",None]}.items():
  for v in values:
   bad=dict(good);bad[key]=v
   try:validate(bad)
   except RuntimeError:neg+=1
   else:raise AssertionError("optical proof scope drift admitted")
 main=(HERE/"run-rear-cadence-v19.py").read_text().split("def main():",1)[1]
 assert 'validate_optical_probe(result["probe"])' in main and 'result["optical_pixels_read_or_saved"]=True' in main
 assert main.index('validate_idle_clocks(result.get("camera_clock_snapshots"')<main.index('analysis=subprocess.run')
 # Kernel transport/ISP allocation policy is byte-identical to48 except identity.
 basecam=a.staged.parent.parent/"native-rgb-rear-generation-20261007-61/camss"
 for name in ["native-rear-queue.inc","native-rear-startup-spare.inc","native-rear-full-cache.inc","native-rear-live-retire.inc","native-rear-reclaim.inc"]:
  declared=(a.staged/name).read_text()
  if name=="native-rear-queue.inc":declared=UNDO_STATS(declared)
  assert declared==(basecam/name).read_text(),("optical changed kernel transport",name)
 report=dict(status="PASS_ACTUAL_PRIVATE_OPTICAL_SYNC_LAYOUT_SAVE_DECODER_AND_SOURCE_FLOW",results=results,
  decoder_known_vector_cases=cases,optical_probe_parser_negative_cases=neg,
  original_Request_metadata_reuse_and_stop_flow_preserved=True,original_kernel_policy_preserved_after_declared_statistics_timestamp=True,
  snapshot_after_original_completion_metadata_admission=True,private_disk_write_after_camera_release=True,
  model_pixels_are_synthetic=True,hardware_DMA_API_is_model=True,physical_hardware_access=False,
  image_bytes_exported=False,preview_matrix_unverified=True)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":
 try:main()
 except subprocess.CalledProcessError as e:print(e.stdout or "",e.stderr or "");raise
