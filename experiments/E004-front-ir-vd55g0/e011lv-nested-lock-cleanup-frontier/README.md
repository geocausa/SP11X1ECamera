# E011LV — nested lock cleanup

PASS. The caller local at `SP+0x78` resolves to the accepted nested lock object RVA `0x1623598`; its vtable slot `+0x10` resolves to method RVA `0x1DF90`. The guarded cleanup path executes its `LeaveCriticalSection` import against resource RVA `0x16235A0`, returns zero, and resumes at `0x5B903C`.

NEXT E011LW closes the `0x5B80A8` epilogue and returns to the original caller at `0x5DE844`.
