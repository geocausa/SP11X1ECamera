#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Test the actual MMIO-free CSIPHY2.1.2 preparation code with pinned GPL bins."""
import argparse
import decimal
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

SOURCE_PINS = {
    "phy-qcom-mipi-csi2-cphy-config.c": "f1ac5a3d30f941579ee6c415dc6872f8dcbc7b8b4a04fbd2356a97370dfc30d3",
    "phy-qcom-mipi-csi2-cphy-config.h": "2550ebb4bce2a655ddf9023fdfa4c97a8e66856f73f26e47c8b9eff52d55fe25",
}
PUBLIC_PIN = "1f5dc382c0d3d62714195022f2b811a058eb80642821c38f5737488d36352bf5"
def pinned(path, pin):
    p = path.absolute()
    for parent in (p, *p.parents):
        if parent.is_symlink():
            raise ValueError("Symlink reference rejected")
    data = p.read_bytes()
    if hashlib.sha256(data).hexdigest() != pin:
        raise ValueError("Reference pin mismatch: " + str(path))
    return data.decode()

TEST = r"""
#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "phy-qcom-mipi-csi2-cphy-config.h"
static const uint64_t bins[] = { BIN_VALUES };
static const uint32_t routes[][3] = {
 {1,0,0},{2,0,0},{3,0,0},
 {1,2,0},{1,3,0},{2,1,0},{2,3,0},{3,1,0},{3,2,0},
 {1,2,3},{1,3,2},{2,1,3},{2,3,1},{3,1,2},{3,2,1}
};
static struct mipi_csi2phy_cphy_request base(void)
{
 struct mipi_csi2phy_cphy_request r = {
  .link_freq_hz = 1200000000, .settle_count = 34,
  .num_trios = 3, .data_lanes = {1,2,3}
 };
 return r;
}
static void reject(const struct mipi_csi2phy_cphy_request *r, int error)
{
 struct mipi_csi2phy_cphy_config c, before;
 memset(&c, 0xa5, sizeof(c)); memcpy(&before, &c, sizeof(c));
 assert(mipi_csi2phy_cphy_prepare(r, &c) == error);
 assert(memcmp(&c, &before, sizeof(c)) == 0);
}
int main(void)
{
 const uint32_t settles[] = {1,34,255,256,65535};
 unsigned int success = 0, ranges = 0, invalid = 0;
 for (unsigned int b = 0; b < sizeof(bins)/sizeof(bins[0]); b++) {
  for (int delta = -1; delta <= 1; delta++) {
   for (unsigned int p = 0; p < sizeof(routes)/sizeof(routes[0]); p++) {
    for (unsigned int s = 0; s < sizeof(settles)/sizeof(settles[0]); s++) {
     struct mipi_csi2phy_cphy_request r = base();
     r.link_freq_hz = bins[b]/2 + delta;
     r.num_trios = p < 3 ? 1 : (p < 9 ? 2 : 3);
     r.settle_count = settles[s];
     memcpy(r.data_lanes, routes[p], sizeof(r.data_lanes));
     if ((b == 0 && delta < 0) || (b == 27 && delta > 0)) {
      reject(&r, -34); ranges++; continue;
     }
     struct mipi_csi2phy_cphy_config c;
     memset(&c, 0xa5, sizeof(c));
     assert(mipi_csi2phy_cphy_prepare(&r, &c) == 0);
     assert(c.link_freq_hz == r.link_freq_hz && c.symbol_rate == 2*r.link_freq_hz);
     assert(c.rate_index == b + (delta > 0));
     assert(c.settle_count == settles[s] && c.num_trios == r.num_trios);
     unsigned int mask = 0;
     for (unsigned int n = 0; n < 3; n++) {
      assert(c.data_lanes[n] == routes[p][n]);
      if (routes[p][n]) mask |= 1U << (2*routes[p][n]-1);
     }
     assert(c.lane_mask == mask && !(c.lane_mask & 0xd5));
     success++;
    }
   }
  }
 }
 struct mipi_csi2phy_cphy_request r;
 const uint32_t counts[] = {0,4,UINT32_MAX};
 for (unsigned int i = 0; i < 3; i++) { r=base(); r.num_trios=counts[i]; reject(&r,-22); invalid++; }
 const uint32_t bad_settles[] = {0,65536,UINT32_MAX};
 for (unsigned int i = 0; i < 3; i++) { r=base(); r.settle_count=bad_settles[i]; reject(&r,-22); invalid++; }
 const uint64_t bad_rates[] = {0,49999999,3000000001,UINT64_MAX,UINT64_MAX/2+1};
 for (unsigned int i = 0; i < 5; i++) { r=base(); r.link_freq_hz=bad_rates[i]; reject(&r,-34); invalid++; }
 const uint32_t bad_lanes[] = {0,4,UINT32_MAX};
 for (unsigned int i = 0; i < 3; i++) { r=base(); r.data_lanes[0]=bad_lanes[i]; reject(&r,-22); invalid++; }
 for (unsigned int i = 0; i < 3; i++) { r=base(); r.data_lanes[i]=r.data_lanes[(i+1)%3]; reject(&r,-22); invalid++; }
 r=base();r.num_trios=1;reject(&r,-22);invalid++;
 r.data_lanes[1]=0;reject(&r,-22);invalid++;
 reject(0,-22);invalid++;
 assert(mipi_csi2phy_cphy_prepare(&r,0)==-22);invalid++;
 r=base();struct mipi_csi2phy_cphy_config c;
 assert(mipi_csi2phy_cphy_prepare(&r,&c)==0 && bins[c.rate_index]==2500000000 && c.lane_mask==0x2a);
 printf("{\"successful_boundary_route_counter_cases\":%u,\"out_of_range_atomic_cases\":%u,\"extra_atomic_error_cases\":%u,\"front_2p4_selects_2p5_bin\":true}\n",success,ranges,invalid);
 return 0;
}
"""
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--candidate-source", type=Path, required=True)
    p.add_argument("--public-header", type=Path, required=True)
    args = p.parse_args()
    prefix = args.candidate_source / "drivers/phy/qualcomm"
    files = {n: pinned(prefix/n, pin) for n, pin in SOURCE_PINS.items()}
    public = pinned(args.public_header, PUBLIC_PIN)
    table = public.split("static struct data_rate_reg_info_t data_rate_settings_2_1_2[] = {",1)[1].split("\n};",1)[0]
    rates = []
    for tag in re.findall(r"\.data_rate_reg_array\[0\]\[0\] = datarate_212_(\w+)", table):
        m = re.fullmatch(r"(\d+(?:p\d+)?)(M|G)sps", tag)
        assert m
        rates.append(int(decimal.Decimal(m[1].replace("p",".")) * (10**6 if m[2]=="M" else 10**9)))
    actual = [int(x) for x in re.findall(r"^\t(\d+)ULL,", files["phy-qcom-mipi-csi2-cphy-config.c"], re.M)]
    assert rates == actual and len(rates) == 28
    records = []
    with tempfile.TemporaryDirectory(prefix="sp11-cphy-prepare-") as tmp:
        tmp = Path(tmp)
        inc = tmp/"linux"; inc.mkdir()
        (inc/"types.h").write_text("#include <stdint.h>\ntypedef uint64_t u64; typedef uint32_t u32; typedef uint16_t u16; typedef uint8_t u8;\n")
        (inc/"bitops.h").write_text("#define BIT(n) (1UL << (n))\n")
        (inc/"errno.h").write_text("#define EINVAL 22\n#define ERANGE 34\n")
        (inc/"kernel.h").write_text("#include <stddef.h>\n#define ARRAY_SIZE(a) (sizeof(a)/sizeof((a)[0]))\n")
        for name, data in files.items(): (tmp/name).write_text(data)
        harness = tmp/"test.c"
        harness.write_text(TEST.replace("BIN_VALUES",",".join(str(x)+"ULL" for x in rates)))
        for compiler in ("gcc","clang"):
            binary = tmp/compiler
            subprocess.run([compiler,"-std=c11","-Wall","-Wextra","-Werror",
                            "-fsanitize=address,undefined","-fno-sanitize-recover=all",
                            "-fno-omit-frame-pointer","-I",str(tmp),
                            str(tmp/"phy-qcom-mipi-csi2-cphy-config.c"),str(harness),
                            "-o",str(binary)],check=True)
            run = subprocess.run([str(binary)],capture_output=True,text=True,check=True)
            records.append({"compiler":compiler,"result":json.loads(run.stdout)})
    print(json.dumps({"result":"PASS_CPHY_NUMERICAL_PREPARATION_SOURCE_ONLY",
                      "source_sha256":SOURCE_PINS,"public_header_sha256":PUBLIC_PIN,
                      "compilers":records,"hardware_qualified":False,
                      "settle_timing_or_clock_domain_qualified":False,
                      "runtime_caller_present":False}))

if __name__ == "__main__":
    main()
