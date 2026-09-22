#!/usr/bin/env python3
"""Run actual candidate CAMSS clock functions with hardware-free stubs.

Usage: python3 verify-clock-candidate.py COPIED_PATCHED_KERNEL_SOURCE
No device or sensor is opened. Clock stubs do not establish physical sufficiency.
"""
from pathlib import Path
import subprocess
import tempfile
import sys

source = Path(sys.argv[1])
camss = (source / "camss/camss.c").read_text()
vfe = (source / "camss/camss-vfe.c").read_text()
def function(text, signature):
    start = text.index(signature)
    brace = text.index("{", start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end] + "\n"
prefix = r"""
#include <stdint.h>
#include <stdio.h>
#include <errno.h>
typedef uint64_t u64;
typedef uint32_t u32;
typedef uint8_t u8;
#define VFE_LINE_NUM_MAX 4
#define VFE_LINE_RDI0 0
#define VFE_LINE_PIX 3
#define MSM_VFE_PAD_SINK 0
struct device { int unused; };
struct entity { int index; };
struct vfe_line { struct { struct entity entity; } subdev;
              int formats, nformats; struct { int code; } fmt[1]; };
struct camss_clock { void *clk; unsigned nfreqs; unsigned long *freq; };
struct vfe_device { struct { struct device *dev; } *camss;
                    struct { int line_num; } *res;
                    struct vfe_line line[4]; int nclocks; struct camss_clock *clock; };
static u64 sensor_rate;
static int selected_line;
static long selected_rate;

#define V4L2_MBUS_CSI2_CPHY 1
#define V4L2_CID_PIXEL_RATE 2
#define ENOIOCTLCMD 515
#define U64_MAX UINT64_MAX
struct v4l2_mbus_config {
    unsigned int type;
    u64 link_freq;
    struct { struct { unsigned int num_data_lanes; } mipi_csi2; } bus;
};
struct v4l2_ctrl { int unused; };
struct v4l2_subdev { void *ctrl_handler; };
struct media_pad { struct entity *entity; unsigned int index; };
static struct v4l2_subdev sensor;
static struct media_pad sensor_pad;
static struct v4l2_mbus_config bus_config;
static int config_result;
static struct media_pad *camss_find_sensor_pad(struct entity *entity)
{
    if (entity->index != selected_line) return NULL;
    sensor_pad.entity = entity; return &sensor_pad;
}
#define media_entity entity
static struct v4l2_subdev *media_entity_to_v4l2_subdev(struct entity *entity)
{ (void)entity; return &sensor; }
static int get_config(struct v4l2_mbus_config *c)
{ *c=bus_config; return config_result; }
#define v4l2_subdev_call(sd, group, op, index, config) get_config(config)
static struct v4l2_ctrl *v4l2_ctrl_find(void *handler, int id)
{ static struct v4l2_ctrl ctrl; (void)handler; (void)id; return sensor_rate ? &ctrl : NULL; }
static u64 v4l2_ctrl_g_ctrl_int64(struct v4l2_ctrl *ctrl)
{ (void)ctrl; return sensor_rate; }
static u64 div64_u64(u64 a, u64 b) { return a/b; }
static int vfe_match_clock_names(struct vfe_device *v, struct camss_clock *c)
{ (void)v; (void)c; return 1; }
static int vfe_check_clock_levels(struct camss_clock *c)
{ (void)c; return 1; }
static u8 camss_format_get_bpp(int a, int b, int c)
{ (void)a; (void)b; (void)c; return 10; }
static void camss_add_clock_margin(u64 *r) { *r = *r * 105 / 100; }
static long clk_round_rate(void *c, unsigned long r) { (void)c; return r; }
static int clk_set_rate(void *c, long r) { (void)c; selected_rate=r; return 0; }
static unsigned long clk_get_rate(void *c) { (void)c; return selected_rate; }
#define dev_err(dev, ...) ((void)(dev))
"""
suffix = r"""
int main(void)
{
    unsigned long rates[] = {345600000,432000000,594000000,675000000,727000000};
    struct camss_clock clock = { .nfreqs=5, .freq=rates };
    struct device dev = {0};
    struct vfe_device vfe = {0};
    typeof(*vfe.camss) camss = { .dev=&dev };
    typeof(*vfe.res) res = { .line_num=4 };
    vfe.camss=&camss; vfe.res=&res; vfe.nclocks=1; vfe.clock=&clock;
    for (int i=0;i<4;i++) vfe.line[i].subdev.entity.index=i;
    const struct { u64 rate; int line; int result; long clock; } cases[] = {
        {0,3,0,727000000},
        {719898240,3,-EINVAL,-1},
        {719898240,0,0,345600000},
        {548570000,3,0,594000000},
    };
    for (unsigned i=0;i<sizeof(cases)/sizeof(cases[0]);i++) {
        sensor_rate=cases[i].rate; selected_line=cases[i].line; selected_rate=-1;
        int ret=vfe_set_clock_rates(&vfe);
        if (ret!=cases[i].result || selected_rate!=cases[i].clock) return 1;
        printf("case=%u sensor_rate=%llu line=%d result=%d selected=%ld PASS\n",
               i,(unsigned long long)sensor_rate,selected_line,ret,selected_rate);
    }
    sensor_rate=719898240; selected_line=3; selected_rate=727000000;
    if (vfe_check_clock_rates(&vfe) != -EBUSY) return 2;
    sensor_rate=548570000; selected_rate=594000000;
    if (vfe_check_clock_rates(&vfe) != 0) return 3;
    puts("check-clock VT rejection and transport acceptance PASS");

    bus_config.type=V4L2_MBUS_CSI2_CPHY;
    bus_config.link_freq=1200000000;
    bus_config.bus.mipi_csi2.num_data_lanes=1;
    sensor_rate=719898240; selected_line=3;
    if (vfe_set_clock_rates(&vfe) || selected_rate!=594000000) return 4;
    if (vfe_check_clock_rates(&vfe)) return 5;
    u64 rate=0;
    if (camss_get_pixel_clock(&vfe.line[3].subdev.entity,10,&rate) || rate!=548571429) return 6;
    selected_line=0;
    if (vfe_set_clock_rates(&vfe) || selected_rate!=345600000) return 7;
    if (vfe_check_clock_rates(&vfe)) return 8;
    puts("C-PHY RAW10: PIX594MHz/RDI345.6MHz selection and checking PASS");
    struct entity *entity=&vfe.line[0].subdev.entity;
    bus_config.bus.mipi_csi2.num_data_lanes=0;
    if (camss_get_pixel_clock(entity,10,&rate)!=-EINVAL) return 9;
    bus_config.bus.mipi_csi2.num_data_lanes=4;
    if (camss_get_pixel_clock(entity,10,&rate)!=-EINVAL) return 10;
    bus_config.bus.mipi_csi2.num_data_lanes=1;
    if (camss_get_pixel_clock(entity,0,&rate)!=-EINVAL ||
        camss_get_pixel_clock(entity,65,&rate)!=-EINVAL) return 11;
    bus_config.link_freq=U64_MAX;
    if (camss_get_pixel_clock(entity,10,&rate)!=-ERANGE) return 12;
    bus_config.link_freq=1200000000;
    config_result=-EIO;
    if (camss_get_pixel_clock(entity,10,&rate)!=-EIO) return 13;
    config_result=-ENOIOCTLCMD;
    if (camss_get_pixel_clock(entity,10,&rate) || rate!=719898240) return 14;
    config_result=0; bus_config.link_freq=0;
    if (camss_get_pixel_clock(entity,10,&rate) || rate!=719898240) return 15;
    puts("Invalid lanes/bpp/overflow/error and legacy fallback cases PASS");
    return 0;
}
"""
functions = function(camss, "int camss_get_pixel_clock(")
functions += function(vfe, "static int vfe_set_clock_rates(")
functions += function(vfe, "static int vfe_check_clock_rates(")
with tempfile.TemporaryDirectory(prefix="sp11-e004ld-clock-") as t:
    c = Path(t) / "clock.c"
    exe = Path(t) / "clock"
    c.write_text(prefix + functions + suffix)
    subprocess.run(["cc", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
                    "-Wno-sign-compare", str(c), "-o", str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
