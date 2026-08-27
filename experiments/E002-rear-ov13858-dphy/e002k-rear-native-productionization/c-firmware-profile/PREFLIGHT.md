# E002k-C — firmware-selected native Surface profile

Status: PREPARED / NOT YET BOOTED

## Goal

Remove all experiment-only `microsoft,e002*` switches from the rear camera DT and driver while preserving the accepted rear-camera behaviour.

## Native selection rule

The driver keeps the ordinary upstream OV13858 mode set by default. If a standard firmware CSI endpoint exists and describes exactly:

- D-PHY;
- four data lanes;
- one link frequency of 592,800,000 Hz;

then it selects the already-validated Surface Pro 11 profile: 4076x2806 at 30 fps, link frequency 592.8 MHz, VT pixel rate 432,732,960 Hz and the clean upstream-common + Surface-delta sensor program.

No private experiment property participates in mode selection or stream permission.

Generic devices without such an endpoint retain the upstream mode set and two-entry 540/270 MHz LINK_FREQ menu.

## Driver cleanup

Removed:

- `microsoft,e002e-no-stream` / stream-block state;
- `microsoft,e002h-allow-stream` / stream-permission state;
- `microsoft,e002f-validate-mode0` and the standby readback validator;
- `microsoft,e002g-native-mode0` mode-selection switch;
- experiment-specific PASS/gate logging.

Retained unchanged:

- standard `dovdd`, `dvdd`, `avdd` supplies and proven order/voltages;
- reset/MCLK lifecycle;
- native identity path;
- Surface PLL/delta and controls;
- standard stream path;
- generic OV13858 fallback mode table.

`SOURCE-AUDIT.txt` mechanically confirms the generic upstream mode table and generic 540 MHz PLL block are unchanged.

## DT delta

Relative to accepted E002k-B, the candidate deletes exactly four boolean properties:

- `microsoft,e002e-no-stream`;
- `microsoft,e002f-validate-mode0`;
- `microsoft,e002g-native-mode0`;
- `microsoft,e002h-allow-stream`.

No other semantic DT line changes. DTC warning count remains 30 -> 30. Standard supply phandles and endpoint metadata are unchanged.

## Reproducibility

- candidate DTB builds A/B byte-identically;
- candidate initrd builds A/B byte-identically;
- exact hashes are in `ARTIFACTS.txt`.

## Runtime acceptance

1. strict one-shot boot; Golden remains saved default;
2. no `microsoft,e002*` properties in the live sensor node;
3. driver logs selection of the four-lane 592.8 MHz firmware profile;
4. V4L2 exposes only 4076x2806 for this profile, LINK_FREQ 592800000 and PIXEL_RATE 432732960;
5. native identity succeeds with only DOVDD/DVDD/AVDD and zero VAF enable events;
6. deterministic test-pattern frame SHA-256 equals `6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`;
7. 16-frame normal stream completes without drops/faults and tears down cleanly;
8. Wi-Fi/audio remain healthy.
