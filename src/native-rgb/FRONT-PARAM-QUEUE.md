# Front parameter transport source qualification

The experimental front pipeline can submit parameters through the CPU-only
`msm_vfe1_params` V4L2 META_OUTPUT node. This uses the generic V4L2 ISP envelope
and a subset of the public CAMSS proposal: QCIP format, empty update or one
GAMMA_256 block (type10, flags0). This is a development compatibility target,
not an accepted upstream ABI. Topology, capability negotiation, licensing and
the startup/profile implementation still require upstream review.

Build with all existing front/profile gates and `--front-param-queue-trial`.
The runtime `native_front_param_queue_trial` module parameter defaults off and
requires the profile gate. This mode omits the private scalar control. Legacy
scalar-only mode is retained; it rejects a gamma update rather than discarding
it. Neither source builder installs modules or opens a camera.

The queue uses four initial buffers and sequential provider identities starting
at5. Each prepared buffer contains a separately owned gamma copy. Successful
DQBUF acknowledges that the provider owns the submission, not that hardware
has applied it. The public envelope contains no frame identity: the driver
assigns identity by queue order, and libcamera checks the acceptance sequence.
Omitted updates preserve the last successful curve. Invalid blocks, flags,
format, slopes, channel continuity and endpoint ranges reject. Enqueue failure
does not advance identity or commit a replacement curve and latches failure
until stream reset. Pixel STREAMOFF owns hardware retirement.

The IPA accepts an explicitly supplied independent YAML file through
`LIBCAMERA_CAMSS_X1E_TUNING_FILE` in the experimental pipeline. Required keys:
`version: 1`, `sensor: imx681`, `layout: rgb257-u10`, and
`gamma_r`, `gamma_g`, `gamma_b`, each with257 integer points in0..1023.
All channels are validated before output publication. Without a file, the IPA
emits empty updates and preserves startup gamma. No tuned curve is bundled.
Validity alone does not establish calibration. Synthetic fixtures in tests
are not runtime tuning.

Qualification: kernel36 full module build W=1/-Werror; libcamera16 pipeline,
actual IPA, generated proxy/worker and cam build Werror. Ten selected tests pass,
two no-device control tests skip as expected. Actual IPA tests use synthetic
YAML and real shared memfd mappings. Codec/state tests6218 and actual kernel
bridge259 pass ASAN/UBSAN. The hosted bridge uses the staged scalar/gamma
submission and section parser; allocation, locks, eligibility, startup loading
and provider enqueue are explicit mocks. Vb2 node behavior, runtime graph,
acceptance timing and optical gamma interpretation remain untested on hardware.

Next is a fresh single-use hardware transport/response qualification. Front
calibration still needs corrected full-chart framing and a fresh Windows
reference passing four-marker and held-out geometry gates. Existing front04
manual-bracket and rear66 evidence remain valid; no new quality-parity claim.

Primary proposal references (proposals, not evidence of merged ABI):
- https://lists.openwall.net/linux-kernel/2026/10/06/1797
- https://www.mail-archive.com/linux-kernel@vger.kernel.org/msg2628674.html
- https://lists.openwall.net/linux-kernel/2026/10/06/1832
