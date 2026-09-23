# E004mg — finite local-only visible RGB optical acceptance

Status: SOURCE-STAGED, NOT YET ARMED OR PHYSICALLY VERIFIED.
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
