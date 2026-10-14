# Fresh05 sensor-owned runtime domain teardown

One DT property change from qualified source29. Same kernel26, module28,
sensor sequencing and CAMSS-first unload order as prior02/03/04. No buffers,
QBUF, STREAMON, pixels, firmware changes or OS sleep. Confirm live sensor/CCI1
TOP domain equality and genpd membership, suspended sensor/rails/MCLK/reset,
then require full post-unload kernel log PASS before observer success.

Reuse pinned existing kernel/initrd and immutable retired04 module tree to
avoid duplicate assets under tight storage. This reuses build artifacts only;
05 is a fresh one-use boot/recovery identity. No retired identity is rearmed.
Golden/default/global installed modules remain protected. Retained watchdog
180s and ExecStopPost return; source and asset pins before arming.
