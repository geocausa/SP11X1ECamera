# Open ISP configuration primitives

These are source-only replacement slices for the SP11 RGB ISP startup
dependencies: mathematical primitives and a typed, kernel-usable C field compiler. It is not a complete startup profile, a public ABI, or a camera
application. It reads no firmware or calibration files and does not access hardware.

Run from the checkout root:

```sh
python3 src/upstream/isp-config/test_open_config.py
python3 src/upstream/isp-config/test_gamma_compat.py
python3 src/upstream/isp-config/test_front_fields.py
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

The next C layer is described in `FRONT-FIELDS-PROVENANCE-20261011.md`.
`sp11-cdm.h` bounds the serialization and a declared DMA window; the kernel
provider must still prove ownership and lifetime. `sp11-front-fields.h` generates
only the verified CST/CCM coefficient and FULL rounding fields, without loading
or patching a private carrier. CCM has the narrower signed-12-bit numerical
policy; CST allows the signed-13-bit range. Both use 13-bit packed fields.

To compare against the exact public reference, obtain the GPL tree/revision in
`cdm-reference-20261011.json` and supply its source path explicitly:

```sh
python3 src/upstream/isp-config/test_cdm_compat.py --source "$SP11_OPEN_CDM_REFERENCE"
python3 src/upstream/isp-config/inventory_front_fields.py docs/UPSTREAM-FRONT-REPLACEMENT-INVENTORY-20261011.json
```

The GPL reference is a test-only input. Its C file and companion header hashes
must match; they are never loaded by the production helpers. Coverage is 34
unique fields / 74 scalar occurrences, not a count of runtime dependencies removed.

The compile-only probe can be rebuilt against a prepared kernel tree. Set
`SP11_KERNEL_SOURCE` and `SP11_KERNEL_BUILD` to those directories first:

```sh
fields_stage=$(mktemp -d)
cp src/upstream/isp-config/sp11-cdm.h src/upstream/isp-config/sp11-front-fields.h src/upstream/isp-config/kernel-compile-probe/Makefile src/upstream/isp-config/kernel-compile-probe/sp11-open-fields-compile.c "$fields_stage/"
make -C "$SP11_KERNEL_SOURCE" O="$SP11_KERNEL_BUILD" M="$fields_stage" W=1 KCFLAGS=-Werror modules
```

Do not load the probe. A passing build proves kernel type compatibility only;
it neither changes camera operation nor qualifies a new startup provider.
