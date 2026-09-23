# E004mr — source-pinned rear-only gated display-preview tone experiment

SOURCE STAGED ONLY, NOT ARMED. Fresh one-time unique Golden-auto-return
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
