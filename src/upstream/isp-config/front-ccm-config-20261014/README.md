# Complete front CCM configuration with the existing measured matrix

The old native CCM patch and sparse upstream encoder already implement the
measured matrix and transpose. They modify six coefficient words, leaving
three offsets and the scale-control word inherited. This package adds only
the surrounding explicit policy and complete ten-word command at0x5868..0x588c.
It emits48 bytes and omits the top-level module command0x5860.

The own run93 GBR Q7 matrix is generated unchanged from its hash-pinned
native_front_ccm_q7 parameter. No optical refit, vendor matrix/default or
private profile/tuning input is used. Offset0/0/0 is an independent neutral
policy. Original common calculation0x9ade70 establishes fractional precision
as scale_control+7 and reproduces the own Q7 coefficients at control0.
The CC131 IQInterface dispatch table at0x1620188 points to that common entry.
The original common, FRINTA helper0x14d0, packer0xb43910 and builder0xb43340
execute locally on SP11, with immutable PE/code and owned partial contexts.
Only helper0x85ee78 is intercepted for command observation/success status;
actual command serialization and constructors are not executed.

A direct source comparison found an important difference from the old helper:
CC131 coefficients occupy twelve bits; its offsets occupy thirteen bits
shifted19, and its scale-control field is only two bits. The old coefficient
helper uses thirteen-bit sign-fill shared with CST. For negative numbers it
sets extra reserved bits12/28. The new wrapper reuses its arithmetic/transpose
and clears those upper sign-fill bits in the staged coefficient image.
Signed numerical values stay unchanged. The old helper and installed native
driver are preserved; its bytes are a historical compatibility reference,
not exact original CC131 packing. Actual CST fields remain thirteen-bit.

The source common accepts factor4 and produces Q11 coefficients, but the
packer truncates its two-bit control to0; that counterexample is recorded
and not admitted. The new policy requires fractional_bits7, zero offsets,
the existing signed-twelve-bit numeric coefficient range and the exact
calibrated front3840x2160-to2560x1440 domain. Other precision/offset/domain
states fail atomically before publication.

456 source cases include453 C-comparison records over three placements,
12 original-common factor0..3 calculations using the measured matrix,
synthetic coefficient sweeps and offset endpoints. GCC/Clang ASan/UBSan
each admit408 cases and reject45 other policy states, with108 atomic
negatives and six compiled unsafe mutations. Those mutations include
retaining the extra reserved sign bits. SP/X19..29/D8..15 restoration,
canaries, immutable source/inputs and nonzero-image residual checks pass.
A native ARM64 W1/Werror compile-only probe and both header styles pass.
Final source/native03 is accepted; native01 exposed the old field mismatch
and a declaration-alignment check and is excluded. Native02 passed; final native03 includes the qfactor4 call in the total common census.

This binds coefficient Q7 to scale0, not physical CCM input/output sample
depth or the entire Gamma/CST/video chain. Zero offsets/image are chosen
policies, not inherited-private equality or physical reset proof. No
module enable, Crop12, core/Gamma/DMI/startup ownership, install, camera,
reboot or private-loader replacement occurs. The calibrated native
unified48/libcamera21/run93/v15 and Golden remain unchanged.

The independent configuration catalog grows101->111 addresses. It remains
incomplete; both private runtime consumers remain and upstream_ready=false.

Reproduction on SP11:
- generate-policy.py --check verifies the unchanged own matrix.
- test-native.py with a fresh output path executes original functional source.
- build-worker.py builds the isolated probe; never load it.
- qualify.py verifies pins and writes derived metadata only.

See docs/FRONT-CCM-CONFIG-20261014.json. Next reuse retained Crop12 and
core/Gamma evidence to finish explicit colour/module/precision policy and
startup around proven native lifetime, then replace private loading in a
fresh isolated candidate and qualify physical/image parity.
