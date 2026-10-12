#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Execute the pinned V4L2 rate fallback against the C-PHY v9 proposal."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
PINS = {
    "drivers/media/v4l2-core/v4l2-common.c": "52aab0e884ce74f08228be7bd2562bea8a284fe7205cabc545e7eb5011a695e4",
    "Documentation/driver-api/media/tx-rx.rst": "d477c2897633372631ea442b092414c669e96d464a86b67128fa9279c8d34b15",
    "Documentation/userspace-api/media/v4l/ext-ctrls-image-process.rst": "13dffdde313d857f16934161b2624d10d207ef525dd76a262dabc69ee971a294",
}
PROPOSAL = ROOT / "src/upstream/phy/cphy-rate-reference-20261012/camss-resend-v9-08.patch"
PROPOSAL_PIN = "75da3f037cd4ba74442049217c86717110a2253ef0285ba809b340c39b5c3846"

def read_pinned(root, name, pin):
    p = root
    for part in Path(name).parts:
        p = p / part
        if p.is_symlink():
            raise ValueError("Symlink reference rejected: " + name)
    data = p.read_bytes()
    if hashlib.sha256(data).hexdigest() != pin:
        raise ValueError("Reference pin mismatch: " + name)
    return data.decode()

def function(text, name):
    start = text.index("static s64 " + name + "(")
    brace = text.index("{", start)
    depth = 1
    end = brace + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]

PRELUDE = r"""
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <errno.h>
typedef int64_t s64;
typedef uint64_t u64;
#define V4L2_CID_LINK_FREQ 1
#define V4L2_CID_PIXEL_RATE 2
#define pr_warn_once(...) ((void)0)
struct v4l2_ctrl { s64 value; };
struct v4l2_ctrl_handler {
 bool has_link, has_pixel, menu_error;
 struct v4l2_ctrl link, pixel;
};
struct v4l2_querymenu { unsigned int id, index; s64 value; };
static struct v4l2_ctrl *v4l2_ctrl_find(struct v4l2_ctrl_handler *h, unsigned int id)
{
 return id == V4L2_CID_LINK_FREQ ? (h->has_link ? &h->link : 0) :
        (h->has_pixel ? &h->pixel : 0);
}
static int v4l2_ctrl_g_ctrl(struct v4l2_ctrl *ctrl) { (void)ctrl; return 0; }
static int v4l2_querymenu(struct v4l2_ctrl_handler *h, struct v4l2_querymenu *q)
{
 q->value = h->link.value;
 return h->menu_error ? -EINVAL : 0;
}
static s64 v4l2_ctrl_g_ctrl_int64(struct v4l2_ctrl *ctrl) { return ctrl->value; }
static u64 div_u64(u64 value, unsigned int divisor) { return value / divisor; }
"""
TEST = r"""
int main(void)
{
 static const s64 rates[] = { 1000000, 24000000, 100000000, 400000000, 800000000 };
 static const unsigned int bpps[] = { 8, 10, 12, 14, 16 };
 struct v4l2_ctrl_handler h = { .has_pixel = true };
 unsigned int discrepancies = 0, dphy_controls = 0, explicit_controls = 0;
 for (unsigned int r = 0; r < sizeof(rates)/sizeof(rates[0]); r++) {
  h.pixel.value = rates[r];
  for (unsigned int b = 0; b < sizeof(bpps)/sizeof(bpps[0]); b++) {
   for (unsigned int n = 1; n <= 3; n++) {
    s64 expected = rates[r] * bpps[b] * 7 / (32 * n);
    s64 proposed = v4l2_get_link_freq_ctrl(&h, 16 * bpps[b], 14 * n);
    s64 inverse = v4l2_get_link_freq_ctrl(&h, 7 * bpps[b], 32 * n);
    assert(inverse == expected);
    assert(proposed != expected);
    discrepancies++;
   }
   for (unsigned int n = 1; n <= 4; n++) {
    assert(v4l2_get_link_freq_ctrl(&h, 16*bpps[b], 32*n) == rates[r]*bpps[b]/(2*n));
    dphy_controls++;
   }
  }
 }
 h.has_link = true; h.link.value = 1200000000;
 assert(v4l2_get_link_freq_ctrl(&h, 16*10, 14*3) == 1200000000); explicit_controls++;
 assert(v4l2_get_link_freq_ctrl(&h, 7*10, 32*3) == 1200000000); explicit_controls++;
 assert(v4l2_get_link_freq_ctrl(&h, 0, 0) == 1200000000); explicit_controls++;
 h.menu_error = true;
 assert(v4l2_get_link_freq_ctrl(&h, 0, 0) == -ENOENT);
 h.menu_error = false; h.has_link = false;
 assert(v4l2_get_link_freq_ctrl(&h, 0, 0) == -ENOENT);
 h.has_pixel = false;
 assert(v4l2_get_link_freq_ctrl(&h, 70, 96) == -ENOENT);
 h.has_pixel = true; h.pixel.value = 0;
 assert(v4l2_get_link_freq_ctrl(&h, 70, 96) == -EINVAL);
 printf("{\"cphy_proposal_discrepancies\":%u,\"dphy_controls\":%u,\"explicit_link_controls\":%u,\"error_controls\":4}\n",
        discrepancies, dphy_controls, explicit_controls);
 return 0;
}
"""
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--kernel-source", type=Path, required=True)
    args = p.parse_args()
    texts = {n: read_pinned(args.kernel_source, n, pin) for n, pin in PINS.items()}
    proposal = read_pinned(PROPOSAL.parent, PROPOSAL.name, PROPOSAL_PIN)
    assert "#define CAMSS_COMMON_PHY_DIVIDENT 16" in proposal
    assert "#define CAMSS_CPHY_DIVISOR 7" in proposal
    assert "v4l2_get_link_freq(sensor_pad, CAMSS_COMMON_PHY_DIVIDENT * bpp, div)" in proposal
    assert "pixel_rate = link_freq * 2 * nr_of_lanes * 16 / k / bits_per_sample" in texts["Documentation/driver-api/media/tx-rx.rst"]
    actual = function(texts["drivers/media/v4l2-core/v4l2-common.c"], "v4l2_get_link_freq_ctrl")
    records = []
    with tempfile.TemporaryDirectory(prefix="sp11-cphy-rate-") as tmp:
        tmp = Path(tmp)
        source = tmp / "rate.c"
        source.write_text(PRELUDE + actual + TEST)
        for compiler in ("gcc", "clang"):
            binary = tmp / compiler
            subprocess.run([compiler, "-std=c11", "-Wall", "-Wextra", "-Werror",
                            "-fsanitize=address,undefined", "-fno-sanitize-recover=all",
                            "-fno-omit-frame-pointer", str(source), "-o", str(binary)], check=True)
            run = subprocess.run([str(binary)], capture_output=True, text=True, check=True)
            records.append({"compiler": compiler, "result": json.loads(run.stdout)})
    print(json.dumps({"result": "PASS_SOURCE_RATE_DISCREPANCY_REPRODUCED",
                      "actual_kernel_function": "v4l2_get_link_freq_ctrl",
                      "source_sha256": PINS, "proposal_sha256": PROPOSAL_PIN,
                      "compilers": records, "hardware_qualified": False,
                      "production_policy": "Require an explicit sensor link frequency; pixel-array rate is not bus pixel rate"}))

if __name__ == "__main__":
    main()
