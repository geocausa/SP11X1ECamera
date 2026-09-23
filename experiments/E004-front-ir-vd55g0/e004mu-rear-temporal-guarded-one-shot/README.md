# E004mu fresh, source-pinned opt-in rear 4K temporal preview physical trial

ACTUAL PHYSICAL FAIL / CONSUMED / RETIRED. New unique one-shot identity, NEVER reuse retired
E004mt, E004ms, failed E004mr, or any earlier Windows oracle identity.
Same sealed front/rear real supported native RGB controls, restored
exactly, UID1000 ordinary user apps, RAW10 Bayer source and native
full10 temporal three-pair diagnostics as prior E004mt. Only NEW
rear-only opt-in temporal NV12 video luma filtering after gated
rear studio-range tone; front, IR, source RAW10, native exposure/gain,
VBLANK/FPS and GStreamer UV/chroma untouched. Maintain one previous
filtered Y plane plus candidate-only one previous unfiltered luma plane
for scalar-only before/after measurement, both zeroed and freed on exit.
No multi-frame delay or user-default camera changes.

High contrast local motion bypasses the 2x2 filter and updates
history with current pixels; scene cut, source sequence break/timing
gap, and tone-not-engaged reset history. This heuristic cannot prove
low-contrast motion safety, optical detail, SNR, black level or Windows
colour/ISP parity. New real physical acceptance requires actual live
30 fps source no sequence gaps; full10 source and front/rear clients,
bounded RAW10 frame pairs, exact native controls restore, real rear
tone gate, scalar-only before-vs-after filtered luminance variation,
actual frame CPU budget, UV untouched, and auto-return protected Golden.

Private optical photos remain only SP11, owner geoca 0700/0600.
No photos/pixels/hashes/raw buffers exported, no front IR illuminator,
no Linux system suspend/standby/hibernate, no reuse/retry of consumed
one-shot. If failure, preserve bounded scalar logs and return Golden.
Production normal publisher and kernel unchanged; no unreviewed
auto-exposure or automatic runtime service enabled.

## E004mu incident / no automatic rearm

Real E004mu physical test ran exactly once under new source-locked
candidate Linux boot `11e69da8-3d03-4622-9607-03a5faa303ef` on
2026-09-23. The real frontend1080/rear4K UID1000 applications,
exact supported native sensor gain restoration, RAW10 source three
sequential frame-pair validator, rear tone-gate and same-session
scalar temporal-filter measurements succeeded. At higher native rear
gain the candidate filtered 137 frames, one-frame history clear/UV
preservation proved, and observed filter mean CPU time3.831ms; e.g.
real frame600 unfiltered consecutive sampled RMS5.05798 display Y,
output vs prior filtered frame RMS3.51504 display Y. The two RMS
figures have DIFFERENT reference histories and do not constitute a
calibrated or unbiased true noise-reduction metric or proof of
actual object detail, correct colour, moving subject safety or true
sensor SNR. No optical pixels, RAW frames, thumbnails or photo hashes
were exported. The four user-private front/rear PNGs remain solely on
SP11 `~/Pictures/SP11-Camera-Private-E004mu/` dir0700 files0600.

**Physical release test FAIL, NOT PASS**: the native rear publisher
reported 707 frames/24.507338s =28.8485 fps, zero native sequence
gaps, mean combined conversion/filter23.695ms. Required minimum29fps
was correctly rejected by the independent validator; do NOT loosen
the gate to make an unacceptable runtime pass. Two separate earlier
non-filter runs E004ms/E004mt measured29.9491/29.9078fps and
20.132/20.197ms conversion. In the E004mu high-gain last four
30-frame source intervals (frames570–690), measured 24.879,24.897,
24.903,24.682fps vs ~30fps in prior non-filter tests; input sensor
FPS/frame timing registers never intentionally changed, so this is
a real processing-load cadence regression, although concurrent GPU
or system scheduling effects cannot be ruled out from these logs.

A NEW GPU display fault occurred at 14:12:49–50 BST (5 GMU OOB
timeouts, one Adreno GPU fault, one DPU hangcheck recovery logged
`gnome-shell`) during frontend camera activity and BEFORE rear
filter start at14:13:01. Read-only survey of 13 accessible persisted
boot kernel journals found no corresponding GPU fault or DPU
hangcheck on 12 other boots, but cannot attribute the fault to any
particular camera operation, compositor, firmware or kernel component.
No logged panic, OOM, thermal shutdown or newly created kernel crash
dump; 31 thermal samples peak49.2°C sensor reading / final camera
sensor36.8°C. The systemd service failed validator at14:13:30 and
requested reboot; Linux reached reboot.target14:13:43 and journal
closed normally. There is no recorded new boot until user powered
SP11 on at14:34:38, so final Linux kernel→firmware reboot handoff,
post-journal system state, and reason it remained off are UNKNOWN.
`watchdog0: watchdog did not stop!` is present in prior successful
reboot journals too, not evidence alone of why E004mu stayed off.

As of fresh Golden boot `57150330-c0a8-4e72-b7a3-f8ae790354ed`,
all E004mu root-private candidate/GRUB/boot/systemd assets are fully
retired, saved GRUB entry remains `sp11-audio-fullio-v19c`, no pending
next-entry, camera nodes/modules/processes off, maintained default
front/rear camera and rear temporal/tone default-OFF unchanged.
Never rearm E004mu. NO new unattended candidate boot until the
GPU/restart-handoff path and reliable out-of-band power recovery have
been separately reviewed. Source-only CPU optimization and quality
gates can continue without device activation or another OS reboot.

Evidence: `RESULT.json`, scalar text files under `evidence/`,
`evidence/SPARSE-SOURCE-CADENCE-COMPARISON.json` and
`evidence/READONLY-GPU-REBOOT-POSTMORTEM.json`. These documents are
not photos or camera frame data.
