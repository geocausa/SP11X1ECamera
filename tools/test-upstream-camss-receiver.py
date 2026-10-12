#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import pathlib,os,pwd,subprocess,json,re,hashlib,traceback,datetime
SELF=pathlib.Path(__file__).read_text()
import argparse
ap=argparse.ArgumentParser(description='Pinned actual C receiver functions with modeled Linux services, GCC/Clang ASAN/UBSAN.')
ap.add_argument('--source',type=pathlib.Path,required=True)
ap.add_argument('--parent-source',type=pathlib.Path,required=True)
ap.add_argument('--output',type=pathlib.Path,required=True)
a=ap.parse_args();S=a.source.resolve();P=a.parent_source.resolve();T=a.output.absolute()
manifest=pathlib.Path(__file__).resolve().parents[1]/'src/upstream/receiver/cphy-x1e-20261012/manifest.json'
m=json.loads(manifest.read_text())
assert not T.exists() and not T.is_symlink() and not T.resolve().is_relative_to(S) and not T.resolve().is_relative_to(P)
for root,pins in [(S,{**m['output_source_sha256'],**m['unchanged_parent_source_sha256']}),(P,{**m['parent_source_sha256'],**m['unchanged_parent_source_sha256']})]:
 for n,pin in pins.items():
  f=root/n;assert not f.is_symlink() and f.resolve().is_relative_to(root),n
  assert (hashlib.sha256(f.read_bytes()).hexdigest() if f.exists() else None)==pin,n
T.mkdir();(T/'runner.py').write_text(SELF)
def func(s,name):
 m=re.search(r'static\s+void\s+'+name+r'\s*\(',s);assert m,name
 a=m.start();i=s.index('{',m.end())+1;d=1
 while d:
  if s[i]=='{':d+=1
  if s[i]=='}':d-=1
  i+=1
 return s[a:i]+'\n'
