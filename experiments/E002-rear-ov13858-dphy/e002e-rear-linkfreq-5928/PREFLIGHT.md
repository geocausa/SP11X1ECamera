# E002e preflight — rear 592.8 MHz transport metadata, no stream

## Question

Can the accepted E002d rear OV13858 -> CSIPHY1 graph and native driver agree mechanically on Windows-proven four-lane D-PHY link frequency **592800000 Hz**, while the sensor remains electrically idle after its normal identity cycle and any attempted stream is blocked before power-up?

## One major unknown

Transport metadata agreement only. Surface mode/PLL register programming is explicitly deferred.

## Exact base

- Golden kernel bytes: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`.
- E002d accepted graph DTB: `ea55cafdc4b35197e4d839a8435c7514c351ef4cfd2933d81458db0bea10472d`.
- E002c accepted power/identity driver is the source base.
- accepted camera RPMh provider unchanged: `ac9269cd4be0842cb5dd3eeef9ccc2dc95100c86b59e57d83b3d86c8f5178ace`.

## Driver delta

E002e module SHA-256:

`68369e6496382a0aa31fbbddc63c92742fd82d39c339c831cd2c663c19a99ee9`

srcversion: `F8251C8C28A8AB99D09BD40`.

Changes from E002c:

1. full-resolution V4L2 link-frequency metadata 540 MHz -> 592.8 MHz;
2. parse sensor endpoint and require explicit four-lane D-PHY + one 592.8 MHz link frequency;
3. DT-selected stream guard returns `-EOPNOTSUPP` before `pm_runtime_resume_and_get()`.

The PLL and mode register arrays are byte-identical to E002c and will not be executed.

## DT delta

Candidate DTB SHA-256:

`0e25c28f604b12e05b1db61a9e3c177dce77845b42361ef84cc10d7714c12428`

Only:

- `microsoft,e002e-no-stream` on rear sensor;
- `link-frequencies = /bits/ 64 <592800000>` on the already accepted rear sensor endpoint.

E002d graph, lane maps, rails, reset, CCI and MCLK are unchanged. DTC warnings remain 30 -> 30.

## Initrd

Golden-based independent builds A/B are byte-identical:

`4851777632c621d336391ef0f865ea3608b2ea5d986584c8d74e249c5bbca4a5`

The semantic layer contains only the already-proven provider/V4L2 dependencies, the E002e native module, deterministic directories, loader and ORDER delta.

## Acceptance

Without any stream call:

1. E002e endpoint validation logs PASS at 592800000 Hz / four lanes;
2. native OV13858 identity still passes;
3. media graph still contains immutable enabled OV13858 -> CSIPHY1 link;
4. read-only V4L2 controls expose LINK_FREQ=592800000 and PIXEL_RATE=474240000;
5. sensor runtime PM returns suspended/usage 0;
6. MCLK1, CSIPHY1 and CSI1 PHY timer enable counts are 0 after probe;
7. Wi-Fi/audio remain healthy.

Optional safety proof: issue only the subdev stream-enable ioctl to verify it returns `-EOPNOTSUPP` **and causes zero camera rail/MCLK/CSIPHY activity**. This is safe because the E002e guard runs before runtime-PM power-up; no sensor register or PHY operation is reached.

## Rollback

Golden `sp11-audio-fullio-v19c` remains saved default. E002e will be separate and one-shot only.
