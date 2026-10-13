# SP11 camera regulator constraint diagnosis — 2026-10-13

This audit reproduces the standard provider's rejection of the historical
exact2.900-V LDO16 request. It diagnoses a source-level failure consistent with
the retained E002b provider-registration failure; it is not a new boot trial.

| Camera role | Standard mapping | Nominal uV | Selector evidence |
| --- | --- | ---: | --- |
| Front IO | PM8010-M LDO3 / pmic5_pldo502ln | 1800000 | selector0 |
| Front analog | PM8550-B LDO7 / pmic5_pldo | 2800000 | selector162 |
| Rear IO | PM8010-M LDO6 / pmic5_pldo502ln | 1800000 | selector0 |
| Rear digital | PM8010-M LDO1 / pmic5_nldo502 | 1200000 | selector84 |
| Rear analog | PM8010-M LDO5 / pmic5_pldo502 | 2800000 | selector162 |
| Rear actuator VAF | PM8550-B LDO16 / pmic5_pldo | 2900000 | no exact selector; adjacent2896000/2904000 |

The PLDO table is1504000 + selector*8000 uV. Fixed min=max2900000 cannot
map to it. Both retained old and candidate voltage-admission bodies reject
that exact constraint. The old core attempts initialization before clamping
and propagates its unreadable cached voltage; the candidate clamps first
and reports unsupported constraints. The standard RPMh callback initially
caches selector requests while its enabled state is unknown. Thus the tested
voltage-registration stage sends zero modeled RPMh requests. This is not
proof that all provider registration stages (mode, parent supplies, enable,
cleanup) send no requests.

The previous blanket description of a normal-regulator boot hang was too
broad. Adding one rejected LDO16 child to Golden's existing provider made
that provider fail registration, affecting unrelated consumers. Retained
isolated-provider/no-constraint boot passed; its later set-voltage call
returned-EPERM. Max-only constraints failed core validation. Those historical
results are preserved in the E002b/r1/r2/r2a experiment notes.

Do not round2.900V to a selector or widen electrical constraints without
qualified rail/device tolerance. The +/-4000-uV test is only an arithmetic
illustration, not a proposed voltage policy. Keep VAF separate from sensor
capture supplies, as the retained E002k work already established. Front1.8/
2.8V selection is supported in source; current Denali candidate has no front
camera provider/consumer graph enabled. Physical rails, initial modes, parent
supply ownership, reset/privacy, timing and teardown remain unqualified.

## Reproduction

```sh
python3 test-constraints.py --baseline-source /path/to/retained-golden-source \
  --candidate-source /path/to/candidate23-source \
  --output /path/to/fresh-audit-output --compiler gcc
```

Repeat with clang and fresh output. reference.json pins both core/provider
sources and the candidate warning policy. The tool imports actual voltage
admission and RPMh voltage cache/set/get bodies and parses actual PMIC rail
mappings/ranges. Selector enumeration/mapping, RPMh transport and surrounding
registration stages are explicitly modeled. It reads no private firmware,
calibration, pixels or camera input.

SP11 GCC and Clang each pass48 ASAN/UBSAN cases. Eight source/pin/output
rejections preserve original files and retained sentinel data. All pinned
kernel inputs remain byte-identical. Initial host compile rejected the
imported code's signedness warning; final fixture uses the pinned kernel's
default/W=1 -Wno-sign-compare policy (W=3 enables the warning). No callback
was rewritten and no other warning was suppressed. The failed first record
is retained; ../../../../docs/UPSTREAM-REGULATOR-CONSTRAINT-VALIDATION-20261013.json
records the successful second qualification and controls.

Scope follows the upstream regulator machine-constraint interface:
https://www.kernel.org/doc/html/v6.7/driver-api/regulator.html .
Exact selector/return behavior here comes from the pinned local source,
not that generic documentation.

No kernel/DT/runtime changes, module install/load, camera capture, boot,
system-sleep test or hardware-qualification claim. Golden remains protected.
NEXT prepare isolated standard front provider/consumer topology, verify supply
parents/modes and bindings, compatible full build, fresh provider-only boot,
then the complete sensor graph and guarded RAW stop/reopen/VT timing.
Both private startup consumers and all14 upstream readiness categories remain.
