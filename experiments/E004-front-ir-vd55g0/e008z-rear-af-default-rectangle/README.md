# E008z — source-derived AF default rectangle, offline only

Status: **PARAMETERIZED SOURCE SLICE; LIVE INPUT/BRANCH OPEN**.
Parent E008y `a8accb0d`.
Linux L4/L5 AF policy, rear color VideoRecord NV12 3840×2160.
Evidence tier S (exact pinned DeviceMFT static source), no new physical runtime.

The exact `af_util_get_roi_default` function in the pinned same-SP11
DeviceMFT reads the AF state's CAMIF width/height, tuning width/height
fractions, zoom factor, optional mode scale and optional PD dimension
scales. It truncates to halfword dimensions, caps height at CAMIF height,
selects a per-axis minimum of 400 for sparse PD or 200 for 2PD, then
centers with halfword shifts. `af-default-rectangle.h` is a bounded
standalone version with every unknown tuning and branch decision explicit.
It rejects unsupported degenerate geometry. It contains no captured OEM
coordinates, tuning values, DMI data or hardware address.

`af_util_adjust_roi` does not always choose this producer. It can return
unchanged ROI, choose face, track, salient, touch, PD multiwindow or the
default path. The PD multiwindow helper requires several simultaneous
tuning, mode and zoom gates; when selected, it splits the default rectangle
by one of eight policy indices. The later adjust stage rounds the packed
rectangle's halfword components even, then BAF forms/clamps its own
coordinate rectangle (E008y). Neither the live per-request policy index,
CAMIF geometry, fractions, zoom nor the packet1→2 origin handoff has been
measured at the intermediate stage. E008x's generic map still needs an
explicit final BAF rectangle and no normal DMI payload has full byte parity.

Next falsifiable gate: resolve selected rear sensor-mode CAMIF dimensions,
AF tuning fractions and initial ROI policy for each of packet1/2, then
privately compare the source-composed default→adjust→BAF→BFStats25 output
with all retained selector-1 records. Reject a candidate unless all records
are byte exact. No native rear ISP runtime, module load or optical output.
