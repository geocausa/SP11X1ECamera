# E004h — bounded 42-write Windows configuration authority

Status: **offline PASS target; no runtime until a separate one-shot package is checkpointed.**

E004h extends only the already-proven E004f VD55G0 prefix. It keeps the sensor in software standby and applies the final Windows configuration block **except** the illumination-coupled GPIO1 strobe selector `0x0468=0x02` isolated by E004g.

The exact Windows final sequence contains 43 writes. A clean-room sequence hash over each little-endian 16-bit register plus 8-bit value is:

- full 43: `9664529aab0c65d6f3ae9778c8c31f54fa1675bde748fdaafc8e2d2ab4ea387c`
- safe 42 after removing exactly `0x0468=0x02`: `159647774f45331210044d0680e50bf16e8aaeeb8c3e98449d2cef7adeffacb2`

The generated Windows header is extracted from the exact local Surface package and is ignored by Git.

Runtime design is intentionally self-checking:

1. revalidate model 0x3047 / revision 0x1111 CUT1 before writes;
2. replay the proven E004f 554-write Surface patch/setup/boot prefix to SW_STBY;
3. read `0x0468` before the final configuration;
4. execute exactly 42 generated Windows writes, with a hard reject if any table entry is `0x0468`;
5. read `0x0468` afterward and require it to be unchanged;
6. read back external clock/data-rate, line/frame timing, manual exposure defaults, ROI, vertical window and GPIO0..3;
7. require GPIO0/2/3 to have Windows value 1 while GPIO1 still equals its pre-write value;
8. remain in SW_STBY and power off.

A successful E004h-family attempt therefore performs **596 total sensor-data writes**: 554 proven prefix writes + 42 non-strobe final writes.

CAMSS, V4L2, streaming, `0x0468=0x02`, and external illumination remain absent.

Reference-only safety corroboration: ST documentation states VD55G0 GPIOs may be configured in software standby but are active only in streaming state. Same-machine Windows remains the parity authority.
