# E004oc — OEM camera backend identities and native Linux ownership

**2026-09-24. Parent: E004ob / e90eee9cb7daa6b121f7444df212377009f1efe3.** This is read-only static investigation of the **same SP11's original OEM ARM64 binaries**. See the [permanent Windows-to-Linux camera stack map](../../../docs/CAMERA-STACK-PORT-MAP.md). No Windows session, hardware, camera firmware, optical image, KD or Golden runtime was modified.

## The missing selection step is now source-backed

The original AVStream driver has a **nine-entry backend table at driver RVA 0x2ECE0**, with a 72-byte stride. Original assembly at 0x208A4–0x208DC constructs per-device records from this table; its binder at 0x20BBC–0x20BE4 looks up the matching 32-bit identity key and passes that entry's GUID to IoGetDeviceInterfaces. E004oa already traced device-object acquisition, an eight-byte returned callable interface, and the subsequent engine's indirect dispatch. **The same internal request code 0x002326AB does not identify a unique recipient: the GUID identifies which device interface is addressed.**

The original table's nine identities, and the matching registration-code identities in **seven different same-SP11 OEM drivers**, are verified below:

| Slot | Interface GUID | Registration-code counterpart | Table class/type |
|---|---|---|---:|
| 0 | d2ff3f74-880f-4858-841c-fb0bc634676c | qccamflash8380.sys | 1 |
| 1 | 5e34e1c5-c5bc-4c7f-b6fc-e2443e45be67 | surfacecamrearsensor8380.sys | 2 |
| 2 | f27170b8-7b88-4f4a-b505-1d065616aadc | surfacecamfrontsensor8380.sys | 2 |
| 3 | 65528936-042e-4693-bb4f-96c419453ccb | surfacecamauxsensor8380.sys | 2 |
| 4 | 3e9c0fdb-cef9-4c4a-8e85-36e4a82eb80f | qccamisp8380.sys | 3 |
| 5 | 8d73ce35-93cf-4795-8db9-40bbe130d859 | qccamplatform8380.sys — shared platform service | 4 |
| 6 | 91761a61-b864-4cd3-bcdd-4afaf16dd2c0 | UNKNOWN in 102 archived OEM .sys files | 2 |
| 7 | 23a032e0-11af-460b-bac1-400da39b428e | UNKNOWN in 102 archived OEM .sys files | 2 |
| 8 | 2a851ba1-8248-4567-b61a-f279610b248c | qccamsecureisp8380.sys — separate protected-camera path | 3 |

**Registration-code proof, not filename inference:** each identified original provider prepares its *matching identity* as the x2 argument to a framework device-interface creation function at its own code location and loads the same framework function-table slot +0x268. Their source RVAs and exact private OEM SHA-256s are in [RESULT.json](RESULT.json), and the original binary instructions are independently checked by [verify.py](verify.py). This establishes the provider's original static registration path, **not** that Windows registered, selected or called it in a particular live rear recording.

**Common platform identity is not a competing ISP provider.** The Qualcomm platform driver has the registration path for slot 5. The original ISP, front and rear sensor drivers separately pass slot 5's GUID into their *interface-query* paths. They may obtain platform facilities while registering **their own** unique sensor or ISP identities. E004ob found the same opaque request number in both ISP and platform: that is consistent with *distinctly addressed interface providers*, not with automatically broadcasting one command to both.

## How this helps us port a clean native Linux stack

The user-facing camera selection belongs above the driver; the verified hardware lifecycle belongs in the Linux CAMSS/V4L2 drivers. In a rear session, the native L0 sensor driver must implement the independently verified sensor mode/power/CCI effects, L1 enforces exclusive CSID1/VFE1 ownership and safe switch, L2 configures the rear CSI/ISP/IQ route, L3 owns the exact live DMA/statistics outputs and IRQ retirement. Optional manual or automatic 3A policy may use a small **open, user-controlled libcamera IPA**. **No Windows service, proprietary .sys/.dll, Studio Effects or AI imaging is a required Linux runtime component.**

The static routing map now gives the next **precise** target: follow the original **ISP slot-4 returned callback interface** through the ISP's request 0x002326AB branch; separately follow the **rear slot-1** and **platform slot-5** callbacks. Only when their receiving functions and argument shapes are identified should we attribute AVStream engine selectors 0x804/0x805/0x809/0x5/0x17/0x18 to actual hardware start/stop operations. Existing static registration **does not** determine the live Windows rear VideoRecord selected backend, exact command order, BF event mode/WM16 retirement, rear-specific IQ/RT-CDM or native Linux processed 4K optical content. Slots 6/7 remain unidentified: class/type 2 alone is not proof of a particular sensor.

## Reproducibility and non-regression

Run: PYTHONDONTWRITEBYTECODE=1 python3 verify.py. It SHA-locks AVStream and seven original providers, verifies their ARM64 device-interface registration call sites, checks all nine table records and GUID identities, proves the shared platform GUID's provider/query distinction, scans all 102 original OEM .sys binaries for the two unresolved identities, and runs **12 fail-closed mutations** that reject invented provider, live camera selection, selector semantics, BF success, Linux native 4K or Golden changes. RESULT.json stores derived GUIDs, relative RVAs and safe scalar booleans only; no private driver bytes, original disassembly, firmware, pixels, buffer addresses or KD credentials are copied to Git. The original front native capture, IR safeguards and rear RAW/software 4K fallback remain preserved.
