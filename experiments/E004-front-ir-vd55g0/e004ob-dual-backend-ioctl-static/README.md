# E004ob — one opaque AVStream interface request, two distinct OEM drivers

**Same SP11 read-only static evidence; 2026-09-24. Parent:** [E004oa](../e004oa-avstream-kernel-interface-bind/README.md), Git `e75dfd6f00e1581b2ad89a42765d9d5e0558aae9`. This resolves an important ambiguity left by E004oa: the OEM internal device-control request `0x002326AB` is **NOT a unique signature identifying a single receiving camera driver**.

The actual same-SP11 original OEM driver files contain three independently verified occurrences of that request code:

| OEM component | Private original SHA256 | Constant's image RVA | Matching branch and directly proven state effects |
| --- | --- | ---: | --- |
| AVStream `surfacecamavs8380.sys` | `b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed` | `0x20DA0` | **Request sender**. E004oa source-verifies backend binding, original NT device-interface imports and a zero-input eight-byte device-control request; selected interface record is supplied to engine dispatcher `0x20DA8`. |
| Platform `qccamplatform8380.sys` | `836714ec41f92f45af363d7bf3c9b9cfc2cccdbd19a1c57f355b471068648049` | `0x6490` | **Static code match** at `0x6334–0x633C` branches to `0x6364`; if a required state pointer is present, it **clears state flag at +0x08** and zeroes the two state fields at `+0x10` and `+0x18`. Its behavior is not the same as the ISP branch. |
| ISP `qccamisp8380.sys` | `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c` | `0x5784` | **Static code match** at `0x5638–0x5640` branches to `0x566C`; for its accepted pointer it writes another driver-held pointer, sets **flag +0x08 = 1**, and installs **state and an ISP-specific callback** at `+0x10` and `+0x18` (`0x5674–0x568C`). |

The receiver branches above are **distinct code paths in distinct installed drivers**. They do not prove that a single request is broadcast to both, that one necessarily follows the other, or that their structures/flags share an identical interpretation. The branch's incoming state pointer, request lengths and per-driver descriptor/dispatch context must be traced independently before treating their effects as an identical interface structure. The OEM numerical request-code's symbolic name remains unproven.

A search of the installed original `surfacecamrearsensor8380.sys` and `surfacecamfrontsensor8380.sys` binary bytes returned **no direct four-byte occurrence** of this specific request constant. This is a **limited direct-literal observation**, not proof that sensor drivers never handle an equivalent request through generated, table-driven, forwarded or firmware-mediated dispatch.

## Porting consequence — client intent is not hardware ownership

The Windows AVStream engine implements camera policy and delegates through a per-device interface. The static `0x002326AB` request is part of interface acquisition/management; **do not copy it, the Windows virtual table or opaque start/stop selectors directly into Linux**. For L0/L1/L2/L3, we need each native recipient's verified hardware effect: power/reset/sensor CSI start, ISP/ICP commands, per-profile enabled DMA outputs and true safe stop. L4 optional auto-exposure/white balance/focus can use a small open user-controlled IPA without importing any Windows effects/AI runtime.

**Next exact evidence dependency:** Match each device-interface identity supplied to AVStream's E004oa binder to the correct OEM platform/ISP/sensor **registered receiving device object**, then trace the actual returned interface's callback implementation for the engine start/stop selectors. A numeric device-control code shared by platform and ISP cannot disambiguate that interface. The true rear VideoRecord selected backend and whether either static path was taken *live* remain unknown. The E004nv BF mode-0 status event, FIFO8 and WM16 register callback remain static-only; neither a live rear BF completion nor a native Linux rear processed-4K ISP optical frame is proven.

## Reproducibility and safety

`verify.py` SHA-locks both original **private** OEM binaries and E004oa's prior safe-scalar sender evidence, checks the ARM64 machine type, both actual original literal values, **20 exact ARM64 receiver instructions** and **12 fail-closed negative mutations** that reject invented unique receiver, identical semantics, live hardware attribution, native 4K proof or Golden changes. `RESULT.json` holds only scalar component names/relative code RVAs and explicitly bounded booleans. The original binaries, disassembly dumps, image samples, kernel pointers and KD logs stay private on SP11/SP7. No Windows capture, debugger, sensor/ISP power, kernel patch/module install, Linux reboot, or Golden modification occurred; native front camera, independent rear RAW/software-4K fallback and IR safeguards remain unchanged.
