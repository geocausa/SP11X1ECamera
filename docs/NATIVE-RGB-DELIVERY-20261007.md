# Native SP11 camera delivery state — 2026-10-07

The product is native Linux front/rear camera support with hardware ISP processing
and standard libcamera pipeline/IPA controls. It is not complete. The user's
acceptance of libcamera supersedes the original literal kernel-only constraint.
No bespoke camera daemon, loopback, CPU pixel ISP, AI/effects or Windows binary
execution belongs in the release path.

## Machines, sources and authority

| Resource | Role | Current use |
|---|---|---|
| SP11 Linux ARM64, via PiMaster | Build and hardware target | Golden FullIO v19c default; kernel7.1.5-sp11-render-parity-v4+ |
| SP11 Windows | Same physical sensors/ISP reference | Demand-driven register/algorithm/quality oracle; not release runtime |
| SP7 | Recovery and Windows KD | Recovery/debug only |
| SP11X1ECamera-driver | Current maintained source | work/native-rgb-driver-20261007 |
| SP11X1ECamera-clean/native/legacy | Prior experiments and retained evidence | Preserve; import only reviewed/hash-pinned needed sources |
| e003i-front-production-src + build-runtime-v4-headers-20260826 | Compatible kernel build toolchain | External modules, W=1/-Werror, fresh outputs |
| Qualcomm camera-driver82ac3a6 | Published hardware programming authority | BUSv3, VFE680, CDM validation; no invented reset/register mapping |
| libcamera pinned ff740913 | Standard Linux control/pipeline framework | Front pipeline physically passes80 cam frames; IPA remains |

Protected Golden assets/default are never overwritten. Original vendor tuning,
raw traces and optical pixels remain private on SP11. No system suspend tests.
Fourteen one-use candidate identities are consumed and retired; none may be rearmed.

## Verified implementation

| Component | Physical or build evidence | Limit |
|---|---|---|
| Front IMX681 timing controls | Read-only720MHz pixel rate, HBLANK2912,1.2GHz link-frequency menu; two-FLL measurements | Full native array/selection geometry still needs authority |
| Correct SP11 OV13858 source | Board supplies/reset/runtime PM;120 rear RAW frames and verified stop | Rear processed ISP output not proved |
| Native front linear NV12 queue | 80 sequential2560x1440 frames at29.989fps; four reused buffers and reversed queue order;405 ownership checks | Fixed manual IQ, no long soak/reopen or live3A |
| FULL storage/8-bit programming | Published packer3, linear MODE guard, UV half height, complete readbacks, local CDM helper audit | No compressed-to-linear transition/reopen proof |
| Stop/return | Explicit STREAMOFF during queue operation; all sensors suspended, graph neutral, Golden unchanged, zero critical faults | Starvation/fault/reopen still unqualified |
| Frame-associated statistics |80 video/metadata pairs with matching identity/timestamps and valid AEC luma;405 ownership checks | Experimental QXS1 format; IPA remains |
| libcamera control/statistics helpers | ARM64 Werror build;8 passes,2 VIMC-dependent skips | Front pipeline passes80 app frames; actual IPA absent |
| Typed front ISP scalars |80 pairs,84 accepted requests,5 negative cases; measured2x gain/reset response;1979 sanitizer checks | Data-only firmware qualified; dynamic tables/live3A remain |
| Kernel-owned startup |80 pairs via data-only firmware; raw control absent; missing/corrupt profile rejected;405 owner checks | Fixed board/mode digest; independent tuning distribution and final ABI remain |
| Standard libcamera front application |80 NV12 frames at30.0056fps,80 statistics pairs,425 owner matches,88 typed requests; clean stop/release | Fixed manual; dark output, no IPA/3A or rear processed capture |
| Rear composition |52 fragments compile against real types | Nonadaptive startup inputs and runtime composition incomplete |

NV12-01 stopped before ISP programming: truthful sensor array timing plus the
generic PIX clock margin exceeded X1E's admitted727MHz maximum. NV12-02 used
that existing maximum only for the exact diagnostic mode; requested727000000Hz,
rounded727000000Hz, actual727000048Hz. No new OPP or fabricated pixels/cycle
ratio was introduced. Production load voting remains a separate qualification.

The continuous NV12 frames have Y means3.68–3.94 and maximum11, with UV near128.
This proves hardware-written NV12 buffers, not colour, exposure, focus or Windows
quality. A dark physical scene, fixed exposure and tuning/processing behaviour
must be distinguished before drawing an optical conclusion.

