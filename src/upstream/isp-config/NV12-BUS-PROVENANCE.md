# Independent VFE680 FULL NV12 setup

sp11-vfe680-nv12.h generates 232 bytes / 12 REG_CONT commands for the FULL Y/C
write clients. It takes even image dimensions and two caller-declared mapped
buffer extents. It reads no file, profile, carrier, schema or old command list.
It performs no allocation, MMIO, queue submission or write-client enable.

This is one part of the private startup replacement. It is not a complete
provider and has no caller in the installed camera driver. Both private runtime
dependencies remain. It cannot be submitted as a register-programming API for
applications; the eventual kernel provider must supply owned, validated inputs.

## Public reference

The exact public source is Qualcomm's camera-driver repository, revision
3f5ef25e12b501a518d2d4f4a870288e9bb127a0, tree
27e77a604ec38e82dcc0cd30d7685679b0f91ebb. Eleven selected GPL-labelled files are
listed with URL, size, Git blob and SHA-256 in nv12-bus-reference-20261012.json.
Identity checks do not settle all provenance or upstream acceptance questions.
The test preserves the source copyright/license header when extracting its
unchanged packer-selection function. Production code is independently written.

| Setup | Definition and policy |
|---|---|
| Clients and addresses | cam_vfe680.h names FULL Y/C clients 0/1, bases 0xe00/0xf00, both in completion group 0. The compiler owns only the 17 programmed fields per client; the test compares all 34 addresses with this exact source. |
| Image size | The public FULL start function writes height shifted 16 OR width. FULL output uses image width, not the RDI stride/16 encoding. Chroma has half the image height and the same interleaved byte stride. |
| Packing | The unchanged public cam_vfe_bus_ver3_get_packer_fmt() returns PLAIN_8_LSB_MSB_10, ordinal 3, for two-plane NV12. NV21 chroma and three-plane output have different choices and are explicitly checked in the reference test. This definition does not prove the processing graph's internal precision. |
| Buffer address and increment | Each address is base plus offset; increment is stride times plane height, following the public uncompressed update semantics. The declared allocation must contain the entire span. Only ordinary 32-bit addresses are supported; expanded-memory and multi-context modes are excluded. |
| Disabled state | Both client configurations are zeroed before either is configured. The compiler emits no subsequent enable. Frame-header fields, UBWC mode and MMU prefetch are cleared; frame-drop and IRQ-subsample policies request every frame. Global IRQ/group routing and ownership remain provider responsibilities. |

The supported subset is single stripe, full-frame origin zero, even dimensions
up to 16384, 16-byte-aligned strides/addresses/offsets, uncompressed two-plane
NV12, line mode and no frame header. Two numerically adjacent planes within one
allocation are legal; overlapping output spans are rejected. A legal span may
end exactly at the 32-bit address boundary. Invalid dimensions, arithmetic,
overlap, short command buffers or input/output alias leave the destination intact.

Buffer-span checks establish arithmetic only. They cannot prove IOMMU ownership,
mapping lifetime, physical aliases, cache coherency, completion, quiescence or
IRQ retirement. Disable commands must never be treated as a physical-halt proof.
Use requires exclusive ownership of an already stopped VFE and both mappings.

## Validation and reproduction

With the pinned public tree files placed below a source root, run:

```sh
python3 src/upstream/isp-config/test_vfe680_nv12.py --reference-dir "$SP11_NV12_PUBLIC_SOURCE"
```

The reference is mandatory. All eleven file identities are checked; changed,
missing and symlink inputs exercise rejection through the real validator.
GCC and Clang with ASan/UBSan run 258 geometry/buffer cases and 266 atomic
rejections each. This includes padded strides, distinct and shared allocations,
overlap, integer/address boundaries and retained output tails. Tests compile the
actual GPL packer function, not a restatement of its output values.

An ARM64 kernel object also builds on the isolated public RFC/CAMSS candidate03
with W=1 and KCFLAGS=-Werror. Only memcpy, memset and stack protection are
undefined. The new production header passes checkpatch. The probe has no camera
caller and must never be loaded; no module was linked or loaded. Evidence is in
docs/UPSTREAM-VFE680-NV12-VALIDATION-20261012.json. For a prepared kernel tree,
copy this header, sp11-cdm.h and nv12-compile-probe into a fresh build stage and
build only sp11-open-nv12.o.

## Remaining startup work

The source audit in docs/UPSTREAM-VFE680-INPUT-AUDIT-20261012.md establishes
that VFE680 uses TOP version 4 and expects top configuration via CDM. The older
CAMIF version 3 input-format logic is not a VFE680 core-field definition. Core
Bayer routing, DEMUX/CHANNEL_GAIN bypass and internal processing precision are
still unresolved. Do not fill these from private tuning or an opaque other-chip
core word.

The future provider must bind reviewed core and CSID setup, this disabled bus
setup and the existing independent processing graph to live owned resources.
It must initialize remaining shared/cache state, map completion group/IRQs,
prove physical stop and retire DMA/CDM before releasing memory. Cold-start,
stop/reopen and switching tests then require a fresh recorded candidate with
private loaders and retained startup/steady-update carrier fallbacks absent.
No system suspend tests are permitted. Rear GRBG processing remains a separate
qualification, although the output-only NV12 geometry helper is reusable.
