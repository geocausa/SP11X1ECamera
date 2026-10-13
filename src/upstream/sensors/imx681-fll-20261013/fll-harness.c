static u32 frame_length(const struct regmap *m)
{ return ((u32)m->bytes[0x033d]<<16)|((u32)m->bytes[0x033e]<<8)|m->bytes[0x033f]; }
static void reset_case(struct regmap *m)
{
 memset(m,0,sizeof(*m));m->bytes[0x033c]=m->bytes[0x0340]=0xa5;
 pm_result=1;range_result=pm_gets=pm_puts=attempts=fail_n=range_max=0;
 release_attempts=stream_attempts=0;last_reg=last_len=0;
}
int main(void)
{
 struct regmap map;
 struct v4l2_ctrl exposure={.id=V4L2_CID_EXPOSURE,.val=IMX681_EXPOSURE_DEF,.minimum=8};
 struct v4l2_ctrl blank={.id=V4L2_CID_VBLANK,.val=IMX681_FRAME_LENGTH_DEF-IMX681_HEIGHT};
 struct imx681 sensor={.regmap=&map,.expo_ctrl=&exposure,.vblank_ctrl=&blank};
 exposure.handler=blank.handler=&sensor.ctrl_handler;setup_sensor=&sensor;
 unsigned int cases=0;
 assert(CCI_REG_ADDR(IMX681_REG_FRAME_LENGTH)==0x033d);
 assert(CCI_REG_WIDTH_BYTES(IMX681_REG_FRAME_LENGTH)==3);
 assert(IMX681_FRAME_LENGTH_DEF==3554 && IMX681_FRAME_LENGTH_MAX==65535);
 reset_case(&map);
 assert(cci_multi_reg_write(&map,imx681_mode_3840x2640,ARRAY_SIZE(imx681_mode_3840x2640),NULL)==0);
 assert(frame_length(&map)==3554);
 blank.val=7108-IMX681_HEIGHT;
 assert(baseline_s_ctrl(&blank)==0);
 assert(frame_length(&map)==3554); /* Old control writes another address. */
 cases++;
 const u32 frames[]={2688,3554,7108,7116,65535};
 for(unsigned int i=0;i<ARRAY_SIZE(frames);i++) {
  reset_case(&map);blank.val=(int)frames[i]-IMX681_HEIGHT;
  assert(imx681_s_ctrl(&blank)==0);
  assert(frame_length(&map)==frames[i]);
  assert(map.bytes[0x033c]==0xa5 && map.bytes[0x0340]==0xa5);
  assert(range_max==(int)frames[i]-IMX681_EXPOSURE_MARGIN);
  assert(pm_gets==1 && pm_puts==1 && attempts==3 && release_attempts==1);
  cases++;
 }
 /* All values within the retained public 16-bit bound: byte order/carry. */
 for(u32 n=2688;n<=IMX681_FRAME_LENGTH_MAX;n++) {
  reset_case(&map);blank.val=(int)n-IMX681_HEIGHT;
  assert(imx681_s_ctrl(&blank)==0 && frame_length(&map)==n);
  assert(map.bytes[0x033c]==0xa5 && map.bytes[0x0340]==0xa5);
  cases++;
 }
 const int pm[]={-EAGAIN,0,1,2};
 for(int id=1;id<=4;id++)for(unsigned int p=0;p<ARRAY_SIZE(pm);p++)
 for(int range=0;range<2;range++)for(int failure=0;failure<=3;failure++) {
  struct v4l2_ctrl ctrl={.id=id,.val=id==1?914:1600,.handler=&sensor.ctrl_handler};
  reset_case(&map);pm_result=pm[p];range_result=range?-EINVAL:0;fail_n=failure;
  int ret=imx681_s_ctrl(&ctrl);
  if(id==1 && range)assert(ret==-EINVAL && pm_gets==0 && pm_puts==0 && attempts==0);
  else if(pm[p]<=0)assert(ret==pm[p] && pm_gets==1 && pm_puts==0 && attempts==0);
  else assert(ret==(failure?-EIO:0) && pm_gets==1 && pm_puts==1 && release_attempts==1);
  cases++;
 }
 blank.val=IMX681_FRAME_LENGTH_DEF-IMX681_HEIGHT;
 reset_case(&map);assert(imx681_start_streaming(&sensor)==0);
 assert(frame_length(&map)==3554 && map.bytes[0x0100]==1 && map.bytes[0x0340]==0xa5);
 assert(pm_gets==5 && pm_puts==4); /* stream reference plus four default controls */
 int total_writes=attempts;cases++;
 for(int n=1;n<=total_writes;n++) {
  reset_case(&map);fail_n=n;
  assert(imx681_start_streaming(&sensor)==-EIO);
  assert(map.bytes[0x0100]!=1 && pm_gets==pm_puts);
  cases++;
 }
 reset_case(&map);pm_result=-EAGAIN;
 assert(imx681_start_streaming(&sensor)==-EAGAIN && attempts==0 && pm_puts==0);cases++;
 printf("{\"cases\":%u,\"baseline_counterexamples\":1,\"startup_writes\":%d}\n",cases,total_writes);
 return 0;
}
