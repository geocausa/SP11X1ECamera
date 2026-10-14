# Sensor-owned TITAN_TOP runtime domain — source29

One DT property gives IMX681 its own claim on the existing shared camera
domain through generic I2C/genpd attachment. Reuses retained CCI1 domain
definition and standard framework ownership. No MCLK source/halt workaround,
manual MMIO, sensor power-sequence or kernel-module change.

Audited before implementation: AUDIT.json. The old sensor relies on other
consumers keeping TOP powered; CAMSS removes its domain link before driver
core runtime-resumes the sensor for removal. Actual old02/03/04 logs show
MCLK branch stuck-off and clk_enable -EBUSY. New property remains a source
fix hypothesis until fresh hardware teardown passes.

Scoped ARM64 DTB build PASS, kernel26 config unchanged; decoded tree differs
only by sensor power-domains. Supplier cells equal retained CCI1 TOP domain.
Exact patch replay and missing/wrong-domain/wrong-provider controls PASS.
All102 parent pins preserved. Sensor binding/schema review still pending.

prepare.py [FRESH_DIRECTORY] detaches the changed hardlink, applies pinned
patch with zero fuzz/offset. Default qualification identity is occupied and
refused. build-worker.py [FRESH_DIRECTORY] builds only the DTB and compares
decoded trees. Neither tool installs or arms hardware.

Hardware uses unchanged kernel26/module28, a fresh recovery identity and
same CAMSS-first unload order that showed the warning; no allocation/capture
repeat. Confirm live DT/domain membership and post-unload logs. PHY hidden
release errors and physical streaming remain separate qualifications.
