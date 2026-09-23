# E004mt — fresh source-locked bounded rear RAW10 same-boot temporal probe

ACTUAL PHYSICAL PASS / UNIQUE ID CONSUMED / RETIRED. Distinct one-shot identity, never reuse E004ms or
failed E004mr. All E004ms native visible RGB front1080/rear4K routes,
exclusive session controls, exact restoration, default-OFF rear gated
video-range tone preview and private image policy remain unchanged.
Add only an opt-in rear source buffer read-only 10-bit green temporal
comparison in the actual root-owned RAW10 publisher. Pair frames90/91
at exact unchanged baseline, 600/601 and630/631 at settled supported
rear trial exposure3200 analogue512 digital2048; no native FPS/VBLANK
changes, IR or Linux OS-level suspend. Verify source video sequence and
capture timestamp continuity within0.5s; fail closed if frames/gain
windows/order missing. Snapshot one 14.3MB RAW10 source frame only in
heap and compare with next native mmap RAW10 source using the already
camera-free-validated raw10_temporal_spatial.h. Zero buffered source
bytes after each comparison, free at cleanup. Only scalar aggregate
means, std, temporal RMS, 12x16 tile-mean std/temporal correlation and
source timestamps logged; no pixel/spatial grids/images/hashes stored,
exported or sent to ChatGPT.

This measures reproducibility of same-boot raw sensor signal and noise
under an uncontrolled physical corner. No known dark reference, fixed
illuminated target or proof of semantic scene detail; fixed sensor noise,
object motion and light flicker cannot be reliably separated by two
frames alone. Any command failure consumes the one-shot and returns
Golden; no retries of this identity. Accepted original four visible
RGB PNGs remain only on SP11 private user Pictures, not Git.

## E004mt actual three real rear RAW10 source frame-pair results

At 13:02 BST on 2026-09-23 new unique source-pinned guarded SP11 boot
`1044cc6c-612c-4146-9589-58d9b3d8202b` captured real front1080
and rear4K user applications plus three consecutive in-memory RAW10
source green Bayer sample pairs. The 14.3MB previous native RAW10
source frame lived ONLY in root-process heap for one frame, was compared
before source buffer QBUF, cleared immediately and freed at cleanup;
no RAW file/pixels/tile arrays/photo hashes were exported. Source
sequence+timestamps were consecutive and each pair passed exact
root-supported native sensor control baseline/settled gain-window
checks. The same front/rear native RGB control profiles as E004ms were
restored exactly, source/profile/app/selector route/STREAMOFF audits
passed, IR was never streamed/illuminated, and Linux OS-level sleep
was not used.

Measured real full10 green Bayer aggregate pairs (11,264 paired blocks
per source frame):

| physical source frame pair | native gap ms | green mean codes frame A/B | per-frame spatial std codes A/B | 12×16 tile mean correlation | pixel temporal difference RMS codes | tile delta RMS codes |
|---|---:|---:|---:|---:|---:|---:|
| baseline 90/91 |31.251|65.5562 /65.5645|0.7802 /0.7728|0.9729|0.8431|0.1159|
| higher gain 600/601 |33.414|84.8078 /84.8286|9.0684 /9.1124|0.9957|5.5284|0.7632|
| higher gain 630/631 |33.426|85.1584 /85.1322|9.1450 /9.1956|0.9964|5.5224|0.7006|

Per-frame pixel temporal fluctuation is substantial compared with
raw sample spatial spread at the higher native gain, despite stable
coarse tile averages. Pixel temporal RMS combines both frames; one
may only infer a per-frame ~3.9-code noise proxy under UNVERIFIED
independent stationary noise/motion/illumination assumptions, NOT
calibrated sensor SNR. Tile correlation alone cannot distinguish
actual corner shading/detail from fixed-pattern sensor response.

SP11-local private PNGs from the separately booted E004ms and E004mt
real *toned* rear gain runs were remeasured without exporting pixels.
They showed full-size grayscale luma correlation0.9795, smoothed
Gaussian-radius8 correlation0.9923, highpass correlation0.0498.
Front gain control, same method/boots, highpass correlation0.8743.
Lighting and pointing across boots were NOT independently certified
identical; low rear highpass agreement is NOT proof it contains zero
optical detail. Combined with native temporal noise, the source evidence
does NOT yet establish recoverable rear fine detail in the dark corner.
See `evidence/SP11-LOCAL-CROSS-RUN-SPATIAL-DETAIL-SCALARS.json` and
`evidence/REAL-REAR-RAW10-TEMPORAL-RESULT.json`, scalar-only.

The candidate also delivered ordinary UID1000 rear4K NV12 with gated
tone still bypassing almost-uniform baseline, and at higher bounded
gain meanY142.332–143.221 / p01=125 / p99=163, tile std7.634–7.872.
This is a second independent physical brightness-range result, not
proof of Windows-equivalent native exposure, color, geometric detail,
object recognizability or low-noise daytime quality.

The single-use attempt PASSED and returned automatically to protected
Golden Linux boot `9798e796-694a-4568-ab14-f0ede5266ac9` at
~13:04 BST. Guard PASS, saved Golden unchanged, no pending boot nor
camera nodes/modules/processes. Retirement removed E004mt root,
GRUB, boot and systemd assets. Original four private front/rear
baseline/gain PNGs are ONLY on SP11 at
`/home/geoca/Pictures/SP11-Camera-Private-E004mt/`, owner geoca folder
0700/files0600; no optical files/pixels/thumbnails/photo hashes
exported or committed. The default maintained camera and front/rear
Golden remain untouched; gated tone helper is default-OFF. NEVER reuse
E004mt identity. Next meaningful validation requires a truly lit
known target and separately controlled optical dark reference, or
camera-free design of motion-aware denoising/exposure policy before
new physical tests; do not turn mere bright luma/noisy corner into
unjustified image-quality release acceptance.
