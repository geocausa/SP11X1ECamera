# Ordinary Linux camera development

User-selected direction, 2026-09-20: practical RGB and ordinary-memory IR
processing alongside the still-blocked protected Windows-equivalence goal.

## Same-machine Windows RGB parity baseline — E004jk

A safe one-shot Windows boot on the **same SP11** measured actual WinRT
CPU-accessible NV12 buffers: rear VideoPreview **1920×1080** (45 frame-handle
acquisitions), rear VideoRecord **3840×2160** (45 acquisitions) and front
VideoRecord **1920×1080** (45 acquisitions). Both RGB camera readers
started successfully. The front source additionally *advertises*
2560×1440 NV12, but that mode was not selected/streamed in this
session. All advertised modes list 30 fps; no sensor frame IDs or
usable WinRT timestamps were captured, so sustained cadence and
unique-frame counts are unproven. CPU SoftwareBitmap access and
dimensions are established; pixel-content export, same-scene optical
quality, photo resolution, concurrent capture, AE/AWB and in-app
switching were not measured. Windows image/colour parity remains
a separate unsatisfied gate.

Windows results were saved privately and a privacy-redacted summary
and the successful Windows probe script are in E004jk. The direct
Windows BootNext was consumed, persistent Linux-first firmware/GRUB
boot order unchanged, and protected Golden independently verified
on the return. These measured Windows front/rear RGB resolutions
supersede relying on another platform's 720p browser demo as our
own SP11 quality target. No IR/Hello test was made.

## Experimental rear 4K NV12 buffer feasibility — E004jl

The **same SP11's Windows** rear VideoRecord delivered 3840×2160 NV12
buffer handles; the current temporary Linux rear webcam was previously
proved only at 1920×1080. A new **offline-only** C converter now
accepts a complete 4076×2806 rear pgAA Bayer frame and generates
3840×2160 NV12 using a 3840×2160 parity-preserving crop and bilinear
8-bit Bayer processing rather than upscaling a 1080p proxy. An
archived **rear hardware colourbar**, not a current optical scene,
produced a complete 12,441,600-byte 4K NV12 buffer consumed by
GStreamer; seven source/negative/format tests and ASan/UBSan replay
passed. This only closes an **offline buffer-format feasibility gate**:
the converter is uncalibrated, its isolated measured conversion times
included 36.840 ms and 60.099 ms, no sustained 4K30 is established,
and neither a live 4K camera nor a 4K virtual webcam was opened.
Front compressed QC10C is completely separate and still undecoded.
No camera power, module, boot or IR state changed. See E004jl README.

## Rear 4K offline conversion performance and exact output preservation — E004jm

A new **offline-only** E004jm fused C path retains E004jl's exact 3840×2160
NV12 output bytes for archived rear colourbar and nonuniform synthetic
packed-Bayer patterns while sharing neighbouring samples across each 2×2
bilinear output tile. All eight baseline-versus-optimized source/format/
negative tests pass; ASan/UBSan and real GStreamer offline replay pass.
Five independent short colourbar runs on this SP11 measured E004jl baseline
36.356–40.733 ms versus fused 12.148–18.086 ms *conversion time only*;
eight repeats of the SAME colourbar measured 11.313 ms fused average
conversion versus 30.732 ms baseline (not independent live optical frames).
This is not 4K30 sustained camera, validated live 4K V4L2 delivery,
colorimetric Windows parity, or a native sensor ISP: real optical capture,
application backpressure and long-run thermal/latency remain separate.
Protected Golden, rear 1080p temporary webcam and front compressed-QC10C
gate remain untouched. E004jm README/test suite records exact evidence.

## Rear 4K offline delivery into a real GStreamer application — E004jn

A separate 3840×2160 NV12 application receiver now accepts the E004jm
rear Bayer→NV12 output through a bounded GStreamer appsrc→queue→
videoconvert→I420 appsink pipeline. Six offline tests pass; two
**synthetic** nonuniform source frames were separately identified at
the application output, and an optional consumer-side hash gate rejects
repeated payloads. A file-free eight-frame pipeline with **eight repeats
of the same archived rear hardware colourbar** delivered 8/8 consumer
samples (15.595 ms averaged converter work, 198 ms application pipeline
interval). The app timestamps were synthesized and this was not an
eight-frame live optical recording, ordinary selectable 4K V4L2 camera,
long-run 4K30 guarantee, measured capture latency, calibrated colour
pipeline or native ISP. Nothing in this new offline path decodes front
QC10C or changes the protected Golden kernel/boot. See E004jn README.

## 4K standard selectable video endpoint — E004jp synthetic one-shot PASS

After the offline E004jm/jn 4K rear conversion/application proof, a NEW,
uniquely consumed isolated Golden-v4 candidate boot physically opened
a **synthetic-only** standard /dev/video90 webcam. The normal independent
V4L2 reader acquired eight complete 3840×2160 NV12 frames, 12,441,600
bytes each, and an actual GStreamer application accepted eight 4K samples.
The source was GStreamer moving-ball synthetic video, not real OV13858
optical pixels. Virtual capture sequences 4,7–13 included an initial gap;
synthetic app PTS and 174 ms bounded app-pipeline duration do not
establish sustained 4K30, per-frame camera latency, no drops, Windows
pixel quality or a working native rear 4K camera. The temporary
loopback module/virtual node unloaded before automatic Golden return,
and the unique boot/runner/staging were completely retired. Existing
Golden default kernel/DTB/initrd and front/IR paths remained untouched.
See E004jp README/RESULT for independently observed metadata. Next
separately bounded **REAL** rear optical→fused 4K converter→independent
standard virtual webcam with strict source/candidate provenance, followed
by sustained cadence/quality validation. Front QC10C remains an
independent unresolved source-to-pixels gate.

## E004jq physical rear 4K candidate — discovery abort, no optical capture

A distinct, source-pinned **real rear 4K one-shot** passed offline 4K
converter/application/publisher, release/R4 and GRUB-ordering preflights.
Its only physical candidate boot initialized rear and front camera sensors
and the IR sensor in standby (no IR illumination or stream), but the
required unified media-graph discovery **did not succeed** before timeout.
The debug output had been suppressed: the precise failure cause remains
**unverified**. No rear colourbar, fresh normal optical frame, 4K virtual
camera, application frame or front capture occurred in that candidate.
The service failed closed, automatically returned to protected Golden,
and the unique boot entry, service, private stage and logs were retired.
This consumed **E004jq** one-shot cannot be rearmed. Earlier E004jp
*synthetic* selectable 4K and E004jh *real 1080p* achievements are
unchanged; do not combine their distinct evidence into a claimed real
4K webcam. Next requires a **new unique** diagnostic candidate that
preserves bounded non-image media inventory, parser stdout/stderr and
kernel graph status before any physical streaming. E004jq RESULT.json
and README contain the verified boundary and Golden-return status.

## E004jr bounded diagnostic source for next unique camera experiment

The E004jq capture attempt failed before a media graph could be discovered,
but its parser error text was discarded. E004jr adds a **read-only non-image**
media inventory helper that preserves bounded `media-ctl -p` stdout,
stderr, exit status and missing expected entities in a root-owned private
directory for a *future distinct one-shot*. The helper has not been used to
probe live camera hardware; nine offline tests on accepted/partial archived
graphs and fail-closed output/CLI conditions pass. A previously accepted
44-entity graph satisfies all required rear/front entity names, while a
42-entity earlier graph correctly reports absent RGB sensors. These
archived samples do not reveal the actual missing E004jq graph: its
cause is still unknown. Golden remains unchanged. See E004jr README.

