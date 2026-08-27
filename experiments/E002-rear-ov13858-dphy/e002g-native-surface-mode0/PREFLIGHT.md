# E002g — native Surface 4076x2806 mode semantics

Status: PREPARED / NOT YET BOOTED

## Goal

Expose the accepted Surface mode-0 timing through native V4L2 semantics without streaming.

## Driver architecture

Generic OV13858 fallback remains intact:

- 540 MHz generic link profile + upstream PLL;
- 270 MHz generic link profile + upstream PLL;
- four generic upstream modes and register arrays byte-identical to E002f/upstream.

SP11 adds a third link profile and a board-selected one-mode set:

- 4076x2806;
- VTS 3214;
- link-frequency index 592.8 MHz;
- pixel-array rate 432,732,960 Hz;
- common GPL upstream full-resolution table;
- compact Surface override list already accepted in E002f.

The mode structure gains an optional clean-room override list. `ov13858_start_streaming()` would apply it after the common mode list, but E002g retains the hard no-stream guard **before `pm_runtime_resume_and_get()`**, so this path cannot execute during the experiment.

## Expected controls

- LINK_FREQ: 592800000
- PIXEL_RATE: 432732960
- HBLANK: 412
- VBLANK: 408
- one enumerated frame size: 4076x2806 RAW10

## Mechanical controls

- E002f sensor module source arrays are byte-identical in E002g: both generic PLL arrays, all four generic mode arrays, Surface PLL and Surface delta.
- stream guard remains before runtime power.
- candidate module SHA-256: `e63e70612dbe66cb14327a214efde909e17a95cfe7c13db28de5ee7066eb0164`;
- module srcversion: `A651DC00F99983AC6A72051`;
- exact Golden v4 vermagic;
- E002f DTB base: `b669db40f44a108560aeca23e9f0d52b312246452d0771c93daf8765fc8d0692`;
- E002g DTB: `bba11b3113f3662c70b734d2cd34a14220e6a4915e22a4ae91c4b7a263177092`;
- DT semantic delta: one boolean `microsoft,e002g-native-mode0`;
- deterministic initrd A/B SHA-256: `24b5c4b48980924610027ec4e21e2c7ccea9f746f1345d2807e00f85b9f9543b`;
- baseline DTC warnings unchanged 30 -> 30.

## Runtime acceptance

Strict one-shot boot only. No streaming ioctl.

Require:

1. E002f standby validator still passes;
2. E002g native mode-selection log appears;
3. frame-size enumeration exposes only 4076x2806;
4. read-only controls return LINK_FREQ=592800000, PIXEL_RATE=432732960, HBLANK=412, VBLANK=408;
5. immutable OV13858 -> CSIPHY1 link remains intact;
6. sensor runtime PM suspended/usage 0 after probe;
7. MCLK1/CSIPHY1/timer clocks at enable count 0;
8. Wi-Fi/audio healthy;
9. Golden remains saved default.
