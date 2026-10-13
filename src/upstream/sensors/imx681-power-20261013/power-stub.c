// SPDX-License-Identifier: GPL-2.0-only
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stddef.h>
#include <errno.h>
#include <stdio.h>
#include <string.h>
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
#define container_of(p, t, m) ((t *)((char *)(p) - offsetof(t, m)))
#define min_t(t, a, b) ((t)(a) < (t)(b) ? (t)(a) : (t)(b))
#define CCI_REG8(a) (a)
#define CCI_REG16(a) (a)
#define CCI_REG24(a) (a)
#define V4L2_CID_VBLANK 1
#define V4L2_CID_EXPOSURE 2
#define V4L2_CID_ANALOGUE_GAIN 3
#define V4L2_CID_DIGITAL_GAIN 4
#define dev_err(d, ...) ((void)(d))
#define dev_info(d, ...) ((void)(d))
#define dev_dbg(d, ...) ((void)(d))
typedef unsigned long long u64;
typedef int64_t s64;
struct device { void *data; };
struct regmap { int unused; };
struct clk { int refs; unsigned long rate; };
struct gpio_desc { int asserted; };
struct regulator { int id, refs; };
struct regulator_bulk_data { const char *supply; struct regulator *consumer; };
struct v4l2_subdev { int entity; };
struct media_pad { int unused; };
struct v4l2_ctrl_handler { int unused; };
struct v4l2_ctrl { struct v4l2_ctrl_handler *handler; int id, val, minimum; };
struct i2c_client { struct device dev; };
static char trace[8192];
static size_t trace_len;
static int fail_clock, fail_enable[2], fail_disable[2], pm_refs;
static int pm_get_result, pm_resume_result, cci_calls, cci_error;
static int suspended_marks, disabled_pm;
static int imx681_global_init_table[1], imx681_mode_3840x2640[1];
static void event(const char *s)
{
 size_t n = strlen(s);
 assert(trace_len + n + 1 < sizeof(trace));
 memcpy(trace + trace_len, s, n + 1); trace_len += n;
}
static void clear_trace(void) { trace_len = 0; trace[0] = 0; }
static void *dev_get_drvdata(struct device *d) { return d->data; }
static void *i2c_get_clientdata(struct i2c_client *c) { return c->dev.data; }
static unsigned long clk_get_rate(struct clk *c) { return c->rate; }
static int clk_prepare_enable(struct clk *c)
{
 event("clock+;"); if (fail_clock) return fail_clock; c->refs++; return 0;
}
static void clk_disable_unprepare(struct clk *c)
{
 event("clock-;"); assert(c->refs > 0); c->refs--;
}
static void gpiod_set_value_cansleep(struct gpio_desc *g, int v)
{
 event(v ? "reset-low;" : "reset-high;"); g->asserted = v;
}
static void usleep_range(unsigned int a, unsigned int b)
{
 if (a == 1000 && b == 1500) event("delay-1ms;");
 else if (a == 10000 && b == 12000) event("delay-10ms;");
 else assert(!"delay differs from retained sequence");
}
static int regulator_enable(struct regulator *r)
{
 event(r->id ? "analog+;" : "io+;");
 if (fail_enable[r->id]) return fail_enable[r->id];
 r->refs++; return 0;
}
static int regulator_disable(struct regulator *r)
{
 event(r->id ? "analog-;" : "io-;"); assert(r->refs > 0);
 if (fail_disable[r->id]) return fail_disable[r->id];
 r->refs--; return 0;
}
static int pm_runtime_get_if_in_use(struct device *d)
{
 (void)d; if (pm_get_result > 0) pm_refs++; return pm_get_result;
}
static int pm_runtime_resume_and_get(struct device *d)
{
 (void)d; if (pm_resume_result >= 0) pm_refs++; return pm_resume_result;
}
static void pm_runtime_put(struct device *d)
{
 (void)d; assert(pm_refs > 0); pm_refs--;
}
static void pm_runtime_put_autosuspend(struct device *d) { pm_runtime_put(d); }
static int cci_read(struct regmap *r, int reg, u64 *v, int *err)
{
 (void)r; (void)reg; (void)err; cci_calls++; *v = 0x0681; return cci_error;
}
static int cci_write(struct regmap *r, int reg, int v, int *err)
{
 (void)r; (void)reg; (void)v;
 if (err && *err) return *err;
 cci_calls++; if (err) *err = cci_error; return cci_error;
}
static int cci_multi_reg_write(struct regmap *r, const int *t, size_t n, int *e)
{
 (void)t; (void)n; return cci_write(r, 0, 0, e);
}
static int __v4l2_ctrl_modify_range(struct v4l2_ctrl *c, int a, unsigned b, int step, int def)
{
 (void)c; (void)a; (void)b; (void)step; (void)def; return 0;
}
static int __v4l2_ctrl_handler_setup(struct v4l2_ctrl_handler *h) { (void)h; return 0; }
static void v4l2_async_unregister_subdev(struct v4l2_subdev *s) { (void)s; }
static void v4l2_subdev_cleanup(struct v4l2_subdev *s) { (void)s; }
static void media_entity_cleanup(int *e) { (void)e; }
static void v4l2_ctrl_handler_free(struct v4l2_ctrl_handler *h) { (void)h; }
static void pm_runtime_disable(struct device *d) { (void)d; disabled_pm++; }
static void pm_runtime_set_suspended(struct device *d) { (void)d; suspended_marks++; }
