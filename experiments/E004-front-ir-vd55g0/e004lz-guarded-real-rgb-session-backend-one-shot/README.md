# E004lz — guarded real RGBSession + Linux software source backend

Unique, source-pinned, root-private, non-default single-use camera candidate.
Its purpose is to integrate the maintained RGBSession (session.py) with the
exact native 119-link media_backend, RGBDeviceBackend and CandidateOwner
against actual front 1080p and rear 4K RAW→NV12 real optical sources and
uid1000 independent standard V4L2 applications. E004ly previously proved
the source publishers, output resolutions and app client crash/reopen under
its older scripted route lifecycle; it was CONSUMED and RETIRED. E004lz is a
NEW boot/service/token/consumption identity, not a retry of E004ly.

Use only the accepted canonical 51-file hardware+R4 stage and exact
pinned ABI-matched private loopback build. The new guarded driver runs
front→verified neutral→rear→verified neutral, three normal 120-frame
unprivileged app opens + intentional SIGKILL/recovery per camera,
independent FD and root-owned publisher exit143/STREAMOFF checks,
complete graph fresh readback on EVERY write, unique controller and
publisher locks, and IR-off checks. Any uncertain graph or stop result
poisons the session. The one-shot service reboots back to protected Golden
on ALL outcomes; if failure do not guess at graph rollback. Linux OS-level
standby/suspend/resume/hibernate and IR illumination/streaming are prohibited.

This is a FINITE guarded proof, not a default or daily-use installer.
Image quality remains uncalibrated, prior scenes were near-black.
No Windows hardware ISP, QC10C decode, or Windows Hello testing.
Prepare hardware and software test assets offline, commit and push all
candidate scripts, run overlap/hygiene and independent rollback guards,
then install unarmed and arm at MOST ONCE. On return inspect RESULT,
CONSUMED and retire the private candidate boot/services/assets.

## Final result (2026-09-23)

**PASS, CONSUMED, RETIRED.** Fresh candidate boot 64698955-b3ab-4c96-85aa-7f4abf2c885f proved actual maintained RGBSession and the real device/route/controller-owner adapters against front1080p and rear4K, sequentially. Front448/rear446 real optical source frames, no source-sequence gaps, ordinary uid1000 first/reopen/kill/recovery, same publisher invocation, verified stop143/STREAMOFF and complete native graph neutral before, between and after. Both optical scenes sampled nearly black (mean Y≈16), so image quality/3A/Windows pixel parity remain unresolved. Golden returned with original saved default, assets retired and E004lz may NEVER be rearmed. RESULT.json, CONSUMED.json and evidence/ are authoritative. Not a persistent opt-in service or long-duration stress proof.
