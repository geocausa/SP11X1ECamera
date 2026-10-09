#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fresh57 actual sender, receiver, timestamp, private recorder and strict receipt."""
import argparse,json,subprocess,tempfile,runpy,os,re
from pathlib import Path
HERE=Path(__file__).resolve().parent;LIB=HERE.parent/"rear-libcamera"
def fn(text,name):
 i=text.index(name+"(");a=text.index("{",i);j=a+1;depth=1
 while depth:depth+=(text[j]=="{")-(text[j]=="}");j+=1
 return text[i:j]+"\n"
def main():
 ap=argparse.ArgumentParser();ap.add_argument("--staged",type=Path,required=True);ap.add_argument("--report",type=Path,required=True);a=ap.parse_args();assert not a.report.exists()
 queue=(a.staged/"native-rear-queue.inc").read_text()
 aux=(a.staged/"native-rear-live-aux-retire.inc").read_text()
 assert aux.index("native_rear_live_replacement_read(vfe")<aux.index("native_rear_statistics_before_aux_release(vfe")<aux.index("e008d_rear_aux_release(vfe")
 actual=(LIB/"camss-x1e-rear-statistics-v2.cpp").read_text()
 root="/var/lib/sp11-camera-native-rear-generation-20261007-57/private-statistics/session-"
 assert actual.count(root)==1
 assert actual.index('if(savePrivateStatistics(sequence,p))')<actual.index('ipa_->processStatistics(buffer->cookie()')
 results=[]
 env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1")
 with tempfile.TemporaryDirectory(prefix="rear57-statistics-model-") as td:
  d=Path(td)
  for compiler,source,std in [("gcc",HERE/"test-rear-statistics-copy.c","gnu11"),("clang",HERE/"test-rear-statistics-copy.c","gnu11"),("g++",LIB/"test-rear-statistics.cpp","c++17"),("clang++",LIB/"test-rear-statistics.cpp","c++17")]:
   exe=d/(compiler.replace("+","p"))
   subprocess.run([compiler,"-std="+std,"-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie","-I"+str(a.staged),"-I"+str(LIB),source,"-o",exe],check=True,capture_output=True,text=True)
   out=subprocess.check_output([exe],text=True,env=env);results.append(dict(compiler=compiler,actual_source=source.name,**json.loads(out)))
  timestamp=r"""
#include <assert.h>
#include <stdint.h>
#include <stddef.h>
#include <stdbool.h>
#include <stdio.h>
#define __KERNEL__ 1
#define NATIVE_REAR_NV12_BYTES 12441600U
#define VB2_BUF_STATE_DONE 1
#define VB2_BUF_STATE_ERROR 2
struct vb2_buffer{uint64_t timestamp;unsigned int payload;};
struct camss_buffer{struct {struct vb2_buffer vb2_buf;unsigned int sequence;}vb;};
struct camss_video{struct camss_buffer *native_rear_inflight[2];unsigned int native_rear_completed,native_rear_live_completed;uint64_t native_rear_statistics_tick;};
static struct camss_video *active;
static unsigned callbacks,gaps;
static void vb2_set_plane_payload(struct vb2_buffer *b,unsigned p,unsigned n){assert(p==0);b->payload=n;}
static void native_rear_gap_complete(uint64_t t,unsigned sequence){assert(t==987654321ULL&&sequence==0);gaps++;}
static void vb2_buffer_done(struct vb2_buffer *b,int state){
 assert(active->native_rear_inflight[0]==NULL);
 if(state==VB2_BUF_STATE_DONE){assert(b->timestamp==987654321ULL&&b->payload==NATIVE_REAR_NV12_BYTES);assert(active->native_rear_statistics_tick==0);}
 else assert(state==VB2_BUF_STATE_ERROR);
 callbacks++;
}
/* ACTUAL */
int main(void){
 struct camss_video v={0};struct camss_buffer b={0};active=&v;
 v.native_rear_statistics_tick=987654321ULL;v.native_rear_inflight[0]=&b;
 native_rear_queue_complete(&v,0,true,true);
 assert(callbacks==1&&gaps==1&&v.native_rear_completed==1&&v.native_rear_live_completed==1&&b.vb.sequence==0);
 native_rear_queue_complete(&v,0,true,true);assert(callbacks==1);
 v.native_rear_inflight[0]=&b;native_rear_queue_complete(&v,0,false,false);
 assert(callbacks==2&&gaps==1&&v.native_rear_completed==1);
 puts("PASS_ACTUAL_KERNEL_TIMESTAMP_BEFORE_CALLBACK_AND_NO_UNPAIRED_SUCCESS");
}
"""
  src=d/"timestamp.c";src.write_text(timestamp.replace("/* ACTUAL */","static void "+fn(queue,"native_rear_queue_complete")))
  for compiler in ["gcc","clang"]:
   exe=d/(compiler+"-timestamp")
   subprocess.run([compiler,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-pie","-no-pie",src,"-o",exe],check=True,capture_output=True,text=True)
   assert subprocess.check_output([exe],text=True,env=env).startswith("PASS_ACTUAL_KERNEL_TIMESTAMP")
  # Only synthetic opaque bytes; substitute a disposable fixture root.
  recorder=r"""
#include <cassert>
#include <cerrno>
#include <cstdint>
#include <cstdlib>
#include <fcntl.h>
#include <string>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>
#include <fstream>
#include <iostream>
#include "native-rear-stats.h"
class RearData{public:int privateDirectory_=-1;uint32_t privateSaved_=0;
int openPrivateStatistics();int savePrivateStatistics(uint32_t,const uint8_t *);};
/* ACTUAL */
int main(int argc,char **argv){
 assert(argc==2);std::string root=argv[1];std::string directory=root+"1";
 RearData r;unsetenv("SP11_REAR_STATISTICS_DIR");assert(r.openPrivateStatistics()==-EINVAL);
 setenv("SP11_REAR_STATISTICS_DIR",(root+"4").c_str(),1);assert(r.openPrivateStatistics()==-EPERM);
 setenv("SP11_REAR_STATISTICS_DIR",directory.c_str(),1);assert(r.openPrivateStatistics()==-ENOENT);
 assert(!mkdir(directory.c_str(),0755));assert(r.openPrivateStatistics()==-EPERM);
 assert(!chmod(directory.c_str(),0700));assert(!r.openPrivateStatistics());assert(r.openPrivateStatistics()==-EBUSY);
 std::vector<uint8_t> data(NATIVE_REAR_STATS_BYTES,0x5a);
 assert(!r.savePrivateStatistics(0,data.data())&&r.privateSaved_==0);
 for(unsigned begin:{56U,120U,184U,248U})for(unsigned offset:{0U,7U,10U,11U,12U,23U})if(unsigned seq=begin+offset;true)assert(!r.savePrivateStatistics(seq,data.data()));
 assert(r.privateSaved_==24);assert(r.savePrivateStatistics(56,data.data())==-EINVAL);
 close(r.privateDirectory_);r.privateDirectory_=-1;
 for(unsigned begin:{56U,120U,184U,248U})for(unsigned offset:{0U,7U,10U,11U,12U,23U})if(unsigned seq=begin+offset;true){
  std::string path=directory+"/statistics-"+std::to_string(seq)+".qxr1";
  struct stat st{};assert(!lstat(path.c_str(),&st)&&S_ISREG(st.st_mode)&&(st.st_mode&0777)==0600&&st.st_size==NATIVE_REAR_STATS_BYTES);
  std::ifstream f(path,std::ios::binary);std::vector<uint8_t> read((std::istreambuf_iterator<char>(f)),{});assert(read==data);
 }
 std::cout<<"PASS_ACTUAL_PRIVATE_RECORDER_24_SYNTHETIC_PACKETS_MODE_LENGTH_CONTENT_AND_PATH_REJECTION\n";
}
"""
  methods="int "+fn(actual,"RearData::openPrivateStatistics")+"int "+fn(actual,"RearData::savePrivateStatistics")
  fixture=str(d/"session-")
  methods=methods.replace(root,fixture)
  src=d/"recorder.cpp";src.write_text(recorder.replace("/* ACTUAL */",methods))
  for compiler in ["g++","clang++"]:
   exe=d/(compiler.replace("+","p")+"-recorder");fixture_dir=d/(compiler.replace("+","p")+"-fixture");fixture_dir.mkdir(mode=0o700)
   # Each compiler has independent fixture path; source remains the actual helper.
   src.write_text(recorder.replace("/* ACTUAL */",methods.replace(fixture,str(fixture_dir/"session-"))))
   subprocess.run([compiler,"-std=c++17","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-pie","-no-pie","-I"+str(a.staged),src,"-o",exe],check=True,capture_output=True,text=True)
   assert subprocess.check_output([exe,str(fixture_dir/"session-")],text=True,env=env).startswith("PASS_ACTUAL_PRIVATE_RECORDER")
 validate=runpy.run_path(str(HERE/"run-rear-cadence-v17.py"))["validate_statistics_join"]
 good=dict(received=400,joined=400,stream=12345,owner=1,failed=0,private_saved=24,decoded_photometry=0,automatic_exposure=0)
 def log(row):return "NATIVE_REAR_STATISTICS_JOIN "+" ".join(str(k)+"="+str(v) for k,v in row.items())
 assert validate(log(good),1)["status"].startswith("PASS")
 negatives=0
 def reject(value):
  nonlocal negatives
  try:validate(value,1)
  except (RuntimeError,ValueError):negatives+=1
  else:raise AssertionError("stale/malformed statistics receipt admitted")
 for k in good:
  bad=dict(good);bad.pop(k);reject(log(bad));reject(log(good)+" "+k+"="+str(good[k]))
 for k,values in {"received":[399,417],"joined":[0,399,401],"stream":[0,2**64],"owner":[0,2],"failed":[1],"private_saved":[0,23,25],"decoded_photometry":[1],"automatic_exposure":[1]}.items():
  for v in values:bad=dict(good);bad[k]=v;reject(log(bad))
 reject("");reject(log(good)+"\n"+log(good));reject(log(good)+" extra=0");reject(log(good).replace("stream=12345","stream=-1"))
 report=dict(status="PASS_REAR57_STATISTICS_INTEGRATION",hosted=results,statistics_receipt_negative_cases=negatives,
  actual_kernel_completion_timestamp_branch_executed=True,actual_private_recorder_synthetic_vectors=True,
  declared_hook_after_original_replacement_proof_before_aux_free=True,original_transport_models_retained=True,
  actual_generated_IPA_test_required_separately=True,hardware_access=False,decoded_photometry=False,automatic_exposure=False)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":
 try:main()
 except subprocess.CalledProcessError as e:print(e.stdout or "",e.stderr or "");raise
