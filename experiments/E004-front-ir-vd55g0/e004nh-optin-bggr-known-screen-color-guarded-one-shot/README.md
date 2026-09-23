# E004nh NEW SOURCE-LOCKED isolated opt-in rear BGGR CFA hypothesis

The preceding E004ng consumed/retired physical known digital SP7
six-colour chart run recorded GREEN digital(20,215,20) as approximate
Linux rear RGB(148,57,147) and WHITE digital(215,215,215)
as(231,154,230). The prior screen ROI is unregistered, and CFA
correctness is NOT yet established. The original full E004ng
runner FAILED because front gain 630->660 30frame fps28.4543
below unchanged29fps; independent original front/rear colour/
final-neutral runner gates never completed. Separate posthoc
real user-GStreamer BT601 metadata-only check PASSED but does
not fix sensor colour. E004ng NEVER REARM.

New distinct E004nh candidate tests ONE optical hypothesis:
real rear native RAW10 Bayer sites may be BGGR rather than
the V4L2-declared GRBG. Only this uniquely source-pinned
candidate rear-convert.c accepts compile-time
SP11_RGB_REAR_BGGR_OPTIN=1, changing ONLY software 2x2
demosaic site lookup while keeping packed upper8 RAW10
positions, 4K YUV601 video range, source bandwidth/crop,
supported native exposure/gain controls, exact neutral graph,
30fps/29fps gates, UV timing, camera apps and front1080
converter untouched. Sensor test-pattern/flip registers,
driver V4L2 format and IR are NEVER changed. Maintained
Golden/default rear-convert.c is byte-for-byte unchanged.

Before any live test: independently compile current maintained
GRBG path on synthetic correctly ordered RAW10 and this isolated
BGGR path on known synthetic cyan/red/green/blue/neutral RAW10.
Both must roundtrip expected RGB, and a deliberate mismatched
mosaic must fail/bias. No private image/pixel/RAW/full-frame
optical data used in tests. Verify E004nh rear publisher
cannot build without BGGR flag and only source-locked, guarded
new ELF can access real sensor on its unique one-use boot.

SP7 will show the SAME six known synthetic digital colour
patches in its interactive user desktop temporarily during
physical E004nh capture, and auto-return after 9min or
explicit close. Compare per-patch aggregate RGB of new
E004nh PRIVATE original rear PNG to earlier PRIVATE E004ng
same chart, with disclosed time/exposure/ROI differences,
and independently check actual RAW10 four native sites if
possible. Pure patch RGB improvement is not color accuracy,
true white balance, recovered detail, calibrated black or
Windows OEM ISP parity.

Original front/rear camera app FPS each settled gain
30frame interval >=29, real RAW10 baseline+late gain pairs
>=300ms after control settle, supported sensor controls exact
restore, real UID1000 source+consumer color BT601, complete
119-edge neutral/GPU safety and automatic Golden return
REMAIN mandatory. If any FAIL, original full run is FAIL,
still preserve scalar source evidence and local private
optical photos. Normal camera/IR/opt-in tone/defaults OFF.
Do not rearm any earlier consumed identity.

All camera optical images/pixels/RAW/thumbs/image hashes
stay ONLY SP11 private, never send through Fabric, ChatGPT,
Git or to SP7/other machines.

## SP7 real LCD lower-band fault and 2026-09-23 replacement target

The user reports a THICK FAULTY BAND in SP7 LCD near the
LOWER screen edge. Prior E004ng six-patch chart used full
screen including that unreliable lower region; approximate
E004ng patch/WHITE/BLUE aggregate measurements may include
known faulty SP7 panel pixels and MUST NOT be accepted as
calibrated evidence of Linux channel error by themselves.
No prior E004ng photo was transferred or altered.

For E004nh the replacement known digital six-colour chart
is expressly drawn ONLY in the upper 60% of the physical
1368x912 SP7 display (two rows each ~274px high), with
BOTTOM 40% black/untrusted. The SP7 interactive user task
reports `KNOWN_RGB_PATCHES_UPPER_60_PERCENT_ONLY_LOWER_SP7_LCD_FAULT_EXCLUDED=YES`
and auto exits after nine minutes; avoid any source capture
if chart no longer active. Any post-test image-colour
comparison MUST register the actual optical display corners
and sample ONLY safely interior known TOP 60% chart patches,
never use old E004ng full-screen ROI mapping as ground truth
or infer correct Bayer pattern from display's damaged band.
The physical display is not colour-calibrated; patch identity
and source-specific native CFA site ratios can corroborate
but cannot by themselves establish Windows ISP parity or
absolute white balance. Do not claim the whole SP7 display
is faultless or that the earlier dark band originated at
the SP11 camera.


