# E003i-FX — Windows AWB selector internals oracle

Status: **staged / unarmed / no FX stream yet.**

FX is a targeted one-stream diagnostic oracle for the remaining CSFStatDistV1 reconstruction gap exposed by FW. It pins the selector call site at DeviceMFT RVA 0x6c4234. On the first selector call only, CDB records the live ratio register/region and dumps 0x240 bytes of the configured selector object from x20, then immediately clears breakpoints and detaches.

The object dump includes the boundary/search-line records used by Windows. This avoids fitting request-specific AWB behavior and lets the clean selector be corrected from exact Windows float coefficients.

The holder uses exactly one StartAsync and one StopAsync and requires explicit START.GO after debugger attachment. Windows is entered via one-shot UEFI BootNext; Golden GRUB remains persistent.
