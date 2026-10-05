# E011GM — helper signed -6 dispatch to CAB1F0 case frontier

The E011GL range index `50` selects the signed 4-byte helper dispatch entry at RVA `0xCAB724`. Exact source qualification gives `-6`. Four source-exact placements execute the original dispatch read and target calculation from `0xCAB1C4` through the branch at `0xCAB1D0`, producing exact selected target `0xCAB1F0`; the selected case itself is not executed.

The selected case source begins by selecting the retained receiver for helper call `0xCACDF8` at `0xCAB1F4`. E011GN executes only that case prefix and stops before the helper call. The retained parser source pointer remains `0x1370762` and parser state remains `7`.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
