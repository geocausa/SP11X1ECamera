# E004oa — exact SP11 AVStream engine → kernel-device interface acquisition

**2026-09-24; parent [E004nz](../e004nz-avstream-profile-control-static/README.md), Git `9cc697e7da1ed32d4595a537bddef53892d63380`.** This is a further **static** Windows request-to-kernel handoff, addressing the owner's clean, native Linux port map [W2→W4/W5/W6 → L0/L1/L2/L3](../../../docs/CAMERA-STACK-PORT-MAP.md). Unlike the previous component inventory, this pins the **actual original OEM AVStream driver instructions and import table** that acquire the backend called by `CCameraEngine::OnStart/OnStop`. It does **not** assign the receiving module, the selector meanings or any runtime camera/AF event without evidence.

Original, private same-SP11 `surfacecamavs8380.sys` 547,192 bytes, SHA256 `b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed`. This directory exports only scalar **relative RVAs, a device-control request code and explicit evidence limits**; the proprietary driver image, disassembly, Windows objects, capture pixels, DMA addresses and KD records are not exported.

## The concrete AVStream → device-driver handoff

~~~mermaid
flowchart TB
  A["Windows client request: pin/profile/controls"] --> B["OEM AVStream CCaptureFilter + CCameraEngine"]
  B --> C["E004nz engine initialization binds instance<br/>OEM RVA 0x1EC18"]
  C --> D["E004oa backend binder 0x20B60<br/>selects one device-instance record"]
  D --> E["IoGetDeviceInterfaces: find matching device interface"]
  E --> F["IoGetDeviceObjectPointer: obtain device/file objects"]
  F --> G["Internal device-control request 0x002326AB<br/>8-byte output acquires callable interface"]
  G --> H["selected record stored; engine lookup RVA 0x1F620"]
  H --> I["common indirect dispatch RVA 0x20DA8<br/>vtable method OR alternate registered callback"]
  I --> J["UNKNOWN receiving driver/actual control meaning<br/>map platform vs sensor vs ISP next"]
~~~

**Trace verified in the original ARM64 source:**

- At RVA `0x1EC08–0x1EC18`, the engine passes a backend manager (`[engine+0x48]`), a device-instance key and an output slot in its 16-byte record array to binder `0x20B60`. It stores the instance key only when binding succeeds. Later engine lookup `0x1F620–0x1F678` returns the matching record's selected interface pointer; this is how the engine chooses a backend before sending a selector.
- Binder `0x20B60` searches its internal table using that key (`0x20BBC–0x20BE0`). The table entry supplies a Windows device-interface identity. The code invokes **`IoGetDeviceInterfaces`** at `0x20BFC–0x20C04`, constructs a Unicode device pathname using **`RtlInitUnicodeString`** at `0x20C14–0x20C1C`, and calls **`IoGetDeviceObjectPointer`** at `0x20C24–0x20C38` to obtain the device and file objects. These are exact original-driver imported function symbols, independently matched to its PE Import Address Table, not guesses based on diagnostic strings.
- At `0x20C98–0x20CB0` it submits a **zero-input, eight-byte output** device-control request. The code is an OEM constant `0x002326AB` at RVA `0x20DA0`; `0x20A50–0x20B04` uses Windows kernel **`IoBuildDeviceIoControlRequest`** and **`IofCallDriver`** and handles pending completion. The returned value is written into the selected backend record; binding stores that record in the engine's requested slot at RVA `0x20CE8`. **The request-code's symbolic OEM name and the receiving driver are still UNKNOWN.** It should not be treated as a Linux IOCTL or run on Linux.
- Engine selector lookup and dispatch RVA `0x20DA8` checks record fields including `record+0x10` and returned interface at `record+0x28`, then calls **either** the returned interface's first virtual-table entry (`0x20DE0–0x20DF4`) **or** an alternate registered callback at `record+0x40` (`0x20DFC–0x20E30`), subject to its recorded mode flag. This gives two dispatch forms; we have NOT observed which form a live rear capture selects. `CCameraEngine::OnStart/OnStop` are confirmed virtual-table entries in the **AVStream driver itself** (entries RVA `0x2FD80` and `0x2FD88`), and their calls to the common dispatcher were pinned in E004nz.

**Consequence:** there is now a source-proven **external Windows kernel-driver interface boundary** between the camera engine and lower-level hardware operations. The previous `0x804/0x805/0x809/0x5/0x17/0x18` start/stop selectors remain **opaque interface parameters**, not sensor command names, VFE register values or a Linux driver sequence. Binding could address different device identities for different front/rear/IR modes; the selected device-interface identity and active Windows rear session remain unknown.

## What we should investigate next

**First, static-only:** trace the binder's **device-instance table entries and interface identity/registration** across the exact original same-SP11 `surfacecamavs8380.sys`, `qccamplatform8380.sys`, `qccamisp8380.sys` and front/rear sensor packages. Find the receiver for the kernel device-control request `0x002326AB` and its returned callable interface contract. Only then attach selector names to source-backed recipient operations, including which component starts/stops the sensor and IFE or submits IQ/RT-CDM. If a receiver is unavailable in the archived binaries, state that and do not invent one. No SP7 KD or Windows reboot is necessary to make this static progress.

**Then, if necessary**, compare a bounded normal Windows rear VideoRecord, preview/photo and front↔rear request and capture *non-image* device/profile/owner/IQ/IRQ state, provided permitted debugging can be conducted safely. Verify real frame flow before interpreting BF event `0x0F` or group8 WM16, and keep the E004nv static BF mode-0 callback separate from a live event. The OEM Device MFT is only **registered**, not established as the source of these backend calls or active during our Windows 4K sessions.

## Native Linux ownership and safety

Port the **observable hardware effects** of device binding and safe multi-step sensor/ISP start/stop into Linux V4L2/CAMSS (kernel L0/L1/L2/L3) and expose standard camera selection/profile/manual controls. Optional exposure, white balance, focus and IQ algorithms belong in a small **open** user-controllable policy/IPA (L4) if needed. Neither Windows kernel-interface acquisition nor Microsoft Frame Server, Windows-specific `.sys/.dll`, Studio Effects or AI filtering is a Linux runtime dependency.

This experiment performed **no** Windows capture, camera power/CSI/ISP/DMA operation, breakpoint, reboot, module build or install; protected Golden v19c, native front PIX, rear RAW/software 4K fallback and IR safeguards remain unchanged. Linux native rear 4K ISP optical frames and live Windows BF/WM16 completion are still **unproven**.

## Repeatable offline checks

`prove-kernel-interface-bind.py` SHA-pins the private original same-SP11 OEM AVStream PE; validates **42 actual ARM64 instruction anchors**, **five original import-table names and indices**, **two engine virtual-table entries**, original device-control constant and **12 fail-closed negative mutations**. It checks the committed safe `RESULT.json` rather than silently replacing it; `--write-new` is single-use. No raw source or image data are emitted.
