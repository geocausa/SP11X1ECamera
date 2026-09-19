#!/usr/bin/env python3
"""Compile and fault-inject the ACTUAL uninstalled patched flash dispatcher."""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import re
import subprocess

from generate_patch import PATCH, produce, require

HERE=Path(__file__).resolve().parent

def run(args,timeout=45):
    result=subprocess.run([str(a) for a in args],capture_output=True,
                          text=True,timeout=timeout,check=False)
    require(result.returncode==0,
            "offline test command failed "+str(args[0])+" "+result.stderr[-2500:]+result.stdout[-400:])
    return result

def main():
    original,expected,patch=produce()
    require(PATCH.is_file() and PATCH.read_text()==patch,"generated patch content drift")
    with TemporaryDirectory(prefix="sp11-e004fz-no-hardware-") as d:
        temp=Path(d)
        target=temp/"drivers/leds/flash/leds-qcom-flash.c"
        target.parent.mkdir(parents=True)
        target.write_text(original)
        run(["patch","-s","--batch","-p1","-d",temp,"-i",PATCH.resolve()],timeout=20)
        require(target.read_text()==expected,"patch does not produce expected source")
        first=expected.index("static int qcom_flash_strobe(struct qcom_flash_led *led,")
        last=expected.index("\nstatic int qcom_flash_strobe_set(",first)
        function=expected[first:last]
        prelude=r'''
#include <errno.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
enum led_strobe { SW_STROBE, HW_STROBE };
enum led_mode { FLASH_MODE, TORCH_MODE };
#define FLASH_TIMER_STEP_MS 10
struct qcom_flash_led {
    struct {struct {void *dev;} led_cdev;} flash;
    unsigned int flash_timeout_ms, max_timeout_ms, flash_current_ma;
};
static char trace[64];
static int count, fail_step, cleanup_off_error, cleanup_module_error, logs;
static int seen_initial, cleanup_started, module_on, channels_on;
static void stage(char letter) {
    if ((size_t)count+1 >= sizeof(trace)) abort();
    trace[count++]=letter;
    trace[count]=0;
}
static int error_at_this_step(void) { return count==fail_step; }
static int set_flash_strobe(struct qcom_flash_led *led, enum led_strobe strobe, bool state) {
    (void)led;(void)strobe;
    if (!state && !seen_initial) {seen_initial=1;stage('D');}
    else if (state) stage('A');
    else {stage('d');if (fail_step && trace[count-2]=='D' && count==2) cleanup_started=1;}
    if (!state && trace[count-1]=='d' && cleanup_off_error) return -EIO;
    if (error_at_this_step()) {
        if (state) channels_on=1; // simulate a bus error AFTER actual hardware arm
        return -EIO;
    }
    channels_on=(int)state;
    return 0;
}
static int update_allowed_flash_current(struct qcom_flash_led *led,
                                        unsigned int *current, bool state) {
    (void)led;(void)current;(void)state;stage('U');
    return error_at_this_step()?-EIO:0;
}
static int set_flash_current(struct qcom_flash_led *led,unsigned int current,
                             enum led_mode mode) {
    (void)led;(void)current;(void)mode;stage('C');
    return error_at_this_step()?-EIO:0;
}
static int set_flash_timeout(struct qcom_flash_led *led,unsigned int timeout) {
    (void)led;(void)timeout;stage('T');
    return error_at_this_step()?-EIO:0;
}
static int set_flash_module_en(struct qcom_flash_led *led, bool state) {
    (void)led;stage(state?'M':'m');
    if (!state && cleanup_module_error) return -EIO;
    if (error_at_this_step()) {
        if (state) module_on=1; // simulate bus error after setting module
        return -EIO;
    }
    module_on=(int)state;
    return 0;
}
static void fake_dev_err(void *dev,const char *format,int code) {
    (void)dev;(void)format;(void)code;logs++;
}
#define dev_err(dev,fmt,code) fake_dev_err((dev),(fmt),(code))
static void check(bool ok,const char *msg) {
    if (!ok) { fprintf(stderr,"E004FZ_TEST_FAIL %s TRACE=%s\n",msg,trace); exit(1); }
}
static void reset(int fault) {
    count=0;fail_step=fault;cleanup_off_error=0;cleanup_module_error=0;
    logs=0;seen_initial=0;cleanup_started=0;module_on=0;channels_on=0;trace[0]=0;
}
'''
        tests=r'''
int main(void) {
    struct qcom_flash_led led={.flash_timeout_ms=40,.max_timeout_ms=1280,
                               .flash_current_ma=25};
    int n,rc;
    reset(0);
    rc=qcom_flash_strobe(&led,HW_STROBE,true);
    check(rc==0 && strcmp(trace,"DUCTMA")==0 && module_on && channels_on,
          "normal enable/arming call sequence");
    for(n=1;n<=6;n++) {
        reset(n);
        rc=qcom_flash_strobe(&led,HW_STROBE,true);
        check(rc==-EIO && count==n+2,"original error or rollback calls lost");
        check(trace[count-2]=='d' && trace[count-1]=='m',
              "missing channel and module rollback after failure");
        check(!module_on && !channels_on,"successful rollback not reflected");
    }
    reset(0);
    led.flash_timeout_ms=0;
    rc=qcom_flash_strobe(&led,HW_STROBE,true);
    check(rc==-EINVAL && strcmp(trace,"Ddm")==0,"disabled timer arm accepted");
    check(!module_on && !channels_on,"disabled timer cleanup failed");
    led.flash_timeout_ms=40;
    reset(6);
    cleanup_off_error=1;
    cleanup_module_error=1;
    rc=qcom_flash_strobe(&led,HW_STROBE,true);
    check(rc==-EIO && logs==2,"hardware rollback errors not logged");
    check(module_on && channels_on,"failed bus writes incorrectly modeled as safe");
    reset(1);
    channels_on=1;module_on=1;
    cleanup_off_error=1;cleanup_module_error=1;
    rc=qcom_flash_strobe(&led,HW_STROBE,true);
    check(rc==-EIO && logs==2 && channels_on && module_on,
          "failed initial disarm plus failed rollback must not be called safe");
    reset(0);
    rc=qcom_flash_strobe(&led,SW_STROBE,false);
    check(rc==0 && !module_on && !channels_on,"normal disarm returned error");
    puts("E004FZ_ACTUAL_PATCHED_C=PASS SIX_FORWARD_FAULT_STAGES");
    puts("EARLY_TIMEOUT_REJECTION=PASS ROLLBACK_DISARM_ATTEMPTS=PASS");
    puts("ROLLBACK_BUS_FAILURE=EXPLICITLY_UNSAFE_LOGGED NO_HARDWARE_OPERATION");
    return 0;
}
'''
        path=temp/"harness.c"
        path.write_text(prelude+function+"\n"+tests)
        binary=temp/"harness"
        run(["clang","-std=c11","-O1","-g","-Wall","-Wextra","-Werror",
             "-fsanitize=address,undefined","-fno-omit-frame-pointer",
             path,"-o",binary],timeout=45)
        tested=run([binary],timeout=35)
        print("E004FZ_PATCH_ROUNDTRIP=PASS ASAN_UBSAN=PASS")
        print(tested.stdout.strip())
        print("PATCH_SHA256="+sha256(PATCH.read_bytes()).hexdigest())

if __name__=="__main__":
    main()
