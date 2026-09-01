# E003h 0066 candidate — ordinary V4L2 two-frame bounded proof

Golden-safe one-shot candidate. Exact 0065 sensor/DT/firmware and existing hardware programming are retained. 0066 adds only software waiting/retirement for the already-prepared second slot. Runtime contract is one boot, one V4L2 helper, two DQBUFs, zero sysfs trigger invocations, then mandatory Golden reboot.
