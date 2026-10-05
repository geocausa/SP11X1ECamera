# E011GN — selected CAB1F0 case to CACDF8 helper-call frontier

Four source-exact placements execute only the selected helper case prefix at `0xCAB1F0`. The instruction selects the exact retained receiver in `x0`; execution stops at `0xCAB1F4` before helper `0xCACDF8` is called. The retained parser source pointer remains `0x1370762` and parser state remains `7`.

Private source inspection of `0xCACDF8` shows its first owned receiver dependency is the pointer at receiver `+0x18`, followed by an alignment/update and then an 8-byte dereference at `0xCACE28`. E011GO source-qualifies that retained pointer from the accepted E011GA receiver setup and executes only through the pointer update, stopping before the dereference.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
