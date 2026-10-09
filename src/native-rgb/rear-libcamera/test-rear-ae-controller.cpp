/* SPDX-License-Identifier: GPL-2.0-only */
#include "rear-ae-controller.h"
#include <array>
#include <cstdlib>
#include <iostream>
#include <limits>
static unsigned checks=0,negatives=0;
#define CHECK(x) do{checks++;if(!(x)){std::cerr<<__LINE__<<": "<<#x<<"\n";std::exit(1);}}while(0)
int main(){
 using namespace RearAe;
 for(bool enabled:{false,true}){
  for(auto bad:std::array<int32_t,4>{-1,0,3,3207}){Controller c;CHECK(c.start(enabled,bad,128,12000)==-EINVAL);negatives++;}
  for(auto bad:std::array<int32_t,4>{-1,0,127,2049}){Controller c;CHECK(c.start(enabled,1600,bad,12000)==-EINVAL);negatives++;}
  for(double bad:{0.0,-1.0,1000001.0,std::numeric_limits<double>::infinity(),std::numeric_limits<double>::quiet_NaN()}){Controller c;CHECK(c.start(enabled,1600,128,bad)==-EINVAL);negatives++;}
 }
 Controller c;Proposal p{true,true,17,19},before=p;
 CHECK(c.observe(0,600,&p)==-EINVAL&&p.lines==before.lines);negatives++;
 CHECK(!c.start(true,1600,128,12000));CHECK(c.start(true,1600,128,12000)==-EINVAL);negatives++;
 CHECK(c.observe(1,600,&p)==-ESTALE);negatives++;
 CHECK(c.observe(0,-1,&p)==-EINVAL);negatives++;
 CHECK(c.observe(0,std::numeric_limits<double>::quiet_NaN(),&p)==-EINVAL);negatives++;
 CHECK(c.observe(0,600,nullptr)==-EINVAL);negatives++;
 for(unsigned n=0;n<8;n++){CHECK(!c.observe(n,600,&p)&&!p.apply);}
 CHECK(!c.observe(8,600,&p)&&p.apply&&p.lines==3200&&p.gain==128&&c.pending());
 CHECK(c.observe(8,600,&p)==-ESTALE);negatives++;
 CHECK(c.applied(9,0)==-ESTALE&&c.pending());negatives++;
 CHECK(!c.observe(9,600,&p)&&!p.apply&&c.pending());
 CHECK(!c.applied(8,0)&&c.lines()==3200&&!c.pending());
 CHECK(c.applied(8,0)==-ESTALE);negatives++;
 for(unsigned n=10;n<16;n++)CHECK(!c.observe(n,600,&p)&&!p.apply);
 CHECK(!c.observe(16,600,&p)&&p.apply&&p.lines==3206&&p.gain==256);
 CHECK(c.applied(16,-EIO)==-EIO);
 CHECK(c.observe(17,600,&p)==-EINVAL);negatives++;
 c.stop();CHECK(!c.start(false,1600,128,12000));
 for(unsigned n=0;n<400;n++)CHECK(!c.observe(n,600,&p)&&!p.apply&&c.lines()==1600&&c.gain()==128);
 unsigned convergence_tests=0;
 for(double scale:{0.003,0.01,0.05})for(unsigned delay:{0U,2U,4U}){
  Controller a;CHECK(!a.start(true,1600,128,12000));
  std::array<double,8> history{};history.fill(1600.0*128);
  double physical=history[0],meter=0;
  for(unsigned n=0;n<160;n++){
   meter=physical*scale;Proposal next;
   CHECK(!a.observe(n,meter,&next));
   if(next.apply){CHECK(next.lines>=4&&next.lines<=3206&&next.gain>=128&&next.gain<=2048);CHECK(!a.applied(n,0));}
   for(unsigned i=0;i<7;i++)history[i]=history[i+1];
   history[7]=double(a.lines())*a.gain();physical=history[7-delay];
  }
  CHECK(std::abs(meter/12000-1)<=0.101&&!a.pending());convergence_tests++;
 }
 for(double meter:{0.0,1e-200,1e100}){
  Controller a;CHECK(!a.start(true,1600,128,12000));bool limited=false;
  for(unsigned n=0;n<240;n++){Proposal next;CHECK(!a.observe(n,meter,&next));if(next.apply)CHECK(!a.applied(n,0));limited=limited||next.limited;}
  CHECK(limited);CHECK(meter>12000?(a.lines()==4&&a.gain()==128):(a.lines()==3206&&a.gain()==2048));
 }
 std::cout<<"{\"status\":\"PASS_BOUNDED_REAR_AE_ACK_SETTLING_CLAMP_AND_DELAYED_PLANT\",\"assertions\":"<<checks<<",\"negative_cases\":"<<negatives<<",\"delayed_plant_convergence_tests\":"<<convergence_tests<<"}\n";
}
