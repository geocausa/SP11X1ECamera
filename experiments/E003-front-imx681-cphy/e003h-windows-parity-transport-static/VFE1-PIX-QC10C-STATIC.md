# E003h VFE1 PIX/QC10C static contract — stream blocked

Date: 2026-08-29

Same-machine Windows remains the behavioral oracle. This layer does **not** create a Linux front-frame path. It only makes the already-proven VFE1 memory/output topology representable without falling through Linux's invalid RDI-style PIX mapping.

## Windows contract now represented

The accepted sensor remains 3840x2640 RAW10. CSID1 IPP produces the Windows 3840x2160 RAW10 VC0 input to VFE1. Windows VFE1 then emits one VIDEO/FULL output as a 2560x1440 TP10-UBWC/QC10C-family surface:

- V4L2 memory format: `V4L2_PIX_FMT_QC10C`;
- V4L2 memory planes: 1 contiguous DMA allocation;
- internal regions: `Y_META -> Y_TP10 -> C_META -> C_TP10`;
- bytesperline/Windows stride: 3584;
- total allocation: `0x76b000` bytes;
- offsets: `0`, `0x6000`, `0x4f2000`, `0x4f5000`;
- FULL clients: WM0 Y + WM1 C, one compression group;
- auxiliary Windows clients retained in the contract: DS4 WM2, DS16 WM3, stats WM11/12/13/14/18;
- inactive/non-parity output clients: PIXEL_RAW WM10 and RDI0/1/2 WM24/25/26.

The exact installed Windows ISP KMD additionally proves `TOP_MASK0=0x0007f051` and `BUS_MASK0=0xd0000000`. In the DPC, TOP status1 bit0 is mechanically converted to event 3, whose exact diagnostic branch is `IFE VIDEO buf done`. Therefore FULL Y/C is one VIDEO completion surface, not two independent V4L2 frames.

`extract_vfe1_video_completion.py` is fail-closed to the exact installed `qccamisp8380.sys`; `extract_vfe1_pix_static_contract.py` then combines that result with the already-hash-pinned Windows BUS and FULL-layout oracles.

## Static Linux `0016`

`0016-x1e-vfe1-pix-qc10c-static-contract.patch` changes only five CAMSS source files and is deliberately fail-closed:

1. Only **X1E IFE1** gets a dedicated PIX format table. IFE0 and both Lite instances remain on their prior tables.
2. The IFE1 PIX media-bus code is exactly `MEDIA_BUS_FMT_SRGGB10_1X10`; its memory format is exactly `V4L2_PIX_FMT_QC10C`.
3. CAMSS QC10C frame-size enumeration is discrete, not continuous: exactly 2560x1440.
4. `TRY_FMT`/default memory geometry is forced to 2560x1440, 3584-byte stride, one V4L2 plane, `sizeimage=0x76b000`.
5. Media-bus-to-memory validation rejects QC10C unless the VFE source is exactly 2560x1440.
6. VFE1 PIX sink fallback uses the sole RAW10 code instead of the old unrelated UYVY fallback.
7. VFE680 retains the Windows FULL/DS/stats/surface/mask/event values as read-only static contract data. There is no relocation/reference from runtime code to those contract tables.
8. Most importantly, `vfe_enable_v2()` returns `-EOPNOTSUPP` for **X1E VFE1 PIX** before stream lock, IRQ enable, output reservation, WM programming, RT-CDM execution, CSID/CSIPHY streaming, or sensor transmission.

The existing VFE680 RDI write-master functions are byte-identical to the pre-`0016` source. `0016` therefore does not convert rear RDI to PIX behavior and does not touch IFE0/Lite routing.

## Build / proof

- module build: PASS, no compiler warning/error diagnostics;
- `qcom-camss.ko` SHA-256: `97fd2dd9a482c0ba8e6c0d3e5a7cf190612bdca4610a81c59a576bc5e4cf7834`;
- Golden vermagic: exact;
- patch SHA-256: `4e0cbba5b169353a4f62cfdf1aacd93ac811ae3366f72658eeee7cefaca7ab03`;
- patch forward/reverse dry-run: PASS;
- application to the five saved pre-`0016` source files reconstructs the candidate byte-for-byte;
- checkpatch patch mode: only missing mail-patch description/Signed-off-by metadata; no code/style finding;
- static inspector SHA-256: `af5b43ac294f442260f132ca4e2731812cf5100186fc0cecc17a103a94936f51`;
- inspection JSON SHA-256: `cb2d5ae35b0879d2f716f1193aec54f921daddf4560e410f0cd0fed7d742fe10`;
- Denali DTB remains byte-identical at `bbe48a77c5bc23f1c155ddc87b9a5b2ed56497656f06cab1a2db8e6346f0304b`.

No module was loaded. No Linux VFE1 PIX register was programmed. No RT-CDM command was submitted. No sensor stream write or frame attempt occurred.

## Next evidence gate

Format, surface geometry, two-WM structure and VIDEO completion ownership are no longer blockers. Before making any VFE1 PIX hardware helper reachable, recover the exact same-machine Windows ordering and ownership for **BUS client programming and dynamic address updates** relative to RT-CDM/IFE start, including the separate DS4/DS16/statistics buffers. Dynamic Windows IOVAs must never be frozen. Only after that ordering/lifetime model is closed should an unreachable write-capable BUS recipe be built and combined with the already-captured IQ/DMI RT-CDM corpus.
