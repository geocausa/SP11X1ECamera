# E003g Windows CSID/VFE oracle checkpoint — 2026-08-27

> **Superseded route interpretation (2026-08-28):** the route-complete follow-up proves the front Windows path is **CSIPHY2 -> CSID1 -> IFE1/VFE1**. VFE0 and VFE1 are separate 16 KiB resources; do **not** resume the old pending `VFE0 +0x4000..+0xefff` capture. Continue from `docs/runbooks/2026-08-28-e003g-route-resolved.md`.

## Resume point

Branch: `experiment/e003-front-imx681-cphy`

Pre-checkpoint code/evidence base: `2df6dfb` (`E003f: accept host-powered C-PHY receiver parity`).

Golden recovery remains:

- kernel `7.1.5-sp11-render-parity-v4+`;
- `sp11_entry=7.1.5-sp11-fullio-v19c`;
- GRUB saved entry `sp11-audio-fullio-v19c`;
- one-shot `next_entry` empty after return from Windows.

## Accepted chain before this checkpoint

- E003b: same-machine IMX681 identity / power / CCI route accepted.
- E003c: native IMX681 V4L2 bind accepted.
- E003d: immutable IMX681 -> CSIPHY2 C-PHY graph accepted.
- E003e: exact Windows init + 3840x2640@30 mode0 programmed in standby, `MODE_SELECT=0`.
- E003f: host-powered receiver-only CSIPHY2 activation accepted at 121/121 Windows-live register parity with clean unwind.

## New E003g evidence

A fresh same-machine Windows/KD run captured full physical windows for the CSID wrapper, CSID0 and CSIPHY2, plus the first 16 KiB of VFE0/IFE0, across:

`IDLE -> LIVE1 -> POST -> LIVE2 -> POST2`.

Both WinRT front-camera reader starts returned `Success`; both live holders were stopped with the normal `MediaFrameReader.StopAsync()` path.

Canonical checkpoint directory:

`experiments/E003-front-imx681-cphy/e003g-windows-csid-vfe-oracle/`

Raw log SHA-256:

`2c35645ae23db4393c669d80a2b52555ec4659b903ca861f13d20a58bb569982`

Hard reproducibility result:

- wrapper LIVE1 == LIVE2: all 1024 dwords;
- CSID0 LIVE1 == LIVE2: all 2048 dwords;
- VFE0 captured subset (`+0x0000..+0x3fff`) LIVE1 == LIVE2: all 4096 captured dwords, all live values zero;
- CSIPHY2: only five live-variable dwords;
- both post-stop dumps equal idle across every captured region.

## Historical aperture interpretation — superseded 2026-08-28

At this checkpoint the address space after VFE0 was temporarily interpreted as a possible continuation of VFE0, leading to a proposed 0xf000-byte follow-up. **Do not execute that follow-up.** The route-complete 2026-08-28 capture separated the actual VFE0 and VFE1 resources and proved the front WinRT stream uses CSID1 -> VFE1 while VFE0 remains inactive. See `docs/runbooks/2026-08-28-e003g-route-resolved.md`.

## Critical interpretation rule

Do **not** label or program the active CSID path from a guessed RDI0 offset map. The full Windows dump shows several repeated path-like CSID0 blocks and stable programming that must first be mapped mechanically to the exact X1E CSID680 layout.

Likewise, do not adopt an external VFE680 `mode=1` choice or the external `LINE_LENGTH_PCK=8704` workaround without same-machine Windows proof.

Windows remains the oracle. External Linux implementations are hypothesis generators only.

## External differential reference

`https://github.com/karsies-wq/sp11-imx681-linux`, inspected at `b08f76f`.

Useful signal from that implementation:

- it directs attention to CSID680 drop/crop state and VFE680 write-master programming;
- its working timing/workaround choices are not automatically Windows-parity choices.

Production target remains the Windows-derived IMX681 mode:

- RAW10 VC0;
- 3840x2640 @ 30 fps;
- line length 6752;
- frame length 3554;
- exact established Windows C-PHY electrical state.

## Historical next task — completed/superseded

The route-resolution work requested by this checkpoint was completed on 2026-08-28. The canonical result is `IMX681 -> CSIPHY2 -> CSID1 -> IFE1/VFE1`, with CSID1 IPP receiving VC0/RAW10 and producing a measured/cropped 3840x2160 path. The old CSID0/VFE0-extension steps are no longer actionable. Resume from `docs/runbooks/2026-08-28-e003g-route-resolved.md`.

No Linux first-frame patch has been applied at this checkpoint.