## Actual 2026-09-23 E004nh physical upper-60%-only SP7 colour target result

SP7 user's reported lower LCD thick defective band was intentionally
EXCLUDED from the NEW chart: the interactive user desktop showed
CYAN/RED/GREEN/BLUE/GRAY/WHITE only in UPPER60% of 1368x912
panel, lower40% black/untrusted. Target visible marker confirmed
from19:15:03 to19:23:22 BST; SP7 original desktop restored,
our temporary scheduled task/scripts removed. The PRIOR E004ng
chart had used full-screen 2x3 patches INCLUDING an unknown portion
of the faulty lower display; old E004ng per-patch and white/blue
estimates must be treated as POTENTIALLY tainted and unregistered.

Fresh distinct E004nh physically ran opt-in candidate-only
SOFTWARE BGGR rear Bayer converter with unchanged Golden
default GRBG source, front processing/sensor registers/IR.
Actual original camera and user-app RGB front1080/rear4K
baseline+gain photos captured; native source front29.9609fps
and rear29.9500fps, zero source-frame gaps. All four rear
high-gain 30frame intervals>=29fps; original rear RAW10
baseline90/91 and both late gain630/631+660/661 full10
source pairs passed with original strict settling requirement.
Exact front and rear native controls restored, selector
front->rear->off->quit passed. BUT the ORIGINAL full
E004nh physical runner FAILED on real native FRONT gain
630->660 window28.0310fps (< unchanged strict29fps).
The original downstream independent bt601 validator and
final native119-edge neutral did NOT execute. No new
candidate GPU/panic/thermal error; automatic protected
Golden reboot3b1410be-fe1c-4148-a17d-1630a5deaf33.
Unique E004nh identity consumed NEVER REARM, all root/boot/
GRUB/systemd assets retired, Golden camera/IR/tone/temporal
settings unchanged. These facts must NOT be relabeled
complete original run success or permanent ISP parity.

SAME SP11-only user-private optical snapshots from earlier
E004ng GRBG/FULL-screen and later E004nh opt-in BGGR/UPPER60
were separately sampled every4x and compared using ONLY
WHOLE-IMAGE/THRESHOLD MASK scalar channel aggregates, NO
optical photo/pixel arrays/RAW/thumbs/image hashes exported.
Older GRBG bright Y>96 RGB mean (196.423,126.612,195.523)
was predominantly MAGENTA (R/G1.5514,B/G1.5443).
Later experimental BGGR NEW upper60 chart bright Y>96 mean
(103.427,165.751,123.292) is GREEN-DOMINANT
(R/G0.6240,B/G0.7438); every sampled bright pixel had
G>R and G>B. This is substantial optical colour change.
It does NOT prove sensor hardware BGGR, measured per-patch
accurate RGB, screen's true spectra, front-camera colour,
or recovered screen text: the two runs have DIFFERENT
physical chart geometry, possibly varied screen/display
lighting and unregistered ROIs, unknown lower-band fault
in the old snapshot and different independent gain timing.
The only defensible interpretation is that software
CFA-site reconstruction is a live candidate cause of
the magenta problem, worth testing against SAME unaffected
registered upper-panel patch positions and genuinely
identical native exposure/gain, not that blue is absent
or that the candidate can be enabled by default.

Private originals ONLY SAME SP11 geoca0700/files0600 at
~/Pictures/SP11-Camera-Private-E004nh/ and earlier E004ng/.
Text-only audit in evidence/REAL-PRIVATE-OLDER-GRBG-VS-
NEW-UPPER60-BGGR-GLOBAL-COLOUR-SCALARS.json and
ORIGINAL-RUN-FAILURE.txt, RETIREMENT.txt, RESULT.json.
Next use a freshly distinct source-locked one-use candidate,
repeat fixed known upper-only colour chart, compare
actual per-patch channel scalar means with robustly
REGISTERED panel bounds EXCLUDING lower LCD band and
native per-CFA-site readbacks. Preserve all >=29fps
native gain-window, exact control restore and final
119-edge neutral gates; do not force colour correction
on Golden until native Bayer order and sensor optics
are independently established.
