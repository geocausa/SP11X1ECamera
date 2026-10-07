# OV13858 source correction — 2026-10-07

The native builder previously copied src/sp11-camera-stack/authority/ov13858.c,
SHA-256 9c6e8f8f53d6e1c49dae957e31302a7f563ea6ad2874187cd71530aef9787622.
That is an upstream-style ACPI-powered snapshot. It does not acquire SP11
regulators/reset, power the sensor before identifying it, select the SP11
four-lane firmware profile, or provide the board runtime power callbacks.
Compilation did not establish board readiness.

The timing-01 test boot exposed this during initial binding/standby checks.
No front or IR stream started; zero critical kernel fault markers were found.
It automatically returned to Golden, whose kernel/initrd/DTB hashes were
unchanged. See NATIVE-RGB-TIMING-01-20261007.json. The consumed identity is retired.

The actual source used by the accepted SP11 kernel build was present at
02-kernel/sp11-camera-e002k-d-src/drivers/media/i2c/ov13858.c. It has the board
power sequence, runtime suspend/resume callbacks, four D-PHY lane/592.8MHz
endpoint mode selection and 4076x2806 Surface profile. It is copied byte-for-byte
into src/native-rgb/ov13858/ov13858.c, with original GPL/copyright attribution.
SHA-256: a417ba2f0e4cc8cd0c6a3f8743f6baac40e9f378eeabc0cde186c13f2f9e94e2.

The maintained builder now pins and builds this source. The historical authority
snapshot and pinned runtime ELF remain untouched for historical reproduction.
A changed build pathname can change ELF debug/path bytes; source equivalence
does not imply byte-identical ELF. Runtime acceptance of the new build is
recorded separately, never inferred from compilation.

The next timing boot uses a fresh identity 02 and this corrected build. It records
the failure phase and individual sensor binding/power states. Idle checks remain
required; no sensor power-state failure is waived.

The import was byte-identical to the recorded kernel source. Maintenance then
removed one unused local and its side-effect-free lookup so W=1/-Werror passes.
No register/control/power behavior changed. Maintained SHA-256: 734e1455a7f94edc15bd2a0ade124378c0b06f5a55751dc4ead195ef9686cad9.
