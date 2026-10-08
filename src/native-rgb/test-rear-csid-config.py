#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual rear transport helper/predicate, simulated MMIO and lookup provider."""
import argparse,json,os,re,subprocess,tempfile
from pathlib import Path
PRELUDE=r"""
#include <stdbool.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <linux/v4l2-mediabus.h>
typedef uint32_t u32;typedef uint8_t u8;typedef uint16_t u16;
#define BIT(n) (1U<<(n))
#define __used __attribute__((unused))
#define CAMSS_X1E80100 100
#define CSID_PHY_SEL_DPHY 0
#define MSM_CSID_PAD_PIX 4
static unsigned assertions,nwrites;
#define CHECK(x) do{assertions++;if(!(x))abort();}while(0)
static u32 memory[512],offsets[32],values[32];
struct csid_format_info {u32 code,decode_format,data_type;};
struct formats {struct csid_format_info *formats;unsigned nformats;};
struct resource {struct formats *formats;};
struct board {int version;};
struct camss {struct board *res;u8 *csid_wrapper_base;};
struct csid_device {
 struct camss *camss;struct resource *res;int id;u8 *base;
 struct {u32 csiphy_id,phy_sel,lane_cnt,lane_assign,en_ipp,en_vc;}phy;
 struct v4l2_mbus_framefmt fmt[5];
};
static bool no_format;
static const struct csid_format_info *csid_get_fmt_entry(
 const struct csid_format_info *f,unsigned n,u32 code){
 return !no_format&&n==1&&f->code==code?f:NULL;
}
static u32 readl(void *p) {return *(u32*)p;}
static void writel(u32 value,void *p){
 uintptr_t offset=(uintptr_t)p-(uintptr_t)memory;
 CHECK(offset<sizeof(memory)&&offset%4==0&&nwrites<32);
 offsets[nwrites]=offset;values[nwrites++]=value;*(u32*)p=value;
}
"""
MAIN=r"""
static struct board board;
static struct camss camss;
static struct resource resource;
static struct formats formats;
static struct csid_format_info format;
static struct csid_device csid;
static void init(void){
 memset(&csid,0,sizeof(csid));memset(memory,0x55,sizeof(memory));nwrites=0;no_format=false;
 board.version=CAMSS_X1E80100;camss.res=&board;camss.csid_wrapper_base=(u8*)memory;
 format=(struct csid_format_info){MEDIA_BUS_FMT_SGRBG10_1X10,2,0x2b};
 formats=(struct formats){&format,1};resource.formats=&formats;
 csid.camss=&camss;csid.res=&resource;csid.base=(u8*)memory;csid.id=1;
 csid.phy.csiphy_id=1;csid.phy.phy_sel=CSID_PHY_SEL_DPHY;csid.phy.lane_cnt=4;
 csid.phy.lane_assign=0x3210;csid.phy.en_ipp=1;csid.fmt[4].code=MEDIA_BUS_FMT_SGRBG10_1X10;
 csid.fmt[4].width=4076;csid.fmt[4].height=2806;memory[CSID_IPP_CTRL/4]=0;
}
int main(void){
 init();native_rear_csid_route_before_reset(&csid);CHECK(nwrites==1);
 CHECK(offsets[0]==4 && values[0]==0x101);CHECK(memory[CSID_IPP_CTRL/4]==0);
 init();CHECK(csid680_native_rear_configure(&csid)==0);CHECK(nwrites==15);
 CHECK(native_rear_csid_reset_command(&csid)==CSID_RESET_CMD_SW_RESET);
 CHECK(memory[CSID_CSI2_RX_CFG0/4]==0x10232103);
 CHECK(memory[CSID_CSI2_RX_CFG1/4]==1);
 CHECK(memory[CSID_IPP_CFG0/4]==0x802b2000);
 CHECK(memory[CSID_IPP_CFG1/4]==0x7241);
 CHECK(memory[CSID_IPP_EPOCH_IRQ_CFG/4]==0x00130013);
 CHECK(memory[CSID_IPP_HCROP/4]==0x55555555);
 CHECK(memory[CSID_IPP_VCROP/4]==0x55555555);
 CHECK(memory[CSID_IPP_FORMAT_MEASURE_CFG0/4]==0x55555555);
 CHECK(memory[CSID_IPP_FORMAT_MEASURE_CFG1/4]==0x55555555);
 CHECK(memory[CSID_IPP_IRQ_SUBSAMPLE_PATTERN/4]==0x55555555);
 CHECK(memory[CSID_IPP_IRQ_SUBSAMPLE_PERIOD/4]==0x55555555);
 CHECK(memory[CSID_IPP_IRQ_MASK/4]==0x55555555);
 CHECK(memory[CSID_IPP_CTRL/4]==0);
 CHECK(memory[CSID_REG_UPDATE_CMD/4]==0x55555555);
 for(unsigned i=0;i<nwrites;i++)
  CHECK(offsets[i]!=CSID_IPP_IRQ_CLEAR&&offsets[i]!=CSID_BUF_DONE_IRQ_CLEAR&&
        offsets[i]!=CSID_TOP_IRQ_CLEAR&&offsets[i]!=CSID_CSI2_RX_IRQ_CLEAR);
 for(unsigned negative=0;negative<20;negative++){
  init();struct csid_device *arg=&csid;
  switch(negative){
  case 0:arg=NULL;break;case 1:csid.camss=NULL;break;case 2:camss.res=NULL;break;
  case 3:board.version=0;break;case 4:csid.id=0;break;case 5:csid.base=NULL;break;
  case 6:camss.csid_wrapper_base=NULL;break;case 7:csid.phy.csiphy_id=2;break;
  case 8:csid.phy.phy_sel=1;break;case 9:csid.phy.lane_cnt=1;break;
  case 10:csid.phy.lane_assign=0;break;case 11:csid.phy.en_ipp=0;break;
  case 12:csid.phy.en_vc=1;break;case 13:csid.fmt[4].code=MEDIA_BUS_FMT_SRGGB10_1X10;break;
  case 14:csid.fmt[4].width=4064;break;case 15:csid.fmt[4].height=2160;break;
  case 16:no_format=true;break;case 17:format.decode_format=3;break;
  case 18:format.data_type=0x2a;break;case 19:memory[CSID_IPP_CTRL/4]=1;break;
  }
  native_rear_csid_route_before_reset(arg);
  CHECK(nwrites==(negative<16?0:1));
  if(negative>=16)CHECK(offsets[0]==4 && values[0]==0x101);
  nwrites=0;
  CHECK(native_rear_csid_reset_command(arg)==(negative<16?(CSID_RESET_CMD_HW_RESET|CSID_RESET_CMD_SW_RESET):CSID_RESET_CMD_SW_RESET));
  CHECK(csid680_native_rear_configure(arg)==(negative==19?-EBUSY:-EINVAL));
  CHECK(nwrites==0);
 }
 printf("{\"assertions\":%u,\"writes\":15,\"negative_cases\":20,\"packet_fields_and_ACKs_untouched\":true}\n",assertions);
 return 0;
}
"""
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args()
 assert not a.report.exists()
 source=(a.staged/"camss-csid-680.c").read_text()
 reset=source[source.index("static int csid_reset("):source.index("int csid680_x1e_front_ipp_poll_epoch0(")]
 assert reset.index("return __csid_sp11_front_ipp_full_config(csid)") < reset.index("native_rear_csid_route_before_reset(csid)") < reset.index("writel(CSID_IRQ_CMD_CLEAR") < reset.index("native_rear_csid_reset_command(csid)")
 macros="\n".join(line for line in source.split("static inline int reg_update_rdi")[0].splitlines() if line.startswith("#define"))+"\n"
 code=PRELUDE+macros+'#include "camss-csid-e004ns-rear-ipp.inc"\n#include "native-rear-csid-config.inc"\n'+MAIN
 results=[]
 with tempfile.TemporaryDirectory(prefix="rear-transport-test-") as tmp:
  tmp=Path(tmp);c=tmp/"check.c";c.write_text(code)
  for compiler in ["gcc","clang"]:
   binary=tmp/compiler
   r=subprocess.run([compiler,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined",
    "-fno-omit-frame-pointer","-I"+str(a.staged),c,"-o",binary],text=True,capture_output=True)
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   r=subprocess.run([binary],text=True,capture_output=True,
    env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   if r.returncode or r.stderr:raise RuntimeError(r.stdout+r.stderr+" return="+str(r.returncode))
   results.append({"compiler":compiler,"result":json.loads(r.stdout),"ASAN_UBSAN_Werror":True})
 report={"status":"PASS_ACTUAL_REAR_TRANSPORT_HELPER_PREDICATE_NO_PACKET_FIELD_OR_ACK_WRITES",
 "exact_rear_SW_reset_and_other_mode_combined_reset_admission_checked":True,"exact_rear_route_before_reset_and_generic_front_unchanged_checked":True,"actual_helper_and_E004ns_predicate_and_RX_derivation":True,
 "MMIO_and_format_lookup_host_models":True,"hardware_access":False,"results":results}
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
