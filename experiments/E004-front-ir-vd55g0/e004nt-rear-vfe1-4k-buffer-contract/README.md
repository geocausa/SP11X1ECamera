# E004nt — isolated compiled rear 4K coherent-DMA surface and VFE1 FULL Y/C relative layout

Parent E004ns `4684273a318856266b35d222de4e8cbf0240fb3c`. Windows E004nq established **rear CSIPHY1 four-lane D-PHY → CSID1 IPP → VFE1 FULL** on SP11. E004nr compiled a rear-only media graph and Windows-derived WM register profile, and E004ns compiled a separate rear CSID1 IPP register-target routine. **E004nt adds the next actual compiled Linux kernel component: a private, bounded, coherent-DMA rear 4K output-surface allocator and WM0/1 metadata/image address builder.** All three experiments remain OFFLINE with no runtime caller, installed module, user application output format, hardware stream or Golden kernel alteration.

## Same-machine Windows rear 4K physical DMA *relative offset* oracle — two passes agree

The new `extract-sp7-rear-relative-layout.ps1` was run **only on SP7** against its existing *private original* E004nq `dd /p` windows, with Windows rear 4K VideoRecord LIVE1 and LIVE2. The routine reads the four original VFE1 WM0/WM1 image/metadata DMA address registers **only in SP7-local variables** and exports only their subtracted relative offsets, frame-increment register scalars, measured configured WM strides and row bounds. It validates the two independent rear capture phases against each other, checks that Y/C metadata bases were page-aligned and their frame windows and row extents are internally consistent. **It never prints, exports, commits or uses original Windows DMA addresses, raw KD logs, optical pixels, thumbnails, RAW frames or hashes.** Its source includes a Windows PowerShell5-specific unsigned 32-bit maximum check, using `[long][uint32]::MaxValue` rather than a signed `0xffffffff` literal.

| Relative to first Y metadata base | Two matching Windows rear 4K capture values |
|---|---:|
| Y metadata offset | `0x000000` |
| Y image data offset | `0x011000` |
| C metadata offset | `0xA9D000` |
| C image data offset | `0xAA6000` |
| Y WM0 FRAME_INCR | `0xA9D000` |
| C WM1 FRAME_INCR | `0x559000` |
| Combined Y + C single-window length | `0xFF6000` (16,736,256 bytes) |
| Both physical WM row strides | 5120 bytes |
| Y physical WM geometry | 3840×2160 |
| C physical WM geometry | 3840×1080 |

Arithmetic and bounds independently match in both captures: `0x11000 + 5120×2160 == 0xA9D000`; `0xAA6000 + 5120×1080 <= 0xFF6000`; C metadata starts at exactly Y's frame-increment boundary and C data starts `0x9000` beyond C metadata. This closes the *relative hardware register-layout* observation that E004nr had intentionally left unresolved. It **does not prove the Windows physical memory mapping, the encoded UBWC layout or the valid format of a Linux user-facing NV12 plane**.

Only the whitelisted derived fields are in `RELATIVE-RESULT.json`. Original Windows KD windows remain private on SP7, original Windows rear WinRT phase logs remain private on SP11 Windows, and no proprietary Windows driver/tuning/firmware or optical image content is exported.

## Actual new Linux kernel source and defensive DMA ownership

`camss-vfe-e004nt-rear-4k-buffer.inc` is real compiled kernel source. It has source-pinned constants for the Y/C metadata and data offsets, two WM frame increments, 3840×2160/1080 output geometry, 5120-byte stride and the 4K-aligned `0xFF6000` minimum surface length. Compile-time `static_assert` gates require both row extents to stay within their respective complete metadata+image windows and the Y and C increments to sum to the total allocation. **These are Windows hardware write-master invariants, not a promise of directly viewable NV12 images.**

