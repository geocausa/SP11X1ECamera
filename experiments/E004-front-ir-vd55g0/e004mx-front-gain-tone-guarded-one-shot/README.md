# E004mx fresh front-only opt-in video-luma trial, with accepted rear NEON control

New, never-before-used one-shot source-locked candidate. Previous
E004mv/ E004mu consumed and RETIRED, NEVER rearmed. Maintained Golden
camera, ordinary video formats, IR, sensor native frame rate and
kernel untouched. E004mx changes ONLY the front1080p display Y plane
AFTER the native source/RAW10-vs-NV12 same-frame prefilter paired
metric, with an explicit compile-time opt-in front tone helper and
verified exact source profile. Existing rear 4K opt-in gain tone and
NEON temporal performance path remains identical to E004mv as
an independent reference and strict >=29fps high-gain-window gate.

E004mv current real source 90-frame front gain p01~30,p50~34,p99~61,
front actual 4x user RGB private image gray mean19.628/p99 47,
front baseline NV12 p01~30/p99~37. E004mx front gate bypasses flat
baseline and above-bright scenes; only higher native front gain may
map p01 to videoY100 and contrast2x; UV/source RAW10 unchanged.
This is a display demo, NOT native auto exposure, real recovered detail,
colour accuracy, Windows ISP or recognized objects. Require real
front same-frame source-before-tone vs independently ordinary uid1000
NV12 client AFTER tone + private on-SP11 baseline/gain optical RGB
only; fail if gain gate not applied or baseline lifted, FPS below29,
source gap, native controls not exact restored, GPU fault or incorrect
front/rear/off service lifecycle. Normal front publisher defaults OFF.

Only SP11-local private photo storage geoca0700/files0600; NEVER
export any photo/pixel/RAW/thumb/image hash to other machine, chat,
Git or Fabric. One-shot boot consumed on first attempt, no retries;
firmware reboot may fail as earlier E004mu, preserve logs and
await online host/physical user power-on only if essential.
