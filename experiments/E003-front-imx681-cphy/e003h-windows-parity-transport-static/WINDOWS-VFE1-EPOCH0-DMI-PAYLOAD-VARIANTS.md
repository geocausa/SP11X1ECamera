# E003h Windows VFE1 Epoch0 DMI payload variants

Date: 2026-08-29

## Result

The five steady-state Epoch0 main-BL shapes from `0024` now have representative same-machine Windows DMI payload bytes captured locally and a fail-closed **hash-only** oracle. Raw DMI payload `.bin` files are intentionally local/untracked and are not repository artifacts.

The accepted live mapping capture is `windows-vfe1-epoch0-dmi-payloads/E003H_VFE1_DMI_VARIANT_RING_20260829.log` (8,868 bytes, SHA-256 `f44d09f8669576fe868a51d2b410c443dd863c8d00b7ab53ad1375b3b4acf3b0`). It records packet/main-BL shape pairs and the exact Windows 15-slot DMI source-ring snapshot used for the hash oracle. The observed `0x8000` source-slot / 15-slot ring geometry is Windows allocator behavior only and is not a Linux constant.

`extract_vfe1_epoch0_dmi_payload_variants.py` hash-pins the exact installed `qccamisp8380.sys`, the live log, the local payload evidence and the accepted `0024` batch topology. It extracts payload hashes from the same source-slot offsets already established by the startup patch/DMI oracle and fails closed if driver instructions, source layout, variant DMI topology or evidence hashes drift.

## Payload topology

The five variants carry nested DMI identity sets:

- `0x5a4`: `3d08/1`, `5a08/1`;
- `0x6b8`: adds `4308/1..3` and `5f08/1..3`;
- `0x83c` / `0x868`: additionally carry `a008/1..2` and `a208/1..2`;
- `0x958`: additionally carries `4708/1` and `4908/1`.

Representative sample counts in the payload oracle are `0x958=2`, `0x868=10`, `0x83c=1`, `0x6b8=4`, `0x5a4=2`. Within those samples:

- `4308/1` and `4308/2` are frame-varying in `0x958`, `0x868` and `0x6b8`;
- `4708/1` and `5a08/1` are also frame-varying in the two captured `0x958` samples;
- the observed `0x5a4` payload identities are invariant across its two samples;
- `0x83c` has only one dedicated payload sample, so within-variant invariance is intentionally not claimed.

The derived JSON contains every payload identity, byte length and SHA-256 set. No raw payload byte string is embedded in the extractor, oracle or kernel source.

## KMD ownership correction

Exact installed-driver disassembly closes the previous “five-way variant selector” wording. `DAL_ife_process_iq_packet` at RVA `0x26838` receives an upstream IQ packet and derives active/changed group masks from its resource records (`0x28080`, `0x28168`, `0x267d0`). Changed groups are processed by `0x28238`; record type is loaded from each entry at `+0x8c`, with type `0x0c` dispatched to the already-known `0x27920` bandwidth/request parser.

Therefore **qccamisp8380 KMD does not own a hidden 0x958/0x868/0x83c/0x6b8/0x5a4 selector**. The observed main-BL shape and the frame-varying IQ payload values are inputs supplied by the upstream IQ packet producer. Linux must not invent a kernel selector or freeze one captured sequence.

## Remaining boundary

`0024` already proves the companion BL4 `GEN_IRQ` userdata equals the monotonic observed batch index. The exact upstream tag/request source is still not closed. Likewise, the producer/value rule for frame-varying IQ payloads remains above KMD.

The next bounded oracle should therefore target the upstream IQ-packet producer/tag handoff, not another Epoch0 batch capture. No RT-CDM FIFO submission, VFE1 PIX/CSID1/MIPI start, IMX681 transmission or Linux front frame is authorized.
