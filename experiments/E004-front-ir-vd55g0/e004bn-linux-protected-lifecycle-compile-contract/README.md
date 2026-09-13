# E004bn — compile-only protected camera lifecycle contract

## Result

**PASS: queue policy, per-buffer protected-sample lifetime, and secure-lane ownership are now modeled as three separate compiler-checked interfaces with zero executable runtime change.**

No protected backend exists and there is still no activation route.

## Why three interfaces

The Windows oracle proved that protected camera capture does not have one monolithic "secure mode" lifetime.

The Linux contract therefore represents three different ownership domains:

### Queue policy

`camss_protected_queue_contract` describes what a protected queue is allowed to expose.

It explicitly separates questions such as:

- CPU mappability;
- ordinary scatter/gather fallback;
- read() exposure;
- mmap exposure;
- whether imported DMABUFs require proof of protected backing.

This is policy, not allocation.

### Per-sample protected backing

`camss_protected_sample` carries:

- stable 16-byte identity;
- up to three device-visible addresses;
- per-plane sizes;
- opaque backend handle;
- prepared state.

`camss_protected_sample_ops` contains only:

- `prepare`;
- `release`.

This models the Windows per-`SecureMediaBuffer` / per-GUID lifetime.

### Secure-lane ownership

`camss_secure_lane_ops` contains only:

- `acquire`;
- `release`.

It intentionally does not live inside `sample_ops`.

That preserves the Windows-proven fact that external sample lifetime and secure CSI/worker ownership are independent resources.

## No runtime implementation

There is:

- no lifecycle-contract instance;
- no protected-sample ops instance;
- no lane ops instance;
- no queue selector;
- no V4L2 control;
- no ioctl;
- no backend handle implementation;
- no secure-memory primitive.

The only source integration is a compile-time contract assertion helper.

## Build proof

Baseline and scaffold were compiled against the Golden kernel headers.

Both report:

`7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

Their executable `.text` sections are byte-identical:

`fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e`

So the additional lifecycle model contributes no runtime instructions.

## Production state

The production CAMSS source remains unchanged.

No generated module was installed or loaded, no camera module became active, and no media/video device node appeared.

No SCM/QCOMTEE/memory-assignment/VMID implementation symbol exists in the scaffold.

## Files

- `CAMSS-PROTECTED-LIFECYCLE-SCAFFOLD.patch`
- `scaffold/camss-protected-sample.h`
- `make-lifecycle-scaffold.py`
- `evidence/BASELINE-BUILD.log`
- `evidence/SCAFFOLD-BUILD.log`
- `evidence/SCAFFOLD-GENERATE.txt`
- `evidence/BUILD-AND-LIFECYCLE-SEPARATION.txt`
- `evidence/POST-BUILD-STATE.txt`

## Next gate

Statically inventory the current kernel for protected-memory facilities that could eventually implement `camss_protected_sample_ops`.

The inventory must answer:

- what allocates the memory;
- what assigns/revokes protection;
- what object represents the allocation;
- whether a device-visible address can be supplied without CPU mapping;
- what cleanup primitive reverses ownership.

Do not invoke any of those facilities yet.