## E004js complete camera media graph physically verified (non-streaming)

A new uniquely identified camera-capable E004js **read-only diagnostic**
candidate bound rear OV13858, front IMX681 and IR VD55G0 sensors and
observed all three runtime-suspended, with no stream or IR illumination.
On its *first* attempt `media-ctl -d /dev/media0 -p` returned a complete
44-entity graph including all ten required roles, 16 video nodes and
28 subdevices (19,307 bytes, exit 0, empty stderr). E004js captured
**zero optical or test-pattern frames**, loaded no virtual webcam and
performed no 4K application delivery. Its automatic return to protected
Golden and retirement of unique candidate boot/service/assets are
verified. Earlier E004jq failure to discover a graph was not logged
well enough to establish its cause; this success shows the graph can
register in a separate equivalent candidate, not why E004jq failed.
No native rear 4K optical webcam or front QC10C decoder is claimed.
Redacted E004js RESULT.json and README record the unique boot/return.

## First physical rear 4K selectable V4L2 webcam delivered to an ordinary app — E004ju

The unique E004ju camera-capable candidate physically captured **27 consecutive
fresh rear OV13858 optical Bayer frames** at 4076×2806 `pgAA` (hardware
sequences 0–26, timestamp-derived source cadence 29.9504 fps over 26
inter-frame intervals), *after* its physical rear colourbar and disabling
test-pattern mode. E004jm-derived bounded, still **uncalibrated** software
conversion produced 27 complete **3840×2160 NV12** buffers in direct
transient pipes (mean conversion-only 11.559 ms). The standard selectable
Linux virtual `/dev/video90` advertised NV12 3840×2160; a **separate
ordinary V4L2 capture process** received eight complete 12,441,600-byte
4K buffers (virtual sequences 6,9,10,11,12,13,14,15), and a genuine
GStreamer I420 application received all eight samples in its bounded
228-ms app interval using synthetic PTS. This is the FIRST physically
observed real rear optical→4K standard V4L2→app chain on SP11 Linux,
not merely synthetic 4K output or an internal appsrc mock. Source-sensor
29.9504 fps does NOT establish 4K30 sustained application output,
lossless buffering, end-to-end latency or Windows-quality ISP; virtual
sequence gaps 7–8 occurred near subscriber startup and require further
diagnosis. Output uses 8-bit proxy bilinear Bayer colour processing
without OEM matrix/exposure/white balance, native ISP or matched pixel
quality. Front QC10C decoding/normal native Linux camera remains open.

The E004ju single-use experiment unloaded virtual video90, neutralized
rear route, returned automatically to protected Golden boot and retired
the unique candidate modules/GRUB/service and private raw colourbar.
No normal optical image file was saved, front/IR was not streamed, and
IR illumination was not enabled. Only redacted E004ju RESULT.json
and README persist. E004ju must never be rearmed.

## Longer real rear 4K concurrency test exposes subscriber/cadence limitation — E004jw

After the earlier physically successful **27-frame rear Bayer→4K NV12→eight
independent application buffers** E004ju result, a NEW E004jw camera
candidate stressed the complete ordinary V4L2 4K pipeline for longer.
The real OV13858 captured and software-converted **180 normal optical
4076×2806 Bayer frames** with contiguous reported hardware sequences
0–179. The physical capture timestamp span was 7.913 seconds over
179 intervals: **22.621 delivered source frames/s** under this load,
with 52 interframe gaps greater than 50 ms, p95 gap 67.938 ms and
average converter-only 16.642 ms. This does **not** demonstrate
sustained sensor or consumer 4K30, even though the previous much shorter
E004ju physical capture measured approximately 29.95 source fps.

The standard temporary /dev/video90 advertised NV12 3840×2160 and
an independent V4L2 reader received **58 complete 4K buffers**
(sequences 6–63, contiguous within the observed reader sample)
but had requested 90. Once the bounded source publisher finished,
the reader could not complete its requested frame count and hit its
65-second timeout. The separate GStreamer app therefore never
reported a completed 90-frame sink count or usable wall-clock frame
cadence. The cause of the shortfall is **not yet established**:
start timing, backpressure, queueing and application consumption must
be isolated. Do not infer lossless virtual delivery from the reader's
contiguous sequence numbers, or a measured 4K30 application rate from
synthetic video timestamps. No normal optical pixels were saved.

The fail-closed experiment removed its temporary virtual module,
neutralized the rear media route and returned automatically to
protected Golden. The consumed E004jw GRUB/service/package, private
test-pattern raw file and logs were retired; no front video or IR
illumination was started. E004ju's earlier bounded physically delivered
rear 4K app result remains valid. E004jv separately adds **real
appsink wall-clock arrival telemetry** for a *future* independent 4K
application run (90 offline unpaced synthetic frames passed; not
physical-capture evidence). E004jw RESULT.json and README contain
redacted findings. The remaining production work includes stream
backpressure/drop/latency and Windows-quality ISP calibration, alongside
correct front QC10C-to-displayable video conversion.

## E004jx offline incomplete-stream diagnostics before another 4K camera boot

The E004jw six-to-eight-second real rear 4K stress attempt returned 58/90
complete virtual V4L2 buffers, and its exact-count-only app was terminated
without a final app-sink cadence result. A new **source-only** E004jx
GStreamer app receiver now measures actual monotonic appsink callback
times and emits flushed in-flight progress per ten full 4K buffers.
On an early upstream EOF or a still-open but idle input pipe it reports
the complete frames already consumed, their observed wall-clock
cadence and explicit shortfall reason, returns nonzero and retains **no
pixel data or hashes**. It never treats an incomplete frame as valid
or a partially complete stream as a successful 4K30 camera run.
Six camera-free tests pass, including a deliberately stalled open pipe,
early EOF, normal synthetic video, invalid/extra input and a no-camera/
boot-activation check. The new app is **not yet** connected to a physical
camera or a V4L2 device; only the previous E004ju finite real optical
4K app test is physically demonstrated. E004jx README contains the
source identity and next fail-closed integration requirements.

## E004jy: real rear 4K app-sink partial and early-subscriber timings now measured

E004jy ran a NEW one-use camera-capable Linux candidate with the same
180-source/90-independent-app 4K workload as E004jw. Actual physical rear
OV13858 Bayer capture completed **180 normal optical 4076×2806 frames**,
consecutively reported sequences 0–179, converted via transient pipes
into 3840×2160 NV12. Its physical source timestamp rate under combined
load was **20.5406 fps** over an 8.71446-s span (p95 interframe gap
100.169 ms); mean software conversion-only cost was 18.469 ms.

The standard temporary virtual `/dev/video90` subscriber started
2.771 ms after discovering its 4K NV12 format, 435.15 ms after the
publisher began. It dequeued **69 full-sized 4K buffers** (virtual seq
7–75). The separate GStreamer appsink successfully received **68 complete
4K samples**, then observed an **incomplete next input frame** with
12,439,552 of 12,441,600 bytes before its six-second idle bound. It
reported this as PARTIAL, never counted the incomplete image and exited
nonzero. A flushed appsink progress line showed an initial **31.2835
observed fps at sample 60**, but the final 68-sample average was
**12.0007 fps**, with a maximum 3,440.065-ms interarrival gap.
Therefore these data **do not** establish continuous app 4K30, zero
repeated virtual frames, a working 90-frame app test or Windows image
quality parity. The observed shortage is not yet tied to a proven
specific sensor/driver/queue mechanism; further isolated byte-counting,
capture cadence, GStreamer and virtual-device backpressure diagnosis
is needed.

