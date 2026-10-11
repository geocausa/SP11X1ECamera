# Front field compiler: provenance and limits

This second slice generates bounded CDM commands from typed coefficients and an
output bit depth. It does not import, reconstruct or patch a private profile.
It is a driver-internal implementation, not an interface accepting registers
from applications. It has no camera access, allocation, MMIO or queue submission.

## Sources

| Part | Definition source | Independently generated data |
|---|---|---|
| CDM REG_CONT / DMI | Qualcomm's GPL camera driver, `cam_cdm_util.c/.h`, pinned revision and hashes in `cdm-reference-20261011.json`. The GPL reference carries Linux Foundation and XiaoMi attribution. The bounded helpers are newly written. | REG_CONT count, aligned register offsets and values supplied by the typed compiler. DMI byte count minus one and an offset inside a caller-declared DMA window; no recorded addresses. |
| CST coefficient fields | Project's front-pattern `native-front-cst.inc`, the independently tested coefficient adapter. Functional register/field observations, not copied colour tuning. | Q10 BT.601 matrix from `open_config.py`, or an explicitly owned matrix. Only the six coefficient fields at 0x6168/0x616c, 0x6180/0x6184 and 0x6198/0x619c. |
| CCM coefficient fields | Same adapter; transpose established in the earlier own colour measurement work. Its qualified numerical bound is signed 12-bit, in 13-bit packed fields. | Q7 identity or independently measured matrix, six fields at 0x5868..0x587c. No offsets/shift/defaults are retained from the old input. |
| FULL round/clamp | `native-front-nv12-commands.h`, independently reconstructed RoundClamp12 semantics, retained E006p work and earlier 10-to-8-bit conversion tests. | 8-/10-bit maximum `(1 << bits) - 1`, round shift `10 - bits`, validated functional luma/chroma mode fields. Exactly eleven fields per plane; crop and the +4 word are excluded. |

The reference mirror origin and exact revision are recorded, rather than a claim
that an old downstream snapshot is current mainline. Its definitions establish
serialization, not ISP startup ordering. Trace-derived functional definitions
still require license/provenance review in the curated submission. No component
is marked upstream-ready by this work.

## Validation

`test_front_fields.py` compiles the actual headers with GCC and Clang, ASan and
UBSan, and runs synthetic vectors. It exercises all 8192 CST and 4096 CCM values,
asymmetric CCM transpose, signed/reserved bits, sparse register ownership,
late-invalid coefficient atomic rejection, short output buffers, overlapping
inputs, count/address overflow and DMA span/alignment boundaries. The generated
10-bit round/clamp fragment passes the existing actual validator; its conversion
to 8-bit is byte-identical to the new 8-bit compiler output.

`test_cdm_compat.py --source <public-tree>/drivers/cam_cdm/cam_cdm_util.c`
checks both public source hashes before extracting unchanged reference structures
and functions into a temporary test. The bounded encoder agrees on 97 contiguous
register commands (including count 65535) and 36 DMI cases, under both compilers
and sanitizers. DMI reference input is the encoded length, as used by the GPL
function; our API deliberately accepts an actual byte count and subtracts one.

The new headers also compile as a separate test module against SP11's prepared
kernel tree with `W=1 KCFLAGS=-Werror`. This module is a compile-only probe and
was not loaded. It proves kernel type/build compatibility, not integration or
camera behaviour. Source and validation pins are in
`docs/UPSTREAM-FRONT-FIELDS-VALIDATION-20261011.json`.

The source inventory reports 34 unique register fields corresponding to 74
scalar occurrences in the old startup/steady topology. These are compiler
capabilities; no installed scalar or firmware consumer has yet been removed.
2529 other mapped register occurrences and 58 non-register semantic words still
need classification as generated configuration, unnecessary disabled blocks or
unresolved work. Tables are a separate account. We need not reproduce unused
vendor modules or their tables merely to match the old command list.

## Admission gates before hardware integration

1. Complete the functional crop/scaler/output and statistics configurations,
   module enables, neutral black-level/denoise decisions and startup order.
   Unexplained words remain errors; never fill unknowns from the old profile.
2. Bind DMI banks and addresses to real kernel-owned mappings. The encoder only
   checks arithmetic inside a declared window. It does not prove ownership,
   bank lifetime, DMA completion, cache coherency or allowed target registers.
3. Assemble a new startup provider from typed blocks without importing the old
   schema or copying its instruction layout. Review per-frame atomic update,
   parameter/stats frame identity, locking, stop/error and allocation lifetime.
4. Compile an isolated candidate; record exact source, artifacts, hypothesis,
   experiment identity and rollback. Only then apply guarded hardware tests.
5. Qualify with both private consumers/fallbacks absent from the candidate. Keep
   the installed baseline intact for rollback, rather than deleting its files.

The current daily camera runtime still depends on both private profiles.
