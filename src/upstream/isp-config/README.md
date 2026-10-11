# Open ISP configuration primitives

This is the first source-only replacement slice for the SP11 RGB ISP startup
dependencies. It is not a complete startup profile, a public ABI, or a camera
application. It reads no firmware or calibration files and does not access hardware.

Run from the checkout root:

```sh
python3 src/upstream/isp-config/test_open_config.py
python3 src/upstream/isp-config/test_gamma_compat.py
python3 src/upstream/isp-config/open_config.py --camera front --output /tmp/front-open.json
python3 src/upstream/isp-config/open_config.py --camera rear --output /tmp/rear-open.json
python3 tools/test-upstream-readiness.py
python3 tools/check-upstream-readiness.py
```

The readiness command is expected to exit 1 until all remaining components are
qualified. The generated configuration explicitly reports `complete_startup_profile:
false` and lists unresolved blocks. Generated files use exclusive creation so earlier
evidence is not overwritten.

The front active mode is RGGB 3840x2160, output 2560x1440. The rear active mode
is GRBG 4064x2286, output 3840x2160. Mode facts were read from the SP11 Linux
media graph. Output storage sizes and metering examples are calculated, not copied
from a startup input. The geometry still needs hardware scaler/crop validation.

Provenance:

- NV12 geometry: even extents, one luma byte per pixel and one interleaved
  chroma byte per luma pixel for each pair of rows, calculated with aligned strides.
- BT.601 full-range conversion: Kr=.299 and Kb=.114; exact rational generation,
  Q10 quantisation with neutral-preserving residual assigned to green.
- Gamma: linear endpoints or standard sRGB transfer function, not a fitted vendor
  curve. Native base/delta data packing follows the project's independently tested
  `native-front-gamma.h`; this module assigns no DMI selector or address.
- CCM: Q7 identity; front field ordering follows the earlier independently tested
  coefficient adapter. Rear packing remains a separate hardware gate.
- LSC: unity Q10 mesh, never a proprietary shading grid. This provides no calibrated
  lens-shading correction. The paired field representation follows the earlier
  own-measured front LSC work, with no DMI selector or bank binding.

The generator's data can be used to develop typed adapters. It must never be
fed to the existing SHA-pinned private input loaders. See
`docs/UPSTREAM-ROADMAP-20261011.md` for the full sequence and hardware gates.
