#!/usr/bin/env python3
"""leds-qcom-flash: release every V4L2 flash device on remove and on probe failure.
The loops index v4l2_flash[leds_count] (one past the last entry, beyond a kcalloc'd array of
leds_count elements) and never reach index 0, so with one LED nothing is released. The flash subdev
stays registered with freed devm memory; the next control access after rmmod is a use-after-free."""
import sys
p = sys.argv[1]
s = open(p).read()
old = """	while (flash_data->v4l2_flash[flash_data->leds_count] && flash_data->leds_count)
		v4l2_flash_release(flash_data->v4l2_flash[flash_data->leds_count--]);
"""
new = """	while (flash_data->leds_count)
		v4l2_flash_release(flash_data->v4l2_flash[--flash_data->leds_count]);
"""
if s.count(old) != 2:
    sys.exit("edit failed (%d)" % s.count(old))
open(p, "w").write(s.replace(old, new))
print("ok")
