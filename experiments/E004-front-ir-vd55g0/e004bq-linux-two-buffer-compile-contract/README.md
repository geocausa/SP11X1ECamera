# E004bq — compile-only Linux two-buffer protected pipeline contract

## Result

**PASS: the Linux compile-only design now mirrors the Windows two-buffer protected-camera architecture while still producing zero executable runtime change.**

E004bp corrected the parity model:

`camera HW → internal CP_CAMERA target → protected transfer/processing → external protected sample`

with queue policy and secure-lane ownership remaining separate concerns.

E004bq represents those ownership domains as separate compiler-checked types.

## Contract domains

### Queue policy

`camss_protected_queue_contract` remains separate from all buffer ownership.

It models whether a protected queue may expose:

- CPU mapping;
- ordinary SG fallback;
- read();
- mmap();
- imported DMABUFs without proof of protected backing.

### Internal secure capture target

`camss_secure_capture_target` is the future analogue of Windows' worker-created CP_CAMERA target.

It carries separate fields for:

- a stable internal identity;
- physical ownership range;
- ownership size;
- CAMSS-visible DMA/IOVA per plane;
- plane sizes;
- opaque backend handle;
- prepared state.

The physical range and CAMSS IOVA are deliberately different fields because E004bo proved that SP11 CAMSS is SMMU-attached and ordinary `sg_dma_address()` is not proof of physical identity.

No VMID or permission value is encoded in this type.

### External protected sample

`camss_external_protected_sample` models the consumer-facing protected object.

It carries:

- stable identity;
- plane sizes;
- opaque backend handle;
- prepared state.

It intentionally contains **no CAMSS IOVA**. E004bp proved the Windows external VTL1 sample is not the direct IFE hardware target.

### Protected transfer boundary

`camss_protected_transfer_ops` takes:

- internal secure capture target as source;
- external protected sample as destination.

It does not define how that transfer is implemented.

That implementation may eventually require a protected execution context, but E004bq makes no such choice.

### Secure lane ownership

`camss_secure_lane_ops` remains an independent acquire/release interface.

It does not live inside either buffer object and does not share their lifetime.

## No runtime implementation

E004bq deliberately defines no:

- contract instance;
- capture-target backend;
- external-sample backend;
- transfer implementation;
- lane implementation;
- queue selector;
- V4L2 control;
- ioctl;
- SCM operation;
- QCOMTEE operation;
- VMID selection.

The only integration into `camss-video.c` is a compile-time assertion helper.

## Mechanical zero-runtime proof

Baseline and scaffold modules were built from the same production CAMSS source with the Golden kernel headers.

Both have vermagic:

`7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

Their extracted executable `.text` sections are byte-for-byte identical:

`fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e`

No operation callback has a call site.

A focused scan finds zero implementation references to Qualcomm SCM, QCOMTEE, memory assignment, DMA-heap allocation, hypervisor assignment, IUM, or protected MMIO helpers.

## Relationship to E004bm / E004bn

E004bm and E004bn were useful compile-only stepping stones, but their single protected-sample object was too coarse for exact Windows parity.

E004bq supersedes that shape conceptually without rewriting prior checkpoints:

- old single protected sample → split into internal capture target + external sample;
- new explicit transfer interface connects them;
- secure lane remains independent;
- queue policy remains independent.

## Safety state

The production CAMSS source is untouched.

No generated module was installed or loaded. No media/video node appeared. No secure-memory operation, SCM call, VMID assignment, QCOMTEE load, or protected MMIO access occurred.

## Files

- `CAMSS-TWO-BUFFER-PROTECTED-CONTRACT.patch`
- `scaffold/camss-protected-pipeline.h`
- `make-two-buffer-scaffold.py`
- `evidence/BASELINE-BUILD.log`
- `evidence/SCAFFOLD-BUILD.log`
- `evidence/SCAFFOLD-GENERATE.txt`
- `evidence/BUILD-AND-ZERO-RUNTIME.txt`
- `evidence/POST-BUILD-STATE.txt`

## Next gate

Statically map what a Linux protected transfer backend would need to provide between the internal CP_CAMERA capture target and the external protected sample.

That analysis must remain non-executing and must not assume that ordinary CPU memcpy is acceptable for the final protected path.
