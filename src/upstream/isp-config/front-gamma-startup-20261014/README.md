# Front startup Gamma data: reuse the calibrated native precision bridge

The integration baseline remains unified48/libcamera21/run93/v15. This package
adds a startup data entry point around two existing codecs. It does not replace
the driver, tone calibration, IPA, allocator, per-frame queue or Gamma algorithm.

## Prior work and exact gap

The working IPA's semantic R/G/B tone curves are257 points each in0..1023.
native_front_isp_encode writes the existing10-bit semantic base/delta envelope.
native_front_isp_decode calls native_front_gamma10_expand, which maps each point
with(value*4095+511)/1023 into the native12-bit range, then emits base12 plus
signed delta12 at bit12. Endpoints map exactly0->0 and1023->4095.

Both codecs and the Gamma conversion already exist and exactly match the
calibrated native source stage. They are reused unchanged. The old startup
still obtains initial data through its private profile; there was no typed
startup entry point using these own points independently of that input.

sp11-front-gamma-startup.h supplies that missing entry point. It calls the
actual encode/decode pair with own points, using caller-owned packet/word
scratch. It emits3072 data bytes,768 words across semantic R/G/B. It does not
emit a CDM program, DMI command, bank, selector, device address or activation.
The compatibility envelope is transient internal scratch, not a new public ABI.

The6160-byte workspace belongs outside the kernel's small stack. Pointer,
extent, alias and retained original calibration-policy checks precede encoding.
Points/policy remain immutable. Output is unchanged on any failure and its
tail is preserved; scratch may change on failure. The caller must own all
declared extents for the synchronous call.

## Precision audit and remaining boundary

| Layer | Retained source fact | What it does not prove |
| --- | --- | --- |
| Front sensor/CSID input | RAW10 selection exists in the qualified input helper | Whole ISP precision |
| Titan680 capability writer | Retained E011M writes capability values18/14/14 | A live front stage's processing mode |
| Own IPA tone domain | Existing v15 curves and interpolation use0..1023 | Native DMI words being10-bit |
| Actual tone bridge |10-bit semantic points expand to12-bit base/delta with0..4095 endpoints | Complete CST/core precision or hardware startup parity |
| Native FULL rounding helper | Existing qualified conversion models10-to8-bit output | Every upstream Bayer/colour stage being10-bit |
| Native CST override | Own coefficient patch leaves offsets/scales/clamps inherited | An independent complete CST startup |

The10-bit tone input and12-bit wire output are distinct. Do not feed unexpanded
10-bit points into native12-bit startup or infer CST clamps solely from the
tone point maximum. The calibrated run93 records an own CCM override; it does
not record a CST matrix override. The optional CST patch function is not proof
that its inherited auxiliary fields or matrix were removed from the baseline.

Next use retained E006r's functional CST12 field packer and original front source
to bind matrix/offset/scale/clamp semantics to the actual calibrated domain.
Reuse own measured CCM and tone; exclude the old rear/vendor reserve values.
Neither source bit-width capacity nor successful Gamma conversion establishes
the unobserved front core routing or the full pipeline precision chain.

## Qualification

test-worker.py compares the actual adapter with the unchanged working encoder/
decoder under GCC and Clang ASan/UBSan. Each passes6209 differential cases:
every10-bit constant base, representable signed slope boundaries, asymmetric
channels, random bounded walks and the existing own v15 curves. Native slope
limits reject1024 cases;3850 count/capacity/policy/late-field rejection cases
preserve output. Disjointness, source immutability and output tails are checked.

An independent integer oracle checks scale, native base and signed delta for
every accepted synthetic word. Own curve arrays and generated data stay on SP11;
only counts, source pins and results are committed. No optical data or private
startup/tuning input is read. No calibration is refitted.

Four compiled unsafe adapter mutations fail under each compiler: premature
publication, bypassed domain policy, missing points/output overlap and shifted
payload output. The original Gamma data compiler and ISP codec/state tests
are also compiled and run unchanged; their provider mock remains a mock.

A tiny native7.1.5 ARM64 W1/Werror probe builds with zero diagnostics. Workspace,
points and output are static test storage; no large kernel stack allocation.
It is never installed or loaded, and CAMSS/kernel are not rebuilt. Header style
is0 errors/0 warnings/0 checks. Final acceptance is host02/native-compile02.
host01/native-compile01 passed functional checks but had two alignment style
checks; only final whitespace/source pins are accepted.

Run on SP11 with unused stages:
- python3 test-worker.py <unique-output-directory>
- python3 build-worker.py
- python3 qualify.py

Evidence: docs/FRONT-GAMMA-STARTUP-20261014.json.

## Integration gate

This is an independent startup data leaf for the existing own calibration.
It adds no configuration register addresses; the45-address candidate count
stays unchanged. It does not compare its own tone with the old private default
curve or establish identical first-frame behavior.

Complete CST/CCM auxiliary state, core/precision/geometry, remaining startup
and own LSC/ABF/statistics activation still need assembly around the proven
native lifecycle. DMI bank/address binding must use the existing owned provider
and its physical lifetime proof. Both installed private consumers remain.
Only after that integration should private loading be replaced in an isolated
candidate and original-domain hardware/image parity tested. Upstream readiness
is false; Golden, daily source and existing calibration are preserved.
