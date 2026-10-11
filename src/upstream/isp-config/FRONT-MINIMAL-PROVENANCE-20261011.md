# Independent front processing sequence

This is the first combined processing sequence for replacing the private front
startup carrier. It is a source-only, driver-internal builder. It has no file
reader, private schema, legacy instruction template, calibration input, MMIO,
allocation or queue submission. The only runtime input is bounded geometry,
10-bit precision and RGGB Bayer order. Unsupported precision/order fails closed.

It is **not a complete camera startup provider**. The installed front and rear
loaders still require their private files. A successful object build does not
remove those dependencies or establish acceptable image quality.

## Source provenance

| Part | Source and status |
|---|---|
| Sixty-four module addresses and bit-zero enable convention | Public GPL-labelled `camss-vfe-680-pp-regs.h`, author WIP revision `8fba120842097db3284f4b1c7fa7351b6cbe3f93`. SHA-256 `bce9607bac5b46ce907a1434b3a772c5c40b753b1c933db7d37822b9c26e020e`. The header says it was generated from a SoC register description; that description's provenance still needs review. We use its named module addresses, not vendor tuning tables. |
| Four demosaic parameters | Public GPL-labelled `vfe_setup_demosaic()` in `camss-vfe-880-pp.c`, Oct 5 IFE RFC for SM8650. SHA-256 `c4845b4e33212267db16200574686b0b8898d5c3af1a73580761fb72c94fefd0`; exact posted source pinned in `docs/UPSTREAM-IFE-RFC-REFERENCE-20261011.json`. The four interpolation/classifier words are explicitly borrowed bring-up parameters, not newly derived mathematics. Their suitability for VFE680 is unproved. The RFC's WB, CCM, gamma tables and opaque core configuration are not copied. |
| CST values | Own rational BT.601 full-range Q10 calculation, input order G,B,R, with exact neutral-preserving row sums. Hypothesised ten-bit range has maximum 1023 and chroma centre 512. Auxiliary fields and minima are zero. This domain/order hypothesis needs hardware proof. |
| Geometry and rounding | Existing independently written typed adapters, with enable-state variants added here. Geometry derives from input/output extents; eight-bit clamping derives from 255 and a two-bit reduction. Functional scaler/rounding mode bits retain the provenance and review gates documented in `GEOMETRY-STATS-PROVENANCE-20261011.md` and `FRONT-FIELDS-PROVENANCE-20261011.md`. |
| CDM serialization | Own bounded helpers; GPL wire definition and pins in `cdm-reference-20261011.json`. No DMI commands are emitted by this processing builder. |

The new code is GPL-2.0-only. Public source identity and a GPL label do not settle
all provenance, copyright attribution, DCO or upstream acceptance questions.
The borrowed function's posted patch headers must be authenticated before a
submission. No private file bytes, values, hashes or images were used in this work.

## Program and policy

The builder emits 1204 bytes containing 81 REG_CONT commands:

1. Disable every named module. This clears enables, including table consumers,
   statistics and unused output paths; it does not erase tables or stop DMA.
2. Program the demosaic parameters, mathematical colour transform, full-frame
   luma/chroma scaling, crop and eight-bit rounding with modules disabled.
3. Enable only demosaic, colour transform, video luma/chroma scaling and their
   rounding/crop blocks. The other 58 module enables remain clear.

This deliberate manual-capture policy omits lens shading, black correction,
white balance, colour correction, gamma, noise reduction, histogram and other
statistics. It does not aim for the daily camera's appearance or auto exposure.
The hypothesis is that optional block bypass permits a simple linear path.
Whether DEMUX/CHANNEL_GAIN can be bypassed and whether the resulting channel
order/precision matches the CST are unresolved; no hardware admission is granted.

Clearing all module enables requires exclusive ownership of a stopped full VFE
pixel path. It must never be appended to a live stream or shared with another
camera. Disable writes do not establish bus-client halt, IRQ retirement or CDM
completion. The helper checks memory extents and rejects overlapping input/output;
it cannot establish those hardware preconditions.

## Reproduce the checks

Obtain the exact public sources pinned above, then run from the checkout root:

```sh
python3 src/upstream/isp-config/test_front_minimal.py \
  --vfe680-header "$SP11_VFE680_PUBLIC_HEADER" \
  --vfe880-source "$SP11_VFE880_PUBLIC_SOURCE"
```

Both arguments are required. Missing, changed or symlink references are rejected.
The test compiles the production headers with GCC and Clang, ASan/UBSan. It checks
384 geometry combinations, 1242 atomic rejection cases per compiler, all 64
public module addresses, the four public demosaic words, 18 calculated CST words,
1024 neutral-colour semantic vectors, four crop words and enable ordering. The
colour oracle establishes mathematical behavior, not actual ISP rounding.

Affected existing field, geometry and CST tests also pass. The existing enabled
wrappers retain their behavior. A separate ARM64 object build uses the prepared
public RFC plus four-patch CAMSS candidate with `W=1 KCFLAGS=-Werror`. Its undefined
symbols are only memcpy, memset and stack protection. No module was linked or
loaded. Commands, source pins and results are recorded in
`docs/UPSTREAM-FRONT-MINIMAL-VALIDATION-20261011.json`.

For a compile-only object, copy the five headers in the recorded include closure
and `front-minimal-compile-probe/Makefile` plus its C source to a fresh stage:

```sh
make -C "$SP11_KERNEL_SOURCE" O="$SP11_KERNEL_BUILD" M="$SP11_COMPILE_STAGE" \
  W=1 KCFLAGS=-Werror sp11-open-front-minimal.o
```

Never load this probe. It contains no camera integration.

## Next work, in dependency-removal order

1. Establish VFE680 core input/Bayer routing and internal precision from reviewed
   public functional definitions. Resolve DEMUX/CHANNEL_GAIN bypass rather than
   copying an opaque core word or restoring private defaults.
2. Bind this processing graph to independently generated CSID, NV12 bus-client
   and CDM setup, with owned memory and physical stop/IRQ retirement. No private
   carrier may be copied into startup or retained for subsequent parameter updates.
3. Compile a distinct, recorded hardware candidate that has no private loader or
   fallback, with a rollback to the preserved daily stack. Qualify cold start,
   stop/reopen and switching while Linux stays awake. First front optical tests
   require the user to turn the front camera toward the SP7 screen's healthy area.
4. Implement the rear provider separately: its GRBG mode and processing domains
   cannot inherit front assumptions. Then add open measured tuning, statistics,
   automatic controls and libcamera integration with explicit provenance.

Both runtime dependencies remain blocked until the respective independent
provider actually streams with its private consumer and fallback absent.
