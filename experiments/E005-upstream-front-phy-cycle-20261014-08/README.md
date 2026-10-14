# Fresh08: owned PHY parent reference release
Three generic PHY C-PHY on/off cycles using the unchanged fresh07 diagnostic.
Only source31 PHY module differs; CAMSS30, sensor25/domain29, kernel26,
initrd and the physical 1-trio/2.406Gsymbol/s profile remain identical.

Fresh07 configured and powered on, then returned -EBUSY at first power-off.
It quarantined its references and auto-returned to Golden; retired, never retry.
Source31 drops only its own parent runtime-PM usage reference with put_noidle.
The generic core retains its active child through this callback and performs
the final child put afterward. Source/model/build evidence in
docs/UPSTREAM-PHY-PARENT-REFERENCE-20261014.json; prior fault in
docs/UPSTREAM-PHY-CYCLE07-20261014.json.

Require 3 complete cycles, provider suspended, unchanged PHY rail/clock users,
sensor suspended/reset-low/MCLK-off, warning-free complete unload and return.
No sensor/CAMSS stream, QBUF, DMA image buffer, pixels or OS sleep.
Faults pin diagnostic/provider ownership until automatic reboot; no retry.
Golden default/assets/global modules/daily branch protected.
