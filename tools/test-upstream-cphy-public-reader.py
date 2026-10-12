#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Execute pinned GPL C-PHY data-rate selection and settle substitution in a host model."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import tempfile

PINS = {
    "cam_csiphy_2_1_2_hwreg.h": "1f5dc382c0d3d62714195022f2b811a058eb80642821c38f5737488d36352bf5",
    "downstream-semantics-01/cam_csiphy_dev.h": "efef1af717f54ad458a1db00c989fcaa4fdd775a8572d49ea8924cfad0ccee82",
    "downstream-semantics-01/cam_csiphy_core.c": "8a0e25e478bb76cef373b6a8ddfba03554a81e3bf9919371541b2c606da22119",
}
def pinned(root, name, pin):
    p = root
    for part in Path(name).parts:
        p /= part
        if p.is_symlink():
            raise ValueError("Reference symlink: " + name)
    data = p.read_bytes()
    if hashlib.sha256(data).hexdigest() != pin:
        raise ValueError("Reference pin mismatch: " + name)
    return data.decode()

def declaration(text, marker):
    start = text.index(marker)
    brace = text.index("{", start)
    end = brace + 1
    depth = 1
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
#include <stddef.h>
#include <string.h>
#include <sys/types.h>
#define BIT(n) (1U << (n))
#define BIT_ULL(n) (1ULL << (n))
#define ARRAY_SIZE(a) (sizeof(a) / sizeof((a)[0]))
#define __iomem
#define MAX_CSIPHY 8
#define CAM_CSIPHY_MAX_DATARATE_VARIANTS 3
#define CAM_CSIPHY_DATARATE_SHORT_CHANNEL 0
#define CAM_CSIPHY_DATARATE_STANDARD_CHANNEL 1
#define CAM_CSIPHY 0
#define CAM_ERR(...) ((void)0)
#define CAM_DBG(...) ((void)0)
#define CAM_BOOL_TO_YESNO(v) ((v) ? "yes" : "no")
#define do_div(n, d) ((n) /= (d))
"""
MODEL = r"""
struct cam_csiphy_dev_cdr_sweep_params {
 bool cdr_sweep_enabled;
 uint32_t cdr_tolerance, tolerance_op_type;
 int32_t *cdr_config_ptr;
};
struct ctrl_reg { struct data_rate_settings_t *data_rates_settings_table; };
struct csiphy_device {
 struct ctrl_reg *ctrl_reg;
 struct { unsigned int index; struct { void *mem_base; } reg_map[1]; } soc_info;
 struct { uint64_t data_rate, settle_time; uint32_t channel_type; } csiphy_info[1];
 struct cam_csiphy_dev_cdr_sweep_params cdr_params;
 unsigned int curr_data_rate_idx;
};
static struct { uint64_t data_rate_aux_mask; } g_phy_data[MAX_CSIPHY];
static unsigned char mmio[0x2000];
static struct { uint32_t offset, value; } writes[128];
static unsigned int count, delays;
static void cam_io_w_mb(uint32_t value, void *address)
{
 uintptr_t offset = (uintptr_t)address - (uintptr_t)mmio;
 assert(offset < sizeof(mmio) && !(offset & 3) && value <= 255);
 assert(count < ARRAY_SIZE(writes));
 writes[count].offset = offset; writes[count++].value = value;
}
static void usleep_range(int32_t low, int32_t high) { assert(low >= 0 && high >= low); delays++; }
static void __cam_csiphy_compute_cdr_value(int32_t *value, struct csiphy_device *device)
{
 (void)value; (void)device;
 assert(!"CDR sweep is outside this test model");
}
"""
TEST = r"""
int main(void)
{
 struct data_rate_settings_t settings = {
  .num_data_rate_settings = ARRAY_SIZE(data_rate_settings_2_1_2),
  .data_rate_settings = data_rate_settings_2_1_2,
 };
 struct ctrl_reg ctrl = { .data_rates_settings_table = &settings };
 struct csiphy_device dev = { .ctrl_reg = &ctrl };
 const uint16_t settles[] = { 0, 34, 256, 65535 };
 unsigned int cases = 0, settle_writes = 0, cdr_writes = 0;
 dev.soc_info.reg_map[0].mem_base = mmio;
 for (unsigned int b = 0; b < ARRAY_SIZE(data_rate_settings_2_1_2); b++) {
  uint64_t bw = data_rate_settings_2_1_2[b].bandwidth;
  for (int delta = -1; delta <= 1; delta++) {
   unsigned int expected = b + (delta > 0 && b + 1 < ARRAY_SIZE(data_rate_settings_2_1_2));
   for (unsigned int phy = 0; phy < MAX_CSIPHY; phy++) {
    dev.soc_info.index = phy;
    for (unsigned int st = 0; st < ARRAY_SIZE(settles); st++) {
     dev.csiphy_info[0].data_rate = bw + delta;
     dev.csiphy_info[0].settle_time = (uint64_t)settles[st] * 200000000;
     count = delays = 0;
     assert(cam_csiphy_cphy_data_rate_config(&dev, 0, 0) == 0);
     assert(dev.curr_data_rate_idx == expected);
     struct data_rate_reg_info_t *bin = &data_rate_settings_2_1_2[expected];
     assert(count == (unsigned int)bin->data_rate_reg_array_size);
     struct csiphy_reg_t *rows = bin->data_rate_reg_array[phy][0];
     unsigned int lowers = 0, uppers = 0, cdrs = 0;
     for (unsigned int i = 0; i < count; i++) {
      assert(writes[i].offset == (uint32_t)rows[i].reg_addr);
      if (rows[i].csiphy_param_type == CSIPHY_SETTLE_CNT_LOWER_BYTE) {
       assert(writes[i].value == (settles[st] & 255)); lowers++; settle_writes++;
      } else if (rows[i].csiphy_param_type == CSIPHY_SETTLE_CNT_HIGHER_BYTE) {
       assert(writes[i].value == (settles[st] >> 8)); uppers++; settle_writes++;
      } else {
       assert(writes[i].value == (uint32_t)rows[i].reg_data);
       if (rows[i].csiphy_param_type == CSIPHY_CDR_LN_SETTINGS) { cdrs++; cdr_writes++; }
      }
     }
     assert(lowers == 3 && uppers == 3 && cdrs == 3);
     cases++;
    }
   }
  }
 }
 count = 0;
 dev.soc_info.index = MAX_CSIPHY;
 assert(cam_csiphy_cphy_data_rate_config(&dev, 0, 0) == -EINVAL && count == 0);
 dev.soc_info.index = 0;
 assert(cam_csiphy_cphy_data_rate_config(&dev, 0, CAM_CSIPHY_MAX_DATARATE_VARIANTS) == -EINVAL && count == 0);
 assert(cam_csiphy_cphy_data_rate_config(&dev, 0, 1) == -EINVAL && count == 0);
 assert(cam_csiphy_cphy_data_rate_config(0, 0, 0) == -EINVAL && count == 0);
 dev.ctrl_reg = 0;
 assert(cam_csiphy_cphy_data_rate_config(&dev, 0, 0) == -EINVAL && count == 0);
 dev.ctrl_reg = &ctrl;
 ctrl.data_rates_settings_table = 0;
 assert(cam_csiphy_cphy_data_rate_config(&dev, 0, 0) == 0 && count == 0);
 ctrl.data_rates_settings_table = &settings;
 dev.csiphy_info[0].data_rate = UINT64_MAX;
 assert(cam_csiphy_cphy_data_rate_config(&dev, 0, 0) == 0);
 assert(dev.curr_data_rate_idx == ARRAY_SIZE(data_rate_settings_2_1_2) - 1);
 printf("{\"bins\":%zu,\"boundary_phy_settle_cases\":%u,\"dynamic_settle_writes\":%u,\"default_cdr_writes\":%u,\"early_error_controls\":5,\"missing_table_noop\":true,\"above_maximum_clamps_last_bin\":true}\n",
        ARRAY_SIZE(data_rate_settings_2_1_2), cases, settle_writes, cdr_writes);
 return 0;
}
"""
def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--reference-directory", type=Path, required=True)
    args = p.parse_args()
    data = {n: pinned(args.reference_directory, n, pin) for n, pin in PINS.items()}
    dev = data["downstream-semantics-01/cam_csiphy_dev.h"]
    hdr = data["cam_csiphy_2_1_2_hwreg.h"]
    core = data["downstream-semantics-01/cam_csiphy_core.c"]
    macros = "\n".join(re.findall(r"^#define CSIPHY_[A-Z0-9_]+\s+BIT\(\d+\).*$", dev, re.M))
    structs = "\n".join(declaration(dev, "struct " + n + " {") + ";" for n in
                        ("csiphy_reg_t", "data_rate_reg_info_t", "data_rate_settings_t"))
    names = re.findall(r"^struct csiphy_reg_t (datarate_212_\w+)\[\]", hdr, re.M)
    assert len(names) == 28
    arrays = "\n".join(declaration(hdr, "struct csiphy_reg_t " + n + "[]") + ";" for n in names)
    table = declaration(hdr, "static struct data_rate_reg_info_t data_rate_settings_2_1_2[]") + ";"
    actual = declaration(core, "static int cam_csiphy_cphy_data_rate_config(")
    records = []
    with tempfile.TemporaryDirectory(prefix="sp11-cphy-public-reader-") as tmp:
        tmp = Path(tmp)
        source = tmp / "reader.c"
        source.write_text("\n".join((PRELUDE, macros, structs, arrays, table, MODEL, actual, TEST)))
        for compiler in ("gcc", "clang"):
            binary = tmp / compiler
            subprocess.run([compiler, "-std=gnu11", "-Wall", "-Wextra", "-Werror",
                            "-fsanitize=address,undefined", "-fno-sanitize-recover=all",
                            "-fno-omit-frame-pointer", str(source), "-o", str(binary)], check=True)
            run = subprocess.run([str(binary)], text=True, capture_output=True, check=True)
            records.append({"compiler": compiler, "result": json.loads(run.stdout)})
    print(json.dumps({"result": "PASS_PUBLIC_CPHY_READER_SEMANTICS_SOURCE_ONLY",
                      "source_sha256": PINS, "actual_function": "cam_csiphy_cphy_data_rate_config",
                      "compilers": records, "hardware_qualified": False,
                      "limits": ["Host MMIO and sleep models", "CDR sweep/auxiliary settings not enabled",
                                 "No generic C-PHY mode/API or live board graph qualification",
                                 "Downstream out-of-range clamp and missing-table no-op must not be treated as upstream admission"]}))

if __name__ == "__main__":
    main()
