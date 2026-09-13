# E004av — trustlet secure IFE bootstrap static map

## Result

**PASS: task-0 bootstrap hands the protected SecureISP aperture into the trustlet's built-in ISP manager, and the 4-byte INIT result is statically identified as the IFE hardware-version value.**

No Linux SecureISP runtime occurred.

## Task-0 bootstrap

The class-1 task dispatcher in `QcISPTrustlet8380.dll` handles INIT as follows:

1. calls the trustlet's ISP-driver initialization with the secure aperture pointer previously produced by `MapSecureIo`;
2. initializes the in-trustlet ISP HW manager;
3. writes the first 32-bit value at that mapped aperture to the 4-byte task output;
4. then performs the ISP-driver configuration stage.

The Windows kernel-side caller independently labels that returned dword:

`IFE_HW_VERSION`

This closes the semantic gap left in E004au: task 0 is not returning an opaque status/value. It returns the IFE hardware-version register/value from the secure-mapped camera aperture.

The actual runtime value is not claimed here because E004av is static-only.

## Internal secure-worker command map

The trustlet does not merely relay host buffers. Its class-1 camera tasks are translated into its own internal ISP-manager command set:

| class-1 task | trustlet stage | internal worker command |
| --- | --- | --- |
| INIT / config | ISPDriverConfig | DeviceConfig |
| START | ISPDriverStart | DeviceStart |
| STOP | ISPDriverStop | DeviceStop |
| CSL packet | ProcessCSLPacket | SendCSLPacket |

This mirrors the operation families already recovered from the Windows SecureISP KMD.

## Secure IFE / CSID ownership

The trustlet itself contains the secure ISP implementation layer, including:

- secure IFE manager initialization and context management;
- secure CSID registration, reset, start/stop and interrupt handling;
- secure IFE and CSID IQ/CSL packet processing;
- secure output-resource and SMMU-buffer handling.

That explains E004y's dynamic observation that real protected IR frames flow while the normal observable Windows CSID/VFE blocks remain inactive: the protected worker owns a separate secure hardware view.

## Base-pointer topology

Static IFE-open code derives several internal addresses from the secure base. For some logical core indices it uses one set of offsets and for other indices a different set.

Those pointer calculations are preserved in `evidence/BASE-TOPOLOGY.txt`, but E004av intentionally does **not** infer which logical core is active for Surface IR or treat one-past-window arithmetic as proof of a live register range. That requires stronger authority than static decompilation alone.

## Evidence

- `evidence/TRUSTLET-BOOTSTRAP-DECOMP.txt` — task dispatcher and secure-base bootstrap.
- `evidence/KMD-INIT-RETURN.txt` — kernel caller labels the task-0 return as `IFE_HW_VERSION`.
- `evidence/TRUSTLET-INTERNAL-COMMANDS.txt` — internal config/start/stop/packet command dispatch.
- `evidence/SECURE-HAL-INDEX.txt` — secure IFE/CSID implementation markers.
- `evidence/BASE-TOPOLOGY.txt` — bounded pointer arithmetic observations without route overclaim.

## Linux consequence

The main parity gap is no longer "find the Windows secure camera path." It is now "model the secure IFE worker well enough to determine which pieces can be represented by Linux firmware/SCM interfaces and which require a protected execution context."

No Linux implementation should directly map or drive the protected aperture based only on this static checkpoint.

## Safety boundary

No qcomtee module was loaded. No secure aperture was mapped on Linux. No camera-domain ownership was changed. No SIP lane call or SecureISP task was executed.

## Next static gate

Recover the exact secure-IFE hardware-version branching / HAL selection and use that to bound the register-model family without reading or touching the protected hardware from Linux.
