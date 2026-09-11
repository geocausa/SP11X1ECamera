# E003i-EK — Linux front AWB OTP read gate

Status: **offline candidate; live probe not yet executed.**

EK is CW plus one read-only probe-time diagnostic. After the already-proven IMX681 power/identity sequence and before mode programming/streaming, it uses the same CCI1 master1 `i2c_adapter` to perform the shipped EEPROM memory-map transaction for `gt24p128f_imx681`: 7-bit slave `0x50`, 16-bit offset `0x0941`, then a 12-byte read. The two-byte pointer phase is address selection only; no EEPROM payload byte is written.

Acceptance is deliberately narrow: the I2C transfer must complete both messages, the kernel must log exactly 12 bytes, no STREAMON occurs, and those bytes must equal EI's same-device Windows oracle `56 03 71 01 ff 03 5d 02 4d 02 fc 03` / SHA256 `e09038cb54497e6309cd1e213d0e0a5f02e1c460ffa9a4ee9ef00ecc326ed7e1`. A mismatch is evidence, not something to normalize away.