The publisher finished its 180 frames in 9.227 seconds; the independent
reader did not reach 90 frames and timed out after 24.443 seconds. The
fail-closed one-shot unloaded /dev/video90 and its temporary module,
neutralized the media route, automatically returned to protected Golden
and retired its camera-enabled boot entry, service, temporary raw
colourbar and private logs. Front video and IR illumination stayed off.
The identity is consumed and must never be rearmed. E004jy RESULT.json
and README retain **redacted text-only** evidence. The earlier E004ju
**short** 27-source/eight-app real optical 4K pass remains valid but
is not a continuous-app-cadence demonstration; correct front QC10C
video and OEM Windows ISP colour/detail parity remain open.

## E004jz: source-only byte-exact 4K pipe-boundary instrumentation

The physical E004jy test's independent reader dequeued 69 complete-sized
4K NV12 buffers, while its GStreamer app counted 68 complete frames and
received only **12,439,552 of 12,441,600 bytes** for the next input image
before an idle timeout. Dequeuing a full V4L2 buffer does not prove the
entire payload was subsequently written to stdout or consumed by the app.

New **source-only** E004jz adds a bounded, byte-preserving, low-overhead
C pipe transducer. In a future uniquely isolated experiment it can sit
between an independent ordinary V4L2 reader and E004jx's GStreamer
consumer and report **bytes actually read and forwarded**, complete
4K frame boundaries, incomplete tail size, input EOF/idle/error and
monotonic full-frame boundary timing. It never emits image bytes to
logs, writes image files, changes pixels or accesses any camera,
module, IR or boot controls. Its seven camera-free Golden tests passed,
including an exact synthetic **2,048-byte** tail shortfall and a real
GStreamer app consuming two complete 4K synthetic frames through the
meter. It has **not yet been tested with the physical camera** and
does not establish either sustained 4K30 or Windows-equivalent ISP
image processing. See E004jz README/tests for source identity.

## E004ka: physical 4K V4L2 reader-to-application byte boundary measured

The unique E004ka physical candidate repeated the accepted real rear optical
OV13858 → software NV12 3840×2160 → ordinary selectable /dev/video90 →
independent V4L2 capture reader → GStreamer app pipeline, now adding the
byte-preserving E004jz meter **between the independent reader's stdout and
the application**. The rear sensor produced 180 complete fresh normal
optical Bayer frames with contiguous reported hardware sequences 0–179,
at **21.8819 delivered source fps** over its 8.18028-second timestamp
span under the combined processing workload. All 180 converted to 4K
NV12; mean converter-only cost was 17.044 ms.

The independent virtual-camera reader dequeued **40 full-sized 4K buffers**
(virtual sequences 7–46). The meter recorded **497,664,000 bytes read
and exactly 497,664,000 bytes forwarded**, 40 complete NV12 frames,
**zero incomplete final-frame bytes**, then stopped on input idle.
The independent GStreamer app accepted exactly the same **40 complete**
frames, then reported partial/EOF from the bounded meter. Thus this
physical run showed **no byte loss between reader stdout, pipe meter
and appsink**, and the requested 90-frame application test failed
because insufficient complete V4L2 reader output was available. The
prior E004jy 2,048-byte truncated-tail observation was *not reproduced*
here; its exact cause is not established.

Initial 30-sample app arrival was 32.6829 measured fps for that SHORT
interval, but the 40-sample final average was only **5.3341 fps** owing
to long stalls (p95 interarrival 2,737.676 ms). The source itself
also ran below 30fps under concurrent load. Neither sustained app
4K30, lossless virtual capture, OEM Windows ISP image-quality parity
nor native front QC10C decoding has been demonstrated. The remaining
bottleneck is at or before the ordinary reader's stdout in this
experiment; available evidence does not isolate its cause among
v4l2loopback, v4l2sink publication, reader timing and V4L2 capture
semantics. Further source-only driver/pacing inspection and bounded
isolated trials are required.

E004ka failed closed, automatically returned to protected Golden,
unloaded /dev/video90 and retired its uniquely identified experimental
boot, service, private colourbar and logs. No normal optical pixel
files, front-camera stream or IR illumination were produced. The
one-shot identity is consumed forever. Redacted E004ka RESULT.json
and README record the physical findings; the earlier E004ju short
rear 4K-to-eight-app-frame result remains separately valid.

## E004kb: GStreamer sink clock lateness is a reproducible candidate bottleneck

The physical E004ka publisher previously sent nominal 30fps timestamps
from `rawvideoparse framerate=30/1` while real rear source delivery
under full load averaged 21.8819 fps, and its independent application
received only 40/90 requested 4K frames. The SP11 Golden-installed
GStreamer 1.28.2 `v4l2sink` defaults were independently inspected
*without opening a camera*: `sync=true`, `qos=true`, and **5-ms
max-lateness**. A source-only fdsrc→rawvideoparse timestamp probe confirmed
nominal 30fps PTS are synthesized from caps, not physical capture cadence.

In an isolated tiny synthetic NV12 stream paced at **22fps** but labeled
**30fps** by rawvideoparse, a real GStreamer fakesink with the same
clock/lateness/QoS settings as v4l2sink rendered just **4/35** buffers
in one bounded run; with `max-lateness=-1` it rendered **35/35**, and
with synchronization disabled it also rendered **35/35**. This is
evidence that late-frame dropping is a plausible **contributor** to
the physical 4K underdelivery, **not a proven causal attribution**:
the experiment did not open /dev/video90, use the actual v4l2sink
implementation to publish video, stream a physical camera or exercise
real 4K pixel throughput. See E004kb README/tests. A NEW unique,
Golden-returning real optical test can change only the sink lateness
policy while retaining the byte meter, physical source timestamps and
independent application count; do not claim continuous 4K30 or Windows
ISP image quality until measured.

## E004kc — full bounded real rear optical 4K Linux V4L2 webcam-to-app delivery

A NEW uniquely protected E004kc physical experiment changed only the
GStreamer `v4l2sink` lateness policy for the rear virtual webcam:
`sync=true qos=true max-lateness=-1` instead of the inherited 5-ms
late-frame drop threshold. It preserved the accepted native rear
OV13858 camera driver, full current-boot media graph, real hardware
colourbar/normal optical stream distinction, same 180-source/90-reader
bounded workload and independent stdout byte-meter/GStreamer app.
The source captured **180 complete fresh normal optical pgAA Bayer
4076×2806 frames** (physical sequences 0–179). All 180 converted
in transient memory/pipes to **3840×2160 NV12**; physical source
hardware timestamps gave **24.0407 delivered sensor frames/s** over
7.445698 seconds, and average converter-only time was 16.230 ms.

The normal selectable temporary Linux **/dev/video90** advertised
NV12 3840×2160, and a separately opened V4L2 subscriber received
**90/90 full 4K buffers** (virtual sequences 6–95 within its sample).
A separate pass-through byte meter verified **1,119,744,000 bytes
read and identically forwarded**, exactly 90 complete 4K buffers
with no incomplete tail and clean EOF. The independent actual
GStreamer I420 appsink received **90/90 complete 4K frames** with
real monotonic first-to-last callback cadence **27.9337 fps** over
its finite 89-interarrival window (p95 interarrival 86.312 ms,
maximum 127.699 ms), rather than using the fabricated 30fps
buffer PTS to claim a rate. The source/reader/app/text validator
all exited successfully. Three app output samples showed in-memory
image variation; this does not prove no repeated buffers, fully
calibrated quality or source cadence across all 180 frames.