cpath='drivers/media/platform/qcom/camss/camss-csid-680.c';vpath='drivers/media/platform/qcom/camss/camss-vfe-680.c'
c=(S/cpath).read_text();v=(S/vpath).read_text();h=(S/'drivers/media/platform/qcom/camss/camss-csid.h').read_text()
defs='\n'.join(m.group() for s in [c,v,h,(S/'drivers/media/platform/qcom/camss/camss-csid-gen3.h').read_text()] for m in re.finditer(r'^#define[^\n]*(?:\\\n[^\n]*)*',s,re.M))+'\n'
enum=''
pre=r'''
#include <assert.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
typedef uint32_t u32;typedef uint8_t u8;
#define BIT(n) (1U<<(n))
#define GENMASK(h,l) (((~0U)<<(l))&((~0U)>>(31-(h))))
#define FIELD_PREP(m,v) (((u32)(v)<<__builtin_ctz(m))&(m))
#define dev_dbg(...) ((void)0)
#define V4L2_MBUS_CSI2_CPHY 1
#define V4L2_MBUS_CSI2_DPHY 4
#define TPG_PAYLOAD_MODE_DISABLED 0
static unsigned char memory[0x20000];
static unsigned count;
static void writel(u32 val,void *p){
 uintptr_t at=(uintptr_t)p-(uintptr_t)memory;assert(at+4<=sizeof(memory)&&!(at&3));
 memcpy(memory+at,&val,4);count++;
}
static u32 readl(void *p){
 uintptr_t at=(uintptr_t)p-(uintptr_t)memory;u32 v;assert(at+4<=sizeof(memory));memcpy(&v,memory+at,4);return v;
}
struct tpg { struct {int mode;} testgen; };
struct camss {struct tpg *tpg; void *dev;};
struct csid_phy_config {int bus_type,lane_cnt,lane_assign,csiphy_id;};
struct v4l2_mbus_framefmt {u32 code;};
struct csid_format_info {u32 data_type;};
struct format_list {const struct csid_format_info *formats; unsigned nformats;};
struct csid_resources {struct format_list *formats;};
struct csid_device {
 struct camss *camss;void *base;bool tpg_linked;struct csid_phy_config phy;
 struct v4l2_mbus_framefmt fmt[8];struct csid_resources *res;
};
static const struct csid_format_info *csid_get_fmt_entry(const struct csid_format_info *f,unsigned n,u32 code){
 assert(n==1);return f;
}
struct v4l2_pix_format_mplane {u32 width,height;struct {u32 bytesperline;} plane_fmt[1];};
struct video {struct {struct {struct v4l2_pix_format_mplane pix_mp;} fmt;} active_fmt;};
struct vfe_output {struct video video_out;struct {u8 bus_client;} wm[1];};
struct vfe_device {void *base;struct camss *camss;bool lite;};
static bool vfe_is_lite(struct vfe_device *v){return v->lite;}
static void vfe_disable_irq(struct vfe_device *v){assert(count==11);}
'''
actual=func(c,'__csid_configure_rx')+func(c,'__csid_configure_rdi_stream')+func(v,'vfe_output_start')
old=func((P/cpath).read_text(),'__csid_configure_rx').replace('__csid_configure_rx','old_rx')
old+=func((P/cpath).read_text(),'__csid_configure_rdi_stream').replace('__csid_configure_rdi_stream','old_rdi')
main=r'''
int main(void){
 struct camss cam={0};struct csid_device cs={.camss=&cam,.base=memory};unsigned cases=0;
 for(int id=0;id<6;id++)for(int lane=1;lane<=4;lane++)for(int assign=0;assign<2;assign++)for(int vc=0;vc<8;vc++){
  struct csid_phy_config phy={V4L2_MBUS_CSI2_DPHY,lane,assign?0xe4:0,id};
  count=0;__csid_configure_rx(&cs,&phy,vc);
  u32 a=readl(memory+CSID_CSI2_RX_CFG0),b=readl(memory+CSID_CSI2_RX_CFG1);assert(count==2);
  old_rx(&cs,&phy,vc);assert(a==readl(memory+CSID_CSI2_RX_CFG0)&&b==readl(memory+CSID_CSI2_RX_CFG1));cases++;
 }
 for(int vc=0;vc<8;vc++){
  struct csid_phy_config phy={V4L2_MBUS_CSI2_CPHY,1,0,2};
  count=0;__csid_configure_rx(&cs,&phy,vc);assert(count==2);
  assert(readl(memory+CSID_CSI2_RX_CFG0)==0x11300000);cases++;
 }
 const struct csid_format_info fmt={.data_type=0x2b};struct format_list fl={&fmt,1};struct csid_resources res={&fl};
 cs.res=&res;cs.phy.lane_cnt=1;
 const u32 forbidden=RDI_CFG1_DROP_H_EN|RDI_CFG1_DROP_V_EN|RDI_CFG1_CROP_H_EN|RDI_CFG1_CROP_V_EN;
 for(u8 port=0;port<4;port++)for(u8 vc=0;vc<8;vc++)for(u8 en=0;en<2;en++){
  count=0;__csid_configure_rdi_stream(&cs,en,port,vc);assert(count==7);
  u32 cfg=readl(memory+CSID_RDI_CFG1(port));assert(!(cfg&forbidden));
  assert(cfg==(RDI_CFG1_TIMESTAMP_STB_FRAME|RDI_CFG1_BYTE_CNTR_EN|RDI_CFG1_TIMESTAMP_EN|RDI_CFG1_PACKING_MIPI));
  u32 cfg0=readl(memory+CSID_RDI_CFG0(port));assert(!!(cfg0&RDI_CFG0_ENABLE)==!!en);
  old_rdi(&cs,en,port,vc);assert((readl(memory+CSID_RDI_CFG1(port))&forbidden)==forbidden);cases++;
 }
 struct vfe_device vf={.base=memory,.camss=&cam};struct vfe_output out={0};
 out.video_out.active_fmt.fmt.pix_mp.width=3840;out.video_out.active_fmt.fmt.pix_mp.height=2640;
 out.video_out.active_fmt.fmt.pix_mp.plane_fmt[0].bytesperline=4800;
 for(int lite=0;lite<2;lite++)for(unsigned wm=0;wm<16;wm++){
  vf.lite=lite;out.wm[0].bus_client=wm;count=0;vfe_output_start(&vf,&out);
  assert(count==12&&readl(memory+VFE_BUS_WRITE_CLIENT_CFG(&vf,wm))==0x10001);
  assert(readl(memory+VFE_BUS_FRAME_INCR(&vf,wm))==12672000);cases++;
 }
 printf("{\"cases\":%u,\"rx_word_dphy_controls_crop_drop_packed_raw\":true}\n",cases);return 0;
}
'''
code=pre+defs+enum+actual+old+main;(T/'actual-functions.c').write_text(code)
result={'ok':False,'compilers':{},'source_sha256':{p:hashlib.sha256((S/p).read_bytes()).hexdigest() for p in [cpath,vpath,'drivers/media/platform/qcom/camss/camss-csid.h','drivers/media/platform/qcom/camss/camss-csid-gen3.h']},'scope':'Actual CSID RX/RDI and VFE RDI start; modeled MMIO/format lookup/IRQ masking. No hardware.'}
try:
 for cc in ['gcc','clang']:
  with (T/(cc+'.log')).open('w') as log:
   a=[cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-Wno-sign-compare','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(T/'actual-functions.c'),'-o',str(T/cc)]
   p=subprocess.run(a,stdout=log,stderr=subprocess.STDOUT);assert p.returncode==0,(cc,'compile')
   p=subprocess.run([str(T/cc)],stdout=log,stderr=subprocess.STDOUT);assert p.returncode==0,(cc,'run')
  result['compilers'][cc]={'ok':True,'output':(T/(cc+'.log')).read_text()}
 result['ok']=True
except Exception as e:result['error']=repr(e);(T/'exception.log').write_text(traceback.format_exc())
result['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(T/'result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
