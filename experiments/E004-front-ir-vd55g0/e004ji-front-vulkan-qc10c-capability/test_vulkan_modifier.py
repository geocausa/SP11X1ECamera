#!/usr/bin/env python3
"""E004ji SP11 Golden-v4 actual Turnip Vulkan read-only modifier regression.

Only Vulkan instance/physical format query; deliberately NO VkDevice, DMA-BUF
import, pixel operations, camera nodes, UBWC reinterpretation, kernel, IR.
"""
from pathlib import Path
import hashlib
import os
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
PRIVATE=Path("/tmp/sp11-e004ji-front-vulkan-20260920")
SOURCE=HERE/"vk-drm-modifier-probe.c"
HEADER=PRIVATE/"headers/usr/include/vulkan/vulkan.h"
LIB="/usr/lib/aarch64-linux-gnu/libvulkan.so.1"
ICD="/usr/share/vulkan/icd.d/freedreno_icd.json"
EXPECTED_COMPRESSED=0x0500000000000001

class PhysicalVulkanCapability(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        for file in (HEADER,SOURCE,Path(LIB),Path(ICD)):
            if not file.is_file():
                raise RuntimeError("E004JI_MISSING_OFFLINE_DEPENDENCY "+str(file))
        cls.target=PRIVATE/"vk-drm-modifier-probe"
        cmd=["gcc","-std=c11","-Wall","-Wextra","-Werror","-pedantic","-O2",
             "-I"+str(PRIVATE/"headers/usr/include"),str(SOURCE),LIB,
             "-o",str(cls.target)]
        build=subprocess.run(cmd,capture_output=True,text=True,timeout=35)
        if build.returncode:
            raise RuntimeError("E004JI_VULKAN_PROBE_COMPILE_FAIL "+build.stderr[-1000:])
        cls.probe=subprocess.run([str(cls.target)],capture_output=True,text=True,
                 env={**os.environ,"VK_ICD_FILENAMES":ICD},timeout=32)
        if cls.probe.returncode:
            raise RuntimeError("E004JI_FREEDRENO_QUERY_FAIL "+cls.probe.stderr[-1000:])
        cls.rows=cls.probe.stdout.splitlines()

    def format(self,name):
        prefix="VK_FORMAT name="+name+" "
        row=next((line for line in self.rows if line.startswith(prefix)),None)
        self.assertIsNotNone(row,name)
        keyvals=dict(part.split("=",1) for part in row.split() if "=" in part)
        return keyvals

    def modifiers(self,name):
        prefix="DRM_MODIFIER format="+name+" "
        rows=[line for line in self.rows if line.startswith(prefix)]
        return [dict(part.split("=",1) for part in line.split() if "=" in part)
                for line in rows]

    def test_actual_sp11_turnip_and_two_external_memory_extensions(self):
        self.assertTrue(any("name=Adreno X1-85" in s and "vendor=0x5143" in s
           and "drm_modifier_ext=1" in s and "dma_buf_ext=1" in s
           for s in self.rows),"\n".join(self.rows))
        self.assertIn("VULKAN_GPU name=Adreno X1-85",self.probe.stdout)

    def test_8_bit_nv12_advertises_linear_and_qualcomm_compressed_modifier(self):
        fmt=self.format("NV12_8BIT")
        self.assertGreater(int(fmt["modifiers"]),0)
        mods=self.modifiers("NV12_8BIT")
        self.assertIn(0,[int(x["modifier"],16) for x in mods])
        self.assertIn(EXPECTED_COMPRESSED,[int(x["modifier"],16) for x in mods])
        for m in mods:self.assertEqual(int(m["planes"]),2)

    def test_ten_bit_two_plane_and_three_plane_not_advertised(self):
        for name in ("P010_10BIT_16_CONTAINER","YUV420_10BIT_3PLANE",
                     "P016_16BIT_CONTAINER"):
            fmt=self.format(name)
            self.assertEqual(int(fmt["optimal"],16),0,name)
            self.assertEqual(int(fmt["linear"],16),0,name)
            self.assertEqual(int(fmt["modifiers"]),0,name)
            self.assertEqual(self.modifiers(name),[])
        # Even P010-style 16-bit-container absence is not a tested exact
        # QC10C/P030 import; this is a reason NOT to attempt unsafe aliasing.

    def test_exact_front_contract_remains_compressed_not_nv12(self):
        import json
        plan=json.loads((REPO/"src/front-imx681/desktop-output-contract.json").read_text())
        self.assertEqual(plan["v4l2_fourcc"],"Q10C")
        self.assertEqual(plan["allocation_bytes"],7778304)
        self.assertEqual([x["name"] for x in plan["regions"]],
             ["Y_META","Y_TP10","C_META","C_TP10"])
        self.assertEqual(sum(x["size"] for x in plan["regions"]),7778304)
        self.assertFalse(plan["linear_nv12"])
        self.assertFalse(plan["desktop_conversion_proven"])

    def test_read_only_probe_has_no_pixel_import_or_camera_activity(self):
        src=SOURCE.read_text()
        for prohibited in ("vkCreateDevice(", "vkCreateImage(", "vkAllocateMemory(",
                           "vkBindImageMemory(", "vkQueueSubmit(", "vkImportMemory",
                           "DRM_IOCTL_", "/dev/video", "/dev/media", "modprobe ",
                           "insmod ", "ILLUMINATION_ON", "grub-reboot"):
            self.assertNotIn(prohibited,src)
        self.assertIn("vkGetPhysicalDeviceFormatProperties2",src)
        self.assertIn("VK_STRUCTURE_TYPE_DRM_FORMAT_MODIFIER_PROPERTIES_LIST_EXT",src)

if __name__=="__main__":
    unittest.main(verbosity=2)
