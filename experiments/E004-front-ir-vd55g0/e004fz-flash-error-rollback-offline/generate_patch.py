#!/usr/bin/env python3
"""Generate an UNINSTALLED error-rollback patch after pinned Linux patch 0003."""
from difflib import unified_diff
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=ROOT/"experiments/E004-front-ir-vd55g0/e004fk-native-flash-disable-ordering/build/source/leds-qcom-flash.c"
PRIOR=ROOT/"src/front-ir-vd55g0/illumination/0003-qcom-flash-align-pmic-timer-encoding.patch"
PATCH=ROOT/"src/front-ir-vd55g0/illumination/0004-qcom-flash-best-effort-error-disarm.patch"
BASE_SHA="cd1f98411545cdb4b679bb21c4c29076a88866517488d5b618c31485caa04727"
PRIOR_SHA="430953b2eade6a9ac08a1c2689982b5685fceb61b30222f02a79ce98cec62de9"

def require(test,what):
    if not test:raise ValueError("E004FZ_SOURCE_FAIL_CLOSED "+what)

def base_after_0003():
    require(sha256(BASE.read_bytes()).hexdigest()==BASE_SHA,"E004fk baseline drift")
    require(sha256(PRIOR.read_bytes()).hexdigest()==PRIOR_SHA,"E004fv patch drift")
    with TemporaryDirectory(prefix="sp11-e004fz-source-") as directory:
        root=Path(directory)
        f=root/"drivers/leds/flash/leds-qcom-flash.c"
        f.parent.mkdir(parents=True)
        f.write_bytes(BASE.read_bytes())
        result=subprocess.run(["patch","-s","--batch","-p1","-d",str(root),
                               "-i",str(PRIOR.resolve())],
                              capture_output=True,text=True,timeout=20)
        require(result.returncode==0,"prior uninstalled patch did not apply")
        return f.read_text()

def produce():
    old=base_after_0003()
    start="static int qcom_flash_strobe(struct qcom_flash_led *led, enum led_strobe strobe,\n"
    end="\nstatic int qcom_flash_strobe_set("
    require(old.count(start)==1 and old.count(end)==1,"unique flash callback missing")
    begin=old.index(start);finish=old.index(end,begin)
    previous=old[begin:finish]
    expected_previous='''static int qcom_flash_strobe(struct qcom_flash_led *led, enum led_strobe strobe,
			     bool state)
{
	int rc;

	rc = set_flash_strobe(led, SW_STROBE, false);
	if (rc)
		return rc;

	if (state && (led->flash_timeout_ms < FLASH_TIMER_STEP_MS ||
		      led->max_timeout_ms < FLASH_TIMER_STEP_MS))
		return -EINVAL;

	rc = update_allowed_flash_current(led, &led->flash_current_ma, state);
	if (rc < 0)
		return rc;

	rc = set_flash_current(led, led->flash_current_ma, FLASH_MODE);
	if (rc)
		return rc;

	rc = set_flash_timeout(led, led->flash_timeout_ms);
	if (rc)
		return rc;

	rc = set_flash_module_en(led, state);
	if (rc)
		return rc;

	return set_flash_strobe(led, strobe, state);
}
'''
    require(previous==expected_previous,"expected after-0003 callback changed")
    replacement='''static int qcom_flash_strobe(struct qcom_flash_led *led, enum led_strobe strobe,
			     bool state)
{
	int rc, off_rc;

	rc = set_flash_strobe(led, SW_STROBE, false);
	if (rc)
		goto attempt_disarm;

	if (state && (led->flash_timeout_ms < FLASH_TIMER_STEP_MS ||
		      led->max_timeout_ms < FLASH_TIMER_STEP_MS)) {
		rc = -EINVAL;
		goto attempt_disarm;
	}

	rc = update_allowed_flash_current(led, &led->flash_current_ma, state);
	if (rc < 0)
		goto attempt_disarm;

	rc = set_flash_current(led, led->flash_current_ma, FLASH_MODE);
	if (rc)
		goto attempt_disarm;

	rc = set_flash_timeout(led, led->flash_timeout_ms);
	if (rc)
		goto attempt_disarm;

	rc = set_flash_module_en(led, state);
	if (rc)
		goto attempt_disarm;

	rc = set_flash_strobe(led, strobe, state);
	if (!rc)
		return 0;

attempt_disarm:
	/*
	 * Best-effort software rollback on every error, including failed
	 * initial channel disarm and failed arm after module enable.
	 * A failed SPMI write may leave hardware ON: neither these retries
	 * nor a host reboot constitute an independent electrical cutoff.
	 */
	off_rc = set_flash_strobe(led, SW_STROBE, false);
	if (off_rc)
		dev_err(led->flash.led_cdev.dev,
			"flash rollback: unable to disarm channels (%d)\\n", off_rc);

	off_rc = set_flash_module_en(led, false);
	if (off_rc)
		dev_err(led->flash.led_cdev.dev,
			"flash rollback: unable to disable module (%d)\\n", off_rc);

	return rc;
}
'''
    new=old[:begin]+replacement+old[finish:]
    patch="".join(unified_diff(old.splitlines(keepends=True),
                               new.splitlines(keepends=True),
                               fromfile="a/drivers/leds/flash/leds-qcom-flash.c",
                               tofile="b/drivers/leds/flash/leds-qcom-flash.c",n=0))
    require(1 <= patch.count("@@ -") <= 24,"unexpected patch hunk count")
    return old,new,patch

if __name__=="__main__":
    old,new,patch=produce()
    PATCH.write_text(patch)
    print("E004FZ_SOURCE_PATCH=GENERATED UNINSTALLED=YES")
    print("PATCH_SHA256="+sha256(patch.encode()).hexdigest())
