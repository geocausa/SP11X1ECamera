/* SPDX-License-Identifier: GPL-2.0-only */
#include "rear-private-optical-v8.h"
#include <cassert>
#include <iostream>
#include <functional>
#include <cstdio>
using namespace RearOptical;
static int syncCalls,mapCalls,unmapCalls,fault,phase;
static int fakeSync(int,bool begin) {
 syncCalls++;
 if(begin){assert(phase==0);phase=1;return fault==1 ? -1 : 0;}
 assert(phase==1 || phase==3);phase=4;return fault==4 ? -1 : 0;
}
static void *fakeMap(int fd,size_t n) {mapCalls++;assert(phase==1);if(fault==2)return MAP_FAILED;phase=2;return mapRead(fd,n);}
static int fakeUnmap(void *p,size_t n) {unmapCalls++;assert(phase==2);phase=3;int r=unmapRead(p,n);assert(r==0);return fault==3 ? -1 : 0;}
static unsigned assertions,negatives;
#define CHECK(x) do{assert(x);assertions++;}while(0)
static void reject(std::function<void()> fn) {try{fn();}catch(const std::runtime_error &){negatives++;return;}assert(false);}
int main() {
 const std::string root="/var/lib/sp11-camera-native-rear-generation-20261007-58/private-optical/session-";
 for(unsigned s=1;s<=3;s++)CHECK(privateDirectoryAllowed(root+std::to_string(s)));
 for(const std::string &bad:std::vector<std::string>{root+"0",root+"4",root+"01",root+"1/",root+"1/../2",root+"x","/tmp/private-optical/session-1",
  "/var/lib/sp11-camera-native-rear-generation-20261007-49/private-optical/session-1",
  "/var/lib/sp11-camera-native-rear-generation-20261007-50/private-optical/session-1",
  "/var/lib/sp11-camera-native-rear-generation-20261007-51/private-optical/session-1",
  "/var/lib/sp11-camera-native-rear-generation-20261007-52/private-optical/session-1",
  "/var/lib/sp11-camera-native-rear-generation-20261007-53/private-optical/session-1",
  "/var/lib/sp11-camera-native-rear-generation-20261007-54/private-optical/session-1",
  "/var/lib/sp11-camera-native-rear-generation-20261007-55/private-optical/session-1",
  "/var/lib/sp11-camera-native-rear-generation-20261007-59/private-optical/session-1"}) {
  CHECK(!privateDirectoryAllowed(bad));negatives++;
 }
 char file[]="/tmp/sp11-optical-synthetic-XXXXXX";
 int fd=mkstemp(file);CHECK(fd>=0);unlink(file);
 std::vector<uint8_t> pattern(ImageBytes,37);pattern[YBytes]=91;pattern[YBytes+1]=165;
 writeAll(fd,pattern);
 Layout layout{fd,fd,0,YBytes,YBytes,UVBytes};
 for(int bad=0;bad<8;bad++) {
  auto p=layout;
  if(bad==0)p.yfd=-1;
  if(bad==1)p.uvfd=fd+1;
  if(bad==2)p.yoffset=1;
  if(bad==3)p.uvoffset=YBytes-1;
  if(bad==4)p.ylength=YBytes-1;
  if(bad==5)p.ylength=YBytes+1;
  if(bad==6)p.uvlength=UVBytes-1;
  if(bad==7)p.uvlength=UVBytes+1;
  reject([&]{copyCompleted(p,15,fakeSync,fakeMap,fakeUnmap);});CHECK(syncCalls==0);
 }
 for(uint32_t seq:{0U,14U,16U,78U,80U,198U,200U}) {
  reject([&]{copyCompleted(layout,seq,fakeSync,fakeMap,fakeUnmap);});CHECK(syncCalls==0);
 }
 for(int f=1;f<=4;f++) {
  fault=f;syncCalls=mapCalls=unmapCalls=phase=0;
  reject([&]{copyCompleted(layout,15,fakeSync,fakeMap,fakeUnmap);});
  CHECK(syncCalls==(f==1 ? 1 : 2));CHECK(mapCalls==(f==1 ? 0 : 1));CHECK(unmapCalls==(f>=3 ? 1 : 0));
 }
 fault=0;syncCalls=mapCalls=unmapCalls=phase=0;
 auto s=copyCompleted(layout,79,fakeSync,fakeMap,fakeUnmap);
 CHECK(s.sequence==79&&s.bytes==pattern);CHECK(syncCalls==2&&mapCalls==1&&unmapCalls==1&&phase==4);
 CHECK(ftruncate(fd,ImageBytes-1)==0);syncCalls=0;
 reject([&]{copyCompleted(layout,79,fakeSync,fakeMap,fakeUnmap);});CHECK(syncCalls==0);close(fd);
 char folder[]="/tmp/sp11-optical-private-model-XXXXXX";CHECK(mkdtemp(folder));
 int dir=open(folder,O_RDONLY|O_DIRECTORY|O_NOFOLLOW);CHECK(dir>=0);
 saveSnapshot(dir,s);
 struct stat st{};CHECK(fstatat(dir,"frame-79.nv12",&st,AT_SYMLINK_NOFOLLOW)==0);
 CHECK(S_ISREG(st.st_mode)&&st.st_uid==0&&(st.st_mode&0777)==0600&&static_cast<size_t>(st.st_size)==ImageBytes);
 reject([&]{saveSnapshot(dir,s);}); /* Never overwrite. */
 CHECK(symlinkat("frame-79.nv12",dir,"frame-15.nv12")==0);
 s.sequence=15;reject([&]{saveSnapshot(dir,s);}); /* No symlink target overwrite. */
 s.sequence=199;s.bytes.pop_back();reject([&]{saveSnapshot(dir,s);});
 s.bytes.push_back(0);s.sequence=200;reject([&]{saveSnapshot(dir,s);});
 unlinkat(dir,"frame-79.nv12",0);unlinkat(dir,"frame-15.nv12",0);close(dir);rmdir(folder);
 std::cout<<"PRIVATE_OPTICAL_MODEL_PASS assertions="<<assertions<<" negatives="<<negatives<<"\n";
}
