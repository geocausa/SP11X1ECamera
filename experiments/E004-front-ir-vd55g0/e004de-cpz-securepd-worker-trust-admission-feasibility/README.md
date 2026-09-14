# E004de — production CPZ/SecurePD worker trust-admission feasibility

## Result

**PASS / CLOSED: the exact SP11 production CDSP trust policy does not expose a legitimate source-controlled admission route for a new parity worker. Shipping modules are admitted either through root-image static per-segment hashes or through authenticated signed-module/root-TCG verification. The optional OEM/test-signature path is conditional on production debug/test policy and no `oemconfig.so`, testsig package, or usable signing credential is present in the exact SP11 software set. We must not patch verification or alter trusted firmware to force admission.**

This is a static-only closure. No worker was launched and no production trust state was changed.

## 1. Static-hash admission is rooted in the CDSP root image

The exact same-machine `qccdsp8380.mbn` contains the shipping `/statichashes/*` namespace itself.

There are 17 embedded entries, covering the shipping FastRPC shells, SecurePD examples, benchmark/sysmon modules and runtime libraries. Important entries include:

- `example_image.so`;
- `example_image_runner.so`;
- `libloadalgo_skel.so`;
- `libbenchmark_skel.so`;
- `fastrpc_shell_3`;
- `fastrpc_shell_unsigned_3`.

There is no camera/SecureISP/SWABF/SWASF parity-worker entry.

Fresh Ghidra recovery identifies the static-hash lookup path. It constructs `/statichashes/%s`, retrieves `num_segments` and a hash array, and the main verifier checks the module's loadable segments against 32-byte stored hashes.

So this is not a host-editable filename allow-list that we can safely extend from Linux.

## 2. Changing a trusted shipping module does not help

E004dd showed the trusted shipping modules do not expose the full Windows camera transfer behavior.

E004de closes the tempting workaround of editing one of those binaries. Static-hash admission validates its loadable segments. Adding our copy/fill/SWAB parity logic would alter those segments and fail the existing trust record unless the module were separately signed by an accepted production authority.

That would no longer be “reuse the trusted module”; it would be a new trust-admission problem.

## 3. Dynamic unsigned workers are explicitly rejected

The exact root firmware's ELF parser has a direct fail path:

`error: dynamic module is unsigned`

when required signature material is absent.

The production FastRPC shell contains the full signature-validation machinery and real CPZ migration path. The unsigned shell's CPZ migration entry remains the error stub already proven by E004dc.

Thus an ordinary source-built Hexagon `.so` cannot simply be loaded into production CPZ/SecurePD.

## 4. Signed modules must match an accepted trust root/TCG

The verifier checks signed image segments and compares the image trust metadata against accepted roots/TCGs. Failure is explicit:

`signature does not match image root`

The diagnostic state distinguishes:

- module signed;
- signature valid;
- static hash found;
- production vs QC-test trust paths.

No Qualcomm/Microsoft/OEM production signing private key or authorized signing service is available in this project, and none is claimed.

## 5. The OEM/test-signature code path is not a production workaround

The firmware contains optional support for:

- `oemconfig.so`;
- `testsig.so` / OEM-specific testsig files;
- debug-fuse state;
- test-signature enable/file-valid state;
- QC-test trust roots.

But a complete scan of the exact Golden firmware, installed Windows DriverStore and recovered SP11 package finds no `oemconfig.so` at all. No test-signature package or project-owned signing credential is available either.

More importantly, deliberately enabling a debug/test root, patching signature verification, or modifying the trusted root firmware would weaken the security property we are trying to reproduce. Those are rejected as parity solutions.

## 6. What this means for the Linux protected-camera architecture

The following pieces are now mechanically solved:

- protected internal and external memory ownership;
- HLOS CPU exclusion;
- CPZ secure context-bank topology;
- protected dma-buf FastRPC map/unmap lifetime;
- CPZ/SecurePD trusted CPU worker habitat;
- worker protected-buffer mailbox/mapping model.

The remaining blocker is narrower but fundamental:

**the exact Windows-equivalent transfer program is not present in the shipping trusted CDSP surface, and a new implementation cannot currently be admitted to the production CPZ trust domain through an authorized source-controlled route.**

That is a trust-root/admission blocker, not a Linux coding bug and not a missing dma-buf mechanism.

## 7. Why runtime remains unauthorized

Enabling secure CB9 and creating CPZ now would not produce camera parity because there is still no admitted worker implementing the required Windows transfer modes.

Running the Gaussian/example worker just to prove CPZ executes would demonstrate infrastructure, but it would not advance the 1:1 camera goal enough to justify crossing the protected-runtime safety boundary.

So protected runtime remains deliberately disabled.

## Safety boundary

SP11 remained on Golden FullIO v19c with empty `next_entry`. No CDSP firmware was modified, verification was not patched, no test/debug root was enabled, CB9 remained disabled, and no FastRPC, CPZ, ownership, camera or Linux SecureISP runtime action occurred.

## Next gate

**E004df — parity worker admission alternatives, architecture closure.**

Do not weaken production CDSP verification. Statistically evaluate only legitimate alternatives:

1. whether the Windows VTL1 transfer worker can be represented by an already-authorized non-CDSP trusted execution environment on Linux without violating the Qualcomm ownership plane;
2. whether a vendor/manufacturer-supported signing or development certificate path exists in the exact SP11 platform material;
3. whether the camera contract can be rearranged so a shipping trusted operation plus untrusted post-processing still preserves the Windows protection boundary — reject it if HLOS sees protected pixels;
4. otherwise mark CPZ parity runtime blocked on unavailable worker trust admission and stop accumulating unsafe scaffolding.

No protected runtime until one route preserves the original security contract.
