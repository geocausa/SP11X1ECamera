# Current full-rate qualification

03 passed1/24/24 control lifecycle,manager shutdown and isolated-worker exit;
spent and retired. Pipeline11 still inserted a spare every4 application frames.
Restored threshold2 in fresh build12. NEXT04 via install-lifecycle.py and
run-throughput-once.py verifies120 standard public scripted requests with
consecutive frame sequences/full30fps and scripted15fps,no optical files,
then stricter1/24/24 contiguous30fps controls/reset/reacquire/shutdown checks.
Pipeline12 passes10 tests/2 virtual skips with Werror. Golden and one-use rules
retained. Native AE/AWB and optical/meter calibration remain unfinished.

# Latest lifecycle test

02 is consumed/retired. Three kernel streams stopped clean6/34/34,custom then
reset physical settings correct;process/49 publicmetadata qualification remains
incomplete after pipe-output timeout,original preserved. Source audit found
retained Camera reference after CameraManager::stop; corrected to reset first.
NEXT03 using install-lifecycle.py/run-lifecycle-once.py,new test binary, direct
private output files/shutdown markers,manager-stop and isolated-worker exit checks.
If needed, bounded backtrace is permitted only after3 STOPs/sensor runtime idle.
No repetition of the already qualified120-frame request capture.

# Current qualification status

request01 is CONSUMED AND RETIRED. Its actual120 public cam requests pass all
control/metadata/readback/write-SOF checks. Original qualification erroneously
required zero-origin owner logs and failed before lifecycle. Original preserved;
retrospective offline correction proves all groups1..154 contiguous, STOPclean.
See docs/NATIVE-RGB-FRONT-REQUEST-CONTROLS-01-20261007.json; no repeat capture.

NEXT fresh request02 using install-lifecycle.py/run-lifecycle-once.py tests ONLY
public lifecycle1/24/24: custom start settings, same-configuration default reset,
release/reacquire reset. Current origin-independent trace checks have6 pure tests.
Golden permanent/service120s/atomicconsume/automaticreturn/pixel privacy retained.

# Standard request control qualification

E-NATIVE-FRONT-REQUEST-CONTROLS-01 is a fresh one-use candidate. It reuses
qualified audit31 kernel modules and builds standard libcamera pipeline11.
The source implements DelayedControls with measured delay2 for all four
non-priority sensor controls, one complete clustered ioctl for each change.
Public controls: manual ExposureTime/AnalogueGain/DigitalGain and bounded
FrameDurationLimits, with AeEnable=false and manual-only mode controls.
Exposure/time conversion uses the existing sensor HBLANK/PIXEL_RATE model;
integer microseconds are rounded, not optical calibration. AE/AWB remain off.

Admission counts startup/spare/app buffers in exact VIDIOC_QBUF order. Every
controlled request must arrive before its delayed slot is pushed (three-frame
scheduling horizon); late controls fail instead of borrowing another frame.
SOF snapshots preserve applied metadata independently of the 16-entry delayed
control ring. SensorTimestamp remains absent. Upstream applyControls is void;
the pipeline checks cached V4L2 readback after each write, and qualification
independently verifies known CCI register reads and write timing.

Hypothesis: real standard cam --script requests are applied to the exact
admitted application frame and reported in public metadata, including all four
sensor fields; stopping and restarting cannot leak previous control history.
Expected:120 NV12 requests, nine explicit request lists/eight actual changes,
all applied metadata/known-register reads/CCI SOF intervals match; public API
lifecycle1/24/24 proves custom start controls then default reset and reacquire.
Golden remains permanent, candidate has a120s service bound and automatic
Golden return on success/failure/timeout. No same-ID retry is permitted.
Pixels remain in the private root-owned SP11 evidence directory. Only derived
scalar evidence goes into Git. Lights last reported ON18:26:29UTC; no new
simultaneous Windows comparison or uninstrumented scene stability claim.
Image quality, automatic exposure and production readiness remain unproven.
