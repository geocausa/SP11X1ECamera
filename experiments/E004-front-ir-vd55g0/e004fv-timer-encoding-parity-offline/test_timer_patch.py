#!/usr/bin/env python3
"""Apply and exercise actual patched Linux timer code, entirely offline."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import re
import subprocess
import sys

from generate_patch import BASE, PATCH, WIN, source_pair

ROOT = Path(__file__).resolve().parents[3]
WINDOWS_SHA = "1d3ab98722a381c64f355b0b71da6cea84c4f569f81da1ebde262f51ea4348ef"

def need(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("E004FV_TEST_FAIL " + message)

def main() -> None:
    before, expected = source_pair()
    need(sha256(WIN.read_bytes()).hexdigest() == WINDOWS_SHA, "Windows source drift")
    win = json.loads(WIN.read_text())["timer_handler"]
    need(win["enabled_value"] == "0x80 | floor((requested_ms - 10) / 10)",
         "different Windows encoding evidence")
    need("timer = timeout_ms / FLASH_TIMER_STEP_MS" in before,
         "original Linux timer formula changed")
    need("timer = (u8)steps | FLASH_TIMER_EN_BIT" in expected,
         "candidate timer formula missing")
    need("if (state && (led->flash_timeout_ms < FLASH_TIMER_STEP_MS ||" in expected,
         "nonzero armed-timeout guard missing")
    with TemporaryDirectory(prefix="sp11-e004fv-no-hardware-") as directory:
        tmp = Path(directory)
        source = tmp / "drivers/leds/flash/leds-qcom-flash.c"
        source.parent.mkdir(parents=True)
        source.write_text(before)
        result = subprocess.run(["patch", "--batch", "-p1", "-d", str(tmp),
                                 "-i", str(PATCH.resolve())],
                                capture_output=True, text=True, check=False)
        need(result.returncode == 0, "patch application: " + result.stderr)
        need(source.read_text() == expected, "patched source differs")
        function = re.search(r"static int set_flash_timeout\(.*?\n\}\n",
                             expected, re.S)
        need(bool(function), "actual timer function not found")
        # This is the actual patched C function, compiled with regmap stubs.
        # No kernel, device node, camera, PMIC, or emitter is accessed.
        preamble = r"""
#include <errno.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
typedef uint8_t u8;
typedef uint32_t u32;
#define FLASH_TIMER_STEP_MS 10u
#define FLASH_TIMER_EN_BIT 0x80u
#define FLASH_TIMER_VAL_MASK 0x7fu
#define REG_CHAN_TIMER 0
#define min_t(t, a, b) ((t)(a) < (t)(b) ? (t)(a) : (t)(b))
struct regmap_field { unsigned int placeholder; };
struct qcom_flash_data { struct regmap_field *r_fields[1]; };
struct qcom_flash_led {
    struct qcom_flash_data *flash_data;
    u32 max_timeout_ms;
    int chan_count;
    u8 chan_id[4];
};
static int writes;
static int fail_on_write;
static u8 encoded[4];
static u8 channels[4];
static int regmap_fields_write(struct regmap_field *field, u8 channel, u8 value)
{
    if (!field || writes >= 4) abort();
    channels[writes] = channel;
    encoded[writes] = value;
    writes++;
    if (fail_on_write && writes == fail_on_write) return -EIO;
    return 0;
}
static void check(int cond, const char *reason)
{
    if (!cond) { fprintf(stderr, "E004FV_FAIL %s\n", reason); exit(1); }
}
"""
        tests = r"""
int main(void)
{
    struct regmap_field timer_field = {0};
    struct qcom_flash_data flash = { .r_fields = {&timer_field} };
    struct qcom_flash_led led = {
        .flash_data = &flash, .max_timeout_ms = 1280,
        .chan_count = 2, .chan_id = {0, 3}
    };
    unsigned int request;
    int rc;
    for (request = 0; request <= 1280; request++) {
        unsigned int expected;
        writes = 0;
        fail_on_write = 0;
        rc = set_flash_timeout(&led, request);
        if (request > 0 && request < 10) {
            check(rc == -EINVAL && writes == 0, "sub-step must reject before I/O");
            continue;
        }
        expected = request ? (0x80u | ((request - 10u) / 10u)) : 0u;
        check(rc == 0 && writes == 2, "normal paired-channel return/writes");
        check(encoded[0] == expected && encoded[1] == expected,
              "byte differs from Windows recovered timer encoder");
        check(channels[0] == 0 && channels[1] == 3,
              "wrong LED1 paired channel");
    }
    /* Clamp to the configured maximum without wrapping the encoded byte. */
    writes = 0;
    check(set_flash_timeout(&led, 2000) == 0 && writes == 2
          && encoded[0] == 0xff && encoded[1] == 0xff,
          "maximum timeout encoding");
    /* If the maximum is too small, a nonzero request cannot arm a timer. */
    led.max_timeout_ms = 9;
    writes = 0;
    check(set_flash_timeout(&led, 100) == -EINVAL && writes == 0,
          "unsafe configured maximum did not fail closed");
    led.max_timeout_ms = 1280;
    writes = 0;
    fail_on_write = 2;
    check(set_flash_timeout(&led, 40) == -EIO && writes == 2
          && encoded[0] == 0x83 && encoded[1] == 0x83,
          "second-channel bus error propagation");
    puts("E004FV_ACTUAL_PATCHED_C=PASS WINDOWS_PARITY_REQUESTS=1271");
    puts("ZERO_DISABLED=PASS SUBSTEP_REJECTED=9 CHANNEL_FAILURE_PROPAGATED=YES");
    puts("EMITTER_ENABLED=NO HARDWARE_ACCESSED=NO");
    return 0;
}
"""
        c = tmp / "timer_harness.c"
        c.write_text(preamble + function.group(0) + "\n" + tests)
        binary = tmp / "timer_harness"
        cc = subprocess.run(["clang", "-std=c11", "-O1", "-g", "-Wall",
                             "-Wextra", "-Werror", "-fsanitize=address,undefined",
                             "-fno-omit-frame-pointer", str(c), "-o", str(binary)],
                            capture_output=True, text=True, check=False)
        need(cc.returncode == 0, "compile failed: " + cc.stderr)
        run = subprocess.run([str(binary)], capture_output=True, text=True,
                             check=False, timeout=30)
        need(run.returncode == 0, "instrumented compiled test failed: " + run.stderr)
        print("E004FV_PATCH_ROUNDTRIP=PASS STANDALONE_ASAN_UBSAN=PASS")
        print(run.stdout.strip())
        print("PATCH_SHA256=" + sha256(PATCH.read_bytes()).hexdigest())

if __name__ == "__main__":
    main()
