# E004bu — internal protected-target ACL contract

## Result

**PASS: the compile-only CAMSS protected-target contract now encodes the Windows-proven simultaneous hardware + trusted-worker visibility lifetime, while retaining zero executable runtime change and no concrete VMID/service/permission choice.**

E004bt changed the architectural premise: protected memory is not correctly modeled as one Boolean `assigned` state. Windows keeps the internal backing mapped to its VTL1 worker while the same section is assigned into SoC domain `0x0d`; Linux SCM can represent multi-owner ACLs, but the camera-specific owner set remains unproven.

E004bu updates the compiler-checked contract to reflect that fact without implementing any secure operation.

## Contract correction

### Explicit owner-set visibility state

`camss_protected_owner_set_contract` now separates:

- owner count;
- camera-hardware visibility;
- trusted-worker visibility;
- normal-HLOS CPU visibility;
- whether concrete owner IDs are resolved;
- whether concrete permissions are resolved.

No VMID, SCM permission constant, QTEE UID, or secure-domain number is encoded.

This means a future backend cannot quietly collapse:

`camera hardware visibility + trusted worker visibility`

into a single `assigned = true` bit.

### Internal target lifecycle phases

The internal target now has explicit phases:

1. `UNPREPARED`;
2. `BACKING_READY`;
3. `ACTIVE_VISIBILITY`;
4. `REVOKING_VISIBILITY`.

This mirrors the Windows lifetime rule proven by E004bt: backing/mapping exists first, hardware-domain visibility is activated while the trusted view remains alive, and hardware assignment is revoked before the trusted mapping/backing is released.

### Split target operations

The old coarse `prepare()/release()` pair is replaced in the compile contract by:

- `prepare_backing()`;
- `activate_visibility()`;
- `deactivate_visibility()`;
- `release_backing()`.

There is still no implementation and no call site.

The external protected sample, protected transfer boundary, queue policy, and secure-lane lifetime remain distinct objects.

## Deliberately absent authority

E004bu does **not** choose:

- `QCOM_SCM_VMID_CP_CAMERA` in code;
- `QCOM_SCM_VMID_TZ` or any supposed QTEE VMID;
- an SCM permission set;
- a QTEE service UID;
- a QSEECOM app;
- a DMA-heap backend;
- an HLOS mapping policy implementation;
- a runtime selector/control/ioctl.

Those values remain blocked on authority, not on data-structure design.

## Mechanical zero-runtime proof

Baseline source is the same production CAMSS preimage used by E004bq:

- `camss-video.c` SHA-256 `2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4`;
- `camss-video.h` SHA-256 `69fdbb6364a772d5b9fe50114878bbc7a1a1ffc61e62af1e71c79fd16e94c982`.

Both baseline and scaffold build against the Golden headers with vermagic:

`7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

The module files differ, as expected from added type/debug metadata, but their extracted executable `.text` sections are byte-for-byte identical:

`fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e`

The generated implementation contains:

- zero `qcom_scm_*` symbols;
- zero concrete `QCOM_SCM_VMID*` symbols;
- zero QCOMTEE implementation calls;
- zero Windows IUM symbols;
- zero callback invocations for the new contract.

No generated module was installed or loaded. SP11 remained on Golden FullIO v19c and no media/video node appeared.

## Why this is not scaffolding for scaffolding's sake

The contract corrects a specific model error that would otherwise infect the runtime backend: treating CP_CAMERA assignment as exclusive ownership and releasing the backing without a separately ordered visibility-revoke phase.

The corrected type boundary now matches the Windows oracle while refusing to guess the Linux owner identity.

## Files

- `scaffold/camss-protected-pipeline.h`
- `make-acl-scaffold.py`
- `CAMSS-ACL-COMPILE-CONTRACT.patch`
- `evidence/SCAFFOLD-GENERATE.txt`
- `evidence/BASELINE-BUILD.log`
- `evidence/SCAFFOLD-BUILD.log`
- `evidence/BUILD-AND-ZERO-RUNTIME.txt`

## Next gate

Return to Windows static authority for **E004bv — external protected-sample metadata contract**.

The next useful question is no longer another Linux ownership abstraction. It is the exact 0x60-byte `PROCESS_DMFT_SURFACE`/secure-image metadata relationship:

- which bytes carry the external secure-section GUID/identity;
- request/frame identity linkage;
- plane offset/size/width/height fields;
- which fields are merely metadata versus trusted mapping state;
- how the metadata joins the CSL internal target object before `OpenSecureSection()` and the internal→external worker transfer.

That should be resolved statically first from the same-machine Windows trustlet/KMD evidence. Windows dynamic tracing is only justified if the static layout leaves a material ambiguity.
