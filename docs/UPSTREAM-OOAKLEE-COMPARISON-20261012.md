# SP11 comparison with ooaklee — 2026-10-12

## User reuse boundary, 2026-10-12

Use independently reverse-engineered Windows hardware behavior and functional
register transactions. Do not copy/extract Windows calibration data, vendor
tables, tuning payloads or blobs into the replacement. Public availability or
a GPL label alone does not establish admissible provenance. A source array
representing independently observed functional transactions is distinguished
from an extracted vendor table; review its derivation before runtime admission.

Compare our existing work and ooaklee component by component. Prefer matching
same-machine hardware evidence, correct interface/timing/power behavior and
maintainable source. Keep our qualified control/timing, allocator/completion/
reset/ownership work and independently measured or mathematically generated
calibration where applicable. No wholesale replacement or fresh calibration
restart. Directly extracted Windows factory tuning remains reference-only and
must not become replacement runtime data.

The reused ooaklee source comments declare independently transcribed MMIO/I2C
observations. Keep that declaration and original authorship; complete the
provenance review rather than treating it as proof. Its imported functional
sequence is a source candidate, not runtime admission or an extracted vendor
calibration profile. Hardware-ISP/NV12 and Windows parity remain the target.
This boundary governs future reuse decisions and supersedes ambiguous earlier
calibration-reuse language. No source/runtime/install changes accompany it.

Existing community work materially shortens the front-camera integration.
This comparison supersedes the August E000 research snapshot's statement that
no community Snapdragon SP11 stream had been proven. It does not convert another
machine's validation into our own hardware qualification.

## Fixed public inputs

The published [merged PR 22](https://github.com/ooaklee/linux_ms_dev_kit-sp11/pull/22)
reports a standalone IMX681/C-PHY/DT front-camera path, ten 10-frame start/stop
cycles, continuous RAW capture at about 30 fps and processed browser video.
Those results are author-reported. This run performed source, hosted and build
verification only.

We fetched 17 relevant source/DT/API files at the reported hardware-validated
revision `64999b9fc6e60ebccdc3755563cafcc63930cc90` and current integration revision
`2cbd1ec3e2da385e7bd91fd65c63ba5a8fb5b865`. All 17 pairs are byte-identical.
API payload sizes and Git blob IDs were independently recomputed; SHA-256 and
immutable source URLs are retained in the sensor reference manifest.
The original initial fetch and corrected filename fetch are both retained.
Ten initially requested optional/incorrect paths were absent; the actual
`phy-qcom-mipi-csi2.h` and `phy-qcom-mipi-csi2-cphy-x1e80100.h` were then fetched.
No camera binary firmware, private original or pixel data was downloaded.

## Reuse decisions

| Area | Published implementation | Our target / decision |
| --- | --- | --- |
| Sensor | Standalone GPL IMX681, 3840x2640, one C-PHY trio | Source candidate imported with attribution and two control-error fixes. Keep current installed mode2 untouched. |
| Receiver | Exact 2.406-Gsymbol/s, trio-zero profile; reset/common/config/IRQ/shutdown sequence | Reuse lifecycle structure and reviewed observations. Qualify our profile explicitly; do not infer hardware support from nominal rate bins. |
| PHY API | Adds MIPI C-PHY mode but carries symbol rate/trio count in D-PHY configure fields | Upstream interface review remains. Do not import the temporary carrier as an established generic ABI. |
| CAMSS | Propagates C-PHY bus type; explicit link frequency; CSID680 route and RDI fixes | Useful bounded integration changes to reconcile with our RFC/allocator/completion/reset patches. Whole-file replacement would lose our changes. |
| Board | CCI1.1 @ 0x10, MCLK4, reset237, PHY2, rails and GPIO225 LED | Compare with our measured board facts and unresolved normal-regulator boot hang before enabling nodes. Published privacy polarity is unqualified. |
| Frame timing | Driver advertises 548571428 pixel rate; header says this is bus throughput and VT clock is unmeasured | Preserve our qualified mode's 720-MHz timing evidence. Review published frame-length metadata before reuse. |
| Frame-length write | 16-bit 0x0340, default2708 | Our qualified control contract is 24-bit 0x033d, FLL3554/7116. Do not replace the control ABI blindly. |
| Link frequency | 1.203 GHz, hence 2.406 Gsymbol/s | Our mode2 exposes 1.200 GHz / 2.400 Gsymbol/s. Actual public configure rejects our rate; tolerance is not implied. |
| Processing | libcamera simple pipeline with software ISP | Reuse applicable sensor/control findings; retain our Qualcomm hardware-ISP/NV12 architecture and existing calibration. |
| Rear / CDM | Front RAW/RDI scope; rear support remains open | Retain our rear work. Raw bring-up does not require completing the processed ISP/CDM startup, and does not prove its DMA retirement. |
| Submission | Downstream integrated code, upstream cleanup listed separately | Curate logical patches, bindings, attribution and hardware evidence; no merged-mainline claim. |

## Concrete reuse completed

`src/upstream/sensors/imx681-ooaklee/` now contains the published standalone
sensor and unchanged init/mode table, a small local adaptation patch and pinned
reference manifest. The adaptation stops register writes on a negative runtime-PM
get result and releases group hold even after an earlier write failed, preserving
the first error. Three original-code counterexamples were reproduced before
the adapted code passed 1,080 fault cases under both GCC and Clang ASAN/UBSAN.

The actual public PHY set_mode/configure functions pass 36 profile, 66 submode
and 3 D-PHY controls per compiler. Invalid-profile output remains unchanged.
The 2.400-Gsymbol/s versus 2.406-Gsymbol/s incompatibility is executed evidence,
not a README inference. Model context/PM/CCI helpers are explicitly scoped.

The adapted sensor module compiles and passes modpost/link against the retained
7.2.0 source/config/symbol checkpoint with W=1/-Werror and zero warnings.
Patch replay reproduces the adapted source byte for byte. Twelve source pin
rejections occur before output creation. This candidate has not been installed,
loaded or used to stream. Existing source artifacts and the protected installation
are unchanged; all 14 end-to-end readiness categories remain open.

## Next implementation frontier

1. Reconcile the existing RAW/RDI sensor/receiver route with our exact mode.
   Either keep a matching published sensor/receiver profile as a separate
   qualified candidate, or derive and qualify the correct 2.400-Gsymbol/s route.
   Do not mix either sensor mode with the other's exact receiver admission.
2. Port bounded receiver lifecycle and CAMSS routing changes onto our retained
   kernel source while resolving the generic C-PHY configure interface and the
   physical-trio numbering (public board zero; numerical helper logical1..3).
3. Validate the sensor's endpoint/clock contract, VT timing, frame-length register,
   bindings and power graph, including the known regulator topology failure.
4. Qualify fresh fully open RAW capture and clean stop/reopen independently.
   Continue hardware-ISP/core/CDM/NV12 integration and reuse existing calibration
   for the final native image-processing path.

The completed source foundations and public working route are progress toward
these milestones. A count of open acceptance categories is not a count of
independent inventions or a calendar estimate.
