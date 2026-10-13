#include <assert.h>
#include <errno.h>
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
typedef uint8_t u8;
typedef uint32_t u32;
typedef uint64_t u64;
#define BIT(x) (1U << (x))
#define GENMASK(h,l) ((~0U << (l)) & (~0U >> (31-(h))))
#define FIELD_GET(mask,v) (((v) & (mask)) >> __builtin_ctz(mask))
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define container_of(p,t,m) ((t *)((char *)(p)-offsetof(t,m)))
#define min_t(t,a,b) ((t)(a)<(t)(b)?(t)(a):(t)(b))
#define MEDIA_BUS_FMT_SRGGB10_1X10 0
#define dev_err(d,...) ((void)(d))
#define dev_dbg(d,...) ((void)(d))
#define regmap_get_device(m) (m)
#define V4L2_CID_VBLANK 1
#define V4L2_CID_EXPOSURE 2
#define V4L2_CID_ANALOGUE_GAIN 3
#define V4L2_CID_DIGITAL_GAIN 4
struct cci_reg_sequence { u32 reg; u64 val; };
struct regmap { u8 bytes[65536]; };
struct v4l2_ctrl_handler { int unused; };
struct v4l2_ctrl { int id,val,minimum; struct v4l2_ctrl_handler *handler; };
struct imx681 {
 void *dev;
 struct regmap *regmap;
 struct v4l2_ctrl_handler ctrl_handler;
 struct v4l2_ctrl *expo_ctrl,*vblank_ctrl;
};
static int pm_result=1,range_result,pm_gets,pm_puts,attempts,fail_n,range_max;
static int release_attempts,stream_attempts;
static unsigned int last_reg,last_len;
static u8 last_bytes[8];
static struct imx681 *setup_sensor;
static int __v4l2_ctrl_modify_range(struct v4l2_ctrl *c,int min,int max,int step,int def)
{ (void)c;(void)min;(void)step;(void)def;range_max=max;return range_result; }
static int pm_runtime_get_if_in_use(void *d) { (void)d;pm_gets++;return pm_result; }
static int pm_runtime_resume_and_get(void *d) { (void)d;pm_gets++;return pm_result<0?pm_result:0; }
static void pm_runtime_put_autosuspend(void *d) { (void)d;pm_puts++; }
static void pm_runtime_put(void *d) { (void)d;pm_puts++; }
static int regmap_bulk_write(struct regmap *m,unsigned int reg,const void *data,unsigned int len)
{
 const u8 *b=data;
 assert(reg+len<=sizeof(m->bytes));assert(len<=sizeof(last_bytes));
 attempts++;last_reg=reg;last_len=len;memcpy(last_bytes,b,len);
 if(reg==0x0104 && len==1 && b[0]==0)release_attempts++;
 if(reg==0x0100 && len==1 && b[0]==1)stream_attempts++;
 if(attempts==fail_n)return -EIO;
 memcpy(m->bytes+reg,b,len);return 0;
}
static void put_bytes(u64 v,void *p,unsigned int n,bool le)
{ u8 *b=p;for(unsigned int i=0;i<n;i++)b[le?i:n-1-i]=(u8)(v>>(8*i)); }
#define put_unaligned_le16(v,p) put_bytes(v,p,2,true)
#define put_unaligned_be16(v,p) put_bytes(v,p,2,false)
#define put_unaligned_le24(v,p) put_bytes(v,p,3,true)
#define put_unaligned_be24(v,p) put_bytes(v,p,3,false)
#define put_unaligned_le32(v,p) put_bytes(v,p,4,true)
#define put_unaligned_be32(v,p) put_bytes(v,p,4,false)
#define put_unaligned_le64(v,p) put_bytes(v,p,8,true)
#define put_unaligned_be64(v,p) put_bytes(v,p,8,false)
