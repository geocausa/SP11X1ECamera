#!/usr/bin/env python3
"""Test-only: mirror Windows' PMIC sequence for the 4-channel flash block - clear bit 0 of base+0x67 (0xee67)
after arming channels for hardware strobe, and set it back when disarming. Exact-match edits on the patched
leds-qcom-flash.c."""
import sys
p = sys.argv[1]
s = open(p).read()

def rep(old, new):
    global s
    if s.count(old) != 1:
        sys.exit("edit failed (%d): %r" % (s.count(old), old[:60]))
    s = s.replace(old, new)

rep("""	u8			torch_clamp;
};""", """	u8			torch_clamp;
	struct regmap		*regmap;
	u32			reg_base;
};

#define FLASH_4CH_HW_STROBE_COMMON_REG	0x67
static bool hw_strobe_common_clear = true;
module_param(hw_strobe_common_clear, bool, 0644);

static void qcom_flash_hw_common(struct qcom_flash_data *fd, bool hw_armed)
{
	if (fd->hw_type != QCOM_MVFLASH_4CH || !hw_strobe_common_clear || !fd->regmap)
		return;
	regmap_update_bits(fd->regmap, fd->reg_base + FLASH_4CH_HW_STROBE_COMMON_REG,
			   BIT(0), hw_armed ? 0 : BIT(0));
}""")

rep("""	rc = set_flash_strobe(led, strobe, state);
	if (!rc)
		return 0;
""", """	rc = set_flash_strobe(led, strobe, state);
	if (!rc) {
		qcom_flash_hw_common(led->flash_data, strobe == HW_STROBE && state);
		return 0;
	}
""")

rep("""	off_rc = set_flash_strobe(led, SW_STROBE, false);
	if (off_rc)
		dev_err(led->flash.led_cdev.dev,
			"flash rollback: unable to disarm channels (%d)\\n", off_rc);
""", """	off_rc = set_flash_strobe(led, SW_STROBE, false);
	if (off_rc)
		dev_err(led->flash.led_cdev.dev,
			"flash rollback: unable to disarm channels (%d)\\n", off_rc);
	qcom_flash_hw_common(led->flash_data, false);
""")

rep("""	rc = devm_regmap_field_bulk_alloc(dev, regmap, flash_data->r_fields, regs, REG_MAX_COUNT);""",
    """	flash_data->regmap = regmap;
	flash_data->reg_base = reg_base;
	rc = devm_regmap_field_bulk_alloc(dev, regmap, flash_data->r_fields, regs, REG_MAX_COUNT);""")
open(p, "w").write(s)
print("ok")