The E004ka physical test using the inherited sink lateness policy
had delivered 40/90 buffers, whereas this NEW E004kc run with
lateness dropping disabled delivered 90/90. The E004kb offline
controlled source-only model separately reproduced GStreamer
late-buffer dropping for ~22fps incoming frames marked with
nominal 30fps PTS. This is compelling evidence for a **testable
sink-lateness contributor**, not conclusive isolation of every
camera/virtual pipeline bottleneck, because separate physical
runs also differed in delivered source cadence and workload timing.

**The result is a finite, physically demonstrated rear 4K standard
Linux webcam-to-ordinary-app chain, not long-run continuous app
4K30 or installed 1:1 Windows camera parity.** The source itself
delivered approximately 24fps in this test and the app's finite
rate was below 30fps; independent pixel quality, colour/AE/AWB,
noise/detail/Windows OEM ISP processing, app latency, buffer
duplication and thermal stability remain to be measured. Front
IMX681 QC10C UBWC still lacks independently proven displayable
Linux NV12 and native front video; IR/Hello can remain outside
the agreed acceptable compromise.

E004kc automatically returned to protected Golden Linux after
unloading /dev/video90, neutralizing the rear media route and
leaving front/IR streams and illumination disabled. Its unique
experimental boot, module copies, service, GRUB entry, root-private
colourbar and logs were retired; no normal optical images were
saved. The one-shot identity is consumed and **must never be
rearmed**. Redacted E004kc RESULT.json, README and consumed marker
record the observation and explicit limits.

## E004kd — extended finite physical rear 4K webcam-to-app uniqueness result

E004kd ran a **NEW** single-use protected camera-enabled Linux candidate
with the normal rear OV13858 hardware, 240 fresh optical 4076×2806
Bayer source frame captures and a separately opened standard
3840×2160 NV12 V4L2 reader of temporary /dev/video90, now requesting
**120 complete 4K frames**. Hardware capture sequences 0–239 were
consecutive; all 240 frames were software converted to 4K NV12 in
volatile pipes, with mean conversion-only time 18.837 ms. Physical
source timestamp delivery averaged **19.9946fps across 11.953231
seconds**; p95 interframe gap was 100.207 ms. This is slower than
the previous 180-source E004kc finite test and is **not** sustained
4K30, despite the nominal 30fps PTS attached by GStreamer.

The independent V4L2 capture reader dequeued **120/120 complete 4K
buffers**, first virtual sequence 6 and last 127. The reader reported
a **two-ID gap, 6→9 (missing 7 and 8), near startup**; therefore
lossless virtual output is not proven. The exact stdout byte meter
read and forwarded **1,492,992,000 bytes**, 120 complete 4K NV12
frames with zero incomplete tail and clean EOF. The independent actual
GStreamer I420 appsink delivered **120/120 complete 4K frames**, and
its private in-memory SHA-256 comparison showed **all 120 app-output
frame payloads were bytewise different** without saving raw frames
or hashes. Bytewise app-frame distinctness does **not** prove no
skipped virtual frames, one-to-one association with individual
sensor exposures, real motion or image quality.

Real app callback arrival averaged **24.5036fps** over 119
interarrival intervals in its approximately 5-second reader
window (p95 gap 90.645 ms, maximum 186.196 ms). The 240-source
publisher continued for approximately 12.626 seconds, so these
source/app average rates describe *different time windows*.
The accepted GStreamer publishing sink kept
`sync=true qos=true max-lateness=-1`, avoiding the prior
5-ms lateness drop threshold. The temporary hardware experiment,
independent byte meter, app and strict validator all passed their
bounded exact-count gates. This demonstrates a longer finite
**physical optical rear 4K→ordinary Linux V4L2 webcam→independent
application path**, but **not long-running 4K30, zero frame loss,
permanent installation, OEM Windows ISP parity, low latency or
front IMX681 QC10C→displayable video**.

E004kd automatically returned to protected Golden with its
original saved boot entry and no camera/virtual nodes or modules.
The rear media route was neutralized, front/IR video and IR
illumination were not activated, and E004kd's unique boot, service,
module/package copies, hardware colourbar/raw test asset and
private logs were retired. Normal optical pixels were not written
to disk. The unique identity is consumed forever and cannot
be rearmed. Redacted `RESULT.json`, README and consumed-marker
evidence record the actual outcomes.

## E004kf — IMX681 front RAW10 generic VFE0 RDI bypass failed to deliver DMA buffers

In an **actual separate camera-capable one-shot** with Golden auto-return,
E004kf completed first-boot media graph discovery and physically enabled only
front IMX681 C-PHY2→CSID1 RDI0→generic **VFE0 RDI0** (front PIX QC10C,
rear and IR routes off). Kernel logs confirmed IMX681 normal optical
MODE_SELECT=1 transmission start and safe stop. The generic V4L2 RDI
node negotiated **SRGGB10P pRAA 3840×2160**, 4,800-byte stride and
10,368,000-byte full image size, but **zero front RAW10 buffers were
dequeued** within the 48-second bounded test. The source byte meter read
zero image bytes, the NV12 software converter correctly rejected empty
input and the actual front GStreamer app received zero displayable frames.
Sensor transmission is **not evidence of camera receiver/DMA delivery**;
the cause of the cross-instance CSID1→VFE0 RDI shortfall is unproven.

The one-shot failed closed, disabled/neutralized all five rear/front-RDI/
front-PIX links, returned automatically to protected Golden Linux,
removed its isolated package/boot/service and deleted private test logs
without writing front optical pixels to disk. E004kf's unique identity
is consumed forever; see text-only E004kf RESULT.json and README.
The earlier physical **front PIX QC10C compressed** captures remain
valid, as do the offline E004ke RGGB RAW10→NV12 1080p tests, but
**neither physical front RAW10 nor a displayable native front webcam
is proven by these tests**. The matched-instance CSID1→VFE1 RDI0
route is a separate candidate for a NEW isolated experiment, while
preserving the original front Windows ISP quality-parity objective.

## Desktop inventory

Run `python3 tools/camera-desktop-status.py` (or `--json`). It queries
package/service presence and lists device nodes. It never starts capture.
Golden normally exposes no cameras; this is not itself a regression.
Desktop prerequisites now include the installed GStreamer libcamera plugin.

## Offline IR preview

`src/sp11-camera-hlos-worker/sp11-offline-preview.py --help` describes the
exporter. Input is ordinary nonprotected, neutral NV12 at 644x604, 1..16
frames. Supply an existing native `sp11-offline-nv12-stream.c` executable
in a user-owned /tmp directory through `--worker`. The unchanged worker is
compiled together with the eight `sp11-parity-worker`/SWABF/SWASF core
source files used by the E004hi verifier; the E004ie regression demonstrates
the exact build and export end to end. No signing is needed for this ARM64
userspace executable.

Example with your own already-prepared ordinary offline input and worker:

```sh
python3 src/sp11-camera-hlos-worker/sp11-offline-preview.py \
  --input /tmp/session/input.nv12 --worker /tmp/session/worker \
  --output /tmp/session/preview.y4m --playback-fps 30
gst-launch-1.0 filesrc location=/tmp/session/preview.y4m ! y4mdec ! videoconvert ! autovideosink
```

