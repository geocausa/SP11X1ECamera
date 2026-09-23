# E004md — guarded RGB sensor gain/exposure-response trial

NEW uniquely guarded one-shot ID E004md, not reused E004mc.
Only approved visible-light front IMX681 and rear OV13858 sensors.
Hypothesis: after E004mc paired source RAW8/Y p99 front19/18,
rear16/16 in morning corner daylight, supported bounded increased
sensor gain and rear exposure should produce a measurable change
in incoming REAL RAW10 upper8 and independent app NV12 luminance
if the configured sensor controls are physically effective. A
readback of new V4L2 control values by itself does NOT establish
physical register programming or useful optical image.

Apply ONLY supported native V4L2_CID_ANALOGUE_GAIN / DIGITAL_GAIN
(front512/512 vs0/256; rear256/2048 vs128/1024) and supported
rear exposure3200 vs1600 within explicitly queried driver bounds.
Front exposure3546 stays unchanged near the active 3554-line
frame limit. This is a short controlled visible-light sensor
software-control test, not guessed register write, Windows ISP
replication or daily default dynamic AE tuning.

While maintained exclusive root-private RGBSession controls one
physical media route at a time, collect paired scalar RAW8/Y
source measurements BEFORE gain/exposure and AFTER a settled
control change using monotonic timestamps (same-frame source
and converter). A separate ordinary uid1000 app 90-frame
scene probe provides image-luma/texture comparison before/after.
All controls MUST be restored to exact previous values BEFORE
stopping the publisher and neutralizing the graph, validated
by readback, normal STREAMOFF143, no leaked FDs and full native
119-edge media graph. Failure or uncertain sensor write/restore
poisons the candidate with no speculative route retry; isolated
one-shot automatically returns to protected Golden.

No frames/photos/thumbnails/pixel hashes or per-tile grids saved;
only sparse aggregate histogram/percentile and control metadata.
No IR sensor streaming/illumination, no OS-level Linux standby/
suspend/resume/hibernate. No destructive persistent sensor or
Golden configuration. Every physical attempt consumes this
identity whether PASS or FAIL. This experiment alone does
NOT establish visual recognition, calibrated white balance or
full Windows ISP image parity.
