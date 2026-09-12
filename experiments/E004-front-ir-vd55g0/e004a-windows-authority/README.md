# E004a — VD55G0 Windows authority

Status: Windows authority captured and mechanically replayable; no Linux VD55G0 probe or Linux IR stream has been performed.

E004a defines the Surface Pro 11 front-IR oracle from this machine's installed Windows camera stack. Same-machine Windows is the parity authority. Public ST/Linux material is kept separately as implementation reference only and does not establish SP11 behavior.

## Windows authority

The exact installed Surface/QTI material establishes:

- sensor package: ST VD55G0 / ACPI SMO55F0 / Surface subsystem MSHW0492;
- QTI sensor address 0xc0, corresponding to Linux 7-bit address 0x60;
- ID register 0x0000 and package expected ID 0x3047;
- CCI0 master0 -> CSIPHY0;
- MCLK0 = 19.2 MHz;
- reset GPIO109;
- Windows resources LDO4_M = 1.8 V, LDO2_M = 1.15 V, LDO7_M = 2.8 V;
- 644x604 RAW10, VC0, CSI-2 data type 0x2b, 60 fps;
- line length 1200, frame length 1955, output pixel clock 84 MHz;
- sensor MIPI data-rate programming = 840,000,000 bps.

The exact sensor package is SHA256
`e574db7eb28231d3fa4f5eee5c1861919125d8ec7a753fc7a0708606e1f1a794`.
`extract_windows_vd55g0.py` reparses that package and mechanically derives the timing values and firmware-patch bytes.

## Same-machine live Windows transport oracle

KD capture on this SP11 observed the live `qccammipicsi8380` MIPI context during IR operation:

- number of data lanes = 1;
- data rate = 840,000,000 bps;
- D-PHY settle count = 0x10;
- observed branch selectors at context +0x4c/+0x54 = 0/0.

The exact installed `qccammipicsi8380.sys` is pinned at SHA256
`033f5b1431ad4c76a12ac3b7f0a5be42e460a03bcff40d249511b3034786d407`.

Its ARM64 code maps 1/2/4 D-PHY data lanes to masks `0x81/0x85/0xd5`.
The same driver names the corresponding receive-status slots
`Lane0, Lane2, Lane4, Lane6, Clk`.
For the observed one-lane path, `0x81` therefore selects `Lane0 + Clk`.

No separate Windows polarity-inversion/swap operation was proven in this path. E004a records this as
`NO_INVERSION_PROVEN`; it does not invent a Linux polarity flag.

For CSI-2 D-PHY, the Windows-observed 840 Mbps bit rate corresponds to a 420 MHz DDR link frequency.

## Same-machine live Windows first-start patch oracle

A fresh Windows boot was stopped under KD before normal camera activation. The first explicit
`Surface IR Camera Front` start then succeeded at NV12 644x604 60 fps.

The Surface aux-sensor driver's sequential InitialConfig submission at RVA `0x4c74` carried a
4880-byte packet (0x1310 bytes), SHA256
`81e96e0470cbfa58065eba12ea1a998349b306111f2edee296d7044a69146cdd`.

Beginning at packet offset `0x1c`, that live Windows transaction contains 552 contiguous register
writes from `0x2000` through `0x2227`. Extracting the 552 data bytes gives SHA256
`5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321`.

That hash is byte-identical to the patch independently extracted from the exact Surface VD55G0
package. Therefore, on this SP11, Windows actually transmits the Surface 552-byte patch during
first IR activation. The patch is not merely unused data embedded in the package.

No separate revision read was observed before that patch transmission in the captured PowerOn path.
That fact is recorded as an observation, not as a claim that the silicon revision is known.

## CSIPHY0 live/idle evidence

Two complete 8 KiB CSIPHY0 live snapshots were captured at physical base `0x0ace4000`.
Each contains 2048 dwords. They differ at only one dword:

- `0x0ace4ef4`: `0x000000c1` vs `0x000000c0`.

The corresponding idle snapshot returned `0x80000000` for all 2048 dwords, establishing the
powered/inaccessible idle behavior for this capture.

The raw KD logs and the captured 4880-byte InitialConfig packet are preserved in this directory and
SHA-pinned by `verify.py`.

## Lifecycle and safety boundary

The Windows QTI package also preserves operation-type-4 poll/wait semantics in the VD55G0 stream
lifecycle. These must not be flattened into blind Linux register writes.

E004a did not perform a Linux VD55G0 probe, Linux stream, Linux firmware upload, or Linux
illumination action. Initial Linux work must keep illumination/strobe paths absent/disabled.

## ST Linux reference — not parity authority

The official ST VD55G0 Linux source snapshot is preserved byte-exact under
`src/front-ir-vd55g0/st-vd55g0/` because it is useful implementation scaffolding and builds
against Golden's headers.

It is explicitly **REFERENCE ONLY**:

- it does not prove Surface lane count or lane mapping;
- it does not authorize the Surface firmware patch;
- its default 804 Mbps / 402 MHz / frame-length 1860 values are not SP11 parity values;
- its CUT1/CUT2 patch blobs are not the Surface Windows patch.

`verify_reference.py` checks the pinned ST snapshot independently. Its result is not an input to
the Windows parity-authority gate.

## Verification

Run:

```
python3 experiments/E004-front-ir-vd55g0/e004a-windows-authority/verify.py
```

A pass requires the exact Windows package and Windows drivers, the raw KD evidence, exact live
InitialConfig packet, transport values, lane-mask ARM64 instructions, CSIPHY0 snapshots, and
package-vs-live patch equality to all agree mechanically.

Reference-only ST checks are separate:

```
python3 experiments/E004-front-ir-vd55g0/e004a-windows-authority/verify_reference.py
```

## Next gate: E004b

E004b may now translate the Windows-proven power and transport facts into a disposable Linux
probe-only candidate:

1. verify/integrate the Linux PM8010 providers corresponding to Windows LDO2_M/LDO4_M/LDO7_M;
2. encode CCI0/master0 -> CSIPHY0 with one D-PHY data lane preserving the Windows `Lane0 + Clk` route;
3. use 840 Mbps / 420 MHz transport and the exact Windows timing;
4. keep the Surface 552-byte patch available as Windows-parity evidence, but make the first Linux
   action an identity/revision-only proof before any patch upload;
5. do not stream and do not enable illumination in that first Linux probe;
6. return to Golden after the bounded experiment.
