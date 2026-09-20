#!/usr/bin/env python3
"""E004ip QC10C scratch safety audit + compile/run the exact inserted C body.

Mock SG entries exercise the actual source body; this is NOT a live SP11
DMA-mapping/codec/camera test. A complete kernel build is run separately.
"""
from pathlib import Path
import json
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=ROOT/"src/front-imx681/kernel/camss"
PATCH=runpy.run_path(str(HERE/"make_qc10c_span.py"))

def run_exact_c_guard(compiler):
    snippet=PATCH["PATCH"]
    assert snippet.startswith("\tif (!buffer->addr[0]") and snippet.endswith("\treturn 0;\n}")
    source=r"""
#include <stdint.h>
#include <stddef.h>
#include <errno.h>
#include <stdio.h>
#define PAGE_SIZE 4096ULL
#define U32_MAX 0xffffffffULL
#define CAMSS_X1E_PIX_GATE_QC10C_BYTES 0x0076b000ULL
#define IS_ALIGNED(a, b) (((a) & ((b)-1)) == 0)
#define min_t(T, a, b) ((T)(a) < (T)(b) ? (T)(a) : (T)(b))
typedef uint64_t u64;
typedef uint64_t dma_addr_t;
struct scatterlist { dma_addr_t addr; unsigned int len; };
struct sg_table { struct scatterlist *sgl; unsigned int nents; };
struct vb2_buffer { struct sg_table *sgt; };
struct buffer { dma_addr_t addr[3]; };
#define sg_dma_address(sg) ((sg)->addr)
#define sg_dma_len(sg) ((sg)->len)
#define vb2_dma_sg_plane_desc(vb, plane) ((vb)->sgt)
#define for_each_sgtable_dma_sg(sgt, sg, i) \
  for ((i)=0, (sg)=(sgt)->sgl; (i)<(sgt)->nents; (i)++, (sg)++)
static int check(struct buffer *buffer, struct vb2_buffer *vb) {
    u64 end;
""" + snippet + r"""
static int failures = 0;
static void check_case(const char *name, struct buffer *b,
    struct vb2_buffer *v, int expected)
{
    int got = check(b, v);
    if ((got==0) != expected) {
        fprintf(stderr,"FAIL %s result=%d expected_accept=%d\n",name,got,expected);
        failures++;
    } else printf("E004IP_C_GUARD_PASS %s\n",name);
}
int main(void)
{
    const uint64_t base=0x10000000ULL;
    struct buffer b={{base,0,0}};
    struct scatterlist sg[3] = {{base, 0x400000}, {base+0x400000,0x36b000}, {0,0}};
    struct sg_table sgt={sg,2};
    struct vb2_buffer vb={&sgt};
    check_case("two_adjacent_segments", &b, &vb,1);
    sgt.nents=1; sg[0].len=0x76b000;
    check_case("single_contiguous_segment", &b, &vb,1);
    sgt.nents=2; sg[0].len=0x400000; sg[1].len=0x36b000;
    sg[1].addr=base+0x400001;
    check_case("one_byte_gap", &b, &vb,0);
    sg[1].addr=base+0x3fffff;
    check_case("one_byte_overlap", &b, &vb,0);
    sg[1].addr=base+0x400000;sg[1].len=0x36afff;
    check_case("short_total", &b, &vb,0);
    sg[1].len=0x36b000;sg[0].len=0;
    check_case("zero_first_segment", &b, &vb,0);
    sg[0].len=0x400000;b.addr[0]=base+4096;
    check_case("cached_dma_base_mismatch", &b, &vb,0);
    b.addr[0]=base;sgt.nents=0;
    check_case("zero_mapped_segments", &b, &vb,0);
    sgt.nents=2;vb.sgt=NULL;
    check_case("missing_mapped_sg_table", &b, &vb,0);
    vb.sgt=&sgt; b.addr[0]=0xffff0000ULL;sg[0].addr=b.addr[0];
    check_case("crosses_32bit_dma_window", &b, &vb,0);
    if (failures) return 1;
    puts("E004IP_EXACT_INSERTED_C_GUARD_ALL_CASES=PASS");
    return 0;
}
"""
    with tempfile.TemporaryDirectory(prefix="sp11-e004ip-c-") as d:
        path=Path(d)
        (path/"guard.c").write_text(source)
        cmd=[compiler,"-std=gnu11","-O1","-g","-Wall","-Wextra","-Werror",
             "-fsanitize=address,undefined","-fno-omit-frame-pointer",
             str(path/"guard.c"),"-o",str(path/"guard")]
        compiled=subprocess.run(cmd,capture_output=True,text=True,timeout=35)
        if compiled.returncode:
            raise RuntimeError("C fixture compilation failed:\n"+compiled.stderr)
        run=subprocess.run([str(path/"guard")],capture_output=True,text=True,timeout=35)
        if run.returncode:
            raise RuntimeError("EXACT inserted C body fixture failure:\n"+run.stdout+run.stderr)
        if run.stdout.count("E004IP_C_GUARD_PASS ")!=10:
            raise ValueError("expected ten successful C guard cases")
        return run.stdout

class StageTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory(prefix="sp11-e004ip-test-")
        self.addCleanup(self.td.cleanup)
        self.scratch=Path(self.td.name)/"camss"
        shutil.copytree(SOURCE,self.scratch,symlinks=True)
        PATCH["make"](SOURCE,self.scratch)

    def test_parent_stage_unchanged_and_scratch_protected(self):
        self.assertTrue(PATCH["audit"](self.scratch)["v4l2_nv12_streaming_still_forbidden"])

    def test_reject_changed_accepted_qc10c_geometry(self):
        target=self.scratch/"camss.c"
        target.write_text(target.read_text().replace(
            "CAMSS_X1E_PIX_GATE_QC10C_BYTES - 1","4096 - 1",1))
        with self.assertRaises(ValueError):
            PATCH["audit"](self.scratch)

    def test_reject_removed_dma_gap_detection(self):
        target=self.scratch/"camss.c"
        target.write_text(target.read_text().replace(
            "sg_dma_address(sg) != cursor", "sg_dma_address(sg) == cursor",1))
        with self.assertRaises(ValueError):
            PATCH["audit"](self.scratch)

    def test_reject_new_hardware_write(self):
        target=self.scratch/"camss.c"
        target.write_text(target.read_text().replace(
            "u64 remaining = CAMSS_X1E_PIX_GATE_QC10C_BYTES;",
            "writel_relaxed(0, hw);u64 remaining = CAMSS_X1E_PIX_GATE_QC10C_BYTES;",1))
        with self.assertRaises(ValueError):
            PATCH["audit"](self.scratch)

    def test_actual_compiled_guard_ten_dma_cases_gcc(self):
        self.assertIn("ALL_CASES=PASS",run_exact_c_guard("gcc"))

    def test_actual_compiled_guard_ten_dma_cases_clang(self):
        self.assertIn("ALL_CASES=PASS",run_exact_c_guard("clang"))

if __name__=="__main__":
    if len(sys.argv)==3 and sys.argv[1]=="--inspect":
        print(json.dumps(PATCH["audit"](Path(sys.argv[2])),sort_keys=True,indent=2))
    else:
        unittest.main(verbosity=2)
