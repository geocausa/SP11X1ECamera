// SPDX-License-Identifier: GPL-2.0-only
static struct imx681 sensor;
static struct i2c_client client;
static struct clk clock_model;
static struct gpio_desc reset_model;
static struct regulator rails[2];
static struct v4l2_ctrl vblank, expo;
static int cases;
static void reset_fixture(void)
{
 memset(&sensor, 0, sizeof(sensor)); memset(&client, 0, sizeof(client));
 clock_model = (struct clk){ .rate = 19200000 };
 reset_model = (struct gpio_desc){ .asserted = 1 };
 rails[0] = (struct regulator){ .id = 0 }; rails[1] = (struct regulator){ .id = 1 };
 client.dev.data = &sensor.sd; sensor.dev = &client.dev;
 sensor.xclk = &clock_model; sensor.reset_gpio = &reset_model;
 sensor.supplies[0].consumer = &rails[0]; sensor.supplies[1].consumer = &rails[1];
 vblank = (struct v4l2_ctrl){ .handler = &sensor.ctrl_handler, .id = V4L2_CID_VBLANK, .val = 914 };
 expo = (struct v4l2_ctrl){ .handler = &sensor.ctrl_handler, .id = V4L2_CID_EXPOSURE, .val = 1600, .minimum = 8 };
 sensor.vblank_ctrl = &vblank; sensor.expo_ctrl = &expo;
 fail_clock = 0; memset(fail_enable, 0, sizeof(fail_enable)); memset(fail_disable, 0, sizeof(fail_disable));
 pm_refs = 0; pm_get_result = 1; pm_resume_result = 0; cci_calls = 0; cci_error = 0;
 suspended_marks = disabled_pm = 0; clear_trace();
}
static void expect_trace(const char *s) { assert(strcmp(trace, s) == 0); }
static void expect_off(void)
{
 assert(!sensor.clock_on && !sensor.dovdd_on && !sensor.avdd_on && !sensor.power_fault);
 assert(clock_model.refs == 0 && rails[0].refs == 0 && rails[1].refs == 0 && reset_model.asserted);
}
static void healthy(void)
{
 assert(imx681_power_on(sensor.dev) == 0 && imx681_power_ready(&sensor));
 expect_trace("reset-low;clock+;io+;analog+;delay-1ms;reset-high;delay-10ms;");
 assert(clock_model.refs == 1 && rails[0].refs == 1 && rails[1].refs == 1);
}
static void check_blocked_io(void)
{
 cci_calls = pm_refs = 0;
 assert(imx681_identify(&sensor) == -EIO && cci_calls == 0);
 assert(imx681_s_ctrl(&expo) == -EIO && cci_calls == 0 && pm_refs == 0);
 assert(imx681_start_streaming(&sensor) == -EIO && cci_calls == 0 && pm_refs == 0);
 assert(imx681_stop_streaming(&sensor) == -EIO && cci_calls == 0 && pm_refs == 0);
}
int main(void)
{
 assert(strcmp(imx681_supply_name[0], "dovdd") == 0 && strcmp(imx681_supply_name[1], "avdd") == 0);
 reset_fixture(); healthy(); cases++;
 clear_trace(); assert(imx681_power_on(sensor.dev) == -EIO); expect_trace(""); cases++;
 assert(imx681_identify(&sensor) == 0); assert(imx681_s_ctrl(&vblank) == 0 && pm_refs == 0); cases++;
 assert(imx681_start_streaming(&sensor) == 0 && pm_refs == 1);
 assert(imx681_stop_streaming(&sensor) == 0 && pm_refs == 0); cases++;
 clear_trace(); assert(imx681_power_off(sensor.dev) == 0);
 expect_trace("reset-low;delay-1ms;clock-;analog-;io-;"); expect_off(); cases++;
 clear_trace(); assert(imx681_power_off(sensor.dev) == 0);
 expect_trace("reset-low;delay-1ms;"); expect_off(); cases++;

 reset_fixture(); clock_model.rate = 24000000;
 assert(imx681_power_on(sensor.dev) == -EINVAL); expect_trace(""); expect_off(); cases++;
 reset_fixture(); fail_clock = -ETIMEDOUT;
 assert(imx681_power_on(sensor.dev) == -ETIMEDOUT);
 expect_trace("reset-low;clock+;"); expect_off(); cases++;
 reset_fixture(); fail_enable[0] = -ETIMEDOUT;
 assert(imx681_power_on(sensor.dev) == -ETIMEDOUT);
 expect_trace("reset-low;clock+;io+;reset-low;delay-1ms;clock-;"); expect_off(); cases++;
 reset_fixture(); fail_enable[1] = -ETIMEDOUT;
 assert(imx681_power_on(sensor.dev) == -ETIMEDOUT);
 expect_trace("reset-low;clock+;io+;analog+;reset-low;delay-1ms;clock-;io-;"); expect_off(); cases++;

 reset_fixture(); healthy(); clear_trace(); fail_disable[1] = -ETIMEDOUT;
 assert(imx681_power_off(sensor.dev) == -ETIMEDOUT);
 expect_trace("reset-low;delay-1ms;clock-;analog-;");
 assert(!sensor.clock_on && sensor.avdd_on && sensor.dovdd_on && sensor.power_fault);
 assert(clock_model.refs == 0 && rails[0].refs == 1 && rails[1].refs == 1 && reset_model.asserted);
 clear_trace(); assert(imx681_power_on(sensor.dev) == -EIO); expect_trace(""); check_blocked_io(); cases++;
 clear_trace(); fail_disable[1] = 0; assert(imx681_power_off(sensor.dev) == 0);
 expect_trace("reset-low;delay-1ms;analog-;io-;"); expect_off(); cases++;

 reset_fixture(); healthy(); clear_trace(); fail_disable[0] = -EREMOTEIO;
 assert(imx681_power_off(sensor.dev) == -EREMOTEIO);
 expect_trace("reset-low;delay-1ms;clock-;analog-;io-;");
 assert(!sensor.clock_on && !sensor.avdd_on && sensor.dovdd_on && sensor.power_fault);
 assert(rails[0].refs == 1 && rails[1].refs == 0); check_blocked_io(); cases++;
 clear_trace(); fail_disable[0] = 0; assert(imx681_power_off(sensor.dev) == 0);
 expect_trace("reset-low;delay-1ms;io-;"); expect_off(); cases++;
 reset_fixture(); fail_enable[1] = -ETIMEDOUT; fail_disable[0] = -EREMOTEIO;
 assert(imx681_power_on(sensor.dev) == -ETIMEDOUT);
 assert(sensor.dovdd_on && sensor.power_fault && rails[0].refs == 1); check_blocked_io(); cases++;
 fail_disable[0] = 0; assert(imx681_power_off(sensor.dev) == 0); expect_off(); cases++;

 for (int bits = 0; bits < 16; bits++) {
  if (bits == 7) continue;
  reset_fixture(); sensor.clock_on = bits & 1; sensor.dovdd_on = bits & 2;
  sensor.avdd_on = bits & 4; sensor.power_fault = bits & 8;
  check_blocked_io(); cases++;
 }
 reset_fixture();
 for (int cycle = 0; cycle < 100; cycle++) {
  clear_trace(); healthy(); assert(imx681_power_off(sensor.dev) == 0); expect_off(); cases++;
 }
 reset_fixture(); healthy(); cci_error = -EREMOTEIO;
 assert(imx681_identify(&sensor) == -EREMOTEIO);
 assert(imx681_s_ctrl(&expo) == -EREMOTEIO && pm_refs == 0);
 assert(imx681_start_streaming(&sensor) == -EREMOTEIO && pm_refs == 0); cases++;
 cci_error = 0; assert(imx681_start_streaming(&sensor) == 0 && pm_refs == 1);
 cci_error = -EREMOTEIO; assert(imx681_stop_streaming(&sensor) == -EREMOTEIO && pm_refs == 0); cases++;
 reset_fixture(); pm_get_result = 0;
 assert(imx681_s_ctrl(&expo) == 0 && cci_calls == 0 && pm_refs == 0); cases++;
 pm_get_result = -EIO; assert(imx681_s_ctrl(&expo) == -EIO && cci_calls == 0 && pm_refs == 0); cases++;
 pm_resume_result = -EIO;
 assert(imx681_start_streaming(&sensor) == -EIO && cci_calls == 0 && pm_refs == 0); cases++;
 reset_fixture(); healthy(); clear_trace(); imx681_remove(&client);
 assert(disabled_pm == 1 && suspended_marks == 1); expect_off(); cases++;
 reset_fixture(); healthy(); fail_disable[1] = -EREMOTEIO; imx681_remove(&client);
 assert(disabled_pm == 1 && suspended_marks == 0 && sensor.power_fault && rails[0].refs == 1); cases++;
 reset_fixture(); healthy(); fail_disable[1] = -EREMOTEIO;
 assert(probe_error_cleanup(sensor.dev, -ENODEV) == -ENODEV && sensor.power_fault); cases++;
 printf("PASS actual-body power/CCI/PM/error cases=%d\n", cases);
 return 0;
}
