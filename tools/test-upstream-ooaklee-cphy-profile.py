#!/usr/bin/env python3
"""Exercise the pinned ooaklee C-PHY profile admission functions."""
import argparse,hashlib,json,re,subprocess,sys
from pathlib import Path

def extract(text,name):
    m=re.search(r'static int\s+'+name+r'\(',text)
    if not m:raise ValueError('function absent: '+name)
    a=m.start();b=text.index('{',a);i=b+1;depth=1
    while depth:
        depth+=(text[i]=='{')-(text[i]=='}');i+=1
    return text[a:i]
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--reference-root',required=True,type=Path)
    p.add_argument('--output',required=True,type=Path)
    p.add_argument('--compiler',choices=['gcc','clang'],required=True)
    a=p.parse_args()
    root=Path(__file__).resolve().parents[1]
    ref=json.loads((root/'src/upstream/sensors/imx681-ooaklee/reference.json').read_text())
    path='drivers/phy/qualcomm/phy-qcom-mipi-csi2-core.c'
    pin=next(v for v in ref['files'] if v['snapshot']=='current' and v['path']==path)
    source=a.reference_root/path
    if source.is_symlink() or not source.is_file():raise ValueError('not regular source')
    data=source.read_bytes()
    if hashlib.sha256(data).hexdigest()!=pin['sha256']:raise ValueError('source changed')
    text=data.decode()
    a.output.mkdir(parents=True,exist_ok=False)
    stub=r'''
#include <assert.h>
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint64_t u64;
typedef int64_t s64;
#define BIT(n) (1UL << (n))
#define BITS_PER_LONG 64
#define CSI2_MAX_DATA_LANES 4
enum phy_mode { PHY_MODE_INVALID, PHY_MODE_MIPI_DPHY, PHY_MODE_MIPI_CPHY };
struct lane { int pol,pos; };
struct mipi_csi2phy_stream_cfg {
 enum phy_mode mode; int combo_mode,cphy_trio,num_data_lanes; s64 link_freq;
 struct { struct lane data[4],clk; } lane_cfg;
};
struct mipi_csi2phy_soc_cfg { unsigned long cphy_symbol_rate,cphy_trio_mask; };
struct mipi_csi2phy_device { const struct mipi_csi2phy_soc_cfg *soc_cfg; struct mipi_csi2phy_stream_cfg stream_cfg; };
struct phy { struct mipi_csi2phy_device *data; enum phy_mode mode; };
struct phy_configure_opts_mipi_dphy { unsigned long hs_clk_rate; unsigned int lanes; };
union phy_configure_opts { struct phy_configure_opts_mipi_dphy mipi_dphy; };
static void *phy_get_drvdata(struct phy *p) { return p->data; }
static enum phy_mode phy_get_mode(struct phy *p) { return p->mode; }
static int dphy_result;
static int phy_mipi_dphy_config_validate(struct phy_configure_opts_mipi_dphy *p)
{ (void)p; return dphy_result; }
'''
    funcs='\n'.join(extract(text,n) for n in ['phy_qcom_mipi_csi2_set_mode','phy_qcom_mipi_csi2_configure'])
    harness=r'''
int main(void)
{
 struct mipi_csi2phy_soc_cfg soc={.cphy_symbol_rate=2406000000UL,.cphy_trio_mask=BIT(0)};
 struct mipi_csi2phy_device dev={.soc_cfg=&soc};
 struct phy phy={.data=&dev,.mode=PHY_MODE_MIPI_CPHY};
 const unsigned long rates[]={0,2400000000UL,2405999999UL,2406000000UL,2406000001UL,UINT64_MAX};
 unsigned int profiles=0,modes=0;
 int ret,expected;
 for(unsigned int lane=0;lane<=5;lane++)
 for(unsigned int rate=0;rate<6;rate++) {
  union phy_configure_opts opts={.mipi_dphy={.lanes=lane,.hs_clk_rate=rates[rate]}};
  struct mipi_csi2phy_stream_cfg before;
  memset(&dev.stream_cfg,0x5a,sizeof(dev.stream_cfg));before=dev.stream_cfg;
  ret=phy_qcom_mipi_csi2_configure(&phy,&opts);
  expected=lane!=1 || !rates[rate] ? -EINVAL :
           rates[rate]!=soc.cphy_symbol_rate ? -EOPNOTSUPP : 0;
  assert(ret==expected);
  if(ret)assert(!memcmp(&before,&dev.stream_cfg,sizeof(before)));
  else assert(dev.stream_cfg.link_freq==2406000000LL &&
              dev.stream_cfg.num_data_lanes==1 &&
              dev.stream_cfg.mode==PHY_MODE_MIPI_CPHY && dev.stream_cfg.combo_mode==1);
  profiles++;
 }
 for(int sub=-1;sub<=64;sub++) {
  struct mipi_csi2phy_stream_cfg before;
  memset(&dev.stream_cfg,0x5a,sizeof(dev.stream_cfg));before=dev.stream_cfg;
  ret=phy_qcom_mipi_csi2_set_mode(&phy,PHY_MODE_MIPI_CPHY,sub);
  expected=sub<0 || sub>=64 ? -EINVAL : sub ? -EOPNOTSUPP : 0;
  assert(ret==expected);
  if(ret)assert(!memcmp(&before,&dev.stream_cfg,sizeof(before)));
  else assert(dev.stream_cfg.cphy_trio==0);
  modes++;
 }
 /* D-PHY validator errors are propagated; modeled validator is not qualified here. */
 phy.mode=PHY_MODE_MIPI_DPHY;
 union phy_configure_opts opts={.mipi_dphy={.lanes=2,.hs_clk_rate=1000000000UL}};
 dphy_result=-EINVAL;assert(phy_qcom_mipi_csi2_configure(&phy,&opts)==-EINVAL);
 assert(phy_qcom_mipi_csi2_set_mode(&phy,PHY_MODE_MIPI_DPHY,1)==-EINVAL);
 assert(phy_qcom_mipi_csi2_set_mode(&phy,PHY_MODE_MIPI_DPHY,0)==0);
 printf("{\"profile_cases\":%u,\"mode_cases\":%u,\"dphy_controls\":3,\"local_2400_rate_admitted\":false}\n",profiles,modes);
}
'''
    c=a.output/'profile.c';c.write_text(stub+'\n'+funcs+'\n'+harness)
    cmd=[a.compiler,'-std=c11','-Wall','-Wextra','-Werror','-O1','-g',
         '-fsanitize=address,undefined','-fno-omit-frame-pointer',str(c),'-o',str(a.output/'profile')]
    r=subprocess.run(cmd,capture_output=True,text=True)
    (a.output/'compile.log').write_text(r.stdout+r.stderr)
    if r.returncode:raise RuntimeError(r.stderr)
    r=subprocess.run([str(a.output/'profile')],capture_output=True,text=True)
    (a.output/'run.log').write_text(r.stdout+r.stderr)
    if r.returncode:raise RuntimeError(r.stdout+r.stderr)
    result=json.loads(r.stdout)
    result.update({'ok':True,'compiler':a.compiler,'scope':'actual public set_mode/configure; model types, PHY context and D-PHY validator','sanitizers':['address','undefined']})
    (a.output/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))
if __name__=='__main__':
    try:main()
    except (ValueError,RuntimeError) as e:sys.exit(str(e))
