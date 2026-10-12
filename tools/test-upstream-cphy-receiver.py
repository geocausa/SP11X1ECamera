#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Run actual candidate C functions with modeled Linux services, not hardware."""
import pathlib, re, subprocess, hashlib, json, os, pwd, datetime, traceback
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
T.mkdir(exist_ok=False);(T/'runner.py').write_text(SELF)
def strip(s): return re.sub(r'^#include.*$', '', s, flags=re.M)
def extract(s,name):
    m=re.search(r'(?:static\s+)?int\s+'+name+r'\s*\(',s); assert m,name
    start=m.start();b=s.index('{',m.end()); depth=1;i=b+1
    while depth:
        if s[i]=='{':depth+=1
        if s[i]=='}':depth-=1
        i+=1
    return s[start:i]+'\n'
paths=['drivers/phy/qualcomm/phy-qcom-mipi-csi2-3ph-cphy.c','drivers/phy/qualcomm/phy-qcom-mipi-csi2-core.c','drivers/phy/qualcomm/phy-qcom-mipi-csi2.h','drivers/phy/qualcomm/phy-qcom-mipi-csi2-cphy-x1e80100.h','include/linux/phy/phy-mipi-cphy.h','include/linux/phy/phy-mipi-dphy.h','include/linux/phy/phy.h']
pins={p:hashlib.sha256((S/p).read_bytes()).hexdigest() for p in paths}
core=(S/paths[1]).read_text(); old=(P/paths[1]).read_text()
enum=re.search(r'enum phy_mode\s*\{.*?\};',(S/paths[-1]).read_text(),re.S).group()
pre=r'''
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <stddef.h>
typedef uint8_t u8;
typedef uint32_t u32;
typedef int32_t s32;
typedef uint64_t u64;
typedef int64_t s64;
typedef int irqreturn_t;
#define __iomem
#define IRQ_HANDLED 1
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define NSEC_PER_USEC 1000
#define max(a,b) ((a)>(b)?(a):(b))
#define max_t(t,a,b) max((t)(a),(t)(b))
#define dev_err(...) ((void)0)
#define MEDIA_BUS_TYPE_CSI2_CPHY 1
#define MEDIA_BUS_TYPE_CSI2_DPHY 4
struct device { int id; };
struct clk { int id; };
struct clk_bulk_data { int unused; };
struct regulator_bulk_data { int unused; };
struct dev_pm_domain_list { int num_pds; struct device **pd_devs; };
struct dev_pm_opp { int unused; };
struct phy { void *data; };
static void *phy_get_drvdata(struct phy *p) { return p->data; }
#define IS_ERR(p) ((intptr_t)(p)<0)
#define PTR_ERR(p) ((int)(intptr_t)(p))
'''
header=strip((S/paths[2]).read_text())
opts=strip((S/paths[4]).read_text())+strip((S/paths[5]).read_text())+'''
union phy_configure_opts {
struct phy_configure_opts_mipi_dphy mipi_dphy;
struct phy_configure_opts_mipi_cphy mipi_cphy;
};
'''
model=r'''
static unsigned char mmio[0x2000];
static struct { u32 addr, val; } writes[2048];
static unsigned nw, ndelay, nsleep;
static int regs, pm, clocks, irq_live, opp_refs, pstate[3], resets, versions, fail;
static unsigned long opp_current, requested_opp, requested_timer;
static long override_opp, override_timer;
static int dphy_error;
static unsigned cases;
static void might_sleep(void) {}
static void writel(u32 value, void *address) {
    uintptr_t a=(uintptr_t)address-(uintptr_t)mmio;
    assert(a < sizeof(mmio) && !(a&3));
    assert(regs==1 && pm==1 && clocks==1);
    assert(nw<ARRAY_SIZE(writes));
    writes[nw].addr=a;writes[nw++].val=value;
}
static void udelay(u32 us) { assert(us>0 && us<=10);ndelay++; }
static void usleep_range(u32 a,u32 b) { assert(a>10 && b>=a+10);nsleep++; }
static int regulator_bulk_enable(unsigned n,void *p) {
    assert(regs==0); if(fail==1)return -EIO;regs=1;return 0;
}
static void regulator_bulk_disable(unsigned n,void *p) { assert(regs==1);regs=0; }
static int pm_runtime_resume_and_get(struct device *d) {
    assert(regs==1 && pm==0);if(fail==2)return -EIO;pm=1;return 1;
}
static void pm_runtime_put_sync(struct device *d) { assert(pm==1 && clocks==0);pm=0; }
static struct dev_pm_opp the_opp;
static struct dev_pm_opp *dev_pm_opp_find_freq_ceil(struct device *d,unsigned long *r) {
    requested_opp=*r;
    if(fail==3)return (void *)(intptr_t)-EIO;
    if(override_opp)*r=override_opp;
    opp_refs++;return &the_opp;
}
static void dev_pm_opp_put(struct dev_pm_opp *o) { assert(opp_refs==1);opp_refs--; }
static unsigned dev_pm_opp_get_required_pstate(struct dev_pm_opp *o,int idx) {
    assert(opp_refs==1);return 10+idx;
}
static int dev_pm_genpd_set_performance_state(struct device *d,unsigned perf) {
    assert(d->id>=0 && d->id<3);
    if(perf && ((fail==4&&d->id==0)||(fail==5&&d->id==2)))return -EIO;
    pstate[d->id]=perf;return 0;
}
static int dev_pm_opp_set_rate(struct device *d,unsigned long r) {
    if(r&&fail==6)return -EIO;
    opp_current=r;return 0;
}
static long clk_round_rate(struct clk *c,unsigned long r) {
    requested_timer=r;if(fail==7)return -EIO;
    return override_timer?override_timer:(long)r;
}
static int clk_set_rate(struct clk *c,unsigned long r) {
    if(fail==8)return -EIO;
    assert(r==(unsigned long)requested_timer);return 0;
}
static int clk_bulk_prepare_enable(unsigned n,void *p) {
    assert(regs==1&&pm==1&&clocks==0);
    if(fail==9)return -EIO;
    clocks=1;return 0;
}
static void clk_bulk_disable_unprepare(unsigned n,void *p) {
    assert(clocks==1&&irq_live==0);clocks=0;
}
static void enable_irq(int irq) {
    assert(irq>0&&clocks==1&&regs==1&&pm==1&&irq_live==0);
    assert(nw==162);irq_live=1;
}
static void disable_irq(int irq) {
    assert(irq>0&&clocks==1&&irq_live==1);irq_live=0;
}
int phy_mipi_dphy_config_validate(struct phy_configure_opts_mipi_dphy *o) {
    return dphy_error;
}
struct fwnode_handle { int dummy; };
static struct fwnode_handle node;
static struct {
    int split, missing, refs, bus, bus_present, count, order_present, order_count;
    int clock_present, pol_present, pol_count, read_error;
    u32 lanes[4], polarities[5], order;
} fw;
static struct fwnode_handle *dev_fwnode(struct device *d) {return &node;}
static struct fwnode_handle *fwnode_graph_get_endpoint_by_id(struct fwnode_handle *d,int p,int e,int f) {
    if((e==1&&!fw.split)||(e==0&&fw.missing))return NULL;
    fw.refs++;return &node;
}
static void fwnode_handle_put(struct fwnode_handle *f) {assert(fw.refs==1);fw.refs--;}
static bool fwnode_property_present(struct fwnode_handle *n,const char *s) {
    if(!strcmp(s,"clock-lanes"))return fw.clock_present;
    if(!strcmp(s,"lane-polarities"))return fw.pol_present;
    if(!strcmp(s,"line-orders"))return fw.order_present;
    return false;
}
static int fwnode_property_read_u32(struct fwnode_handle *n,const char *s,u32 *o) {
    assert(!strcmp(s,"bus-type"));
    if(!fw.bus_present)return -EINVAL;
    *o=fw.bus;return 0;
}
static int fwnode_property_count_u32(struct fwnode_handle *n,const char *s) {
    if(!strcmp(s,"data-lanes"))return fw.count;
    if(!strcmp(s,"lane-polarities"))return fw.pol_present?fw.pol_count:-EINVAL;
    if(!strcmp(s,"line-orders"))return fw.order_present?fw.order_count:-EINVAL;
    assert(false);return -EINVAL;
}
static int fwnode_property_read_u32_array(struct fwnode_handle *n,const char *s,u32 *o,unsigned count) {
    if(fw.read_error)return -EIO;
    int num=fwnode_property_count_u32(n,s);
    if(num<(int)count)return -EINVAL;
    if(!strcmp(s,"data-lanes"))memcpy(o,fw.lanes,count*sizeof(*o));
    else if(!strcmp(s,"lane-polarities"))memcpy(o,fw.polarities,count*sizeof(*o));
    else if(!strcmp(s,"line-orders"))*o=fw.order;
    else assert(false);
    return 0;
}
'''
leaf=strip((S/paths[0]).read_text())
table=strip((S/paths[3]).read_text())
names=['phy_qcom_mipi_csi2_set_clock_rates','phy_qcom_mipi_csi2_configure','phy_qcom_mipi_csi2_set_mode','phy_qcom_mipi_csi2_power_on','phy_qcom_mipi_csi2_power_off','phy_qcom_mipi_csi2_parse_routing']
actual=''.join(extract(core,n) for n in names)
oldfunc=''.join(extract(old,n).replace(n,n+'_old') for n in ['phy_qcom_mipi_csi2_configure','phy_qcom_mipi_csi2_parse_routing'])
main=r'''
static void reset_op(struct mipi_csi2phy_device *d){resets++;}
static void version_op(struct mipi_csi2phy_device *d){versions++;}
static int lanes_op(struct mipi_csi2phy_device *d,struct mipi_csi2phy_stream_cfg *c){
    if(fail==10)return -EIO;
    return d->phy_mode==PHY_MODE_MIPI_CPHY?mipi_csi2phy_cphy_enable(d,c):0;
}
static void stop_op(struct mipi_csi2phy_device *d,struct mipi_csi2phy_stream_cfg *c){
    assert(irq_live==0);
    if(d->phy_mode==PHY_MODE_MIPI_CPHY)mipi_csi2phy_cphy_disable(d);
}
static const struct mipi_csi2phy_hw_ops ops={
    .reset=reset_op,.hw_version_read=version_op,.lanes_enable=lanes_op,.lanes_disable=stop_op
};
static const struct mipi_csi2_genpd domains[3]={{"a",true},{"b",false},{"c",true}};
const struct mipi_csi2phy_soc_cfg mipi_csi2_dphy_4nm_x1e={
    .ops=&ops,.num_supplies=2,.num_clk=3,
    .cphy_symbol_rate=2406000000ULL,.cphy_core_rate=480000000,.cphy_timer_rate=400000000,
    .genpds=domains,.num_genpds=3
};
static struct device dev={0}, pd0={0},pd1={1},pd2={2};
static struct device *pds[]={&pd0,&pd1,&pd2};
static struct dev_pm_domain_list pd_list={3,pds};
static struct clk timer;
static struct mipi_csi2phy_device make_device(void){
    struct mipi_csi2phy_device d={0};
    d.dev=&dev;d.phy_mode=PHY_MODE_MIPI_CPHY;d.cphy_supported=true;d.irq=479;
    d.base=mmio;d.timer_clk=&timer;d.pd_list=&pd_list;d.soc_cfg=&mipi_csi2_dphy_4nm_x1e;
    d.stream_cfg.num_data_lanes=1;d.stream_cfg.symbol_rate=2406000000ULL;
    return d;
}
static void reset_model(void){
    nw=ndelay=nsleep=0;regs=pm=clocks=irq_live=opp_refs=0;opp_current=0;
    resets=versions=fail=dphy_error=0;override_opp=override_timer=0;
    requested_opp=requested_timer=0;memset(pstate,0,sizeof(pstate));
}
static void balanced(void){
    assert(!regs&&!pm&&!clocks&&!irq_live&&!opp_refs&&!opp_current);
    for(unsigned i=0;i<ARRAY_SIZE(pstate);i++)assert(!pstate[i]);
}
static void expect_table(unsigned *at,const struct x1e80100_cphy_reg *t,unsigned n){
    for(unsigned i=0;i<n;i++){
        assert(writes[*at].addr==t[i].reg_addr&&writes[*at].val==t[i].reg_data);(*at)++;
    }
}
static void check_start(void){
    assert(nw==162);unsigned at=0;
    expect_table(&at,x1e80100_cphy_reset,ARRAY_SIZE(x1e80100_cphy_reset));
    expect_table(&at,x1e80100_cphy_toggle,ARRAY_SIZE(x1e80100_cphy_toggle));
    expect_table(&at,x1e80100_cphy_common,ARRAY_SIZE(x1e80100_cphy_common));
    expect_table(&at,x1e80100_cphy_config,ARRAY_SIZE(x1e80100_cphy_config));
    expect_table(&at,x1e80100_cphy_irq_clear,ARRAY_SIZE(x1e80100_cphy_irq_clear));
    assert(at==162&&ndelay>0&&nsleep>0);
}
int main(void){
    struct mipi_csi2phy_device d=make_device();
    assert(mipi_csi2phy_cphy_validate(NULL,&d.stream_cfg)==-EINVAL);
    assert(mipi_csi2phy_cphy_validate(&d,NULL)==-EINVAL);cases+=2;
    const u64 rates[]={0,1,2400000000ULL,2405999999ULL,2406000000ULL,2406000001ULL,UINT64_MAX};
    for(unsigned rate=0;rate<ARRAY_SIZE(rates);rate++)
    for(unsigned count=0;count<5;count++)
    for(unsigned pos=0;pos<4;pos++)
    for(unsigned pol=0;pol<2;pol++){
        reset_model();d=make_device();d.stream_cfg.symbol_rate=rates[rate];
        d.stream_cfg.num_data_lanes=count;d.stream_cfg.lane_cfg.data[0].pos=pos;
        d.stream_cfg.lane_cfg.data[0].pol=pol;
        bool valid=rates[rate]==2406000000ULL&&count==1&&pos==0&&pol==0;
        regs=pm=clocks=1;
        int r=mipi_csi2phy_cphy_enable(&d,&d.stream_cfg);
        assert((r==0)==valid);
        if(valid)check_start();else assert(nw==0&&ndelay==0&&nsleep==0);
        cases++;
    }
    for(unsigned variant=0;variant<4;variant++){
        reset_model();d=make_device();
        struct mipi_csi2phy_soc_cfg other=mipi_csi2_dphy_4nm_x1e;
        if(variant==0)d.cphy_supported=false;
        if(variant==1)d.phy_mode=PHY_MODE_MIPI_DPHY;
        if(variant==2)d.soc_cfg=&other;
        if(variant==3)d.stream_cfg.lane_cfg.clk.pol=1;
        assert(mipi_csi2phy_cphy_enable(&d,&d.stream_cfg)==-EOPNOTSUPP);assert(nw==0);cases++;
    }
    reset_model();d=make_device();regs=pm=clocks=1;
    assert(mipi_csi2phy_cphy_irq(d.irq,&d)==IRQ_HANDLED);
    assert(nw==24&&ndelay==4&&nsleep==0);cases++;
    reset_model();d=make_device();regs=pm=clocks=1;mipi_csi2phy_cphy_disable(&d);
    assert(nw==38);unsigned at=11;
    for(unsigned i=0;i<11;i++)assert(writes[i].addr==0x102c+4*i&&writes[i].val==0);
    expect_table(&at,x1e80100_cphy_irq_clear,24);
    expect_table(&at,x1e80100_cphy_shutdown,3);assert(at==38);cases++;
    for(unsigned count=0;count<5;count++)
    for(unsigned rate=0;rate<ARRAY_SIZE(rates);rate++){
        reset_model();d=make_device();struct phy phy={&d};
        union phy_configure_opts o={0};o.mipi_cphy.num_trios=count;o.mipi_cphy.symbol_rate=rates[rate];
        struct mipi_csi2phy_stream_cfg saved=d.stream_cfg;
        int r=phy_qcom_mipi_csi2_configure(&phy,&o);
        assert((r==0)==(count==1&&rates[rate]==2406000000ULL));
        if(r)assert(!memcmp(&saved,&d.stream_cfg,sizeof(saved)));
        assert(nw==0);cases++;
    }
    d=make_device();struct phy phy={&d};assert(phy_qcom_mipi_csi2_configure(&phy,NULL)==-EINVAL);cases++;
    for(int mode=PHY_MODE_INVALID;mode<=PHY_MODE_MIPI_CPHY;mode++)
    for(int sub=-1;sub<=1;sub++){
        d=make_device();int r=phy_qcom_mipi_csi2_set_mode(&phy,mode,sub);
        assert((r==0)==(mode==PHY_MODE_MIPI_CPHY&&sub==0));cases++;
    }
    for(unsigned lane=0;lane<=5;lane++)for(unsigned error=0;error<2;error++){
        d=make_device();d.phy_mode=PHY_MODE_MIPI_DPHY;
        struct mipi_csi2phy_device e=d;struct phy oldphy={&e};
        union phy_configure_opts o={0};o.mipi_dphy.lanes=lane;o.mipi_dphy.hs_clk_rate=1000000000;
        dphy_error=error?-EIO:0;
        int r=phy_qcom_mipi_csi2_configure(&phy,&o),q=phy_qcom_mipi_csi2_configure_old(&oldphy,&o);
        assert(r==q&&!memcmp(&d.stream_cfg,&e.stream_cfg,sizeof(d.stream_cfg)));cases++;
    }
    for(int f=0;f<=10;f++){
        reset_model();fail=f;d=make_device();int r=phy_qcom_mipi_csi2_power_on(&phy);
        if(f){assert(r<0&&!d.irq_enabled&&nw==0);balanced();}
        else {
            assert(!r&&d.irq_enabled&&irq_live);check_start();
            assert(requested_opp==480000000&&requested_timer==400000000);
            assert(!resets&&!versions);unsigned before=nw;
            assert(!phy_qcom_mipi_csi2_power_off(&phy));
            assert(nw==before+38&&!d.irq_enabled);balanced();
        }cases++;
    }
    for(unsigned variant=0;variant<3;variant++){
        reset_model();d=make_device();
        if(variant==0)override_opp=500000000;
        if(variant==1)override_timer=399999999;
        if(variant==2)d.irq=0;
        assert(phy_qcom_mipi_csi2_power_on(&phy)<0);assert(nw==0);balanced();cases++;
    }
    reset_model();d=make_device();d.phy_mode=PHY_MODE_MIPI_DPHY;d.stream_cfg.link_freq=1200000000;
    assert(!phy_qcom_mipi_csi2_power_on(&phy));
    assert(requested_opp==300000000&&requested_timer==300000000&&resets==1&&versions==1);
    assert(!irq_live&&nw==0);assert(!phy_qcom_mipi_csi2_power_off(&phy));balanced();cases++;
    for(unsigned variant=0;variant<13;variant++){
        reset_model();d=make_device();memset(&fw,0,sizeof(fw));
        fw.bus_present=1;fw.bus=1;fw.count=1;
        if(variant==1)fw.clock_present=1;
        if(variant==2)fw.pol_present=1;
        if(variant==3)fw.count=0;
        if(variant==4)fw.count=2;
        if(variant==5)fw.lanes[0]=1;
        if(variant==6){fw.order_present=1;fw.order_count=1;}
        if(variant==7){fw.order_present=1;fw.order_count=1;fw.order=1;}
        if(variant==8){fw.order_present=1;fw.order_count=2;}
        if(variant==9)fw.split=1;
        if(variant==10)fw.missing=1;
        if(variant==11)fw.read_error=1;
        if(variant==12)fw.bus=3;
        int r=phy_qcom_mipi_csi2_parse_routing(&d);
        assert((r==0)==(variant==0||variant==6));assert(fw.refs==0&&nw==0);cases++;
    }
    for(unsigned n=0;n<=5;n++)for(unsigned pol=0;pol<3;pol++){
        d=make_device();memset(&fw,0,sizeof(fw));fw.count=n;
        for(unsigned j=0;j<4;j++)fw.lanes[j]=j+1;
        fw.pol_present=pol>0;fw.pol_count=pol==1?(int)n+1:(int)n;
        if(fw.pol_count>5)fw.pol_count=5;
        struct mipi_csi2phy_device e=d;
        int r=phy_qcom_mipi_csi2_parse_routing(&d),q=phy_qcom_mipi_csi2_parse_routing_old(&e);
        assert(r==q&&!memcmp(&d.stream_cfg,&e.stream_cfg,sizeof(d.stream_cfg)));
        assert(fw.refs==0);cases++;
    }
    printf("{\"cases\":%u,\"admission_mmio_irq_power_routing\":true}\n",cases);return 0;
}
'''
code=pre+enum+'\n'+opts+header+model+table+leaf+actual+oldfunc+main
(T/'actual-functions.c').write_text(code)
result={'scope':'Actual receiver leaf + core functions; Linux PM/clock/IRQ/fwnode services modeled. No hardware, D-PHY timing validator modeled; differential controls compare old/new call behavior.','source_sha256':pins,'compilers':{},'ok':False}
try:
    for cc in ['gcc','clang']:
        log=T/(cc+'.log')
        cmd=[cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-Wno-sign-compare','-fsanitize=address,undefined','-fno-omit-frame-pointer',str(T/'actual-functions.c'),'-o',str(T/cc)]
        with log.open('w') as f:
            p=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT);assert p.returncode==0,(cc,'compile',p.returncode)
            p=subprocess.run([str(T/cc)],stdout=f,stderr=subprocess.STDOUT);assert p.returncode==0,(cc,'run',p.returncode)
        result['compilers'][cc]={'ok':True,'output':log.read_text(),'compiler':subprocess.check_output([cc,'--version'],text=True).splitlines()[0]}
    result['ok']=True
except Exception as e:
    result['error']=repr(e);(T/'exception.log').write_text(traceback.format_exc())
result['finished_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
(T/'result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
