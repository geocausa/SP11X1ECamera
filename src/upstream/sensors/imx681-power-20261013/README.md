# Retained SP11 IMX681 power sequence port

Sensor-only candidate25 on the pinned candidate24 FLL package. E003b and the
working native driver already prove the hardware sequence: asserted active-low
reset, MCLK4 19.2MHz, LDO3_M IO 1.8V, LDO7_B analog 2.8V, 1ms delay, reset
release, 10ms delay. Shutdown asserts reset, waits1ms, stops MCLK, releases
analog then IO. Their source/evidence pins are in manifest.json. E003b reports
ID0x0aff at its historical register; this port preserves the imported driver's
0x0016/0x0681 identity check and its distinct2.406 profile.

The patch replaces bulk enables with explicit ordering and owned-reference
tracking. Failed analog release retains IO; failed releases retain their
reference and fault state. Power-on cannot acquire duplicate references.
CCI entry points reject incomplete power; control/start guards balance their
new PM reference. Probe preserves its primary error and logs cleanup errors.
Remove reports a power-off fault and does not mark runtime PM suspended.
These flags describe Linux API ownership, not electrical measurements after
a failed transport operation. Unbind/probe failure cannot promise recovery
from an unresponsive provider; reset remains asserted and the fault is logged.

Mode tables, FLL/control payloads, endpoint admission and clock-rate checks
are preserved. Functional reconstruction is reused; proprietary inputs are
excluded. No new discovery of the known sequence or separate provider boot
is required by this package. The standard full7.2 graph still needs integration
and a bounded test of this changed implementation, followed by RAW stop/reopen
and imported-profile timing. Existing native timing/calibration remains valid
for its original profile. No firmware, installed modules, boot settings,
captures or system-sleep operations are changed here.

Reproduce (use fresh output paths):

```sh
python3 prepare.py --parent-source /path/to/candidate-24/source --output /path/to/fresh-source
python3 test-power.py --parent-source /path/to/candidate-24/source --source /path/to/fresh-source --output /path/to/fresh-tests
```

Hosted tests compile actual source functions with GCC/Clang ASAN/UBSAN and
fault models for clock/regulator/CCI/PM APIs. They check the retained order,
all acquisition/release faults, cleanup retry, transaction guards, PM balance
and remove/probe error reporting. Six mutated regressions must be rejected.
API/transport responses and register tables in the hosted fixture are modeled;
this is source qualification, not a new hardware result.