The isolated functions `vfe680_e004nt_rear_surface_alloc()`, `vfe680_e004nt_rear_surface_addrs()` and `vfe680_e004nt_rear_surface_free()` are compiled into an ARM64 CAMSS module and retained for inspection. If explicitly wired in a later approved source revision, allocation will use `dma_alloc_coherent()` with **the actual Linux CAMSS/IOMMU device** to obtain one device-contiguous 16,736,256-byte DMA aperture, rather than wrongly assuming that the first entry of a `vb2-dma-sg` table spans the entire rear image. The candidate requires page-aligned Linux DMA, checks **the complete span** against the 32-bit VFE address aperture, bounds-checks the row and metadata regions, and only then derives four **Linux** output register addresses from the newly allocated base. Failure releases and clears the allocation; a surface marked in flight cannot have its addresses rebound or be freed. This source does not include or print any Windows IOVAs.

**Not yet implemented:** real runtime activation of this surface, Linux VB2/V4L2 output-format negotiation and synchronization, known-correct UBWC compression/metadata interpretation, rear OV13858-specific IFE IQ/3A/RT-CDM commands, separate stats allocation and per-frame bind/retire, and exclusive shared CSID1/VFE1 front/rear lifecycle. Even successful `dma_alloc_coherent()` in a future trial will not on its own prove that rear hardware can produce a valid 4K image. `vfe680_e004nt_rear_4k_runtime_authorization()` **always returns `-EOPNOTSUPP`**. There is NO caller to the new functions in the current probe, V4L2, sysfs, streaming or front-runner paths. All hardware/output behavior remains unchanged.

## Build/test and protected Golden evidence

`stage-build.sh` checks the exact parent Git SHA, Golden camera guard, original accepted front/rear kernel source hashes, and each new source include's hash, and creates a **unique isolated build directory**. It copies original CAMSS unchanged, then inserts exactly one source-only E004nr rear media-graph profile include into staged `camss.c`, the E004ns rear IPP include into staged `camss-csid-680.c`, and E004nt's new 4K DMA source include into staged `camss-vfe-680.c`. Removing each added include leaves the **exact original integrated file contents byte-for-byte**. The pre-existing dirty Denali DTS was not changed.

An actual SP11 ARM64 CAMSS module was built with `W=1 -j4` against the prepared Golden headers, with no warnings or errors. `aarch64-linux-gnu-nm -a` confirms the compiled E004nt target/allocator/address/free/deny symbols as well as E004nr and E004ns rear symbols. The isolated module remains **only locally on SP11**, uninstalled/unloaded:

`/home/geoca/Documents/SP11-PROJECT/02-kernel/e004nt-rear-4k-buffer-build/camss/qcom-camss.ko`

- module bytes: **13,621,984**
- SHA256: `f5cc00181a2d1966cd9499544067b1a920e76bf4db73e8063bae052540fb0b04`
- vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

`BUILD-RESULT.json` includes only the scalar build/safety provenance, NOT the compiled module. The offline `verify.py` cross-checks the two distinct private-Windows-derived Y/C relative layouts against BOTH E004nr WM configs, every new C compile-time layout constant, coherent 32-bit DMA safety and in-flight protection, original source-byte preservation, actual compiled ARM64 module SHA/vermagic and retained symbols. Its **18 fail-closed negative cases** reject front-sized stride/offset/rows, mismatched second Windows capture, insufficient total buffer space, bad metadata/packer/frame increments, unsafe pointer export and false layout proof. It DOES NOT allocate memory or access any camera. All checks were run under Golden with overlap guard passing.

Next development step is a distinct **rear VFE1 WM0/WM1 output programming and event/ownership contract** plus separately validated IQ/3A/RT-CDM sequence, then a guarded Linux hardware test with full rollback. The accepted front native VFE1 E003i 27-frame path, rear Linux RAW E004lr path and E004ne full software4K fallback must remain available. E004nt does **NOT** prove a native Linux rear 4K optical ISP frame, real DMA allocation success, UBWC decoding or image quality.