Evidence: NATIVE-RGB-TIMING-03-20261007.json,
NATIVE-RGB-NV12-01-20261007.json, NATIVE-RGB-NV12-02-20261007.json,
NATIVE-RGB-NV12-BUILD-20261007.json and NATIVE-RGB-LIBCAMERA-BUILD-20261007.json.

## Why progress stalled

1. Historical NEXT pointers directed work into tiny Windows metadata/control-flow
   steps, even when those steps did not unblock a native Linux camera requirement.
2. Mock-only fragments and compile success were mixed with hardware readiness.
   Actual integration exposed real-type mismatches and a stale rear ACPI source.
3. The front runtime grew named frame/capsule/result fields through frame27.
   That is a bounded experiment, not a reusable continuous queue.
4. Native timing metadata, ordinary FULL storage, stream ownership and host3A
   were separate unresolved dependencies. Extending captured capsules could not
   resolve those architecture boundaries.
5. Readiness/handoff records preserved obsolete software-service and kernel-only
   policies. The authoritative prefixes and structured state now identify the
   approved native/libcamera workstream and the exact bounded hardware proof.

## Remaining delivery gates, in dependency order

**1. Continuous front queue and request contract.**
The isolated native path now runs one serialized two-slot queue beyond the old
27-frame bound. Queue01 passed80 delivered frames, including changed buffer order
and explicit STREAMOFF;81 retirements had405 consumed-owner checks. Its two command
slots preserve synchronous CDM BL_DONE and full DMA-owner retirement before reuse.
This establishes short continuous capture, not a long soak, restart or optical gate.

The qualified front profile mode removes the raw-command control and loads
validated data-only tuning through the kernel firmware loader. Original tuning
remains private; independent distribution is still unresolved.
Frame-associated statistics now pass80 pairs on the V4L2 metadata queue.
Typed validated scalar parameters now pass84 real requests and measured hardware
gain/reset response. Complete dynamic semantic tables and request association for libcamera.
Expose scalar/ROI/table values with bounded sizes and supported ranges; the kernel
owns register addresses, CDM framing and DMA binding. Do not expose arbitrary
MMIO, vendor binary execution or unvalidated command streams as product APIs.
DMI bank selection and per-request IQ cadence need a source-qualified rule;
blindly replaying request4 forever is not a substitute.

Already passed: native NV12 queue reuse beyond the old27-frame bound, ordered
delivery, explicit STREAMOFF, stop-before-free, neutral graph and standby.
Finite capture tail now passes using retired internal spare buffers. Remaining:
fault/reopen qualification, full typed tables and automatic request controls.
Use fresh identities; do not extend one named frame at a time.

**2. libcamera pipeline and IPA runtime.**
Front graph/request/statistics integration now passes the standard cam app with
fixed manual settings. pipeline01 tail starvation was diagnosed and corrected;
pipeline02 passed and both identities retired. Actual IPA/3A remains.
Discover this exact media graph, configure front/rear modes and streams, associate
sensor controls/ISP parameters/statistics with libcamera requests, and connect
the already-tested helpers. Implement 3A inside standard libcamera IPA code.
Verify exposure/gain control changes and statistic latency on hardware before
closed-loop tuning. Choose an ordinary pipeline-supported clock policy from
qualified active-pixel throughput and actual resource votes.

Acceptance: standard libcamera app gets processed hardware NV12 without a
bespoke daemon, loopback or software pixel ISP; controls respond correctly,
AE/AWB converge and failures return owned resources safely.

**3. Rear native ISP.**
Supply only the missing reviewed nonadaptive startup semantics, integrate the
existing bounded source fragments with actual ownership/completion logic, and
prove rear processed output/stop before enabling normal application selection.
Use Windows or KD only to resolve a specific absent hardware/algorithm rule.

Acceptance: rear native frames, safe switching, no stale cross-sensor requests,
and repeat open/close. RAW success alone cannot open this gate.

**4. Optical and product acceptance.**
Compare front and rear against Windows using controlled lighting, scene,
distance, resolution, frame rate and exposure. Measure colour/white balance,
detail/noise, clipping, frame cadence, exposure transitions and rear focus.
Resolve the very dark diagnostic output first. Validate repeat starts, long
capture, application switching, idle power and sensor runtime PM.
AI/effects remain excluded unless a concrete hardware contract requires an
inert presence; no such requirement has been established.

## Execution discipline

Every change must identify the product blocker it removes, its exact source
authority and a falsifiable build/hardware/optical result. A failed one-use boot
is recorded and retired; only a specific reviewed change earns a fresh identity.
A compile-only result never becomes a runtime PASS. A four-frame result never
becomes continuous or quality PASS. Keep one authoritative checkout and current
handoff; historical experiment chains are evidence, not an automatic work queue.
