# E011HD — CA9840 helper-return branch to RVA 0x1370762 byte frontier

Four exact placements execute `0xCA9840..0xCA9848` with accepted helper return `w0=1`. The zero branch at `0xCA9844` is not taken and the receiver source pointer reload at `0xCA9848` selects image RVA `0x1370762`.

Execution stops before the signed byte read at `0xCA984C`. E011HE separately source-qualifies that byte, executes only the read/pointer/receiver-byte update and immediate branch, and stops before the selected target executes.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
