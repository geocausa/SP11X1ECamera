#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Source-only CDM 2.1 test. Public oracle never enters production source."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

PINS = {
    "cam_cdm.h": "fd4fa4a7469c2de259148e4e4921c2e2b4620c1330428b6fc799bb6846b252c2",
    "cam_cdm_hw_core.c": "97189415ec8f1d0edf92b68e7590a907a009ee83a4d1ef0f9faf67635a4270d8",
    "cam_cdm_hw_reg_2_1.h": "cc05c85f95e41d8d4940bf84620cdfe7cc320be10e05f21387a04af37d096955",
}
def load_reference(root):
    if root.is_symlink() or not root.is_dir():
        raise ValueError("reference root missing or symlink")
    result = {}
    for name, digest in PINS.items():
        path = root / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("reference missing or symlink: " + name)
        data = path.read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError("reference pin mismatch: " + name)
        result[name] = data.decode()
    return result

def function(text, name):
    m = re.search(r"static int\s+" + name + r"\s*\(", text)
    if not m:
        raise ValueError("missing function")
    begin = text.index("{", m.start())
    depth = 1
    end = begin + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[m.start():end]

def block(text, typename, name):
    m = re.search(r"struct\s+" + typename + r"\s+" + name + r"\s*=\s*\{.*?\n\};", text, re.S)
    if not m:
        raise ValueError("missing descriptor: " + name)
    return m.group()

