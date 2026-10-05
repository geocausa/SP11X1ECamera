# E011FH: CED0D8 zero return to CED330 caller frontier

Status: **PASS_CED0D8_ZERO_RETURN_TO_CED330_FRONTIER**.

E011FH resumes accepted E011FG at `0xCED194`. The original source moves the retained zero result into `x0`, branches through the `0xCED110` epilogue, restores the exact saved return link `0xCED330`, executes `ret`, and lands in the `0xCED2F0` caller with `x0=0`. Stack depth moves from `-1552` to `-1488` relative to the inherited outer entry, and the caller output pointer in `x19` is exactly outer-entry `SP-1448`. The selected-object lock remains released and no selected-object or retired 76-byte-owner reads occur after release.

Four cases reject 1,568 current-path mutations plus 264 inherited thread-producer API mutations. The caller's `0xCED330` result store is deliberately not executed yet. No new camera Start, reboot, kernel build, production change, or rear runtime is used.

NEXT **E011FI** qualifies that exact zero result store and its zero branch before carrying the caller into its thread-error path.
