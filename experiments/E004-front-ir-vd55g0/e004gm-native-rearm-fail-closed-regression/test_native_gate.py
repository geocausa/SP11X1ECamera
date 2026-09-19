#!/usr/bin/env python3
"""Prove patched Linux flash callback refuses rearm after initial OFF error.

Offline original patched C under ASan/UBSan and prior pinned Windows VM tests.
NOT proof of physical LED-off or authorization for emitter installation.
"""
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import subprocess
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
FZ=ROOT/"experiments/E004-front-ir-vd55g0/e004fz-flash-error-rollback-offline"
GL=ROOT/"experiments/E004-front-ir-vd55g0/e004gl-ghidra-flash-lifecycle-fault-audit"
PATCH=ROOT/"src/front-ir-vd55g0/illumination/0004-qcom-flash-best-effort-error-disarm.patch"
PATCH_SHA="cbc8bc73882fd258e81549e96323f11c7bdefa2fefed6870f7da82be838b55ce"

def need(ok,what):
    if not ok:raise AssertionError("E004GM_OFFLINE_FAIL_CLOSED "+what)

def checked(args,timeout=140,env=None):
    r=subprocess.run([str(x) for x in args],cwd=ROOT,capture_output=True,
                     text=True,timeout=timeout,env=env,check=False)
    need(r.returncode==0,"test execution failed: "+str(args[:2])+
         "\n"+r.stdout[-800:]+"\n"+r.stderr[-800:])
    return r.stdout

