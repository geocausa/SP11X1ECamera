#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Check open gamma against the actual existing C packer under sanitizers.

Both implementations run on synthetic mathematical curves. No firmware input,
camera devices, kernel loading or selector/register programming is involved.
"""
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import open_config as c


def main():
    repo = Path(__file__).resolve().parents[3]
    header = repo / "src/native-rgb/native-front-gamma.h"
    if not header.is_file():
        raise RuntimeError("existing independent gamma packer is missing")
    fixtures = []
    for name in ("identity", "srgb"):
        p = c.gamma_points(name)
        fixtures.append((p * 3, c.gamma_words(p) * 3))
    decl = []
    for i, (points, words) in enumerate(fixtures):
        decl.append(f"static const uint16_t points{i}[771] = {{" + ",".join(map(str, points)) + "};")
        decl.append(f"static const uint32_t expected{i}[768] = {{" + ",".join(map(str, words)) + "};")
    source = '''#include <assert.h>
#include <stdio.h>
#include <string.h>
#include "native-front-gamma.h"
''' + "\n".join(decl) + '''
static uint32_t le32(const uint8_t *p)
{
 return (uint32_t)p[0] | (uint32_t)p[1]<<8 | (uint32_t)p[2]<<16 | (uint32_t)p[3]<<24;
}
static void check(const uint16_t *points, const uint32_t *expected)
{
 uint8_t out[3072];
 unsigned int i;
 assert(native_front_gamma12_pack(points,771,out,sizeof(out))==0);
 for(i=0;i<768;i++) assert(le32(out+4*i)==expected[i]);
}
int main(void)
{
 uint8_t out[3072], before[3072];
 uint16_t bad[771];
 check(points0,expected0); check(points1,expected1);
 memset(out,0xa5,sizeof(out)); memcpy(before,out,sizeof(out));
 memcpy(bad,points0,sizeof(bad)); bad[770]=4096;
 assert(native_front_gamma12_pack(bad,771,out,sizeof(out))==-ERANGE);
 assert(!memcmp(out,before,sizeof(out)));
 memcpy(bad,points0,sizeof(bad)); bad[1]=2048;bad[0]=0;
 assert(native_front_gamma12_pack(bad,771,out,sizeof(out))==-ERANGE);
 assert(!memcmp(out,before,sizeof(out)));
 assert(native_front_gamma12_pack(points0,770,out,sizeof(out))==-EINVAL);
 assert(!memcmp(out,before,sizeof(out)));
 assert(native_front_gamma12_pack(points0,771,out,sizeof(out)-1)==-EINVAL);
 assert(!memcmp(out,before,sizeof(out)));
 puts("PASS:1536 gamma words; malformed last channel/delta/count/size reject atomically");
 return 0;
}
'''
    result = []
    with tempfile.TemporaryDirectory(prefix="sp11-open-gamma-") as tmp:
        d = Path(tmp)
        f = d / "test.c"
        f.write_text(source)
        for cc in ("gcc", "clang"):
            if not shutil.which(cc):
                raise RuntimeError(f"required compiler missing: {cc}")
            exe = d / cc
            cmd = [cc, "-std=c11", "-Wall", "-Wextra", "-Werror", "-O1", "-g",
                   "-fsanitize=address,undefined", "-fno-omit-frame-pointer",
                   "-I", str(header.parent), str(f), "-o", str(exe)]
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            p = subprocess.run([str(exe)], check=True, capture_output=True, text=True)
            result.append({"compiler": cc, "asan": True, "ubsan": True,
                           "result": "PASS", "detail": p.stdout.strip()})
    print(json.dumps({"hardware_qualified": False, "tests": result}, indent=2))


if __name__ == "__main__":
    main()
