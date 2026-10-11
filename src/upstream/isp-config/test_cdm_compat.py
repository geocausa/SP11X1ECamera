#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compare bounded encoding against pinned, actual GPL CDM source functions.

The public source is an explicit test-only input. Production headers do not load
it. Private profile inputs and camera devices are never read. Reference function
bodies are extracted unchanged into temporary test source, with attribution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


def extract(text, pattern):
    match = re.search(pattern, text, re.S | re.M)
    if not match:
        raise ValueError(f"reference declaration missing: {pattern}")
    return match.group(0)


def function(text, name):
    match = re.search(r"^uint32_t\s*(?:\*\s*)?" + name + r"\s*\(", text, re.M)
    if not match:
        raise ValueError(f"reference function missing: {name}")
    begin = text.index("{", match.start())
    level = 0
    for at in range(begin, len(text)):
        level += (text[at] == "{") - (text[at] == "}")
        if level == 0:
            return text[match.start():at + 1]
    raise ValueError(f"unclosed reference function: {name}")


def reference(source, manifest):
    data = source.read_bytes()
    header = source.with_suffix(".h").read_bytes()
    for name, content, expected in [("C source", data, manifest["sha256"]),
                                    ("header", header, manifest["header_sha256"])]:
        if hashlib.sha256(content).hexdigest() != expected:
            raise ValueError(f"{name} differs from the pinned GPL reference")
    text = data.decode()
    license_comment = text.split("#include", 1)[0]
    parts = [license_comment,
             extract(header.decode(), r"enum cam_cdm_command \{.*?^\};"),
             extract(text, r"^#define CAM_CDM_SW_CMD_COUNT[^\n]+"),
             extract(text, r"^static unsigned int CDMCmdHeaderSizes\[.*?^\};"),
             extract(text, r"^struct cdm_regcontinuous_cmd \{.*?^\} __attribute__\(\(__packed__\)\);"),
             extract(text, r"^struct cdm_dmi_cmd \{.*?^\} __attribute__\(\(__packed__\)\);")]
    parts += [function(text, name) for name in
              ("cam_cdm_get_cmd_header_size", "cam_cdm_write_regcontinuous", "cam_cdm_write_dmi")]
    return "\n".join(parts)


HARNESS = r'''
static void check_reg(size_t count, uint32_t reg)
{
 uint32_t *values=calloc(count,4), *expected=calloc(count+2,4);
 uint8_t *actual=malloc((count+2)*4+4);
 assert(values && expected && actual);
 for(size_t i=0;i<count;i++) values[i]=(uint32_t)(i*2654435761U);
 memset(actual,0xa5,(count+2)*4+4);
 assert(cam_cdm_write_regcontinuous(expected,reg,count,values)==expected+count+2);
 assert(sp11_cdm_reg_cont(actual,(count+2)*4+4,reg,values,count)==0);
 assert(!memcmp(actual,expected,(count+2)*4));
 for(size_t i=(count+2)*4;i<(count+2)*4+4;i++) assert(actual[i]==0xa5);
 free(values);free(expected);free(actual);
}
int main(void)
{
 const uint32_t lengths[]={4,16,68,256,512,884,1024,4096,65536};
 const uint32_t selectors[]={0,1,3,255};
 uint32_t expected[3];uint8_t actual[16];
 for(size_t count=1;count<=96;count++) check_reg(count,0x400+count*4);
 check_reg(65535,0);
 for(size_t n=0;n<sizeof(lengths)/sizeof(lengths[0]);n++)
 for(size_t s=0;s<sizeof(selectors)/sizeof(selectors[0]);s++) {
  /* Synthetic DMA addresses, not addresses observed on hardware. */
  uint32_t base=0x100000U,off=64U,reg=0x500U;
  memset(expected,0,sizeof(expected));memset(actual,0xa5,sizeof(actual));
  assert(cam_cdm_write_dmi(expected,CAM_CDM_CMD_DMI,reg,selectors[s],base+off,
                           lengths[n]-1)==expected+3);
  assert(sp11_cdm_dmi(actual,sizeof(actual),reg,selectors[s],base,
                      lengths[n]+off,off,lengths[n])==0);
  assert(!memcmp(actual,expected,12));
  for(size_t i=12;i<16;i++) assert(actual[i]==0xa5);
 }
 puts("PASS: 97 REG_CONT and 36 DMI cases match the actual pinned GPL functions");
 return 0;
}
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    manifest = json.loads((here / "cdm-reference-20261011.json").read_text())
    ref = reference(args.source, manifest)
    preamble = '''#include <assert.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sp11-cdm.h"
#if __BYTE_ORDER__ != __ORDER_LITTLE_ENDIAN__
#error "The GPL reference's bitfield ABI comparison requires little endian"
#endif
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-parameter"
'''
    source = preamble + ref + '\n#pragma GCC diagnostic pop\n' + HARNESS
    results = []
    with tempfile.TemporaryDirectory(prefix="sp11-open-cdm-") as tmp:
        d = Path(tmp)
        f = d / "test.c"
        f.write_text(source)
        for cc in ("gcc", "clang"):
            if not shutil.which(cc):
                raise RuntimeError(f"required compiler missing: {cc}")
            exe = d / cc
            subprocess.run([cc, "-std=c11", "-Wall", "-Wextra", "-Werror", "-O1", "-g",
                            "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
                            "-I", str(here), str(f), "-o", str(exe)],
                           check=True, capture_output=True, text=True)
            p = subprocess.run([str(exe)], check=True, capture_output=True, text=True)
            results.append({"compiler": cc, "result": "PASS", "asan": True, "ubsan": True,
                            "detail": p.stdout.strip()})
    print(json.dumps({"hardware_access": False, "private_profile_read": False,
                      "reference_sha256": manifest["sha256"], "tests": results}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        print(error.stderr or error.stdout, file=sys.stderr)
        raise
