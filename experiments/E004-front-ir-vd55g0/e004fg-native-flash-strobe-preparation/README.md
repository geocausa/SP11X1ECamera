# E004fg: prepare native external flash strobe

**PASS offline; no emitter activation or driver installation.**

E004ff found that qcom-flash's external-trigger callback only enables the module
and channels. Brightness and timeout callbacks cache requests. V4L2's transition
to FLASH first switches torch off, whose callback selects torch current and
clears the timeout. External arming can therefore inherit unsuitable settings.

The patch shares the existing software-strobe preparation with external strobe:
disarm channels, obtain the allowed current, program flash current and timeout,
then enable the module and the selected trigger. Disabling also releases the
current reservation through the same existing path. It changes generic upstream
code, contains no Surface-specific policy, and leaves the kernel source anchor
and installed module tree untouched.

## Validation

- Patch reapplies byte-exactly to the hash-pinned original source.
- Isolated module compiles against the prepared Golden build with `W=1`.
- Strict checkpatch: zero errors, warnings or checks, with signoff checking
  disabled because this development patch has not been submitted.
- The test extracts the actual C callbacks, including brightness and timeout,
  and compiles them against hardware-state stubs. The baseline reproduces an
  external-arm preparation failure. The patch passes 16 cases both normally and
  with address/undefined-behaviour sanitizers: software/external enable/disable,
  capped current, timeout preparation, six injected helper failures per trigger,
  and preparation of a subsequent request after stale torch state.

The model asserts state at arming; it does not simulate registers or validate
hardware-helper internals. Existing helper failure cleanup and errors while
disabling remain separate work. Test current/timeout values are synthetic inputs,
not authorization or configuration for the SP11 emitter. Checkpatch's boilerplate
'ready for submission' message is a style result, not physical validation or
maintainer acceptance.

## Reproduce

From the camera repository, set `K` to the recorded kernel source anchor and
`E` to this experiment directory. In a disposable directory, copy
`$K/drivers/leds/flash/leds-qcom-flash.c` to that same relative path and apply
`src/front-ir-vd55g0/illumination/0001-qcom-flash-prepare-external-strobe.patch`
using `git apply`. Copy the patched file into `$E/build/source`, then run:

```sh
python3 "$E/test_strobe_contract.py" \
  --baseline "$K/drivers/leds/flash/leds-qcom-flash.c" \
  --patched "$E/build/source/leds-qcom-flash.c" \
  --output "$E/evidence/CONTRACT.json"
```

The module Makefile is `obj-m += leds-qcom-flash.o`. Build with
`make -C "$K" O=/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826 M="$E/build/source" W=1 modules -j4`.
`RESULT.json` records exact source, config, patch, module and test hashes.

## Machine state and next gate

SP11 remains on Golden FullIO v19c, boot
`ad301aa8-ce0f-49c9-9ba9-5e254a8aea50`, with no camera nodes/modules or active
camera processes and no pending GRUB candidate. This boot differs from the
post-E004fe Golden return. The previous journal ends without a recorded shutdown
reason; pstore is empty. Its cause is unknown, not attributed to a camera test.

The physical emitter channel, pulse width/duty cycle and effective safety timeout
still need same-machine evidence before an illumination candidate is prepared.
No protected SecureISP runtime is enabled. No upstream message has been sent.
