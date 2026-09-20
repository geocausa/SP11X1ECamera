#!/usr/bin/env python3
"""E004io: mutation tests for scratch-only contiguous DMA-span protection."""
from pathlib import Path
import json
import runpy
import shutil
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ACCEPTED=ROOT/"src/front-imx681/kernel/camss"
PATCH=runpy.run_path(str(HERE/"make_dma_span.py"))

class DmaSpanTests(unittest.TestCase):
    def setUp(self):
        self.td=tempfile.TemporaryDirectory(prefix="sp11-e004io-test-")
        self.addCleanup(self.td.cleanup)
        self.scratch=Path(self.td.name)/"camss"
        shutil.copytree(ACCEPTED,self.scratch,symlinks=True)
        PATCH["make"](ACCEPTED,self.scratch)

    def test_compiled_source_plan_is_fail_closed(self):
        r=PATCH["audit"](self.scratch)
        self.assertEqual(r["required_mapped_dma_segments"],1)
        self.assertEqual(r["required_first_mapped_segment_bytes"],5529600)
        self.assertTrue(r["non_contiguous_mapped_vb2_buffer_rejected"])
        self.assertEqual(r["new_mmio_calls"],0)

    def mutate_and_reject(self,old,new):
        f=self.scratch/"camss-vfe-680.c"
        content=f.read_text()
        self.assertIn(old,content)
        f.write_text(content.replace(old,new,1))
        with self.assertRaises(ValueError):
            PATCH["audit"](self.scratch)

    def test_reject_removed_single_dma_segment_check(self):
        self.mutate_and_reject("sgt->nents != 1", "sgt->nents > 4")

    def test_reject_wrong_mapped_dma_size(self):
        self.mutate_and_reject("sg_dma_len(sgt->sgl) < VFE680_X1E_LINEAR_NV12_ALLOCATION",
                               "sg_dma_len(sgt->sgl) < 4096")

    def test_reject_stale_dma_base(self):
        self.mutate_and_reject("sg_dma_address(sgt->sgl) != buffer->addr[0]",
                               "sg_dma_address(sgt->sgl) == buffer->addr[0]")

    def test_reject_unverified_chroma_address(self):
        self.mutate_and_reject("buffer->addr[1] != (dma_addr_t)chroma", "false")

    def test_reject_mapped_sg_table_bypass(self):
        self.mutate_and_reject("vb2_dma_sg_plane_desc(&buffer->vb.vb2_buf, 0)",
                               "NULL")

    def test_reject_early_streaming_authorization(self):
        self.mutate_and_reject("out->approved_for_hardware = false;",
                               "out->approved_for_hardware = true;")

    def test_reject_unrelated_live_driver_change(self):
        f=self.scratch/"camss.c"
        f.write_text(f.read_text()+"\n/* unexpected live source change */\n")
        with self.assertRaises(ValueError):
            PATCH["audit"](self.scratch)

if __name__=="__main__":
    if len(sys.argv)==3 and sys.argv[1]=="--inspect":
        print(json.dumps(PATCH["audit"](Path(sys.argv[2])),sort_keys=True,indent=2))
    else:
        unittest.main(verbosity=2)
