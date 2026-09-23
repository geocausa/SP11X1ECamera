# E004mg — finite local-only visible RGB optical acceptance

Status: PHYSICAL CAPTURE PASS / IMAGE USABILITY NOT ACCEPTED / ONE-SHOT CONSUMED AND RETIRED.
Completely new single-use identity after retired E004mf and E004kt.
This candidate builds byte-verified canonical unified camera hardware and
immutable native RGB pipeline from accepted authority; front/rear opt-in
publisher binary has its own literal new exact boot token embedded in C.
IR remains off and cannot be selected; Golden remains persistent default.
No Linux OS-level standby/suspend/resume/hibernate is tested.

A bounded root-only GStreamer client additionally reads eight front1080p
or rear4K RGB frames from the already-owned single-camera virtual output
and locally saves just one baseline RGB PNG per camera under root-owned
`/var/lib/sp11-camera-e004mg/private-optical` (0700 folder, 0600 files).
Private camera pixels are NEVER printed, hashed/exported, committed to Git,
read by remote tools, or shown in chat. Finite independent ordinary uid1000
app frame and RAW10/Y scalar controls remain separately validated.
The PNG is a local visual-inspection artifact, not evidence by itself that
scene detail is recognizable or equivalent to Windows. Ambient/daylight
and camera pointing are NOT calibrated or Windows-matched. Only after a
checked return to Golden should the retirement helper copy the two photos
to the local user's `~/Pictures/SP11-Camera-Private-E004mg` (0700 folder,
0600 files), then remove this candidate's root-private stage and boot assets.
Never rearm after an attempted candidate boot, including a failure.

The new loopback module is independently reproduced from the exact pinned
Ubuntu `v4l2loopback-source_0.15.3-1ubuntu2_all.deb` under this candidate's
isolated build path, yielding a different ELF SHA from historical E004mf;
its candidate SHA and kernel vermagic are both checked before activation.
This is a disposable image probe, not a change to protected Golden.

## Actual physical result (2026-09-23 morning)

E004mg passed front1080/rear4K independent UID1000 apps, sparse full-10-bit
Bayer profiles, paired RAW/NV12, sensor controls/restoration and native
neutral graph checks. Two original front/rear baseline RGB PNGs are local
ONLY in `~/Pictures/SP11-Camera-Private-E004mg` (0700 folder, 0600 files).
No image or image hash was exported to chat or Git. Image usability
FAILED: the locally downsampled front RGB image has mean luminance .804,
p99 9, and 99.74% of samples below20; the rear has mean/p99 0, all
samples below20. Original full-size PNG front RGB channel p99=8 and
rear channel p99=0. The independent same-boot NV12 app baseline Y p99
front27/rear17 rose to front60/rear25 under reversible native controls.
NV12 video-range Y and converted RGB pixel codes are NOT equivalent;
near-video-black clipping can exacerbate a dark RAW source, especially
rear. This does NOT isolate the converter as sole root cause, prove a
calibrated black offset or demonstrate any recognizable scene detail.
Light/scene were not controlled or Windows matched. New physical boot
48105350-6c6b-4a26-be75-72a673936b43 returned automatically to Golden
1eea56cf-f9a7-498a-8368-219a7ff76b1d, all candidate assets retired.
NEVER rearm E004mg. Next: source black/exposure target, offline-verified
tone transfer, fresh guarded lit-scene visual acceptance.
