#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Exercise actual shared VFE prefix and rear admission/readback with modeled MMIO."""
import argparse,json,os,re,subprocess,tempfile
from pathlib import Path
def function(s,signature):
 i=s.index(signature);a=s.index("{",i);depth=1;j=a+1
 while depth:
  depth+=(s[j]=="{")-(s[j]=="}");j+=1
 return s[i:j]+"\n"
PRE=r"""
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
typedef uint32_t u32;
#define BIT(x) (1U<<(x))
#define CAMSS_X1E80100 99
#define VFE680_E004NU_REAR_CLIENTS 10
#define VFE_BUS_WRITE_CLIENT_CFG_EN 1
struct res {int version;};struct camss {struct res *res;void *dev;};
struct vfe_device {struct camss *camss;int id;bool lite;uint8_t *base;};
static bool vfe_is_lite(struct vfe_device *v){return v->lite;}
static u32 mem[0x8000/4],offsets[32],values[32];
static unsigned writes,assertions;static bool contract=true,corrupt,masked_readback;static unsigned bad_readback;
static const struct {unsigned wm;} vfe680_e004nu_rear_wm_contract[10]={{0},{1},{2},{3},{11},{12},{13},{14},{16},{18}};
#define CHECK(x) do {assertions++;if(!(x)){fprintf(stderr,"failed line%d\n",__LINE__);exit(1);}}while(0)
static u32 readl(void *p){unsigned off=(uint8_t*)p-(uint8_t*)mem;CHECK(off<sizeof(mem)&&!(off&3));u32 value=mem[off/4];if(masked_readback){if(off==0x24)value&=~2U;if(off==0xc18)value&=~0x0c000000U;}if(bad_readback&&off==0x24)value=4;if(bad_readback==2&&off==0xc18)value=0xc0000000;return value^((corrupt&&off==0xc58)?1:0);}
static void writel(u32 v,void *p){unsigned off=(uint8_t*)p-(uint8_t*)mem;CHECK(off<sizeof(mem)&&!(off&3)&&writes<32);mem[off/4]=v;offsets[writes]=off;values[writes++]=v;}
#define writel_relaxed writel
static void *vfe680_x1e_bus_reg(struct vfe_device *v,unsigned wm,unsigned off){return v->base+0xe00+wm*0x100+off;}
static bool vfe680_e004nu_rear_wm_contract_valid(void){return contract;}
static struct res board;static struct camss cam;static struct vfe_device vfe;
static void init(void){for(unsigned i=0;i<sizeof(mem)/4;i++)mem[i]=0x55555554;board.version=99;cam=(struct camss){&board,&board};vfe=(struct vfe_device){&cam,1,false,(uint8_t*)mem};writes=0;contract=true;corrupt=false;masked_readback=false;bad_readback=0;}
"""
MAIN=r"""
int main(void){
 init();CHECK(native_rear_vfe_configure(&vfe)==0);CHECK(writes==7);
 const u32 wantoff[7]={0x34,0x38,0xc1c,0x24,0x28,0xc18,0xc58};
 const u32 wantval[7]={0x7f051,0,0,7,0x10,0xdc000000,0x1046};
 for(unsigned i=0;i<7;i++){CHECK(offsets[i]==wantoff[i]);CHECK(values[i]==wantval[i]);}
 for(unsigned i=0;i<10;i++)CHECK(mem[(0xe00+vfe680_e004nu_rear_wm_contract[i].wm*0x100)/4]==0x55555554);
 CHECK(mem[0x9c/4]==0x55555554);CHECK(mem[0xe04/4]==0x55555554);CHECK(mem[0x260/4]==0x55555554);
 for(unsigned i=0;i<18;i++){
  init();struct vfe_device *arg=&vfe;
  switch(i){case 0:arg=NULL;break;case 1:vfe.camss=NULL;break;case 2:cam.dev=NULL;break;
   case 3:cam.res=NULL;break;case 4:board.version=0;break;case 5:vfe.id=0;break;
   case 6:vfe.lite=true;break;case 7:vfe.base=NULL;break;
   default:mem[(0xe00+vfe680_e004nu_rear_wm_contract[i-8].wm*0x100)/4]|=1;break;}
  CHECK(native_rear_vfe_configure(arg)==(i<8?-EINVAL:-EBUSY));CHECK(writes==0);
 }
 init();contract=false;CHECK(native_rear_vfe_configure(&vfe)==-EINVAL);CHECK(writes==0);
 init();corrupt=true;CHECK(native_rear_vfe_configure(&vfe)==-EIO);CHECK(writes==7);
 init();masked_readback=true;CHECK(native_rear_vfe_configure(&vfe)==0);CHECK(writes==7);CHECK(mem[0x24/4]==7);CHECK(mem[0xc18/4]==0xdc000000);
 for(unsigned i=1;i<=2;i++){init();masked_readback=true;bad_readback=i;CHECK(native_rear_vfe_configure(&vfe)==-EIO);CHECK(writes==7);}
 printf("{\"assertions\":%u,\"writes\":7,\"admission_negatives\":19,\"readback_faults\":3,\"WM_IQ_and_addresses_untouched\":true}\n",assertions);
 return 0;
}
"""
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 s=(a.staged/"camss-vfe-680.c").read_text()
 needed=["VFE680_X1E_WINDOWS_BUS_MASK0","VFE_TOP_IRQn_MASK","VFE_BUS_IRQn_MASK","VFE680_X1E_WINDOWS_TOP_MASK0","VFE680_X1E_SP11_DAL_CORE_CFG0","VFE680_X1E_SP11_DAL_CORE_CFG1","VFE680_X1E_SP11_DAL_BUS_MASK0","VFE680_X1E_BUS_UBWC_STATIC_CTRL","VFE680_X1E_WINDOWS_UBWC_STATIC_CTRL"]
 macros="\n".join(l for l in s.splitlines() if l.startswith("#define") and any(re.match(r"#define\s+"+n+r"(?:\(|\s)",l) for n in needed+["VFE680_X1E_SP11_DAL_CORE_CFG0_VALUE","VFE680_X1E_SP11_DAL_CORE_CFG1_VALUE"]))+"\n"
 code=PRE+macros+function(s,"static bool vfe680_x1e_bus_target(")
 other=(a.staged/"camss-vfe-e004nt-rear-4k-buffer.inc").read_text()
 code+="static bool "+function(other,"vfe680_e004nt_rear_4k_target(")
 code+=function(s,"int vfe680_x1e_pix_runtime_start_prefix(")+(a.staged/"native-rear-vfe-config.inc").read_text()+MAIN
 results=[]
 with tempfile.TemporaryDirectory() as t:
  t=Path(t);c=t/"check.c";c.write_text(code)
  for compiler in ["gcc","clang"]:
   binary=t/compiler
   r=subprocess.run([compiler,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer",str(c),"-o",str(binary)],capture_output=True,text=True)
   if r.returncode:raise RuntimeError(r.stdout+r.stderr)
   r=subprocess.run([str(binary)],capture_output=True,text=True,env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   if r.returncode or r.stderr:raise RuntimeError(r.stdout+r.stderr)
   results.append({"compiler":compiler,"ASAN_UBSAN_Werror":True,"result":json.loads(r.stdout)})
 report={"status":"PASS_REAL_SHARED_VFE_PREFIX_REAR_ADMISSION_AND_READBACK","full_and_same_SP11_observed_readback_models_checked":True,"actual_prefix_predicate_and_helper":True,"MMIO_and_contract_validity_host_models":True,"hardware_access":False,"results":results}
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
