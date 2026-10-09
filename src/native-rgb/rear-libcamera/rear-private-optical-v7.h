/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef SP11_REAR_PRIVATE_OPTICAL_H
#define SP11_REAR_PRIVATE_OPTICAL_H
#include <array>
#include <cerrno>
#include <cstdlib>
#include <cstring>
#include <cstdint>
#include <fcntl.h>
#include <linux/dma-buf.h>
#include <stdexcept>
#include <string>
#include <sys/ioctl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <vector>
namespace RearOptical {
constexpr size_t YBytes=8294400, UVBytes=4147200, ImageBytes=12441600;
inline void require(bool ok,const char *reason) {if(!ok)throw std::runtime_error(reason);}
struct Layout {int yfd,uvfd;size_t yoffset,uvoffset,ylength,uvlength;};
inline void validate(const Layout &p) {
 require(p.yfd>=0 && p.yfd==p.uvfd && p.yoffset==0 && p.uvoffset==YBytes &&
         p.ylength==YBytes && p.uvlength==UVBytes,"optical exact contiguous NV12 plane layout");
}
struct Snapshot {uint32_t sequence;std::vector<uint8_t> bytes;};
inline int syncRead(int fd,bool begin) {
 dma_buf_sync sync{};sync.flags=DMA_BUF_SYNC_READ | (begin ? DMA_BUF_SYNC_START : DMA_BUF_SYNC_END);
 int ret;do {ret=ioctl(fd,DMA_BUF_IOCTL_SYNC,&sync);}while(ret<0 && errno==EINTR);
 return ret;
}
inline void *mapRead(int fd,size_t bytes) {return mmap(nullptr,bytes,PROT_READ,MAP_SHARED,fd,0);}
inline int unmapRead(void *ptr,size_t bytes) {return munmap(ptr,bytes);}
inline Snapshot copyCompleted(const Layout &layout,uint32_t sequence,
 int (*sync)(int,bool)=syncRead,void *(*map)(int,size_t)=mapRead,
 int (*unmap)(void *,size_t)=unmapRead) {
 validate(layout);
 require(sequence==15 || sequence==79 || sequence==199,"optical selected completed sequence");
 off_t size=lseek(layout.yfd,0,SEEK_END);
 require(size>=static_cast<off_t>(ImageBytes),"optical DMA extent");
 Snapshot out{sequence,std::vector<uint8_t>(ImageBytes)}; /* Allocate before CPU START. */
 require(sync(layout.yfd,true)==0,"optical DMA CPU START READ");
 void *ptr=map(layout.yfd,ImageBytes);
 if(ptr==MAP_FAILED) {
  (void)sync(layout.yfd,false);
  throw std::runtime_error("optical readonly DMA mapping");
 }
 std::memcpy(out.bytes.data(),ptr,ImageBytes);
 int unmapped=unmap(ptr,ImageBytes);
 int ended=sync(layout.yfd,false); /* Always END even if unmap fails. */
 require(unmapped==0 && ended==0,"optical DMA CPU END READ or unmap");
 return out;
}
inline void writeAll(int fd,const std::vector<uint8_t> &bytes) {
 size_t cursor=0;
 while(cursor<bytes.size()) {
  ssize_t n=write(fd,bytes.data()+cursor,bytes.size()-cursor);
  if(n<0 && errno==EINTR)continue;
  require(n>0,"optical private write");cursor+=static_cast<size_t>(n);
 }
 require(fsync(fd)==0,"optical private fsync");
}
inline void saveSnapshot(int dirfd,const Snapshot &s) {
 require(s.bytes.size()==ImageBytes && (s.sequence==15 || s.sequence==79 || s.sequence==199),"optical snapshot size and sequence");
 const std::string name="frame-"+std::to_string(s.sequence)+".nv12";
 int fd=openat(dirfd,name.c_str(),O_WRONLY|O_CREAT|O_EXCL|O_NOFOLLOW|O_CLOEXEC,0600);
 require(fd>=0,"optical private create without overwrite");
 try {
  struct stat stat{};
  require(fstat(fd,&stat)==0 && S_ISREG(stat.st_mode) && stat.st_uid==0 &&
          (stat.st_mode&0777)==0600,"optical sealed0600 frame");
  writeAll(fd,s.bytes);
  int ret=close(fd);fd=-1;require(ret==0,"optical private close");
 } catch(...) {if(fd>=0)close(fd);throw;}
}
inline bool privateDirectoryAllowed(const std::string &path) {
 const std::string root="/var/lib/sp11-camera-native-rear-generation-20261007-57/private-optical/session-";
 return path==root+"1" || path==root+"2" || path==root+"3";
}
class PrivateFrames {
public:
 PrivateFrames() {
  const char *value=getenv("SP11_REAR_OPTICAL_DIR");
  require(geteuid()==0 && value,"optical root private directory required");
  std::string path(value);
  require(privateDirectoryAllowed(path),"optical exact fresh directory");
  dir_=open(path.c_str(),O_RDONLY|O_DIRECTORY|O_NOFOLLOW|O_CLOEXEC);
  struct stat stat{};
  if (!(dir_>=0 && fstat(dir_,&stat)==0 && S_ISDIR(stat.st_mode) &&
        stat.st_uid==0 && (stat.st_mode&0777)==0700)) {
   if(dir_>=0)close(dir_);
   dir_=-1;
   throw std::runtime_error("optical sealed0700 directory");
  }
  snapshots_.reserve(3);
 }
 ~PrivateFrames() {if(dir_>=0)close(dir_);}
 PrivateFrames(const PrivateFrames &)=delete;
 PrivateFrames &operator=(const PrivateFrames &)=delete;
 void capture(const Layout &layout,uint32_t sequence) {
  if(sequence!=15 && sequence!=79 && sequence!=199)return;
  require(snapshots_.size()<3,"optical finite snapshot count");
  const uint32_t expected=std::array<uint32_t,3>{15,79,199}[snapshots_.size()];
  require(sequence==expected,"optical ordered selected snapshots");
  snapshots_.push_back(copyCompleted(layout,sequence));
 }
 void saveAfterRelease() {
  require(snapshots_.size()==3,"optical three completed snapshots required");
  for(const auto &s:snapshots_)saveSnapshot(dir_,s);
  require(fsync(dir_)==0,"optical private directory fsync");
 }
private:
 int dir_=-1;
 std::vector<Snapshot> snapshots_;
};
}
#endif
