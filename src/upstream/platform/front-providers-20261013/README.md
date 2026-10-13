# E005 standard front provider registration — 2026-10-13

Hypothesis: the supported fixed 2.8 V LDO7_B and 1.8 V LDO3_M
constraints register through the standard RPMh driver when isolated from
Golden's existing provider objects and connected to their documented parents.
This distinguishes provider admission from later enable/mode/sequence behavior.

The public Denali board source at revision
64999b9fc6e60ebccdc3755563cafcc63930cc90 maps LDO7_B to BOB2 and
LDO3_M to SMPS4_C. Retained OLED DTS SHA256
2beacc7b5136a2f9ff90c50f4a9c3896c4cbaf3a25c48fc633501f2848cab3ea;
base DTSI afdc9d83fefba1223639c140a8de9558be59f4ddbf0991a206a52a4ed9967eca.
Our earlier E003b identity source independently used these two front rails.
The public source's HPM initial-mode votes are deliberately omitted in this
registration-only experiment; they are not qualified by this test.

The pinned old RPMh source starts each child with unknown enable state,
unrecoverable cached selector and invalid mode. Its set-voltage callback caches
an admitted selector without issuing a request while enable remains unknown.
The old regulator core's late cleanup skips non-positive is_enabled results.
The prior actual-body voltage audit qualifies admission, not hardware state:
see ../regulator-audit-20261013 and
../../../../docs/UPSTREAM-REGULATOR-CONSTRAINT-VALIDATION-20261013.json.
The boot trace must independently corroborate absence of requests for each new
resource's voltage/enable/mode addresses. No direct firmware table is exported.

prepare.py pins all three deployed Golden assets. It copies the exact Golden
DTB, adds only regulators-10/ldo7 and regulators-11/ldo3, and checks every old
node/property byte, the reservation map, boot CPU, exact new properties,
resource ownership and existing parent phandles. It introduces no sensor,
CCI, CAMSS, reset, privacy LED or clock node. No actuator/VAF rail is included.
The supported voltages follow the separately qualified standard selectors;
no voltage rounding or tolerance is invented.

test-delta.py rejects six graph/constraint mutations. The original controls
also verify that run-once.py refuses on Golden before creating any attempt
marker. Both Golden and candidate pass the retained full kernel's scoped RPMh
DT schema without diagnostics. This is not whole-board schema certification.
The first combined validation command timed out during an unnecessary broad
schema-path search after writing PASS controls; its completed evidence was
read back before proceeding. No candidate was installed by that command.

install.py requires a clean, pushed source checkpoint and Golden guard. It
creates new root-sealed assets, a fresh GRUB identity and a conditional one-use
service. It never arms/reboots, replaces Golden payloads or modifies modules.
The candidate uses byte-identical Golden 7.1.5 kernel/initrd, not the unbuilt
7.2 camera candidate23/24. Existing clk_ignore_unused/pd_ignore_unused and other
Golden command-line flags remain. Only entry/token, camera blacklist and early
RPMh tracing/dynamic debug are added.

run-once.py atomically consumes the identity before observations, verifies
boot-writer completion/order, empty next entry, Golden default and sealed
hashes; then checks the actual standard platform bindings, regulator cache,
zero users and exact parent supply symlinks. It never opens a camera node,
loads a module, enables a rail, programs a mode or writes a clock/reset/GPIO.
Raw kernel/RPMh logs remain on SP11. Debug resource addresses and scalar
trace counts are allowed evidence. Trace loss or unexpected child requests
fail closed. Absence of traced requests is scoped to kernel tracing, not an
electrical rail-off measurement or absence of bootloader/other-processor votes.

The dedicated service runs after the two existing GRUB writers and before
the display manager. Success, failure and timeout all invoke a token-guarded
return script, setting a one-shot Golden return and requesting a normal reboot.
The saved default remains Golden. If the kernel never reaches the service,
a subsequent independent reboot uses the saved Golden path. Never reuse this
identity once armed or attempted; missing replies require state reconciliation.
No OS suspend/hibernate is permitted.

Expected: both providers bind, cached voltages equal 2.8/1.8 V, users zero,
parent links point to BOB2/SMPS4_C, no child RPMh requests in complete retained
kernel trace, existing sound/network devices present, automatic Golden return.
Audio/network device registration alone does not prove functional playback or
network throughput. Sensor power order, mode votes, physical voltage, full7.2
runtime, privacy and capture remain unqualified. Later sensor graph admission
must preserve the separately measured local mode/calibration; the imported
3840x2640/2.406 profile's VT clock remains unmeasured.

Reproduce on SP11 with a fresh output path:

```sh
python3 prepare.py --out /absolute/fresh-stage
python3 test-delta.py --candidate /absolute/fresh-stage/front-providers.dtb --out /absolute/fresh-controls
# Use candidate-16/schema-venv/bin/dt-validate with its processed-schema.json,
# -l qcom,rpmh-regulator, independently on Golden and the candidate.
```

Source base f16a3c6a249e851d2736c26f31478cc5f48eee75; source checkpoint
recorded by installer EXPECTED-HEAD. Prepared candidate SHA256
 ae9e93ef6f62990b712f884bebdbf9d5f35638cfcee1c363f637c60c9f58553c.
Stage: /home/geoca/Documents/SP11-PROJECT/02-kernel/standard-front-providers-20261013-01.
Hardware identity: sp11-camera-standard-front-providers-20261013-01.
Current hardware result is pending until fresh boot evidence and Golden return
are verified. No upstream acceptance, DCO certification or submission claimed.
