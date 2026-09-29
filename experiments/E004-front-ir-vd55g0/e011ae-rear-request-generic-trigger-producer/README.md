# E011AE — rear request generic triggers and offline BPC startup binding

Status: **SOURCE ARITHMETIC + OFFLINE FULL BPC CHAIN + HOST PACKET BINDING PASS.** Live upstream AEC/context binding, complete E008o composition and independent WM16 retirement remain OPEN. Parent: 12e386ba2f9db745d40604e32eafbd321f88fb8c (E011AD).

## Derived producer boundary

E011AD directly captured ordinary trigger IDs [2,5,1]. This checkpoint identifies their producer through IQInterface::IQSetupTriggerData (RVA0x88A4E8) and SetupGenericTrigger (RVA0x897B78). The primary IFE request calls the latter at RVA0x746F4C; the shared helper is also used by other node paths. Do not infer the live BPC caller's node/context from that IFE reference alone.

| Trigger ID / shared index | Semantic | Source production |
| --- | --- | --- |
| 2 | DRC gain | AEC +0x78, floor at 1.0 |
| 5 | mid/short exposure-sensitivity ratio | AEC +0x24 divided by +0x0C; unit fallback for abs(short) < binary64 1e-6 |
| 1 | selected AEC sensor linear gain | short +0x08, mid +0x20 or long +0x38, selected by explicit request context |

The type1 terminal selector previously called “exposure” consumes selected sensor linear gain, rather than exposure time or E011X's post-sensor dGain. Generic setup copies fixed trigger fields +0x20F4 / +0x20AC / +0x20B0 into current shared vector +0x17190 indices 2/5/1. E011AD's ordinary two-float vector builder maps these type IDs directly.

The gain precedence is source-derived:

1. ISP +0xF4 == 1 forces the mid gain.
2. Otherwise any node/snapshot/input context == 3 selects short.
3. Otherwise any context == 1 selects mid.
4. Otherwise any context == 0 selects long.
5. Remaining all-2 context is unsupported: the original retains an existing gain. The independent API rejects it rather than manufacturing a new value.

The snapshot-context metadata lookup (Node::GetSnapshotFrameExposureType RVA0x5D4158) is not ported or treated as closed. Its resolved context is an explicit semantic input. The API also rejects the separately observed IPE QLL short-gain override domain; live validation must establish whether that branch applies to the actual observed module. No IFE/IPE context is guessed from the BPC output.

Sensitivity arithmetic uses binary32 FSUB/FABS, binary64 epsilon comparison, then native binary32 division. This differs from the binary64 arithmetic used by the interval and region interpolation. The similarly named fixed field +0x20A8 uses another zero test and is not the generic index5 source.

## Independent implementation and validation

producer.py takes caller-owned semantic AEC gains, short/mid sensitivities, DRC gain, three resolved contexts and an explicit request ID. It generates typed inputs and passes the selected sensor gain to E011AD's source interval selector, E011AC's full107-field interpolation and E011AA's common calculation/packing. Captured scalar/region/common/register bytes are never producer inputs.

verify-private.py SHA-checks the original installed DeviceMFT and validates18 instruction/constant anchors. Four bounded original arithmetic/mapping fragments execute in local Unicorn memory only. The external snapshot lookup's return value is a declared test input; no full Node metadata lookup, full IQSetupTriggerData execution or hardware execution is claimed.

674 input cases include all admitted context-precedence combinations,512 deterministic finite AEC inputs, adjacent binary32 epsilon values, zero/subnormal denominators and DRC floor edges. All2022 selected trigger scalar comparisons match. Twelve API-domain rejection tests pass.

The full downstream chain uses original native interval callbacks, full107-field blend and selected common-calculation fragments, independently of the new producer:

- 1348 request/mode chain cases;
- 4044 exact native interval decisions;
- 144236 exact native region fields;
- 40440 exact native selected common scalars;
- 9436 exact register words through the existing C E007a provider.

The C provider consumes clean semantic fields over a private34-byte host-test wire; numeric inputs and outputs stay in same-SP11 process memory. No generated tuning table, capture or register constants are saved as policy.

## Cold seed and packet composition step

startup_common() produces the cold Default common state plus explicit request1/request2 states. The cold seed uses E011AC's independently established equivalence of all six Default source leaves. It needs no assumed initial gain and no replay of the captured zero trigger vector. Cold common output also passes the original native common fragment.

camss-e011ae-rear-startup-bpc-bind.inc installs these three source-produced semantic states into four already independently allocated E008o packet objects. The schedule is [cold, request1, request2, held request2], from E011AB. Source request IDs0/1/2 are distinct from caller-owned E008o materializer IDs, which must already be >=4 and agree with each scalar object's phase/identity. No materializer identity is invented.

The helper validates all source states and all four packet identities before writing anything. It copies only BPC semantic fields by value, leaves unrelated semantics and identities intact, and marks the entire result unsealed and every packet unready. Completing LSC/GTM with E011Z or any other step cannot replace the remaining full semantic validation.

compile-check.c compiles with -std=c11 -Wall -Wextra -Werror and checks four independent packet states, the request3 hold, identity preservation, unready/unsealed output,20 rejects without partial mutation, and runtime authorization -EOPNOTSUPP. It uses the actual E007a provider and an E008o shape adapter; it does not exercise full E008o recursive DMI validation or constitute a kernel build/runtime witness.

## Remaining work

The source request-trigger arithmetic is closed in its explicit domain. Live upstream AEC/context-to-actual-BPC-vector binding remains open: E011AD captured the resulting scalars but not the AEC frame-control fields and resolved branch context needed by this producer. A fresh narrow observer must bind those inputs to the actual module-owning process and startup calls, establish any QLL/other override, and verify same-request lineage before that gate can close.

Cold shared-vector initialization is not independently source-closed, although cold BPC common output is already independently producible from the invariant Default source region. Do not turn that intermediate uncertainty into a new cold BPC value guess.

Next: resolve/capture upstream AEC/context provenance, then complete the remaining E008o base objects and compose all four unsubmitted startup packets. WM16 same-generation IRQ/DMA/IOMMU retirement/lifecycle is a separate hardware gate. Native Linux rear ISP remains denied.

## Reproduction and machine state

On SP11 Linux, run python3 verify-private.py in this directory. Original DeviceMFT SHA c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35 and rear tuning SHA4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635 remain private on SP11; authority.py checks tuning provenance. Only derived code/facts/aggregate JSON enter Git.

No fresh Windows run occurred in E011AE. The earlier E011AD RunB714 valid4K handles is retained evidence, not a new E011AE live result. No Linux camera/module/MMIO/DMI/RT-CDM invocation, IR emitter, suspend or boot change occurred. SP11 remains idle on FullIO v19c Golden boota6a56cbc-7618-43e0-b77c-297ece7ff69d, kernel7.1.5-sp11-render-parity-v4+, with Windows NTFS unmounted.