PREFIX = r"""
#include <assert.h>
#include <stdio.h>
#include "sp11-cdm21-state.h"
#define CAM_CDM_BL_FIFO_REG_NUM 10
#define CAM_CDM 0
#define CAM_ERR(...) ((void)0)
#define CAM_DBG(...) ((void)0)
struct cam_cdm_bl_pending_req_reg_params {
    uint32_t rb_offset, rb_mask, rb_num_fifo, rb_next_fifo_shift;
};
struct cam_cdm_common_regs {
    struct cam_cdm_bl_pending_req_reg_params *pending_req[5];
};
struct cam_cdm_hw_reg_offset { struct cam_cdm_common_regs *cmn_reg; };
struct cam_cdm { struct cam_cdm_hw_reg_offset *offsets; };
struct cam_hw_info { void *core_info; };
static uint32_t raw_regs[2];
static int read_fail;
static int cam_cdm_read_hw_reg(struct cam_hw_info *hw, uint32_t reg, uint32_t *out)
{
    (void)hw;
    assert(reg == 0x6c || reg == 0x70);
    if (read_fail) return -EIO;
    *out = raw_regs[reg == 0x70];
    return 0;
}
"""
MAIN = r"""
static unsigned long checks, snapshots, sequences;
#define CHECK(x) do { checks++; assert(x); } while (0)
static void compare(struct cam_hw_info *hw, uint32_t a, uint32_t b)
{
    struct sp11_cdm21_pending out;
    uint32_t raw[2] = {a, b};
    unsigned int i;
    snapshots++;
    raw_regs[0] = a; raw_regs[1] = b;
    CHECK(sp11_cdm21_decode_pending(SP11_CDM21_VERSION, raw, &out) == 0);
    for (i = 0; i < 4; i++) {
        uint32_t oracle = 0xffffffffU;
        CHECK(cam_hw_cdm_bl_fifo_pending_bl_rb_in_fifo(hw, i, &oracle) == 0);
        CHECK(out.count[i] == oracle);
    }
}
int main(void)
{
    struct cam_cdm_common_regs cmn = {
        .pending_req = {&cdm_hw_2_1_bl_pending_req0, &cdm_hw_2_1_bl_pending_req1}
    };
    struct cam_cdm_hw_reg_offset offsets = {&cmn};
    struct cam_cdm core = {&offsets};
    struct cam_hw_info hw = {&core};
    struct sp11_cdm21_reset_observation state = {0}, saved;
    struct sp11_cdm21_pending output, old;
    unsigned int i, v, a, b, c, d, n, j, bit;
    uint32_t random = 0x51cd2101U, raw[2] = {0, 0};
    uint32_t unsupported[] = {0, 0x20000000U, 0x20020000U, 0x30010000U, 0xffffffffU};
    for (i = 0; i < 4; i++)
        for (v = 0; v < 512; v++) {
            uint32_t pair[2] = {0xfe00fe00U, 0xfe00fe00U};
            pair[i / 2] |= v << (16 * (i % 2));
            compare(&hw, pair[0], pair[1]);
        }
    for (i = 0; i < 10000; i++) {
        uint32_t x;
        random ^= random << 13; random ^= random >> 17; random ^= random << 5;
        x = random;
        random ^= random << 13; random ^= random >> 17; random ^= random << 5;
        compare(&hw, x, random);
    }
    for (i = 0; i < 4; i++) {
        uint32_t sentinel = 123;
        read_fail = 1;
        CHECK(cam_hw_cdm_bl_fifo_pending_bl_rb_in_fifo(&hw, i, &sentinel) == -EIO);
        CHECK(sentinel == 123);
        read_fail = 0;
    }
    v = 123;
    CHECK(cam_hw_cdm_bl_fifo_pending_bl_rb_in_fifo(&hw, 10, &v) == -EINVAL);
    CHECK(v == 123);
    memset(&output, 0xa5, sizeof(output)); old = output;
    for (i = 0; i < sizeof(unsupported) / sizeof(*unsupported); i++) {
        CHECK(sp11_cdm21_decode_pending(unsupported[i], raw, &output) == -ENODEV);
        CHECK(!memcmp(&output, &old, sizeof(old)));
        CHECK(sp11_cdm21_reset_begin(&state, unsupported[i], 1) == -ENODEV);
        CHECK(!state.armed && state.epoch == 0);
    }
    CHECK(sp11_cdm21_decode_pending(SP11_CDM21_VERSION, NULL, &output) == -EINVAL);
    CHECK(!memcmp(&output, &old, sizeof(old)));
    CHECK(sp11_cdm21_decode_pending(SP11_CDM21_VERSION, raw, NULL) == -EINVAL);
    CHECK(sp11_cdm21_decode_pending(SP11_CDM21_VERSION, output.count, &output) == -EINVAL);
    CHECK(!memcmp(&output, &old, sizeof(old)));
    CHECK(sp11_cdm21_decode_pending(SP11_CDM21_VERSION, output.count + 1, &output) == -EINVAL);
    CHECK(!memcmp(&output, &old, sizeof(old)));
    CHECK(sp11_cdm21_reset_begin(NULL, SP11_CDM21_VERSION, 1) == -EINVAL);
    CHECK(sp11_cdm21_reset_begin(&state, SP11_CDM21_VERSION, 0) == -EINVAL);
    CHECK(sp11_cdm21_reset_note(NULL, 1, 0, 1) == -EINVAL);
    CHECK(sp11_cdm21_reset_close(NULL, 1) == -EINVAL);
    CHECK(!sp11_cdm21_reset_ack_complete(NULL, 1));
    /* All 24 IRQ bank orders with no-ACK, duplicate and stale-epoch events. */
    for (a = 0; a < 4; a++) for (b = 0; b < 4; b++)
    for (c = 0; c < 4; c++) for (d = 0; d < 4; d++) {
        unsigned int order[4] = {a, b, c, d};
        uint64_t epoch;
        if (a == b || a == c || a == d || b == c || b == d || c == d) continue;
        sequences++;
        epoch = sequences * 2;
        CHECK(sp11_cdm21_reset_begin(&state, SP11_CDM21_VERSION, epoch) == 0);
        saved = state;
        CHECK(sp11_cdm21_reset_begin(&state, SP11_CDM21_VERSION, epoch + 1) == -EBUSY);
        CHECK(!memcmp(&saved, &state, sizeof(state)));
        for (n = 0; n < 4; n++) {
            CHECK(sp11_cdm21_reset_note(&state, epoch, order[n], 6) == 0);
            CHECK(!sp11_cdm21_reset_ack_complete(&state, epoch));
            CHECK(sp11_cdm21_reset_note(&state, epoch - 1, order[n], 1) == -ESTALE);
            CHECK(sp11_cdm21_reset_note(&state, epoch + 1, order[n], 1) == -ESTALE);
            CHECK(sp11_cdm21_reset_note(&state, epoch, order[n], 7) == 0);
            CHECK(sp11_cdm21_reset_ack_complete(&state, epoch) == (n == 3));
            CHECK(!sp11_cdm21_reset_ack_complete(&state, epoch + 1));
            CHECK(!sp11_cdm21_reset_ack_complete(&state, 0));
            CHECK(sp11_cdm21_reset_note(&state, epoch, order[n], 1) == 0);
            CHECK(sp11_cdm21_reset_ack_complete(&state, epoch) == (n == 3));
        }
        CHECK(sp11_cdm21_reset_close(&state, epoch - 1) == -ESTALE);
        CHECK(sp11_cdm21_reset_ack_complete(&state, epoch));
        CHECK(sp11_cdm21_reset_close(&state, epoch) == 0);
        CHECK(!sp11_cdm21_reset_ack_complete(&state, epoch));
        CHECK(sp11_cdm21_reset_note(&state, epoch, 0, 1) == -ESTALE);
        CHECK(sp11_cdm21_reset_close(&state, epoch) == -ESTALE);
        CHECK(sp11_cdm21_reset_begin(&state, SP11_CDM21_VERSION, epoch) == -ESTALE);
        CHECK(sp11_cdm21_reset_begin(&state, SP11_CDM21_VERSION, epoch - 1) == -ESTALE);
    }
    /* Any non-completion bit faults both partial and complete observations. */
    for (bit = 3; bit < 32; bit++) for (n = 0; n <= 4; n++) {
        uint64_t epoch = 100 + bit * 5 + n;
        CHECK(sp11_cdm21_reset_begin(&state, SP11_CDM21_VERSION, epoch) == 0);
        for (j = 0; j < n; j++) CHECK(sp11_cdm21_reset_note(&state, epoch, j, 1) == 0);
        CHECK(sp11_cdm21_reset_note(&state, epoch, 0, 1U << bit) == -EIO);
        CHECK(state.fault);
        CHECK(!sp11_cdm21_reset_ack_complete(&state, epoch));
        for (j = 0; j < 4; j++) CHECK(sp11_cdm21_reset_note(&state, epoch, j, 1) == -EIO);
        CHECK(sp11_cdm21_reset_close(&state, epoch) == 0);
    }
    CHECK(sp11_cdm21_reset_begin(&state, SP11_CDM21_VERSION, UINT64_MAX) == 0);
    CHECK(sp11_cdm21_reset_note(&state, UINT64_MAX, 4, 1) == -EIO);
    CHECK(!sp11_cdm21_reset_ack_complete(&state, UINT64_MAX));
    CHECK(sp11_cdm21_reset_close(&state, UINT64_MAX) == 0);
    CHECK(sp11_cdm21_reset_begin(&state, SP11_CDM21_VERSION, 1) == -ESTALE);
    printf("{\"checks\":%lu,\"pending_snapshots\":%lu,\"bank_order_sequences\":%lu}\n",
           checks, snapshots, sequences);
    return 0;
}
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--reference", type=Path, required=True)
    parser.add_argument("--headers", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    ref = load_reference(args.reference)
    expected = [
        (ref["cam_cdm.h"], r"CAM_CDM_VERSION_2_1\s*=\s*0x20010000"),
        (ref["cam_cdm.h"], r"CAM_CDM_BL_FIFO_REG_NUM\s+0xA"),
        (ref["cam_cdm.h"], r"CAM_CDM_IRQ_STATUS_RST_DONE_MASK\s+0x1"),
        (ref["cam_cdm.h"], r"CAM_CDM_IRQ_STATUS_INLINE_IRQ_MASK\s+0x2"),
        (ref["cam_cdm.h"], r"CAM_CDM_IRQ_STATUS_BL_DONE_MASK\s+0x4"),
        (ref["cam_cdm_hw_reg_2_1.h"], r"\.num_bl_fifo\s*=\s*0x4"),
        (ref["cam_cdm_hw_reg_2_1.h"], r"\.num_bl_fifo_irq\s*=\s*0x4"),
        (ref["cam_cdm_hw_reg_2_1.h"], r"\.cdm_status\s*=\s*0x0"),
    ]
    for text, pattern in expected:
        if not re.search(pattern, text):
            raise ValueError("descriptor mismatch: " + pattern)
    source = PREFIX
    for n in range(2):
        source += "\n" + block(ref["cam_cdm_hw_reg_2_1.h"],
                             "cam_cdm_bl_pending_req_reg_params",
                             "cdm_hw_2_1_bl_pending_req" + str(n))
    source += "\n" + function(ref["cam_cdm_hw_core.c"],
                              "cam_hw_cdm_bl_fifo_pending_bl_rb_in_fifo") + "\n" + MAIN
    own = {}
    for name in ("sp11-cdm.h", "sp11-cdm21-state.h"):
        path = args.headers / name
        if path.is_symlink() or not path.is_file():
            raise ValueError("helper missing or symlink")
        own[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    results = []
    with tempfile.TemporaryDirectory(prefix="sp11-cdm21-test-") as tmp:
        tmp = Path(tmp)
        c = tmp / "test.c"
        c.write_text(source)
        for compiler in ("gcc", "clang"):
            exe = tmp / compiler
            argv = [compiler, "-std=c11", "-O1", "-g", "-Wall", "-Wextra", "-Werror",
                    "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
                    "-I", str(args.headers), str(c), "-o", str(exe)]
            subprocess.run(argv, check=True, capture_output=True, text=True)
            run = subprocess.run([str(exe)], check=True, capture_output=True, text=True)
            results.append({"compiler": compiler, "sanitizers": ["address", "undefined"],
                            "counts": json.loads(run.stdout), "stderr": run.stderr,
                            "compiler_version": subprocess.check_output([compiler, "--version"], text=True).splitlines()[0]})
        rejected = []
        for name in PINS:
            for mode in ("changed", "missing", "symlink"):
                fixture = tmp / (name + "-" + mode)
                fixture.mkdir()
                for other in PINS:
                    (fixture / other).write_bytes((args.reference / other).read_bytes())
                target = fixture / name
                if mode == "changed": target.write_bytes(target.read_bytes() + b"\n")
                else:
                    target.unlink()
                    if mode == "symlink": target.symlink_to(args.reference / name)
                try:
                    load_reference(fixture)
                except ValueError:
                    rejected.append({"file": name, "mode": mode})
                else:
                    raise AssertionError("accepted invalid reference")
    result = {"schema": "sp11-cdm21-host-validation-v1", "status": "PASS_SOURCE_ONLY",
              "reference_pins": PINS, "helper_pins": own,
              "oracle": "unchanged public FIFO decoder and two exact public descriptors; test-only structures/MMIO adapter",
              "runs": results, "reference_rejections": rejected,
              "hardware_qualified": False, "installed": False, "dma_retirement_proven": False}
    with args.output.open("x") as out:
        json.dump(result, out, indent=2)
        out.write("\n")
    print(json.dumps(result))

if __name__ == "__main__":
    main()
