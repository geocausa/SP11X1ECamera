# E004bf — Windows secure-lane start/stop ordering oracle

## Result

**PASS: the accepted Windows dynamic trace establishes the protected-lane ordering around the secure worker lifecycle.**

Windows remains the parity authority. Static analysis is used only to name the already-observed operation/task IDs.

No new Windows boot was needed: the existing accepted E004aq trace already contains the required ordering.

## Dynamic Windows ordering

The protected-start transition appears in this order:

1. SecureISP operation `0x804`
2. secure-lane enable dispatch, mask `0x8`
3. secure-camera configuration with protect = 1
4. task `2`

The protected-stop transition appears in this order:

1. SecureISP operation `0x805`
2. task `3`
3. secure-lane disable dispatch, mask `0x8`
4. secure-camera configuration with protect = 0
5. later teardown operation `0x80e`

Those are line-order observations from the accepted same-machine Windows trace.

## Static semantic labels

Static KMD analysis labels the dynamic events:

- operation `0x804` = DeviceStart;
- task `2` = protected worker START;
- operation `0x805` = DeviceStop;
- task `3` = protected worker STOP.

The DeviceStart implementation configures the secure camera before it sends task 2. The DeviceStop implementation sends task 3 before it clears the secure-camera configuration.

So the Windows parity rule is:

**protect first -> start protected worker**

and on teardown:

**stop protected worker -> unprotect**

This symmetry is stronger authority than selecting hook placement from Linux conventions alone.

## Intentionally unresolved

The accepted trace does **not** sample the physical CSIPHY0 register image at the exact protection transition.

Therefore E004bf does not claim whether ordinary CSIPHY register programming happens before or after the protect call. A new read-only Windows observation was considered for that question, but the debugger-session setup was blocked by the platform before SP11 left Golden.

That unanswered detail must not be filled in by assumption.

## Linux consequence

E004be now gives Linux a compile-proven representation of the exact Windows lane-protection call.

E004bf constrains how that primitive must relate to the eventual protected-worker lifecycle:

- protection must be established before the Linux equivalent of protected worker start;
- protected worker activity must be stopped before protection is released;
- rollback must preserve the same order.

It does **not** yet authorize selecting a particular CAMSS call site.

## Evidence

- `evidence/WINDOWS-DYNAMIC-ORDER.txt`
- `evidence/KMD-START-STOP-SEMANTICS.txt`
- `evidence/GOLDEN-NO-REBOOT.txt`
- accepted E004aq raw trace authority
- E004be compile-only SCM parity wrapper

## Safety boundary

No new Windows boot occurred for E004bf. No Linux secure-camera runtime occurred. No lane-protection call was issued from Linux. No memory ownership changed. QCOMTEE remained unloaded.

## Next gate

Resolve where the Windows protected-worker start maps into the Linux CAMSS pipeline. Prefer a Windows dynamic observation if the tooling path becomes available; otherwise use the already-observed Windows sequence plus static Windows/Qualcomm analysis, with any remaining physical-CSIPHY timing uncertainty explicitly carried forward.
