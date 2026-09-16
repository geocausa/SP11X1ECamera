# E004fd: native libcamera processed monochrome pattern

Hypothesis: the generic VD55G0 sensor identity/helper plus E004fc's monochrome
CPU software ISP can deliver 16 complete 644x604 RGB888 frames through libcamera's
normal simple/qcom-camss pipeline, with automatic backend/tuning selection.

The only kernel change from E004fb sets the media entity model to `vd55g0` with
`v4l2_i2c_subdev_set_name`; binding/module names remain unchanged. CAMSS and DT
hashes are unchanged. E004fc preserves both libcamera patches, byte-exact upstream
base/application sources, ordinary tests and the address/undefined sanitizer gate.
BUILD-MANIFEST.json and APP-MANIFEST.json record exact input/output hashes. The
application uses its isolated build's RPATH and built-in build-tree IPA discovery.
No modified system libcamera is installed; no forced CPU environment is used.

Use the previously verified Horizontal greyscale sensor pattern, GPIO outputs
all disabled. The initial cached request is exposure=1000, analogue code=16,
digital=256; native IPA auto-exposure may update exposure/analogue gain thereafter.
No protected-memory/SecureISP call or illumination control is introduced.

Expected: generic gain helper advertises gain 1..4, monochrome fallback is loaded,
16 consecutive complete RGB frames have equal channels, monotonic horizontal
ramps spanning at least 80 output levels, identical rows and cleared padding.
Check kernel warning/fault absence, sensor start/stop and runtime suspension.
This proves generated-pattern processing only, not useful optical scene quality.

Lifecycle: install separate payload, push exact source, arm one fresh GRUB entry,
one bounded capture with a 120-second Golden return timer, automatic return and
hash-checked retirement. Never overwrite Golden FullIO v19c or retry a consumed
identity. Inspect RUNTIME-RESULT.json even if the harness exits zero.
