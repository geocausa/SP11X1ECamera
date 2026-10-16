# SP11 IR face unlock (Howdy) - lab setup

Working on the `sp11-ir-flash-lab` boot (16 Oct 2026): `sudo` authenticates by face via Howdy,
with the password as fallback.

Chain: VD55G0 (Peter Marshall's vd55g1 driver + our fixes, LED strobe on GPIO1) -> CAMSS RDI (Y10P) ->
`sp11-ir-bridge.py` (top 8 bits, auto-levels, gamma 0.6) -> v4l2loopback `/dev/video42` (GREY 644x604,
~55-60 fps) -> Howdy (dlib 20.0.1, built from source; Howdy master d3ab993, meson, prefix /usr).

- The IR LED (PM8550 flash, 350 mA per channel = Windows' drive, ~0.86 ms pulses) is armed only while
  the bridge runs: `sp11-ir-on` (pam_exec) starts it for 8 s per authentication.
- `sp11-ir-stack.service` loads the camera stack only on the lab boot entry.
- Howdy config: `device_path = /dev/video42`, `timeout = 6`, `dark_threshold = 90` (IR scene is mostly
  dark around the face). `howdy-gtk` renamed to `.disabled` (its auth UI crashes without a display and
  spams crash reports).
- Enrol: start the bridge (`sp11-ir-bridge --seconds 20`), then `howdy -U geoca -y add`.

Not yet: login/lock screen (common-auth), daily-boot integration (needs the flash DT node, our
leds-qcom-flash build and the vd55g1 driver in the daily package).
