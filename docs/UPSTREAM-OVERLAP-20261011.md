# Upstream overlap checked on 2026-10-11

This replaces the earlier unverified current-upstream-overlap placeholder.
Primary sources below are authored mailing-list posts and review replies,
retrieved through public mirrors. These are proposals/review, not a claim of
merged support. No maintainer was contacted.

## Current direction

Bryan O'Donoghue's 2026-10-05 74-patch RFC targets SM8650/VFE780, with a VFE880
pixel-pipe helper. It extends existing CAMSS lines/outputs and adds native YUV,
Bayer histogram statistics and parameter handling. Its patch list includes
X1E PIX declaration/format changes; its hardware testing is on SM8650 HDK,
not SP11. It incorporates generic extensible ISP statistics and gives base
commit `8d3ae59288f1e7d58d76558a6ee96d533bc5019f`.
Primary cover:
https://lists.openwall.net/linux-kernel/2026/10/05/1511

Qualcomm's October 6/7 45-patch IFE series targets SM8250, SA8775P and QCS8300,
using a separate IFE subdevice with modules/bus/scaler interfaces and generic
ISP params/stats. Its resend uses linux-next next-20260909 and excludes the
new PHY reorganisation. Cover:
https://lkml.rescloud.iu.edu/2610.0/11983.html

The October 7 review asks that the work be integrated on the evolutionary
CAMSS/VFE foundation rather than introducing a parallel driver. Qualcomm's
author agrees to collaborate. This is the basis for our integration choice;
the final combined implementation is not settled.
https://lkml.iu.edu/2610.0/12136.html

The same discussion rejects a new pixel-only DT compatible. Reuse the existing
SoC binding when adding IFE functionality; this is separate from the unresolved
SP11 actuator-regulator boot problem.
https://lkml.iu.edu/2610.0/12291.html

Linaro's X1E camera DTSI v7 was posted September17. PHY reorganisation v20 was
posted September18. These need actual patch/base comparison before our C-PHY/
board series is formed; cover-level discovery is not a completed rebase.
https://lists.openwall.net/linux-kernel/2026/09/17/1648
https://patchew.org/linux/20260918-b4-linux-next-25-03-13-dtsi-x1e80100-camss-v20-0-dc244e124e71@linaro.org/

## Hardware and source limits

RFC patch52 supplies a public GPL-2.0 VFE880 pixel-pipe setup. A bounded download
from the author's mailing-list post reconstructed the complete612-line new file
on SP11; metadata/source hash are in
`docs/UPSTREAM-PUBLIC-IFE-REFERENCE-20261011.json`. It is a review reference,
not compiled, loaded, transplanted or advertised as a VFE680/SP11 provider.
https://lists.openwall.net/linux-kernel/2026/10/05/1601

Its CST register names/locations match the nineteen-field ownership set, but
its coefficient word arrangement and clamp choice differ from the existing SP11
contract. A matching address is not proof of identical encoding or image-domain
policy. It names the signed auxiliary lane SUBOFFSET; its SP11 mathematical
interpretation still needs validation. Do not copy static tuning values or
register defaults between hardware generations.

The two proposals overlap our needed output grouping, typed metadata transport,
ISP setup and lifetime work. Existing source-only compiler tests can remain
field-validation tools while the production provider is built around the agreed
upstream structures. CDM topology and our local QCIP/private scalar interfaces
are not submission ABI.

Full RFC mbox retrieval failed: lore HTTP403, Patchew HTTP500. The fallback
obtained patch52 from an authored mail mirror, not a complete series/tree.
A further bounded mirror download retained eight other patch mails before the
60second tool deadline; its partial receipt is preserved in the same metadata.
No completed rebase, patch application, maintainers' consensus on every detail,
or SP11 hardware support is claimed.

## Next implementation order

1. Obtain and pin the complete current RFC/dependencies; inspect updates and
   review. Map existing output groups, stream routing, generic params/stats,
   locking and teardown into the SP11 VFE680 backend.
2. Reconcile public per-block definitions with our source-tested fields,
   including CST channel order/clamps and gamma encodings. Preserve independent
   math/tuning producers and source attribution.
3. Add minimal source-owned VFE680 pixel setup and real output/stats/DMI
   allocations to the existing CAMSS architecture. Eliminate both private input
   consumers and fallbacks in the isolated candidate.
4. Compile, review DMA stop/error lifetime, then use a fresh guarded hardware
   identity. Only after that curate C-PHY/sensor/actuator/DT/kernel/libcamera
   series on the current maintainer base.

The roadmap's dependency-removal and hardware gates stay in force. The public
proposals can reduce duplicated framework work, but do not clear any of our14
readiness components or resolve calibrated image quality.
