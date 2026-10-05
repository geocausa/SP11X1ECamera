# E011GL — CAB178 helper entry to CAB724 signed-read frontier

Four source-exact placements execute helper `0xCAB178` under the accepted E011FZ opaque-cookie axes. The helper frame/prologue and cookie producer execute, receiver ownership is retained, and the signed byte read at receiver `+0x39` is exactly `0x73`, yielding range index `50`. The range branch is not taken and the dispatch base is `0xCAB65C`.

Execution stops at `0xCAB1C4` before the signed 4-byte dispatch-table read. The selected table element is therefore RVA `0xCAB724`; its exact signed value and selected target remain intentionally unclaimed until E011GM source-qualifies that entry and executes the original dispatch calculation only to the selected-case frontier. The retained parser source pointer remains `0x1370762` and parser state remains `7`.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
