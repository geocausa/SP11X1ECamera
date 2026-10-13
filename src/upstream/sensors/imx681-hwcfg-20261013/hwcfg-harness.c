
static void reset(void)
{
 missing=0;bus_value=1;lane_count=1;lane_value=0;order_present=0;order_count=1;order_value=0;
 clock_lane=polarities=noncontinuous=read_error=parse_error=parsed_bad=0;
 freq_count=1;no_freq=ref_puts=frees=parses=reg_error=clk_error=0;
 xclk_rate=19200000;frequency=1203000000;event_count=0;memset(events,0,sizeof(events));
}
static unsigned int cases;
static void check(bool valid,bool parser,int expected)
{
 int r=imx681_check_hwcfg(&sensor);
 assert(r==expected);assert((r==0)==valid);assert(ref_puts==(missing?0:1));
 assert(parses==(parser?1:0));assert(frees==(parser?1:0));assert(event_count==0);cases++;
}
int main(void)
{
 struct device dev={0};sensor.dev=&dev;
 reset();check(true,true,0);
 reset();order_present=1;check(true,true,0);
 reset();missing=1;check(false,false,-ENXIO);
 for(int b=-1;b<=8;b++) {reset();bus_value=b;check(b==1,b==1,b==1?0:-EINVAL);}
 for(int n=-2;n<=9;n++) {reset();lane_count=n;check(n==1,n==1,n==1?0:-EINVAL);}
 for(int l=-1;l<=9;l++) {reset();lane_value=l;check(l==0,l==0,l==0?0:-EINVAL);}
 for(int n=-2;n<=9;n++) {reset();order_present=1;order_count=n;check(n==1,n==1,n==1?0:-EINVAL);}
 for(int o=-1;o<=8;o++) {reset();order_present=1;order_value=o;check(o==0,o==0,o==0?0:-EINVAL);}
 for(int flags=1;flags<8;flags++) {
  reset();clock_lane=flags&1;polarities=flags&2;noncontinuous=flags&4;check(false,false,-EINVAL);
 }
 for(int e=1;e<=3;e++) {reset();order_present=1;read_error=e;check(false,false,-EINVAL);}
 for(int n=0;n<=3;n++) {reset();freq_count=n;check(n==1,true,n==1?0:-EINVAL);}
 const u64 rates[]={0,1200000000,1202999999,1203000000,1203000001,2406000000,UINT64_MAX};
 for(unsigned int i=0;i<ARRAY_SIZE(rates);i++) {
  reset();frequency=rates[i];check(rates[i]==1203000000,true,rates[i]==1203000000?0:-EINVAL);
 }
 reset();no_freq=1;check(false,true,-EINVAL);
 for(int p=1;p<=5;p++) {reset();parsed_bad=p;check(false,true,-EINVAL);}
 const int errors[]={-EIO,-ENOMEM,-ENXIO};
 for(unsigned int i=0;i<ARRAY_SIZE(errors);i++) {reset();parse_error=errors[i];check(false,true,errors[i]);}
 const unsigned long clocks[]={0,19200000,19200001,19199999,24000000,~0UL};
 for(unsigned int i=0;i<ARRAY_SIZE(clocks);i++) {
  reset();xclk_rate=clocks[i];check(clocks[i]==19200000,true,clocks[i]==19200000?0:-EINVAL);
  /* A rate changed after probe still cannot reach a regulator enable. */
  reset();xclk_rate=clocks[i];int ret=imx681_power_on(&dev);
  assert(ret==(clocks[i]==19200000?0:-EINVAL));
  assert(!strcmp(events,clocks[i]==19200000?"RCGD":""));cases++;
 }
 for(unsigned int a=0;a<ARRAY_SIZE(errors);a++) {
  reset();reg_error=errors[a];assert(imx681_power_on(&dev)==errors[a]);assert(!strcmp(events,"R"));cases++;
  reset();clk_error=errors[a];assert(imx681_power_on(&dev)==errors[a]);assert(!strcmp(events,"RCr"));cases++;
 }
 printf("{\"cases\":%u,\"ok\":true}\n",cases);return 0;
}