Preview files contain the processed image data and are deliberately retained
for viewing; delete them when no longer needed. Cadence is for playback only.
No camera, illuminator, protected buffer, face model or login interface is
opened by the exporter. Full transaction success is required before export.

## Front QC10C decoder input and same-machine Windows MFT evidence — E004jj

A SHA-locked offline audit of the archived SP11 Windows camera
`QcDeviceMFT8380.dll` found **both** `IMAGE_FORMAT_LINEAR_NV12`
and `IMAGE_FORMAT_UBWC_TP_10` references: the former near BPS
striping-library assertions and the latter near IPE striping-library
assertions. These are source-location clues, **not evidence** that
either library actually converts the captured front camera's QC10C
pixels into the Windows WinRT reader's selected 1920×1080 NV12.
The archived WinRT holder created and started its selected reader,
but contains no independently checked output video-frame pixels.

The actual installed Golden-v4 Qualcomm Iris VDEC has **encoded
H264/HEVC/VP9/AV1 bitstream** input formats and NV12/QC08C output
formats; it cannot be used as a generic QC10C camera-buffer input
converter. Newer upstream Iris QC10C support also concerns compressed
**video decoder output**, not direct QC10C source conversion. The
front remains 2560×1440 processed TP10 UBWC with four contiguous
Y-meta/Y-data/C-meta/C-data regions, 7,778,304 bytes per buffer.
Do not reinterpret it as linear NV12, P010 or encoded HEVC.
Five readonly archive/source regression tests PASS. No reboot,
sensor, codec driver or IR illumination was activated. See E004jj
README and machine-readable `format-route-gate.json` for the
remaining independent decoded-image or safe full-ISP-mode gate.

## Front QC10C indirect hardware encoder route gated — E004jo

A source-hash-pinned read-only check of the **installed Golden** Iris VENC
driver finds encoder raw INPUT formats limited to NV12 and QC08C; H264
and HEVC are its encoded OUTPUT formats. The physical front camera
produces **QC10C**, not QC08C or a codec bitstream, and the installed
encoder's source-level format admission does not accept that QC10C as
input. Five exact same-machine source/direction tests pass; this was
**not** a live encoder format IOCTL or a proof that no future GPU/ISP/
alternative dedicated conversion mechanism exists. E004jj independently
excluded incorrectly sending QC10C directly to Iris video DECODER
bitstream input. Front app-displayable Linux 1080p video is still
unproven; keep the actual QC10C decompression or safely verified
linear-ISP conversion gate. See E004jo README.

## Installed SP11 Vulkan Turnip does not advertise 10-bit YUV compressed import — E004ji

The **real physical Adreno X1-85** Turnip Vulkan driver was queried
read-only with `vkGetPhysicalDeviceFormatProperties2` and DRM modifier
lists. The installed Mesa 26.0.8 Turnip ICD advertises NV12 **8-bit**
with both linear and Qualcomm compressed modifier
`0x0500000000000001` (two planes), but tested 10-bit 2-plane,
10-bit 3-plane and 16-bit two-plane YUV Vulkan formats have **zero
reported tiling features and zero advertised modifiers**. This
extends the previous EGL Mesa result to a genuine **Vulkan runtime
format query** rather than assuming an EGL restriction applies to
Vulkan. It neither decodes a QC10C frame nor proves that another
GPU API, a custom shader, version-matched driver, validated UBWC
decoder or alternate safe ISP output could not provide a solution.
The queried 10-bit Vulkan formats have P010-style 16-bit containers,
not verified packed TP10/P030 compatibility. **Do not alias front
QC10C to compressed 8-bit NV12.** No camera, GPU image, module,
reboot or IR emitter was opened/changed. See E004ji README and
source-compiled probe/tests.

## Real rear optical frames reach an independently selectable webcam — E004jh

A new uniquely bounded camera-capable E004jh boot integrated both
previously independent rear paths. The **actual OV13858 sensor**
delivered 27 real 4076×2806 packed Bayer10 frames at 29.9502 fps,
converted immediately in memory into 1920×1080 NV12 previews and
published via GStreamer `v4l2sink` to discoverable standard
`/dev/video90` (`SP11-Rear-Preview`). A **separate, ordinary V4L2
capture client** opened that virtual webcam and retrieved eight
complete 3,110,400-byte NV12 buffers with ordered virtual sequences
7..14; a separate GStreamer app consumed all eight. The bounded
27-source/8-consumer stream elapsed 1,247 ms, including startup and
teardown; no normal optical or NV12 intermediate file was written.
The colour converter remains **uncalibrated** and this result does not
establish per-frame camera-to-screen latency or multi-minute cadence.

The test unloaded virtual camera `/dev/video90` before a neutral
handoff to front IMX681, which captured 27 distinct compressed QC10C
frames through the live mapped-DMA guard and shadow policy (zero later
native sensor writes). All sensors suspended, the final graph was
neutral, and the test automatically returned to unchanged protected
Golden. The root-private optical colourbar, front QC10C files,
virtual module, one-shot boot entry and service were retired/deleted.
**This is the first physically proven *standard app-selectable rear
camera endpoint*, but it was deliberately temporary, not installed as
a persistent desktop service.** The rear still needs a supported
long-running lifecycle and calibrated image quality; the front still
needs proper QC10C decoding or verified true linear ISP output plus
its own separate standard endpoint. IR illumination/Hello remain
protected. See E004jh README and RESULT.json.

## Synthetic virtual V4L2 rear device passes on Golden-v4 ABI — E004jg

Ubuntu 26.04's GPL `v4l2loopback` source was compiled **offline** against
the exact Golden-v4 custom kernel ABI. A unique synthetic-only boot used
Golden's original kernel, initrd and **non-camera DTB**, then created a
standard discoverable `/dev/video90` card `SP11-Rear-Preview`.
A bounded GStreamer synthetic ball publisher negotiated 1920×1080 NV12;
an independent standard V4L2 reader acquired eight complete frames and
passed them to a real GStreamer application consumer. It unloaded the
loopback module, removed the node and returned automatically to Golden.
The one-shot boot assets and private copied module were retired.
**No real rear optical camera was connected to this device in this test.**
E004jf separately established eight *real* rear V4L2 optical frames into
GStreamer. The next gate is the **combined real rear-to-virtual camera
path**, proper image calibration and sustained application delivery;
front compressed QC10C still needs decoding or verified linear ISP NV12.
See E004jg README/RESULT.json.

## Real rear V4L2 Bayer10 to GStreamer appsrc, then front 27 QC10C — E004jf

The new uniquely bounded E004jf candidate loaded the E004jd R4-complete
51-file camera package and a separately SHA-pinned E004je streaming bridge.
In **one real SP11 camera-capable boot**, the rear OV13858 V4L2 producer
piped eight fresh normal-scene Bayer10 frames (hardware sequence 0..7,
29.9545 fps, 14,321,824 bytes each) directly to the converter and then
GStreamer `appsrc → videoconvert → appsink`. The real application received
all eight 1920×1080 NV12-derived frames. Converter-only mean 3.275 ms per
frame; eight-frame bounded pipe elapsed 514 ms including startup, V4L2
acquisition and shutdown, **not** per-frame sensor-to-screen latency.
No normal optical Bayer or intermediate NV12 frame file was written.

