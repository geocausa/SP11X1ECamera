#!/usr/bin/env python3
"""Second-stage test-only edits (run after vd-dbg.py): fw_file=<name> loads an external sensor patch
(no version check), extra=0xRRRRVV,... writes 8-bit regs just before START, failed stop resets the sensor."""
import sys
p = sys.argv[1]
s = open(p).read()


def rep(old, new):
    global s
    if s.count(old) != 1:
        sys.exit("edit failed (%d): %r" % (s.count(old), old[:60]))
    s = s.replace(old, new)


rep("""static int oif_override = -1;""", """static char *fw_file;
module_param(fw_file, charp, 0644);
static unsigned int extra[32];
static int n_extra;
module_param_array(extra, uint, &n_extra, 0644);
static int oif_override = -1;""")

rep("""	/* Start streaming */
	vd55g1_write(sensor, REG_STBY, VD55G1_STBY_START_STREAM, &ret);""",
    """	{
		int i;

		for (i = 0; i < n_extra; i++)
			if (extra[i]) cci_write(sensor->regmap, CCI_REG8(extra[i] >> 8),
				  extra[i] & 0xff, &ret);
		if (n_extra)
			dev_info(sensor->dev, "SP11DBG wrote %d extra regs ret=%d\\n",
				 n_extra, ret);
	}
	sp11_dbg_dump(sensor, "prestart");
	/* Start streaming */
	vd55g1_write(sensor, REG_STBY, VD55G1_STBY_START_STREAM, &ret);""")

rep("""	if (ret)
		dev_warn(sensor->dev, "Can't disable stream\\n");
""", """	if (ret) {
		dev_warn(sensor->dev, "Can't disable stream; SP11DBG resetting sensor\\n");
		gpiod_set_value_cansleep(sensor->reset_gpio, 1);
		ret = 0;
	}
""")

rep("""static int vd55g1_patch(struct vd55g1 *sensor)
{
	const struct vd55g1_firmware *fw = sensor->revision->builtin_fw;
	u64 patch;
	int ret = 0;

	if (sensor->revision->needs_patch) {
		vd55g1_write_array(sensor, REG_FWPATCH_START_ADDR,
				   fw->size, fw->data, &ret);""",
    """static int vd55g1_patch(struct vd55g1 *sensor)
{
	const struct vd55g1_firmware *fw = sensor->revision->builtin_fw;
	const struct firmware *ext = NULL;
	u64 patch;
	int ret = 0;

	if (sensor->revision->needs_patch && fw_file && *fw_file) {
		ret = request_firmware(&ext, fw_file, sensor->dev);
		if (ret) {
			dev_err(sensor->dev, "SP11DBG fw %s: %d\\n", fw_file, ret);
			return ret;
		}
		vd55g1_write_array(sensor, REG_FWPATCH_START_ADDR,
				   ext->size, ext->data, &ret);
		dev_info(sensor->dev, "SP11DBG wrote external patch %s (%zu bytes) ret=%d\\n",
			 fw_file, ext->size, ret);
		release_firmware(ext);
		vd55g1_write(sensor, REG_BOOT, VD55G1_BOOT_PATCH_AND_BOOT, &ret);
		vd55g1_poll_reg(sensor, REG_BOOT, 0, &ret);
		vd55g1_read(sensor, REG_FWPATCH_REVISION, &patch, &ret);
		dev_info(sensor->dev, "SP11DBG external patch revision %d.%d ret=%d\\n",
			 (u8)(patch >> 8), (u8)(patch & 0xff), ret);
		if (ret)
			return ret;
	} else if (sensor->revision->needs_patch) {
		vd55g1_write_array(sensor, REG_FWPATCH_START_ADDR,
				   fw->size, fw->data, &ret);""")

rep("""#include <linux/module.h>""", """#include <linux/firmware.h>
#include <linux/module.h>""")

open(p, "w").write(s)
print("ok")
