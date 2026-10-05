# E011GK — CA9838 receiver argument to CAB178 helper-call frontier

Four source-exact placements execute only the selected case prefix at `0xCA9838`. The instruction moves the exact retained receiver into `x0`; execution stops at `0xCA983C` before helper `0xCAB178` is called. The retained parser source pointer remains `0x1370762`, retained byte remains `0x73`, and parser state remains `7`.

Private source inspection of helper `0xCAB178` shows it reuses the already-qualified opaque cookie producer at `0x11D0`, then reads receiver `+0x39 = 0x73`, deriving range index `50`. Its first new source dependency is the signed 4-byte helper dispatch entry at RVA `0xCAB724`, read by `0xCAB1C4`. E011GL executes the helper entry under opaque-cookie axes and stops before that read.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