Following a verified neutral media handoff, front IMX681 again produced
27 distinct ordered compressed QC10C frames with the live-tested E004ip
mapped-DMA guard; 24 producer rows passed under shadow policy, zero
later native sensor writes. All sensors suspended, the final graph was
neutral and automatic reboot returned to untouched protected Golden.
The consumed E004jf boot entry, root-private package, optical colourbar,
front QC10C files and GStreamer bridge were retired/deleted. Only
redacted metadata is committed; see E004jf README/RESULT.json.

This establishes **bounded live rear V4L2→GStreamer application frame
delivery**, but does NOT establish a persistent app-discoverable rear
virtual webcam, colour calibration or sustained multi-minute cadence.
The front remains QC10C/TP10-UBWC: no verified linear NV12/decoder or
ordinary front webcam endpoint yet. Protected IR/Hello remain gated.

## Bounded rear NV12-to-GStreamer application pipe — E004je

A source-only bounded rear RGB bridge now converts whole packed Bayer10
`pgAA` frames from STDIN using the **same validated E004iu colour proxy**,
then sends proper 1920×1080 NV12 frame bytes to a real GStreamer
`appsrc → videoconvert → appsink` application pipeline with 30fps buffer
PTS, bounded queues, count/EOS validation and no intermediate image files.
On protected Golden, the archived hardware rear **colour-bar** frame
reproduced its exact accepted NV12 hash and an eight-frame repeated
colour-bar pipe delivered eight app samples. Nine offline tests pass;
no camera was opened. This is not a live V4L2 producer test or a
system-wide virtual webcam; the physical live pipeline and ordinary
app discovery remain separate gates. See E004je README.

## Production package includes required SHA-pinned front bootstrap — E004jd

The E004jc real front test needed a separately installed root-private
R4 derived bootstrap sidecar because Git archive omitted the ignored
`r4-bootstrap.bin`. E004jd fixes this in the maintained production
source: an exact 41,088-byte hash- and provenance-verified R4 is now
included in newly staged packages and **both** generated manifests.
A freshly source-built 51-file package and its packaged front launcher
passed offline checks, including eight positive/negative tests for
missing or corrupt R4, symlinks and unlisted files. Historical 50-file
packages do **not** satisfy the strict new production gate.
The package is not installed into protected Golden and neither front
QC10C decoding nor a live rear desktop endpoint is implied. See
E004jd README.

## Both real RGB camera hardware routes validated — E004jc

A unique source-locked, candidate-only E004jc camera boot added the missing
front 41,088-byte SHA-verified derived R4 bootstrap as a separately
staged root-private sidecar to the unchanged accepted camera package.
The **actual packaged** front launcher passed an offline dry-run before
the single boot was armed. The candidate boot successfully captured
**eight distinct normal optical rear OV13858 Bayer10 frames at 29.9501
fps**, returned the graph to neutral, then captured **27 distinct,
sequential 7,778,304-byte front IMX681 QC10C frames** using the E004ip
mapped-DMA guard module on actual SP11 V4L2/vb2 buffers. The front
producer passed 24 rows under shadow policy with zero later native
sensor writes; all sensors suspended and the final route was neutral.
Both Ubuntu GRUB writers finished successfully in the E004iy-ordered
configuration, and the unconditional service returned the machine to
protected Golden. The camera-candidate root tree, R4 sidecar, optical
frames and unique boot entry/service were retired/deleted following
redacted proof. The candidate driver is not installed as the Golden
default.

This completes the **bounded live front/rear capture and mapped-DMA guard
regression**, NOT ordinary application camera parity. Rear still needs a
live calibrated Bayer-to-NV12 pipeline and app endpoint; the front
remains compressed Qualcomm QC10C/TP10-UBWC and needs a verified
decoder or true safe linear ISP NV12 output before apps can display it.
No IR emitter/Hello or native post-G3 writes were enabled. See E004jc
README and RESULT.json.

## Real rear optical NV12 preview, front bootstrap packaging gate — E004ja

The distinct, consumed E004ja one-shot successfully captured the rear
OV13858 hardware colourbar plus **eight distinct real normal-scene Bayer10
frames** at 29.9504 fps; the rear-to-front handoff route was neutral.
The eight normal optical Bayer frames were privately converted to eight
distinct 1920×1080 NV12 previews on Golden; the real eight-frame output
was accepted by GStreamer. Mean conversion-only time was 3.4232 ms per
frame, and the batch I/O+conversion average was 5.8776 ms per frame.
This is a fast **uncalibrated offline colour proxy**, not yet a live
ordinary Linux camera endpoint. The optical frames and previews were
kept private on SP11 then deleted after non-sensitive evidence collection.

The front QC10C launcher stopped **before streaming**, because the
accepted package's git-archive staging excludes the pinned 41,088-byte
`r4-bootstrap.bin` through `*.bin` ignore. The local accepted file
exists and hashes to the exact launcher-pinned digest; a new candidate
must stage it independently as a private, separately verified sidecar,
then prove a launcher dry-run without hardware before attempting live
front capture. The E004ja one-shot and private system assets were
retired; the physical QC10C DMA guard remains untested. The E004iy
reversible GRUB writer ordering passed again on E004ja and remained
installed. See E004ja README and RESULT.json.

## First combined rear/front candidate — E004iz consumed before streaming

The new E004iz one-shot verified that both GRUB writer services completed
successfully and in the intended order on a real camera-capable candidate
boot, then loaded the exact accepted camera package with the new front
QC10C mapped-DMA guard and discovered the media topology. The initial
idle graph unexpectedly had **both rear links already enabled** and
both front links disabled (`rear-only`); the script had expected neutral
and therefore stopped before any front or rear frame. Its cleanup
explicitly returned the graph to neutral, and the automatic reboot
returned to protected Golden with no loaded camera modules. E004iz's
identity and all private boot/package staging were retired, never
rearmed. A new independent candidate must recognize only the verified
idle rear-only or neutral graph, explicitly neutralize it and prove
neutral before starting the accepted rear-to-front sequence. The
front real DMA guard and normal rear optical output remain physically
untested by E004iz. See E004iz README/RESULT.json.

## Reversible GRUB writer serialization — E004iy

After the disposable-file E004ix race reproducer, a scoped removable
`grub2-common.service` drop-in now requests and waits for the stock
`grub-initrd-fallback.service` to finish before writing the shared
GRUB environment. The original Ubuntu commands, persistent Golden boot
and kernel/DTB/initrd remain unchanged. A controlled real service start
and an ordinary Golden cold reboot both completed with BOTH GRUB services
successful and in the intended order. No transient environment-read
failure appeared on that reboot; its Golden GRUB environment bytes
matched the pre-install private snapshot. This is **one** Golden reboot
and does not prove indefinitely reliable boot behaviour or authorize
unbounded camera access. The ordering drop-in is still installed with
an independent rollback script and no camera or one-shot boot armed.
See E004iy README and RESULT.json.

## GRUB writer concurrency reproduced without touching Golden — E004iw/E004ix

E004iw's new camera-free candidate proved that a **read-only GRUB
environment check can pass after both stock GRUB writer services reach
terminal state**, and returned to Golden. But `grub2-common.service`
failed an environment read during that candidate boot **and during the
next normal Golden boot**, while `grub-initrd-fallback.service` finished.
E004ix reproduced transient GRUB read/write failures on separately
created **/tmp environment fixtures**: 120 simultaneous-reader/writer
trials produced two reader and two writer failures; the 120 serialized
controls had zero failures. The Golden GRUB environment checksum stayed
unchanged. A minimal proposed service ordering has been verified on
**disposable copies of the stock units only** and is NOT installed.
This supports a writer-concurrency hypothesis; it does not conclusively
establish the cause of the earlier E004iq camera-boot failure or certify
a corrected physical capture boot. Both live RGB camera paths remain
gated. See E004iw and E004ix README/RESULT evidence.

