
#include <assert.h>
#include <errno.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdarg.h>
typedef uint32_t u32;
typedef uint64_t u64;
#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))
#define V4L2_FWNODE_BUS_TYPE_CSI2_CPHY 1
#define V4L2_MBUS_CSI2_CPHY 7
#define V4L2_MBUS_CSI2_CPHY_LINE_ORDER_ABC 0
#define IMX681_LINK_FREQ 1203000000
#define IMX681_XCLK_FREQ 19200000
#define IMX681_XCLR_MIN_DELAY_US 6200
#define IMX681_XCLR_DELAY_RANGE_US 1000
struct fwnode_handle { int unused; };
struct device { int unused; };
struct v4l2_subdev { int unused; };
struct imx681 { struct device *dev; void *xclk,*reset_gpio; int supplies[2]; };
struct csi2 { unsigned int num_data_lanes,data_lanes[8],line_orders[8],flags; };
struct v4l2_fwnode_endpoint { int bus_type; struct {struct csi2 mipi_csi2;} bus;
 u64 *link_frequencies; unsigned int nr_of_link_frequencies; };
static const char *const imx681_supply_name[]={"dovdd","avdd"};
static struct imx681 sensor;
static struct fwnode_handle endpoint;
static struct v4l2_subdev subdev;
static int missing,bus_value,lane_count,lane_value,order_present,order_count,order_value;
static int clock_lane,polarities,noncontinuous,read_error,parse_error,parsed_bad;
static int freq_count,no_freq,ref_puts,frees,parses,reg_error,clk_error;
static unsigned long xclk_rate;
static u64 frequency;
static char events[32]; static unsigned int event_count;
static void event(char c) { assert(event_count<sizeof(events)-1);events[event_count++]=c; }
static struct fwnode_handle *dev_fwnode(struct device *dev) {(void)dev;return &endpoint;}
static struct fwnode_handle *fwnode_graph_get_next_endpoint(struct fwnode_handle *f,void *p)
{(void)f;assert(!p);return missing?NULL:&endpoint;}
static void fwnode_handle_put(struct fwnode_handle *f) {assert(f==&endpoint);ref_puts++;}
static int fwnode_property_read_u32(struct fwnode_handle *f,const char *name,u32 *v)
{
 assert(f==&endpoint);
 int which=!strcmp(name,"bus-type")?1:!strcmp(name,"data-lanes")?2:3;
 if(read_error==which)return -EIO;
 *v=(u32)(which==1?bus_value:which==2?lane_value:order_value);return 0;
}
static int fwnode_property_count_u32(struct fwnode_handle *f,const char *name)
{assert(f==&endpoint);return !strcmp(name,"data-lanes")?lane_count:order_count;}
static bool fwnode_property_present(struct fwnode_handle *f,const char *name)
{
 assert(f==&endpoint);
 if(!strcmp(name,"line-orders"))return order_present;
 if(!strcmp(name,"clock-lanes"))return clock_lane;
 if(!strcmp(name,"lane-polarities"))return polarities;
 assert(!strcmp(name,"clock-noncontinuous"));return noncontinuous;
}
static int v4l2_fwnode_endpoint_alloc_parse(struct fwnode_handle *f,struct v4l2_fwnode_endpoint *b)
{
 assert(f==&endpoint);assert(b->bus_type==V4L2_MBUS_CSI2_CPHY);parses++;
 b->bus.mipi_csi2.num_data_lanes=1;b->bus.mipi_csi2.data_lanes[0]=0;
 b->bus.mipi_csi2.line_orders[0]=0;b->link_frequencies=no_freq?NULL:&frequency;
 b->nr_of_link_frequencies=(unsigned int)freq_count;
 switch(parsed_bad) {
 case 1:b->bus_type=99;break;
 case 2:b->bus.mipi_csi2.num_data_lanes=2;break;
 case 3:b->bus.mipi_csi2.data_lanes[0]=1;break;
 case 4:b->bus.mipi_csi2.line_orders[0]=1;break;
 case 5:b->bus.mipi_csi2.flags=1;break;
 }
 return parse_error;
}
static void v4l2_fwnode_endpoint_free(struct v4l2_fwnode_endpoint *b)
{(void)b;frees++;}
static int dev_err_probe(struct device *dev,int err,const char *fmt,...)
{(void)dev;(void)fmt;return err;}
static unsigned long clk_get_rate(void *clk) {(void)clk;return xclk_rate;}
static void *dev_get_drvdata(struct device *dev) {(void)dev;return &subdev;}
static struct imx681 *to_imx681(struct v4l2_subdev *sd) {assert(sd==&subdev);return &sensor;}
static int regulator_bulk_enable(unsigned int n,int *supplies)
{assert(n==2&&supplies==sensor.supplies);assert(!strcmp(imx681_supply_name[0],"dovdd")&&!strcmp(imx681_supply_name[1],"avdd"));event('R');return reg_error;}
static int regulator_bulk_disable(unsigned int n,int *supplies)
{assert(n==2&&supplies==sensor.supplies);event('r');return 0;}
static int clk_prepare_enable(void *clk) {(void)clk;event('C');return clk_error;}
static void gpiod_set_value_cansleep(void *gpio,int v) {(void)gpio;assert(v==0);event('G');}
static void usleep_range(unsigned int a,unsigned int b) {assert(a==6200&&b==7200);event('D');}
#define dev_err(...) ((void)0)
