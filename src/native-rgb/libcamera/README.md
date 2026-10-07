# Actual native front standard libcamera IPA

Build06 integrates a real IPA module and generated standard proxy. Hardware pixel
processing stays in the Qualcomm ISP. The IPA reads shared statistics, validates
frame identity, computes the retained AEC meter and emits typed mask0 defaults.
No exposure or colour feedback is enabled. Metrology and sensor delays are next.

Nine offline tests pass with Werror; two VIMC-dependent tests skip. An actual IPA
implementation test uses real memfd mappings and covers negative admission,
ordering, nonzero metering and lifecycle reset. Fresh pipeline04 will force normal
libcamera IPA process isolation and require80 associated application frames.
No bespoke camera daemon is introduced; the worker belongs to standard libcamera.
No physical IPA claim until that candidate passes. Optical comparison requires
Windows on the same physical camera, scene and lighting, with capture times.

# Native X1E libcamera pipeline and helpers

Current physical proof: build03/audit27 delivers standard cam80 NV12/statistics
pairs2560x1440 at30.0056fps, and public API same-camera1/80/80 restart/reacquire
passes161 app frames/880 owner checks. Fixed manual only; real IPA/3A absent.
Latest build04/audit27 pipeline03 passes80 standard cam frames at29.9919fps,
with the incorrect SensorTimestamp field removed. Pairing uses completion time;
first-row exposure/CLOCK_BOOTTIME remains unqualified. Actual IPA/3A is next. Earlier helper-only descriptions below are historical.

The approved product is Linux sensor/CAMSS drivers, Qualcomm hardware ISP and
a standard libcamera pipeline/IPA. Automatic control calculations execute in
libcamera; pixel processing belongs to the hardware ISP.

This integration builds the retained front sensor-control adapter, front AEC
statistics meter and rear neutral ISP scalar producer inside real libcamera
libipa. The IMX681 helper registers the measured/reconstructed Sony analogue
gain law; it deliberately leaves unknown black level unset.

The front adapter validates every control before returning one four-control
transaction (VBLANK, exposure, analogue gain, digital gain) and residual ISP gain.
Apply the returned list through one extended-control operation. The sensor
ControlInfoMap must outlive the list. This preserves the driver's group-held
cluster. Failed validation leaves outputs unchanged.

Statistics use the retained bounded-front envelope, not a new public metadata
ABI. Both generation and sequence must match the caller's expected identity.
The rear scalar wrapper preserves the validated float/quantization arithmetic
and prevents partially published results on error.

## Reproduce

Use fresh source and build outputs outside the camera checkout:

```sh
python3 src/native-rgb/libcamera/build.py \
  --source /home/geoca/Documents/SP11-PROJECT/06-camera/reference/libcamera-v0.7.0-native-ir \
  --out /home/geoca/Documents/SP11-PROJECT/06-camera/reference/libcamera-native-rgb-NEW \
  --build-dir /home/geoca/Documents/SP11-PROJECT/02-kernel/libcamera-native-rgb-NEW \
  --jobs 4
```

The reference commit and source inputs are pinned. Clone copies committed files
only: earlier uncommitted software-ISP changes in the reference are excluded.
The retained statistics file's private fadd/fsub/fmul names receive a prefix to
avoid GNU math declarations; arithmetic is unchanged. Original retained files
remain untouched. The build enables warnings as errors, verifies staged hashes,
requires the native test to pass, and records selected tests and binary digests.
Source, setup, compile and test logs remain in the isolated outputs.

This build enables UVC/VIMC and the test-only virtual pipeline, not a CAMSS X1E
pipeline. SoftISP is disabled. Nothing is installed or opened on camera hardware.
The helper test covers gain conversion, nominal and extended exposure, complete
control publication, range rejection, neutral/asymmetric rear gains, preservation
after late errors, nonzero AEC metering, and stale/malformed statistics.

## Remaining integration

This is a compiled algorithm integration, not a completed IPA or pipeline.
Native linear NV12 capture, continuous streaming, parameters/statistics queues,
front/rear ownership and hardware-correlated delayed controls remain required.

The front driver lacks HBLANK/PIXEL_RATE and selection information. Its unused
548570000 mode field describes transport-derived throughput and must not be
published as array PIXEL_RATE. Retained Windows exposure policy uses an effective
719898240 timing model from 6752 * 3554 * 30. The public September 23 IMX681 v7
patch measures 720 MHz with the same VT PLL divisors but a different mode/platform.
Measure this SP11 mode before publishing truthful timing controls. Do not guess
full pixel-array bounds from the current crop.

Retained files keep their original licences (front GPL-2.0-only, rear MIT).
This does not relicense them as LGPL or claim upstream acceptance. No Windows
binary, tuning dump, optical frame, daemon, loopback or software pixel ISP is added.


The frame-associated metadata consumer now validates the experimental QXS1
envelope, stream ID, video sequence and pixel timestamp before reducing AEC
luma. Malformed, stale and discontinuous input leaves the caller output untouched.
It uses the exact shared kernel/probe envelope definition. This helper passed
the real ARM64 libipa build and tests, with no installation or hardware access;
see docs/NATIVE-RGB-LIBCAMERA-METADATA-BUILD-20261007.json. A complete pipeline/IPA
is still required to schedule requests and connect this consumer at runtime.


The typed front parameter encoder now forwards bounded caller-owned quantized
gains/ratios through the exact shared kernel schema, rejecting invalid masks,
sizes, sequence bounds and ranges without modifying the caller output.
See docs/NATIVE-RGB-LIBCAMERA-PARAMETERS-BUILD-20261007.json. Scheduling and the
camera pipeline remain unfinished; the private startup profile is diagnostic.

An optional --front-pipeline-trial build now stages a real CAMSS X1E pipeline
and standard cam. It matches the data-only front driver, owns four startup
buffers and pairs app images/statistics before libcamera request completion.
The first version uses fixed manual settings, no IPA/automatic controls.
Hardware pipeline02 and lifecycle03 passed the bounded scopes above. Hardware qualification lives in
src/native-rgb/front-pipeline with a fresh one-use boot.