## Camera-free boot diagnostic status — E004iv

The original QC10C DMA-guard one-shot E004iq aborted at a GRUB environment
read before camera activation. A new camera-free E004iv one-shot established
that the two GRUB environment writers can be ordered to **finish before**
the diagnostic service starts. E004iv's root-owned script then failed an
unrelated Git ownership check **before reaching the GRUB read**; it created
no camera attempt and the automatic service reboot returned to Golden.
A read-only owner-scoped Git command was subsequently tested on Golden;
it does not set a global trusted directory. The E004iv identity and
all temporary boot assets are retired. The original GRUB failure root
cause and real QC10C DMA guard remain unproven. No new front/rear video
endpoint is implied; see E004iv README and RESULT.json.

## Fast bounded rear Bayer-to-NV12 offline batch — E004iu

The E004is rear Bayer-to-NV12 preview was functionally correct but
needed roughly 53–56 ms per archived colour-bar frame on SP11, too slow
for a single-threaded 30 fps pipeline. E004iu adds a separately
validated, **uncalibrated** C11 nearest-Bayer-tile colour proxy. It
reads actual accepted 4076x2806, stride-5104 `pgAA` rear frame
payloads and outputs real 1920x1080 NV12 bytes. A 27-frame offline
batch of **27 repetitions of one previously captured rear test-pattern
frame**, not fresh optical captures, averaged approximately 3.0 ms
conversion time or 5.2 ms including that batch's input/output file
operations per frame; its resulting 27-frame NV12 stream passed
GStreamer. Fifteen source/colour/sanitizer/IO/batch regression tests
pass. These timings exclude compiling the offline helper, live sensor
acquisition and application presentation. No full spatial demosaic,
calibrated IQ, **live 30 fps camera** or app device is proven; front
QC10C compressed data cannot use this Bayer converter. A new
privacy-controlled normal rear sample, proper colour processing and
a separate standard rear video endpoint are still necessary. See
E004iu README/RESULT.json.

## Both RGB cameras: source-aware desktop readiness — E004it

The read-only `python3 tools/camera-desktop-status.py --json` now reports
**rear OV13858 and front IMX681 independently**. A new shared output
contract validates the accepted rear `pgAA`/GRBG10 frame against E004is
real archived-rear-to-NV12 offline evidence, and the accepted front
`Q10C` compressed surface against its existing exact hardware contract.
The diagnostic reports both possible future 1920x1080 NV12 application
endpoints as `NOT_VERIFIED`; a synthetic-only front linear NV12 scaler
is NOT mistaken for a working QC10C decoder or a real front stream.
Fourteen positive and negative tests pass, including rejection of false
live-device, switching and default-install claims. SP11 already has its
libcamera/GStreamer/PipeWire prerequisites, but no cameras are exposed
on protected Golden, and the running kernel lacks v4l2loopback.
No kernel/video/IR module is loaded and the read-only diagnostic opens
no camera. See E004it README and `src/sp11-camera-stack/rgb-desktop-output-contract.json`.

## Rear RGB ordinary-video prototype — E004is

The accepted OV13858 rear path already captured 4076x2806 GRBG10 packed
Bayer at an aligned 5104-byte stride and approximately 30 fps; its
14,321,824-byte colour-bar frame and eight normal frames are documented
in E004dz. E004is now **unpacks a checksum-verified previously captured
rear colour-bar frame**, builds a basic 2x2 Bayer-tile colour proxy,
centre-crops to 16:9 and writes private 1920x1080 NV12. A real
GStreamer `rawvideoparse ! videoconvert ! fakesink` pipeline accepted
that frame. Nine offline tests pass, including packed-bit order,
colour layout, incorrect-format rejection and file isolation. The
preview is not colour-calibrated or full demosaic, and no live desktop
video device or sustained throughput is claimed. The previously accepted
front QC10C compressed format cannot be fed to this rear converter;
front's E004ij scaler needs genuine linear NV12 not yet available
from the SP11 front ISP. Both cameras still need standard app-facing
devices, repeatable selection and per-camera IQ/PM/cadence checks.
See E004is README/RESULT.json.

## Work remaining

1. Front RGB: convert accepted ISP-processed 10-bit QC10C/TP10-UBWC YUV
   into a standard desktop format. It is neither Bayer RAW nor linear NV12.
   The current 27-frame launcher is not a continuous webcam. The installed
   EGL driver advertises compressed NV12 but only linear P030/P010; exact
   QC10C import and conversion remain unproven. Run
   `python3 tools/camera-gpu-import-status.py` to inspect current support.
2. Validate fresh RGB-only candidate capture, then repeated use, switching,
   suspend and application integration, preserving Golden.
3. IR: use offline previews for ordinary pixel work; useful live scene signal
   and independently validated illumination safety remain unresolved.
4. Keep passwords/security keys for login. Preview and face-model experiments
   provide neither liveness nor secure biometric authentication.

## One combined, non-runnable NV12 kernel build — E004im

E004im builds the alternate V4L2 negotiation and the separately checked
kernel-native Y/UV DMA planner together in a single disposable SP11 ARM64
CAMSS module. Exact source-hash and geometry consistency checks and seven
negative integration tests PASS. QC10C stays first/default, NV12 STREAMON
fails before pipeline PM and the planner remains without runtime callers.
The module is not installed. Real linear ISP output and compression reset
are still open hardware gates. See E004im README.

## Read-only boot-environment diagnostic — E004ir

Review of the consumed E004iq candidate boot found that two systemd GRUB
services which modify grubenv started in the same second as the failed
camera preflight; this is a plausible but unproven scheduling hazard. The
original invalid environment bytes were not retained. E004ir supplies an
**uninstalled, diagnostic-only** unit ordered after both GRUB writers and
a read-only script that rejects unreadable GRUB state, a non-Golden saved
default, a still-armed or absent next_entry and mismatched candidate boot
markers. Eleven temporary-fixture tests and systemd-analyze verification
passed on SP11. This does not authorize a replacement one-shot, and it
cannot establish the cause of the prior invalid GRUB environment. See
E004ir README/RESULT.json. No camera or boot configuration was changed.

## E004iq QC10C-only physical one-shot — pre-camera abort, retired

The unique E004iq candidate booted on SP11 but its dedicated service failed
at the initial `grub-editenv` preflight (`invalid environment block`). The
service triggered the configured reboot into protected Golden; the consumed
candidate captured **zero frames** and never loaded its camera module or
reached real mapped-DMA validation. The one-shot identity, private staging
root and service were retired; the original QC10C driver is unchanged. The
candidate-only boot-environment read failure is not explained by the valid
Golden GRUB state after return, and this identity must **not** be rerun.
See E004iq `evidence/PRE-CAMERA-ABORT.json` and `RESULT.json`. The next
candidate must establish the boot rollback/preflight contract independently
before a new unique test identity can be justified. NV12 linear output and
UBWC-state reset remain separate open gates.

## Separate bounded QC10C-only physical regression candidate — E004iq

