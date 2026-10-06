# E011KC — native function vector +0xC0 through CFG check frontier

PASS. A bounded same-boot Windows front-camera oracle resolves the seven function-vector slots at object RVA `0x17A70D0` as image RVAs `0x5BA750, 0x5BA6B0, 0x5BA880, 0x5FDB90, 0x5BA820, 0x5BCC00, 0x5BA850`; the vector is identical before and after a successful `NV12 1920x1080` reader Start. This explicitly separates E011JJ's accepted cold zero-selector model from the successful native front context.

Source-exact replay executes `0x5B8274` and resolves object `+0xC0` to RVA `0x5BA820`, forms `x0=caller SP+0x60`, and executes the `GuardCFCheckFunctionPointer` check through cell RVA `0xF7E7B8` (target RVA `0x1A8C0`). It stops before `0x5B828C -> 0x5BA820`. One bounded front Start and one one-shot Windows reboot were used; rear runtime remains denied, and the machine is back on Golden Linux.

NEXT E011KD executes `0x5BA820`, qualifies its descriptor output and zero return, and stops at `0x5B8290`.
