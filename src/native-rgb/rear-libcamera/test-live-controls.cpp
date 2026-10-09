/* SPDX-License-Identifier: GPL-2.0-only */
#include <cstdio>
#include <limits>
#include <vector>
#include <stdexcept>
#include "rear-manual-controls.h"
#include "rear-live-luma.h"
static unsigned assertions=0,negatives=0;
static void check(bool ok){if(!ok)throw std::runtime_error("model assertion");assertions++;}
static int starts=0,ends=0,maps=0,unmaps=0,mode=0;
static std::vector<uint8_t> y(RearOptical::YBytes,73);
static int syncMock(int,bool begin){if(begin){starts++;return mode==1?-1:0;}ends++;return mode==4?-1:0;}
static void *mapMock(int,size_t n){check(n==RearOptical::YBytes);maps++;return mode==2?MAP_FAILED:y.data();}
static int unmapMock(void *p,size_t n){check(p==y.data() && n==RearOptical::YBytes);unmaps++;return mode==3?-1:0;}
template<typename F> static void reject(F f){try{f();}catch(const std::runtime_error&){negatives++;return;}throw std::runtime_error("bad model admitted");}
int main(){
 int32_t out=0;
 for(int32_t n=4;n<=3206;n++){check(RearManual::exposureLines(RearManual::exposureUs(n),&out) && out==n);}
 for(int32_t code=128;code<=1024;code++){check(RearManual::gainCode(float(code)/128,&out) && out==code);}
 for(int32_t value:{-1,0,RearManual::exposureUs(4)-1,RearManual::exposureUs(3206)+1,2147483647}){check(!RearManual::exposureLines(value,&out));negatives++;}
 for(float value:{0.0f,-1.0f,0.999f,8.001f,std::numeric_limits<float>::infinity(),std::numeric_limits<float>::quiet_NaN()}){check(!RearManual::gainCode(value,&out));negatives++;}
 check(!RearManual::gainCode(1,nullptr));check(!RearManual::exposureLines(100,nullptr));negatives+=2;
 unsigned count=0;for(unsigned n=0;n<400;n++)count+=RearManual::sampleSequence(n);check(count==96);
 char name[]="/tmp/sp11-synthetic-luma-XXXXXX";int fd=mkstemp(name);check(fd>=0);unlink(name);check(ftruncate(fd,RearOptical::ImageBytes)==0);
 RearOptical::Layout p{fd,fd,0,RearOptical::YBytes,RearOptical::YBytes,RearOptical::UVBytes};
 check(RearLiveLuma::mean(p,syncMock,mapMock,unmapMock)==73);check(starts==1 && ends==1 && maps==1 && unmaps==1);
 for(int failure=1;failure<=4;failure++){mode=failure;starts=ends=maps=unmaps=0;reject([&]{RearLiveLuma::mean(p,syncMock,mapMock,unmapMock);});check(starts==1 && ends==(failure==1?0:1) && unmaps==(failure==1||failure==2?0:1));}
 mode=0;auto bad=p;bad.uvoffset++;reject([&]{RearLiveLuma::mean(bad,syncMock,mapMock,unmapMock);});
 check(ftruncate(fd,RearOptical::ImageBytes-1)==0);reject([&]{RearLiveLuma::mean(p,syncMock,mapMock,unmapMock);});close(fd);
 std::printf("LIVE_CONTROLS_MODEL_PASS assertions=%u negatives=%u\n",assertions,negatives);
}