A provenance-correct rebuild reproduced the accepted hardware module hashes
using the originally recorded kernel source frontend, and the resulting
current stack manifest matches the already validated E004id 50-file package.
E004iq additionally compiled a QC10C-only module with the *sole* code delta
being the E004ip mapped DMA-coverage guard in `camss.c`. Unlike earlier
uninstalled E004io combined scratch modules, this candidate does **not**
advertise the proposed NV12 format. A unique, non-default, strictly
one-shot front-RGB test is prepared with a root-owned private package,
source-pinned 27-frame `shadow` launcher and an automatic return to the
persistent Golden GRUB default after success, failure or timeout.
At the offline preparation checkpoint, no boot was armed, camera opened or
new module installed; a live mapped-buffer/optical result is **not** yet
claimed. IR illumination/login are excluded and ISP linear NV12 plus
compression-state reset are independently unresolved. See E004iq README.

## QC10C mapped-DMA safety candidate — E004ip

Source review found the already accepted front QC10C capture path checks the
V4L2 allocation length and 32-bit base/end but does not establish that the
entire 7,778,304-byte compressed surface is covered by a continuous
*device-mapped* DMA address range. An E004ip scratch-only kernel patch now
checks actual mapped scatter-gather entries for complete adjacent DMA
coverage, supporting multiple contiguous DMA segments and rejecting gaps,
short mappings, zero-length entries and stale cached DMA bases. The exact
inserted C guard passed ten synthetic cases each under GCC and Clang
ASan/UBSan, with six source-integrity/negative tests and a full ARM64
Golden-v4 uninstalled CAMSS module build PASS. This is NOT yet the accepted
QC10C driver: real SP11 mapped-buffer behavior and bounded live capture
regression remain to be verified before installing this candidate.
NV12 STREAMON remains blocked and separate ISP/UBWC linear-output authority
is unchanged. See E004ip README.

## DMA-contiguous NV12 buffer gate — E004io

The next strictly uninstalled Golden-v4 kernel build strengthens the
experimental NV12 buffer planner against an overlooked scatter-gather DMA
hazard. Current vb2_dma_sg logic records the DMA address of the first SG
segment, but a large V4L2 allocation does not guarantee one continuous
DMA-mapped span for the 5,529,600-byte linear Y+UV image. E004io therefore
requires one **mapped** DMA segment with at least the entire image's byte
length, matching DMA base and computed UV offset. Eight offline positive/
mutation tests and a complete scratch ARM64 kernel build PASS. This may
reject valid multi-segment maps conservatively. No device DMA mapping
was actually exercised, and the stage remains uninstalled with NV12
STREAMON blocked before media power. ISP linear output and safe UBWC
reset still need separate physical proof. See E004io README.

## Kernel-compiled FULL Y/C NV12 dry-run plan — E004in

The next uninstalled SP11 kernel build combines the proposed NV12 V4L2 queue,
validated kernel-native Y/UV DMA plan and a **data-only** WM0/WM1 FULL
configuration proposal (image geometry, explicit Y/C strides, generic public
packer 3, per-client frame increments and DMA image addresses). Seven
positive/negative tests and the full ARM64 Golden-v4 scratch build PASS.
There are no new hardware call sites, and NV12 streaming remains blocked
before pipeline power. The real VFE680 global-reset callback is a no-op
completion; the accepted bus-stop function disables WMs without clearing
UBWC MODE_CFG. Explicit SP11 compression-state reset/verification and
RAW10-to-8-bit ISP output authority remain required before any real NV12
frames. See E004in README.

## Separate NV12 V4L2 negotiation, hard streaming gate — E004il

The exact-source-locked E004il experimental kernel overlay adds a proposed
2560x1440 single-memory-plane NV12 format to the dedicated X1E80100 front
PIX format table **after** the accepted QC10C default, with exact format
negotiation and discrete framesize metadata. Both the pipeline-PM prepare
stage and stream-start stage reject this NV12 format with EOPNOTSUPP *before*
any new camera power, pipeline or MMIO activity. Seven offline source/negative
tests and a complete scratch SP11 ARM64 kernel module build PASS. It is NOT
installed or enabled and the new format has not been tested via a real
video-device IOCTL. Real ISP linear output and safe UBWC reset remain
unproven. See E004il README.

## Kernel-native, uninstalled linear-NV12 planner — E004ik

A separate fail-closed SP11 kernel-sidecar source now compiles into a
**disposable/uninstalled** CAMSS kernel module against the actual Golden v4
build ABI. It explicitly rejects the existing QC10C video queue even if its
buffer has sufficient bytes, and checks an independently negotiated NV12
queue, exact geometry and stride, active frame, DMA alignment and both Y/UV
32-bit bounds. The sidecar has no active callers, format advertisements,
MMIO writes or module install; authorization always returns EOPNOTSUPP.
Six offline static/negative tests PASS. It is not yet a working NV12
capture mode: the SP11-specific linear ISP/BUS/UBWC transition remains
unproven. See E004ik README.

## Windows WinRT 1920x1080 NV12 target and offline bridge — E004ij

A previously overlooked SHA-pinned original SP11 Windows holder log establishes
an actual successful WinRT front Color/VideoRecord reader with NV12 1920x1080.
This is the app-facing format of that holder, not proof of stock Camera UI's
default resolution. Distinguish it from sensor RAW10 3840x2160 and internal
processed QC10C 2560x1440 FULL output. The offline-only E004ij prototype
converts two synthetic 2560x1440 linear-NV12 frames to two 1920x1080 NV12
frames through installed GStreamer. Both frames retained their distinct
constant Y and neutral UV; all six tests PASS. The converter **cannot** read
compressed QC10C. Actual linear ISP image capture/colourimetry and webcam
application integration remain unproven. See E004ij README.

## Offline linear-NV12 buffer implementation — E004ii

A separate fail-closed ARM64 C component now calculates the proposed NV12
Y/UV buffer and both FULL-client DMA addresses, rejecting undersized or
out-of-32-bit allocations and mismatched/compressed plans. Public Qualcomm
BUS ver3 source is SHA-pinned and confirms an uncompressed NV12 packer (3)
separate from TP10 (11). Twenty-six C/ASan/UBSan checkpoints and three
public-source-verifier Python tests PASS on SP11. This is offline code,
not a driver, physical frame or final Windows application resolution.
The actual SP11 bus programming and clean UBWC-to-linear state transition
still need independent authority. See E004ii README.

## Separate linear-NV12 offline candidate — E004ih

Qualcomm's public VFE BUS ver3 code has a distinct noncompressed NV12 FULL
Y/C format case. A source-locked, fail-closed offline experiment proposes
2560x1440 NV12 in 5,529,600 contiguous bytes at a *proposed* 2560-byte
stride and verifies that original QC10C files are unchanged (10 tests PASS).
The exact SP11 VFE1 uncompressed programming, pixel output and lifecycle
are NOT proven; there is no executable NV12 camera mode yet. See
`experiments/E004-front-ir-vd55g0/e004ih-linear-nv12-isp-authority/README.md`.
No new camera boot or IR change is authorized by this specification.

## Conversion implementation finding — E004ig

Official Mesa 26.0.8 and current upstream Freedreno snapshots explain the
missing compressed P030 advertisement: the generic DRI format mapping is
not backed by a TP10 texture/layout path in the inspected implementation.
A modifier-list edit or routine Mesa upgrade is not a demonstrated fix.
Next inspect a separate linear-YUV ISP output candidate, preserving the
accepted QC10C parity path, before any new camera runtime. Full details and
source hashes are in E004ig. No conversion implementation is claimed.
