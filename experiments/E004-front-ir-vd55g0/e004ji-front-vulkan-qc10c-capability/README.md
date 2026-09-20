# E004ji — actual SP11 Turnip Vulkan read-only QC10C import capability

2026-09-20. Parent `bbf9699`. Hardware: Microsoft SP11 X1E80100,
Adreno X1-85. **No camera modules, V4L2 nodes, DMA-BUF import, VkDevice,
GPU command submission, framebuffer, reboot, or system installation.**
Protected Golden v4 and its saved GRUB entry are unchanged.

## Why this specific additional check was necessary

E004jc/E004jh proved **27 real front IMX681 compressed QC10C frames**
with the mapped-SG DMA guard, but not converted/displayable front NV12.
The *separate* E004jh breakthrough produced a **temporary app-selectable
real optical rear** NV12 endpoint. The front needs a true compressed
10-bit decode or a separately proved safe uncompressed ISP output.

E004if/E004ig had already verified that **EGL/GBM** on installed Mesa
26.0.8 exposes a Qualcomm compressed modifier for **8-bit NV12**
but not for P030/P010 10-bit compressed formats. These EGL/GL
findings did not cover the separate Vulkan Turnip driver.
A 2026 upstream developer discussion reported displaying QC10C
buffers via a Vulkan DMA-BUF import path on *other Qualcomm hardware*:
https://lists.openwall.net/linux-kernel/2026/04/09/64 .
That experience is **not** X1E80100 driver/format authority.

## Actual live, non-invasive Vulkan format query

Instead of interpreting opaque `vulkaninfo --show-formats` summaries,
`vk-drm-modifier-probe.c` creates only a Vulkan **instance**, enumerates
the actual physical GPU and uses
`vkGetPhysicalDeviceFormatProperties2` with
`VkDrmFormatModifierPropertiesListEXT` to query format features,
modifier identifiers and DRM plane counts for five candidate YUV
formats. It uses the actual installed Mesa Freedreno **Turnip**
ICD `/usr/share/vulkan/icd.d/freedreno_icd.json`, Mesa
26.0.8-1ubuntu0.3. The Vulkan 1.4.341 headers and `vulkaninfo`
tool were downloaded from Ubuntu into a **disposable private /tmp
directory only**; no driver or package was installed on Golden.

Observed GPU: `Adreno X1-85`, Vulkan API 1.4, Qualcomm vendor
`0x5143`, actual hardware device `0x43050c01`. The device
advertises `VK_EXT_image_drm_format_modifier` and
`VK_EXT_external_memory_dma_buf`. Exact format/modifier enumeration:

| Vulkan queried format | Optimal/linear features | DRM modifiers reported |
| --- | --- | --- |
| 8-bit 2-plane NV12 `VK_FORMAT_G8_B8R8_2PLANE_420_UNORM` | nonzero | **linear 0** (2 planes) and **QCOM compressed `0x0500000000000001`** (2 planes) |
| 8-bit three-plane YUV420 | nonzero | linear 0 (3 planes) only |
| 10-bit two-plane YUV420 in P010-style 16-bit container | **zero/zero** | **none** |
| 10-bit three-plane YUV420 in 16-bit containers | **zero/zero** | **none** |
| 16-bit two-plane YUV420 | **zero/zero** | **none** |

Five executable tests PASS against the real physical GPU and the exact
source-locked front capture contract. The probe never creates
`VkDevice`, allocates/imports memory, reads any optical images or
asserts external image-import success for even the advertised formats.

**Engineering consequence:** the *installed* SP11 Turnip Vulkan
multiplanar YUV format interface does **not** advertise a 10-bit
compressed import path. This is an independent live runtime finding
consistent with the earlier EGL/GBM limitation. The tested 10-bit
Vulkan formats use 16-bit P010-style containers, **not** the exact
packed P030/TP10 `QC10C`/UBWC four-plane Y-meta/Y-data/C-meta/C-data
memory layout. A zero-feature result for them is a reason NOT to
attempt a guessed alias. It is **not** proof that a custom Vulkan
compute shader, proprietary GPU interface, different driver version,
separate CPU/hardware decoder or safe true-linear ISP output can
never solve the camera conversion.

In particular, do **not** relabel any QC10C bytes as 8-bit NV12,
use the advertised compressed NV12 modifier as if it represented
TP10, change the supported format table, reinterpret the 7,778,304
byte output as linear NV12, or arm a speculative E004in linear-ISP
candidate. The E004in FULL Y/C output proposal still lacks the
same-machine verified UBWC reset/state-clear and complete ISP
RAW10-to-8-bit NV12 programming authority.

## Reproduce with *read-only* hardware and private build inputs

The local replay requires an extracted Ubuntu arm64
`libvulkan-dev` 1.4.341.0-1 header package at
`/tmp/sp11-e004ji-front-vulkan-20260920/headers/usr/include`.
The executable is linked against the **already-installed**
`/usr/lib/aarch64-linux-gnu/libvulkan.so.1`.

```sh
cd /home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
python3 -m unittest discover \
 -s experiments/E004-front-ir-vd55g0/e004ji-front-vulkan-qc10c-capability \
 -p test_vulkan_modifier.py -v
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
```

**Next justified front path:** inspect an actual version-matched
Qualcomm 10-bit TP10/UBWC decompressor/import path with exact
metadata, tiling, alignment and independent image oracle, or
obtain precise X1E80100 ISP linear output + compression-state-reset
register evidence before any new candidate camera boot. Rear virtual
webcam remains a **temporary validated milestone**, not an
installed long-running standard camera service.
