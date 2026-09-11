# E003i-GW — minimal changed post-G3 control authority

Status: **PASS OFFLINE authority / no camera runtime / no live candidate yet.**

GV proved that exact-equal G4..G6 `S_EXT_CTRLS` calls are deduplicated by V4L2 before the IMX681 driver, so a true post-G3 sensor transaction requires an actual changed cluster.

GW defines the smallest practical transport sentinel:

- only source **G4** may request it;
- only if native G4 is bit-identical to the last successfully applied G3 tuple;
- copy that tuple and increment only IMX681 `digital_gain_code` by **one register LSB**;
- all FLL/exposure/analogue gain and the native ISP-gain field remain untouched;
- all other sources are shadow-only;
- if native G4 has changed on its own, the sentinel is suppressed rather than stacking a synthetic delta on a real controller change.

The consumed GV tuple is FLL=7116, exposure=7108, analogue=960, digital=1471 (`0x05bf`). The sentinel is digital=1472 (`0x05c0`). With the IMX681 1/256 digital-gain scale this moves 5.74609375x to 5.75000000x: **+0.06798%** relative sensor digital gain. It changes no frame timing.

Under the established delayed-control law, source G4 is written immediately after completed G5 and is expected to affect G7. Later controls remain shadow-only, so this gate seeks exactly one new post-G3 sensor hardware transaction and nothing broader.
