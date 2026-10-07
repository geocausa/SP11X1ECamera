# Native front RAW control isolation — E-NATIVE-RAW-CONTROL-01

Fresh identity native-raw-control-20261007-01, one use only. Never rearm a
consumed identity. Diagnostic metrology; no release daemon, software ISP,
loopback, pixel files, effects or AI.

Hypothesis: the known clustered exposure and gain controls alter native sensor
RAW values independently of the ambiguous processed ISP/statistics response.
Reuse SHA-verified audit31 source-built modules. All ISP/owner/meta/profile/SOF
trial flags remain disabled. Only sensor known-register trace/readback is enabled.
Front route is CSIPHY2 -> CSID1 pad1 -> VFE1 RDI0, SRGGB10 packed pRAA,
3840x2160, 4800-byte rows, 10368000 bytes. No rear/IR stream.

The probe reads four Bayer phases on a fixed interior 16-pixel grid, 31654
samples/phase/frame, and outputs aggregates only. No demosaic, black-level
subtraction, image conversion, calibrated brightness or nominal 2x optical
gain is claimed. All optical source memory remains on SP11. Six source-derived
analysis tests plus unpack/bounds/timing and synthetic sampler checks pass.

320 sequential RAW buffers, FLL3554, exposure1000, analogue0, digital256 baseline.
After DQBUF/requeue sequences15..287, alternate raised/restored controls every
16 frames: exposure2000 for steps1/3/5, analogue512 for7/9/11, digital512
for13/15/17. Other controls stay baseline. Final 32 frames are restored; an
explicit final baseline ioctl is verified. The unchanged final ioctl need not
produce an extra CCI write: expect19 commits/readbacks and20 command records.
Four known hardware registers must match every committed tuple; in-stream
I2C timestamps must lie inside ioctl timing. No arbitrary register access.

Last8 frames of each16-frame plateau are compared using measured temporal
noise, repeated restoration and storage saturation screens. Response qualification
is distinct from healthy capture. RAW has no qualified FRAME_SYNC source here:
DQBUF is completion, not SOF. This test cannot qualify gain frame application
delay, SensorTimestamp, metering optical units, AE target, Windows image parity
or a brightness defect. Matched same-scene Windows reference remains absent;
physical lighting/orientation is not instrumented. Rain/cloud reported by user
on2026-10-07 is a possible illumination confounder.

Build/install tools run only under protected Golden and idle graph. Installer
prepares UNARMED SHA-sealed assets; atomic entry consumption and root-only arm
check protect against duplicate invocation. Verified boot writers finish first;
systemd timeout/stop hook reboots to saved Golden on success or failure.
Kernel/DTB/initrd manifests are sealed before arm, with unchanged Golden hashes.
An uncertain stop/graph failure gets no guessed same-boot rollback/retry.
Retire the boot directory/unit/GRUB writer after return, retain private evidence.

## Hardware01 result — consumed and retired

Source9e9e44c5 passed320frames at30.005318fps;19 hardware register reads matched,
STOP clean,sensors idle,graph neutral,critical0,Golden unchanged. Candidate
a64b9f97-99f7-4bee-a38a-3462ac44452a returned Golden
e0c99b76-ca28-4be3-9332-86c7cdf6eecd. No rearm/retry this identity.

Original mean-response analysis is preserved and remains unqualified for all
three fields. RAW sample medians64,p01=62/63,p99=65..67; the cause and optical
black calibration are unestablished. Retrospective variance analysis using the
same temporal-jitter/restoration/clipping checks passes all4 phases in all3
cycles for analogue and digital. Nine analyzer tests pass. Spatial distribution
variance changes do prove captured RAW response to controls; do NOT translate
this into scene brightness,nominal optical gain,exposure SOF delay or covered
lens/night/driver brightness failure. No additional hardware experiment was run.
Derived evidence: docs/NATIVE-RGB-FRONT-RAW-CONTROL-01-20261007.json.
Next matched Windows same physical front camera/scene/light with Linux bracket;
record UTC/settings/environment and explicitly reject optical parity if changed.
