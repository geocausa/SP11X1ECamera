# E004cx — X1E downstream secure CB9 recovery

## Result

**PASS: the exact missing X1E secure FastRPC stream identity is recovered from the same-machine Windows oracle. SP11's Qualcomm SMMU package explicitly maps FASTRPC `S1_COMPUTE_CP_P` to SID `0x0c09`, mask `0x0020`, in a protected CP-P SMMU context. This exactly fills the hole left by Golden Hamoa's `compute-cb@9 is secure` comment. The Linux CPZ PD type is `6` by Qualcomm downstream FastRPC contract; that property value is derived from the downstream ABI rather than copied from an unavailable Hamoa downstream DTS.**

No Windows boot, DT change, SMMU programming, FastRPC request, CPZ process, ownership transition, camera runtime or SecureISP runtime occurred.

## 1. Windows provides the missing same-machine hardware authority

The exact installed SP11 package:

`qcsmmu8380.inf`

SHA-256:

`c1afd89419c12ca093a7d3b1f80ef980723d78d3549ceb158b9ee1a1ca051846`

contains a complete client/context-bank/VM map.

For FASTRPC client `0x17`, ordinary compute contexts are:

- S1_COMPUTE_1 through S1_COMPUTE_8 — HLOS;
- S1_COMPUTE_10 through S1_COMPUTE_13 — HLOS.

It then has a separate protected entry:

- hardware CB37 / index `0x25`;
- name `S1_COMPUTE_CP_P`;
- VM class `CP-P`;
- stream ID `0x0c09`;
- stream mask `0x0020`.

The registry mapping is explicit:

`S2CB\0x17\0x10\0x25 -> 0x0c09 / 0x0020`.

So `0x0c09` is no longer a numeric guess.

## 2. It matches the Linux hole exactly

Golden Hamoa/X1E exposes:

- compute-cb@1 → `0x0c01 0x20`;
- ...
- compute-cb@8 → `0x0c08 0x20`;
- **`compute-cb@9 is secure`** — node omitted;
- compute-cb@10 → `0x0c0c 0x20`;
- ...
- compute-cb@13 → `0x0c0f 0x20`.

The exact Windows table uses those same stream IDs and masks for the ordinary FASTRPC contexts, then supplies the missing protected stream as `0x0c09 0x20`.

This cross-OS correlation is stronger than copying a value from another SoC.

## 3. Do not confuse logical CB9 with Windows hardware CB37

Linux `compute-cb@9` uses `reg = <9>` as the FastRPC session/context identifier.

Windows' protected entry is hardware SMMU context-bank 37 (`0x25`).

These are different namespaces. The stable cross-OS identity is the SMMU stream tuple:

`SID 0x0c09, mask/flags 0x20`.

## 4. Windows FastRPC itself deliberately lists only ordinary banks

The exact SP11 `qcadsprpc8380.inf` ordinary CDSP table lists twelve contexts corresponding to Linux banks 1–8 and 10–13. It excludes the protected S1_COMPUTE_CP_P bank.

That is consistent with the already-proven Windows architecture: normal camera CDSP/BitML work uses ordinary FastRPC, while protected IR's final frame worker lives in VTL1 rather than CPZ.

The secure SMMU resource exists on the platform even though Windows camera DeviceMFT does not use it for protected IR.

## 5. CPZ PD type is ABI-derived, not guessed

Qualcomm's downstream FastRPC ABI defines:

`CPZ_USERPD = 6`.

Its typed-context-bank code reads `pd-type` at context-bank probe, and secure-memory allocation selects the CPZ_USERPD typed bank when PD typing is enabled.

Therefore the Linux CPZ candidate requires:

`pd-type = <6>`.

Evidence boundary:

- `iommus = <&apps_smmu 0x0c09 0x20>` is directly proven by same-machine Windows hardware policy;
- `pd-type = <6>` is derived from Qualcomm downstream FastRPC semantics;
- an exact proprietary Hamoa downstream DTS containing that property was not recovered.

That distinction is retained deliberately.

## 6. CDSP firmware DTBs were checked and rejected as host authority

The exact Windows `cdsp_dtbs.elf` contains Hamoa and Purwa DSP-internal FDTs. They contain no host FastRPC compute-CB, SMMU SID, CPZ host-policy, or `pd-type` definition.

So the correct host-side oracle is the Windows SMMU package, not the DSP firmware DTB.

## Safety boundary

Golden FullIO v19c remained active with no one-shot armed. No DT/SMMU state changed and no FastRPC, CPZ, protected-memory, camera or SecureISP runtime action occurred.

## Next gate

**E004cy — compile-only X1E secure CB9 topology candidate.**

Encode the recovered topology only in an offline DTS/DTB scaffold:

- `compute-cb@9`;
- `reg = <9>`;
- `iommus = <&apps_smmu 0x0c09 0x20>`;
- `dma-coherent`;
- CPZ process type 6 as the downstream-derived `pd-type` candidate.

Prove it compiles and that the resulting node is isolated from live Golden. Do **not** install a DTB, reprobe a context bank, expose CPZ runtime, or perform an ownership transition.
