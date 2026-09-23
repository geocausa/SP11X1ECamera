# E004ms — fresh opt-in rear tone, instrumented RGB selector startup

PHYSICAL PASS / CONSUMED AND RETIRED / DEFAULT GOLDEN UNCHANGED. Distinct NEW one-shot, NEVER rearm failed/retired
E004mr nor E004mp. Default maintained camera and protected Golden remain
unchanged. Reuses same native front/rear baseline+bounded gain controls,
front1080/rear4K source-pinned studio-range RAW10→NV12 publishers and
rear-only gated preview tone as E004mr. Adds only root-owned durable
control-socket trace instrumentation in a candidate-private selector
copy so unexpected first camera activation records its precise exception
BEFORE fail-closed Golden reboot. Logs scalar/command metadata ONLY,
no image pixels, thumbnails, hashes or unauthorized sensor controls.

Strict observed source checksum, exact new boot token, candidate opt-in
rear studio/tone compile gates, production output default OFF, IR OFF,
no Linux OS system sleep. Preserve four optical PNGs on SP11 ONLY if
real frames are actually captured; failed pre-stream candidate must
archive its selector trace and immediately auto-return Golden then
retire assets. No inherited E004mr boot assets or reuse. This is a
fresh attempt to distinguish a selector service race/fault from image
rendering; no Windows parity or image-quality claim without live frames.

## Actual physical E004ms outcome — 2026-09-23

The NEW unique source-pinned candidate booted as
`686e93be-b40f-4eba-91a5-780bc3613d79` at ~12:32–12:34 BST.
Both ordinary UID1000 V4L2 RGB applications obtained actual front1080p
and rear4K video. Source full10 RAW10 Bayer profile, paired upper-eight
source / converted NV12, camera app/client life-cycle, exact native
sensor-control restoration, STREAMOFF/neutral, IR OFF and no Linux OS
system sleep were validated. The sealed selector trace records
successful front→rear→off→quit operation. The one-shot runner reported
`PASS_E004MS_REVERSIBLE_RGB_SENSOR_GAIN_AND_PAIRED_RAW8_NV12_NO_IR`
and its rear tone gate reported the uniform baseline BYPASSED and the
later bounded gain trial APPLIED. The former E004mr first-front
selector no-reply did not recur; E004mr upstream cause remains unknown.

The real ordinary-user rear NV12 app measured baseline mean Y30.22–30.23,
p01 30, p99 31, 12x16 tile-mean std0.22. With the previously accepted
rear trial exposure3200/analogue512/digital2048 and candidate-only
studio-range Y mapping, app mean Y145.46–145.67, p01 125, p99 167,
tile std9.8–9.87. Source-rear tone scalar log at frames600/630 showed
input p01/p50/p99=32/37/44, mapped estimates125/142/167, whereas
uniform baseline frames1/30/90/180 with p99≈31 bypassed tone. The
front camera was NOT tone-adjusted; all original/native RAW and UV
chroma bytes were unchanged by tone. Root-private rear RGB PNG
256x144 downsampled BT709 Y mean144.399, p01 126, p99 165, tile
std10.525, zero Y endpoint-clipped pixels; RGB channel means
R148.427/G142.852/B148.638 do not establish colour accuracy.

The fresh earlier Windows E004wp rear 4K NV12 auto-exposed output had
mean Y149.15–150.41, p01 118–119, p99 169–171 and spatial tile
std11.46–12.06. The E004ms rear Linux user-visible *brightness range*
now overlaps Windows' approximate rendered brightness, but captures
were not simultaneous, sensor exposure/illumination and statistical
sampling differ, and actual scene recognizability/colour detail, noise,
calibrated optical black, true Windows ISP/automatic exposure and
normal daily-use integration are NOT proven. A local-only 12x16 tile
comparison of E004ms toned rear gain with E004mp original untoned gain
showed correlation0.99686; stable scene structure OR fixed sensor
pattern noise can produce such a correlation. Do not generalize the
heuristic p01-anchored preview LUT into calibrated real ISP or AE.

E004ms automatically returned to protected Golden Linux boot
`5e400c52-4c3f-4c69-ab7e-19065f514527`. After verifying the
post-boot guard, retirement removed E004ms GRUB/service/boot/root stage
and preserved exactly four original front/rear baseline/gain private
RGB PNGs ONLY on SP11 in
`/home/geoca/Pictures/SP11-Camera-Private-E004ms/`, folder owner geoca
mode0700 and each photo mode0600. No original photo, pixels,
thumbnail or photo hash is in repository, exported or sent to ChatGPT.
E004ms is CONSUMED and must NEVER be rearmed. Default maintained
camera publisher is unchanged and opt-in tone remains OFF in Golden;
no user-side file opening, reboot or manual operation is required to
use this experimental proof as the basis for further engineering.

Safe follow-up engineering: develop an independently source-locked,
non-default rear exposure/tone policy with measured temporal stability,
white balance/colour and dark-reference noise checks; demonstrate
recognizable detail and reliable powered-on service lifecycle, ideally
with an actual fixed target and distinct dark reference. Do not
implicitly raise rear exposure beyond current mode max3206 or change
4K fps/VBLANK/IR. See RESULT.json and text-only evidence; normal
production camera must NOT be declared Windows-equivalent yet.
