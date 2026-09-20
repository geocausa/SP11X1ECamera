# E004hx — runtime PMIC descriptor source and bounded computed-address candidate

**ORIGINAL VERSION-MATCHED UEFI OFFLINE PASS, 2026-09-20.** This stage
reconstructs an original, conditional runtime-descriptor initialization
path rather than assuming the archived PE's uninitialized data are boot-time
hardware values. It reads no live PMIC, SPMI, firmware, camera, or IR hardware.

## Original address metadata is created at runtime

The original SHA-pinned PmicDxe generic write helper at +0x12188 calls
per-device descriptor lookup +0x12a98, whose +0x12aa8 calls a lazy init
+0x12764. That original initializer checks the initialization flag at
+0x39ee8, obtains original firmware table entries (+0x12824..+0x12834,
+0x128f4..+0x12908), issues a metadata-read call at +0x129c0,
and conditionally calls descriptor initialization at +0x129e0. The latter
is +0x1236c, which derives a device's base halfword from the discovered
record at +0x12554 and stores it at allocated descriptor offset +0x20
at +0x12558. On a successful path, +0x12748 inserts that initialized
descriptor in an indexed array at +0x39ef0. The archived PE's 14 entries
there are all zero **ON DISK ONLY**; the original code plainly has a
conditional mechanism to populate them in running firmware.

On one distinct original descriptor-initialization path, original
+0x125f0..+0x12600 stores a pointer to an original static data template
at +0x2fed8 in the descriptor's [+0x8] pointer field. The exact
original data there contain 16-bit values 0x0100 (peripheral stride) and
0x0040 (additional offset). The generic computed-address writer
+0x1221c..+0x12244 reads them from the per-device pointer if that
template path was used; a different, existing-descriptor path
+0x12628..+0x12644 accesses distinct preexisting metadata and need not
use this static template. No boot-time source/path was observed in this
offline analysis.

For the method from E004hv, **if and only if** it uses this template,
the original second requested write computes:

    runtime_discovered_base + (0x0e × 0x0100) + 0x3e + 0x0040
    = runtime_discovered_base + 0x0e7e.

For that expression alone to equal absolute flash timer address 0xee3e,
the original runtime-discovered base would have to equal 0xdfc0.
**No such actual base, caller value, method invocation, or timer write
is established.** The software path remains a concrete candidate that
must not be misreported as the first timer 0x93 writer.

## Safety, verification, next work

verify_descriptor.py SHA-pins the original archived ARM64 image through
E004hv and the exact E004hw prior result; it pins the original lookup,
runtime initialization, metadata-read, descriptor storage, fallback
template and alternative metadata-path instructions and 16-bit template
values. test_descriptor.py exercises **66 independent in-memory mutation
negatives**, without modifying the OEM archive. The stage stores only
source, original-image-derived RVAs and hashes/metadata in Git.

Next discriminate whether any genuine original UEFI client calls method
+0x240 on protocol ae6ae96e-483f-42ae-9cc1-9fac1b584728, and whether
an original runtime-derived base in the candidate path could point to the
four flash timer addresses. A byte-presence GUID match does not establish
a client call. A post-boot Windows oracle alone does not establish a
pre-OS firmware write; reserve authorized one-shot Windows boots for
specific, fresh questions. Independent physical stuck-trigger/host-failure
IR-emitter cutoff, power/current/irradiance and optical pulse remain
unproven; Linux native emitter and biometric login remain OFF.
