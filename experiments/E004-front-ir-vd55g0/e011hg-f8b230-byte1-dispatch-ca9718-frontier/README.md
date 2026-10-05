# E011HG — F8B230 byte 1 through signed -52 dispatch to CA9718 frontier

The pinned image source separately qualifies second parser-table RVA `0xF8B230 = 1`. Four exact placements execute `0xCA95D8`, store parser state `1`, and reuse the already-qualified signed dispatch entry at `0xCA98F0 = -52`. Original `0xCA95F4..0xCA9600` selects target `0xCA9718`.

Execution stops before the selected case body. E011HH reuses E011GF's case semantics under the new receiver state and stops before `0xCA984C` reads source RVA `0x1370763`.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
