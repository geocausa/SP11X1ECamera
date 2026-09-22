#!/usr/bin/env python3
"""Compile the actual accepted VFE clock selector with hardware-free stubs."""
from pathlib import Path
import subprocess
import tempfile

root = Path(__file__).resolve().parents[3]
source = (root / "src/front-imx681/kernel/camss/camss-vfe.c").read_text()
start = source.index("static int vfe_set_clock_rates(")
end = source.index("\n/*", start)
selector = source[start:end]
start = source.index("static int vfe_check_clock_rates(")
selector += source[start:source.index("\n/*", start)]
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
static int camss_get_pixel_clock(struct entity *e, u64 *r)
{
    if (e->index != selected_line || !sensor_rate) return -EINVAL;
    *r = sensor_rate;
    return 0;
}
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
    return 0;
}
"""
with tempfile.TemporaryDirectory(prefix="sp11-e004lc-clock-") as t:
    c = Path(t) / "clock.c"
    exe = Path(t) / "clock"
    c.write_text(prefix + selector + suffix)
    subprocess.run(["cc", "-std=gnu11", "-Wall", "-Wextra", "-Werror",
                    "-Wno-sign-compare", str(c), "-o", str(exe)], check=True)
    subprocess.run([str(exe)], check=True)
