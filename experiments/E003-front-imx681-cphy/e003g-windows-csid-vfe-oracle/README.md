# E003g Windows CSID0 / VFE0 oracle checkpoint

Date: 2026-08-27

## Purpose

Freeze the same-machine Windows state of the front-camera receiver path before making any Linux CSID680/VFE680 first-frame change. The first acquisition fully covers CSID wrapper/CSID0/CSIPHY2 and captures only the first 16 KiB of the larger SP11 VFE0 aperture. This checkpoint exists specifically to prevent a working external Linux implementation from becoming a substitute for Windows parity.

## Acquisition

- Physical target: this Surface Pro 11 / X1E80100.
- Windows device explicitly selected: `Surface Camera Front` / Sony IMX681.
- Camera trigger: the same WinRT `MediaCapture` + `MediaFrameReader` mechanism used for the accepted E003a C-PHY oracle.
- `MediaFrameReader.StartAsync()` returned `Success` in two independent live passes.
- Both passes were stopped through the holder's normal `MediaFrameReader.StopAsync()` path.
- SP7 KDNET broke the live Windows kernel and read physical MMIO.
- No debugger credential/key is present in the committed capture.

Physical windows captured in every phase:

| block | physical range | size |
|---|---|---:|
| CSID wrapper | `0x0acb6000..0x0acb6fff` | 4 KiB |
| CSID0 | `0x0acb7000..0x0acb8fff` | 8 KiB |
| VFE0 / IFE0 **captured subset** | `0x0ac62000..0x0ac65fff` | 16 KiB |
| CSIPHY2 | `0x0ace8000..0x0ace9fff` | 8 KiB |

Capture sequence was `IDLE -> LIVE1 -> POST -> LIVE2 -> POST2`.

**Aperture correction discovered during repo validation:** the SP11 Denali baseline declares VFE0 at `0x0ac62000` with size `0x0000f000` (60 KiB), ending at `0x0ac70fff`. The initial KD command used the upstream 16 KiB VFE0 size and therefore captured only `+0x0000..+0x3fff`. The remaining `+0x4000..+0xefff` must be captured on the next Windows pass before VFE write-master/mode parity can be decided.

Raw capture:

- `raw/E003G_CSID_VFE_ORACLE_20260827.log`
- bytes: `1307128`
- SHA-256: `2c35645ae23db4393c669d80a2b52555ec4659b903ca861f13d20a58bb569982`

## Hard results

`extract_oracle.py` validates the full expected dword count for every region in every phase and emits the machine-readable summary/CSVs.

- CSID wrapper: LIVE1 and LIVE2 are identical across all 1024 dwords; both post-stop dumps equal the idle dump exactly.
- CSID0: LIVE1 and LIVE2 are identical across all 2048 dwords; both post-stop dumps equal the idle dump exactly.
- VFE0 captured subset (`+0x0000..+0x3fff` only): LIVE1 and LIVE2 are identical across all 4096 captured dwords; both post-stop dumps equal the captured idle subset exactly. All 4096 live values in this subset are zero. **This does not prove the full 0xf000-byte VFE0 state.**
- CSIPHY2: 2043/2048 dwords are identical between the two live captures and five offsets are live-variable; both post-stop dumps equal idle exactly. This is consistent with the already accepted E003a/E003f C-PHY oracle behavior.
- During powered-off IDLE/POST, CSID wrapper/CSID0/VFE0 reads return `0x80000000` across the captured windows. This is preserved as an observed powered-off/inaccessible MMIO sentinel and is **not** interpreted as each register's architectural reset value.

Some stable Windows-live values useful as anchors for the next decode pass are deliberately kept as raw offsets rather than prematurely assigning RDI/IPP semantics:

- wrapper `+0x000 = 0x00000001`, `+0x004 = 0x00000101`, `+0x008 = 0x00000001`;
- CSID0 `+0x000 = 0x30000000`, `+0x080 = 0x00000001`;
- CSID0 `+0x200 = 0x00032103`, `+0x204 = 0x00000001`;
- CSID0 has stable non-zero programming around `+0x24c..+0x268` and repeated path-like blocks beginning around `+0x300`, `+0x500`, `+0x600`, `+0x700`, `+0x800`, `+0x900`, and `+0xb00`.

See `csid0-live-nonzero.csv`, `vfe0-live-nonzero.csv`, `wrapper-live-nonzero.csv`, and `csiphy2-live-nonzero.csv` for the literal live values.

## Interpretation boundary

The active Windows CSID route and VFE write-master mode are **not yet semantically decoded**. VFE semantic decoding is additionally blocked on a second Windows capture of the missing VFE0 `+0x4000..+0xefff` range. In particular, offsets initially guessed to be an RDI0 block were shown by the full dump not to be a sufficient description of the active Windows path. Do not turn guessed labels into Linux programming.

The next step is to mechanically map the stable Windows-live offsets against the exact X1E CSID680/VFE680 register layout and our kernel's stream lifecycle. Only after that mapping is complete should Linux CSID/VFE programming change.

## External implementation policy

A separate working Linux implementation (`karsies-wq/sp11-imx681-linux`, inspected at commit `b08f76f`) is useful as a differential reference, not as an oracle.

It highlighted concrete areas to investigate, including CSID drop/crop handling and a VFE680 write-master mode choice. It also uses an `8704` line-length workaround. None of those values/choices are accepted into our production path merely because they work there.

Our required production target remains the same-machine Windows mode already established in E003: RAW10 VC0, `3840x2640 @ 30 fps`, line length `6752`, frame length `3554`, one-trio C-PHY at the established Windows electrical state. Any external delta is promoted only if Windows on this machine proves the same behavior.

## Safety state after acquisition

The Windows boot was one-shot only. After the oracle capture the machine returned to:

- kernel `7.1.5-sp11-render-parity-v4+`;
- `sp11_entry=7.1.5-sp11-fullio-v19c`;
- GRUB `saved_entry=sp11-audio-fullio-v19c`;
- empty `next_entry`.

No Linux camera runtime patch was made as part of this oracle checkpoint.
