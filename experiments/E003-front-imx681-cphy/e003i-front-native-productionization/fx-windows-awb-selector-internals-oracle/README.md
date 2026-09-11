# E003i-FX — Windows AWB selector internals oracle

Status: **PASS / consumed — first configured selector object captured in one bounded Windows stream; Golden returned.**

FX is a targeted one-stream diagnostic oracle for the remaining CSFStatDistV1 reconstruction gap exposed by FW. It pins the selector call site at DeviceMFT RVA 0x6c4234. On the first selector call only, CDB records the live ratio register/region and dumps 0x240 bytes of the configured selector object from x20, then immediately clears breakpoints and detaches.

The object dump includes the boundary/search-line records used by Windows. This avoids fitting request-specific AWB behavior and lets the clean selector be corrected from exact Windows float coefficients.

The holder uses exactly one StartAsync and one StopAsync and requires explicit START.GO after debugger attachment. Windows is entered via one-shot UEFI BootNext; Golden GRUB remains persistent.

FX completed with one Windows stream. The first selector call reported region 3 and ratio 0.743285, dumped exactly 0x240 bytes, then CDB detached. The sealed object SHA256 is ef2d954f099ae484ad26955e89c4b0ff76e3cbdbc2bd87b3eb4d412e99a9d61a; the sealed Windows evidence ZIP SHA256 is 00bca65042dfc5199f19f6d972160d0f8e377c08bab6fce9da264265c6d6f8a4. SP11 then returned to Golden with BootNext consumed.
