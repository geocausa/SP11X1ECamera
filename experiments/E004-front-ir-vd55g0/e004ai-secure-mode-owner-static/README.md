# E004ai — Windows SecureMode owner static mapping

## Result

**PASS: surfacecamavs8380.sys owns the SecureMode switch that gates the protected CSI path.**

E004ah proved that the normal WinRT IR holder produces real IR frames without exercising the qccamsecureisp control ABI. E004ai explains why.

Static authority is same-machine Windows `surfacecamavs8380.sys` (SHA-256 `b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed`).

Key findings:

- SecureMode SET handler: RVA `0x83120` (`FUN_140083120`), reached through wrapper RVA `0xb460`.
- SecureMode GET handler: RVA `0x83040` (`FUN_140083040`), reached through wrapper RVA `0xb490`.
- The active SecureMode state is one byte at capture-filter object offset `+0x2ad`.
- SET treats extended-property value `2` as enabled and writes that boolean to `+0x2ad`; GET reports value `2` when enabled and value `1` when disabled.
- Initialization/policy helper RVA `0x1ebb0` refuses requested secure mode unless object field `+0x18` matches the AUX-camera discriminator literal `0x65528936`; on mismatch it logs `SecureMode is only available for AUX camera, setting SecureMode to false` and clears the request.
- The same helper uses literal `0x2a851ba1` when registering the accepted AUX secure-mode item.
- `CCaptureFilter::SendPacketInternal` RVA `0x9b18` handles packet major opcode `5`. For sub-op `0`, it enters the secure CSI diversion only when `+0x2ad == 1`.
- In that secure branch it obtains CSIPHY identity, copies the CSI PHY payload, and calls the secure KMDISP vtable method at `(*device + 0x10)->+0x48` with operation `2`, buffer `object+0x2b4`, length `0x0c`.
- Secure frame completion paths are separately present (`IFE_MSG_ID_GROUP0_SECURE_IMAGE`, `IFE_LITE_SECURE_MSG_ID_PREPROCESSED_RAW`, `SECURE_BUFFER`).

## Interpretation

The ordinary WinRT `MediaCapture` / `MediaFrameReader` holder used in E004ah does not itself enable `KSCAMERA_EXTENDEDPROP_SECUREMODE`, so successful IR frames do not imply that the protected qccamsecureisp control path was active.

The next justified Windows behavioral gate is therefore **explicit SecureMode-property activation on the AUX/IR camera**, followed by a bounded trace of the surfacecamavs secure dispatch and qccamsecureisp boundary. Repeating the same unmodified WinRT holder is not useful.

Linux SecureISP runtime remains **NOT AUTHORIZED**.

## Evidence

- `ghidra/SURFACECAMAVS-SECURE-XREFS.txt` — secure strings, xrefs, and decompilations.
- `ghidra/SURFACECAMAVS-SECURE-CALLERS.txt` — caller/wrapper map.
- `ghidra/ExtractSecureModeXrefs.java` and `ghidra/ExtractSecureModeCallers.java` — extraction scripts.

