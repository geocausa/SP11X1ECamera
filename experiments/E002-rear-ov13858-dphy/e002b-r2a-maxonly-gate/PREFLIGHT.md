# E002b-r2a preflight — max-only regulator permission gate

Purpose: permit later consumer voltage requests without registration-time voltage application.

This candidate is accepted E002b-r1 plus exactly four DT properties on the isolated camera-only regulators:

- LDO6_M: `regulator-max-microvolt = <1800000>`;
- LDO1_M: `regulator-max-microvolt = <1200000>`;
- LDO5_M: `regulator-max-microvolt = <2800000>`;
- LDO16_B: `regulator-max-microvolt = <2900000>`.

There are no `regulator-min-microvolt` properties. Therefore OF parsing yields min=0, max>0: `REGULATOR_CHANGE_VOLTAGE` is allowed because min != max, while `apply_uV` remains false because both bounds are not nonzero.

No sensor node, CCI pinmux, reset GPIO, MCLK consumer or probe module exists in r2a. Kernel and initrd remain byte-for-byte FullIO v19c Golden.

Hashes:
- overlay: `140ffc78f86862743a0e75ea76409c53e3d2a07071992a5fda530658263b913b`
- merged DTB: `6d9d42a2c60dd2de19cf45e415c4268d4d28f34cb2eb8ddd9182440cafdb6f42`
- Golden -> r2a normalized diff: 0 removed Golden lines.

PASS requires Wi-Fi + playback + capture + CAMSS intact, all regulator providers bound, all four camera rails still 0 users/0 mV, and no regulator registration errors.
