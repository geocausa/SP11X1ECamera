# E004be — camera SCM parity wrapper, compile-only

## Result

**PASS: a dormant Linux 7.1.5 SCM wrapper representing the exact Windows-observed protected-CSIPHY call compiles cleanly without modifying the shared kernel source or executing the call.**

Windows remains the parity authority. Historical Qualcomm Linux source is used only as independent corroboration.

## Windows ABI authority

E004as recovered the Windows request shape and E004bd supplied its live Surface IR values.

The Windows request is a standard 32-bit SIP call with:

- camera service 0x18;
- lane-protection operation 0x07;
- two scalar arguments;
- argument 0 = protect/unprotect;
- argument 1 = lane-protection mask.

For the real Surface IR route, Windows dynamically used mask 0x8 on both sides of the transition.

The mechanically reconstructed Windows call header matches the previously recovered header exactly.

## Important convention finding

The local 7.1.5 generic SCM path negotiates one machine-wide calling convention and, on ARM64, probes the 64-bit convention first.

Using that generic path blindly would therefore not be sufficient for strict Windows parity: the Windows camera request is explicitly encoded using the 32-bit standard SIP convention.

The compile-only wrapper in this checkpoint deliberately fixes that discrepancy by requesting the Windows-observed convention for this camera operation instead of inheriting the general machine convention.

## Qualcomm historical corroboration

A public Qualcomm camera implementation independently uses:

- camera service 0x18;
- lane-protection operation 0x07;
- two scalar arguments containing protect state and the CSIPHY protection mask;
- Qualcomm's SIP function-ID macro whose encoded form is the same 32-bit SIP family observed on Windows.

This is useful corroboration, but it does not replace the Windows oracle.

## Patch scope

The saved patch changes only three kernel source files:

- the internal Qualcomm SCM service/operation constants;
- the public function declaration;
- the wrapper implementation/export.

It does **not** wire the function into CAMSS and does not add any call site.

## Compile proof

The patch was applied to a fresh overlay view of the 7.1.5 source and only the Qualcomm SCM object was built.

Results:

- patch dry-run: PASS;
- patch replay: PASS;
- object build: PASS;
- expected wrapper symbol present and exported;
- object references the existing low-level SCM transport;
- no object was installed;
- no kernel was built for boot;
- no secure-camera runtime occurred.

After the build, the overlay was unmounted and the three shared source files were byte-identical to their pre-test hashes.

## Why this checkpoint matters

E004bd proved the exact Windows operation. E004be proves Linux can represent that operation without silently changing its calling convention.

This leaves integration as the next problem rather than ABI discovery.

## Evidence

- `0001-qcom-scm-camera-protect-phy-lanes.patch`
- `evidence/WINDOWS-SCM-ABI.txt`
- `evidence/QUALCOMM-HISTORICAL-CAMERA-SCM.txt`
- `evidence/LOCAL-SCM-CONVENTION.txt`
- `evidence/COMPILE-ONLY-BUILD.txt`
- `evidence/PATCH-REPLAY.txt`
- `evidence/SHARED-SOURCE-IMMUTABILITY.txt`

## Safety boundary

The wrapper is compile-only. It was never installed, loaded, called, or booted. No Linux camera lane protection, camera memory reassignment, QCOMTEE activity, or protected MMIO access occurred.

## Next gate

Map the **Windows dynamic ordering** around lane protection relative to protected-device configuration/start/stop and translate that ordering into a dormant CAMSS integration patch. Only after the order is proven should a candidate be considered for a bounded runtime.
