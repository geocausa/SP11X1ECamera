# E004mr — source-pinned rear-only gated display-preview tone experiment

PHYSICAL ATTEMPT FAILED PRE-STREAM, CONSUMED/RETIRED, GOLDEN RETURNED. Fresh one-time unique Golden-auto-return
candidate; never reuse E004mh/mp/wn/wp or another retired identity.
Controlled E004mp baseline and gain/exposure trial profile is unchanged:
rear baseline exposure1600 analogue128 digital1024; trial exposure3200,
analogue512, digital2048; front baseline and trial unchanged. Current
rear mode exposure maximum3206, NO VBLANK/FPS/sensor/IR change.

Only difference from E004mp: rear standard output NV12-Y is transformed
in an opt-in, studio-range-only isolated publisher using pure in-memory
`iq/rear_preview_tone.h`, and ONLY if sparse source Y p01 in20..50,
p99<=65 and p99-p01>=8. It maps 1st-percentile source Y to125 with
slope 3.5 and clamps output to video-range16..235. Nearly constant
baseline/very dark and bright scenes are deliberately BYPASSED. Chroma,
native RAW source, front output and system camera default untouched.
This is a deliberately bounded demonstration of rendering current real
rear signal at Windows-like LUMA, NOT actual Windows ISP, true AE or
calibrated black/colour/scene detail. It must not be presented as
recognizable optical quality absent local visual acceptance.

Exactly source-pinned compilation -DSP11_RGB_NV12_VIDEO_RANGE=1 AND
-DSP11_RGB_REAR_PREVIEW_TONE=1 required; no alternate C source or
retired boot token accepted. Existing synthetic four-camera safety,
app/reopen, source RAW10 and paired same-frame probes and root-private
front/rear baseline/gain local images run exactly once. Private optical
pixels stay on SP11, never export/commit/chat; only scalar result.
Failure consumes identity and returns Golden without retries. After
successful return, move original private photos to
`~/Pictures/SP11-Camera-Private-E004mr/` owner geoca directory0700,
photos0600, retire candidate GRUB/service/root stage. Linux OS system
sleep/standby/resume/hibernate prohibited; front IR/illuminator OFF.

## Actual guarded E004mr run (not a successful live preview)

The unique source-locked candidate physically booted at ~12:21 BST
2026-09-23 and consumed boot token
`2bd02d4f-0a7e-492c-a77a-89019f67228c` exactly once. Full native
RGB device discovery and neutral-route checks passed. The selector
server accepted initial OFF/status but first front activation returned
socket EOF (`OSError RGB_SELECTOR_DID_NOT_REPLY`) and the independent
selector acceptance failed. No camera profile, front/rear client-cycle,
private optical PNG or live rear-tone metrics were produced: this is
**a pre-stream harness/selector failure, not evidence that the tone
algorithm failed or succeeded optically**. Exact upstream error is
unresolved; server stderr was empty and its result file absent when
checked. No retry/rearm of E004mr is allowed. Fail-closed single-use
runner returned SP11 automatically to protected Golden Linux boot
`a4998ac2-a031-4702-9601-4b5efc26b618`; overlap guard PASS with no
nodes/modules/processes. Candidate service/GRUB/root assets were
retired. No E004mr photos existed, so none were exported.

Only the earlier E004mp private gain photo has a separate SP11-local
**offline** grayscale tone simulation in
`~/Pictures/SP11-Camera-Private-E004mp/rear-gain-offline-tone-preview-private.png`.
It is NOT a real E004mr capture. A local-only measurement showed
sampled mean Y 23.102→149.406 and no zero/255 clipping for that
arbitrary display LUT; neither optical black, color accuracy, actual
scene recognizability, live frame cadence nor Windows parity is proven.
The evidence/FAILURE-SUMMARY.txt is explicitly a reconstruction from
observed runtime output: root-stage original logs were NOT archived
before cleanup and are not represented as original copies. The next
fresh separately guarded harness should first persist a bounded selector
error/exit reason before its failure cleanup, and not blindly repeat
a consumed candidate.
