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