def main():
    need(sha256(PATCH.read_bytes()).hexdigest()==PATCH_SHA,"prior uninstalled rollback patch modified")
    previous=json.loads((GL/"evidence/RESULT.json").read_text())
    need(previous["status"]=="PASS_GHIDRA_DECOMPILED_AND_ORIGINAL_ARM64_LIFECYCLE_FAULT_EMULATION_OFFLINE" and
         previous["previous_off_request_failure_does_not_prevent_subsequent_rearm_request"] is True and
         previous["native_emitter_enable_authorized"] is False,"Windows prior proof changed")
    sys.path.insert(0,str(FZ))
    from generate_patch import PATCH as BASE_PATCH, produce
    _,patched,patch=produce()
    need(BASE_PATCH==PATCH and PATCH.read_text()==patch,"original patched Linux source or patch drift")
    start=patched.index("static int qcom_flash_strobe(struct qcom_flash_led *led,")
    end=patched.index("\nstatic int qcom_flash_strobe_set(",start)
    function=patched[start:end]
    # Only this actual Linux source callback is compiled; fake regmap helpers
    # explicitly record *requests*, not hardware state or PMIC behavior.
    prelude=r"""
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
enum led_strobe {SW_STROBE,HW_STROBE};
enum led_mode {FLASH_MODE,TORCH_MODE};
#define FLASH_TIMER_STEP_MS 10
struct qcom_flash_led {
  struct {struct {void *dev;} led_cdev;} flash;
  unsigned int flash_timeout_ms,max_timeout_ms,flash_current_ma;
};
static char trace[64];
static unsigned idx;
static int initial_seen,initial_error,rollback_off_error,rollback_module_error;
static int module_on,channels_on,log_errors;
static void add(char c) {if(idx>=sizeof(trace)-1)abort();trace[idx++]=c;trace[idx]=0;}
static int set_flash_strobe(struct qcom_flash_led *led,enum led_strobe mode,bool state) {
  (void)led;(void)mode;
  if(state) {add('A');channels_on=1;return 0;}
  if(!initial_seen) {
    initial_seen=1;add('D');
    if(initial_error)return -EIO;
  } else {
    add('d');
    if(rollback_off_error)return -EIO;
  }
  channels_on=0;return 0;
}
static int update_allowed_flash_current(struct qcom_flash_led *led,
                                        unsigned int *cur,bool state) {
  (void)led;(void)cur;(void)state;add('U');return 0;
}
static int set_flash_current(struct qcom_flash_led *led,unsigned int ma,enum led_mode mode) {
  (void)led;(void)ma;(void)mode;add('C');return 0;
}
static int set_flash_timeout(struct qcom_flash_led *led,unsigned int ms) {
  (void)led;(void)ms;add('T');return 0;
}
static int set_flash_module_en(struct qcom_flash_led *led,bool state) {
  (void)led;add(state?'M':'m');
  if(!state && rollback_module_error)return -EIO;
  module_on=state;return 0;
}
static void fake_error(void *dev,const char *fmt,int code){
  (void)dev;(void)fmt;(void)code;log_errors++;
}
#define dev_err(dev,fmt,code) fake_error((dev),(fmt),(code))
static void require(bool ok,const char *what){
  if(!ok){fprintf(stderr,"E004GM_TEST_FAILED %s TRACE=%s\\n",what,trace);exit(1);}
}
static void reset(int a,int b,int c) {
  idx=0;trace[0]=0;initial_seen=0;initial_error=a;
  rollback_off_error=b;rollback_module_error=c;
  module_on=1;channels_on=1;log_errors=0;
}
"""
    tests=r"""
int main(void) {
  struct qcom_flash_led led={.flash_timeout_ms=40,.max_timeout_ms=1280,
                             .flash_current_ma=25};
  int rc;
  // Regression against Windows: INITIAL OFF request reports failure,
  // then all later callbacks MUST NOT request any new arm.
  reset(1,0,0);
  rc=qcom_flash_strobe(&led,HW_STROBE,true);
  require(rc==-EIO && strcmp(trace,"Ddm")==0 &&
          !module_on && !channels_on,"rearm after failed prior OFF");
  puts("E004GM_INITIAL_OFF_FAILURE_FAILS_CLOSED=PASS NO_REARM=PASS");
  // If even best-effort cleanup requests fail, simulated hardware can remain
  // ON. Software-level fail-closed does not prove autonomous electrical off.
  reset(1,1,1);
  rc=qcom_flash_strobe(&led,HW_STROBE,true);
  require(rc==-EIO && strcmp(trace,"Ddm")==0 &&
          module_on && channels_on && log_errors==2,
          "failed bus cleanup was mistaken for LED off");
  puts("E004GM_FAILED_SPMI_ROLLBACK=EXPLICITLY_UNSAFE NO_REARM=PASS");
  reset(0,0,0);
  rc=qcom_flash_strobe(&led,HW_STROBE,true);
  require(rc==0 && strcmp(trace,"DUCTMA")==0 &&
          module_on && channels_on,"normal synthetic request path changed");
  puts("E004GM_NORMAL_SOFTWARE_PATH=PASS ASAN_UBSAN=PASS");
  return 0;
}
"""
    with TemporaryDirectory(prefix="e004gm-uninstalled-linux-") as temp:
        source=Path(temp)/"original_patched_callback_test.c"
        binary=Path(temp)/"callback_test"
        source.write_text(prelude+function+"\n"+tests)
        checked(["clang","-std=c11","-O1","-g","-Wall","-Wextra","-Werror",
                 "-fsanitize=address,undefined","-fno-omit-frame-pointer",
                 source,"-o",binary],timeout=45)
        output=checked([binary],timeout=35,
                      env={**os.environ,"ASAN_OPTIONS":"detect_leaks=1:halt_on_error=1",
                           "UBSAN_OPTIONS":"halt_on_error=1"})
    for token in ("E004GM_INITIAL_OFF_FAILURE_FAILS_CLOSED=PASS",
                  "E004GM_FAILED_SPMI_ROLLBACK=EXPLICITLY_UNSAFE",
                  "E004GM_NORMAL_SOFTWARE_PATH=PASS"):
        need(token in output,"missing actual compiled callback test marker "+token)
    previous_windows=checked(["python3",GL/"test_flash_lifecycle.py"],timeout=90)
    need("E004GL_REARM_AFTER_MOCKED_OFF_FAILURE" in previous_windows,
         "original Windows weakness not reproduced")
    previous_linux=checked(["python3",FZ/"test_rollback.py"],timeout=110)
    need("E004FZ_ACTUAL_PATCHED_C=PASS" in previous_linux,
         "original Linux six-fault-stage source regression not reproduced")
    out={
        "experiment":"E004gm",
        "status":"PASS_UNINSTALLED_NATIVE_LINUX_REARM_FAIL_CLOSED_VS_WINDOWS_EMULATED_GAP",
        "uninstalled_patch_sha256":PATCH_SHA,
        "source_sha256":sha256(Path(__file__).read_bytes()).hexdigest(),
        "windows_actual_arm64_prior_off_failure_can_still_rearm":True,
        "linux_uninstalled_original_patched_c_refuses_rearm_after_initial_off_error":True,
        "linux_best_effort_rollback_bus_failure_physically_proves_off":False,
        "normal_original_linux_six_stage_fault_regression":"PASS",
        "normal_and_asan_ubsan":"PASS",
        "linux_flash_patch_installed":False,
        "native_ir_emitter_authorized":False,
        "camera_windows_kd_pmic_or_emitter_activity":False,
        "golden_modified":False,
    }
    (HERE/"evidence").mkdir(exist_ok=True)
    (HERE/"evidence/RESULT.json").write_text(json.dumps(out,indent=2)+chr(10))
    print(output.strip())
    print("E004GM_WINDOWS_VS_LINUX_ORIGINAL_SOURCE_COMPARISON=PASS")
    print("IR_EMITTER=OFF HARDWARE_AUTONOMOUS_LED_OFF=NOT_PROVEN")

if __name__=="__main__":main()
