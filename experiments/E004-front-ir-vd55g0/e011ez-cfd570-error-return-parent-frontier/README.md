# E011EZ: CFD570 error return to parent frontier

Status: **PASS_CFD570_ERROR_RETURN_TO_PARENT_FRONTIER**.

E011EZ resumes E011EY at `0xCFD704`. Original source branches to `0xCFD5DC`, calls original `0xCAECF8`, performs a third original Windows `FlsGetValue2` lookup of the same source-qualified 968-byte thread owner, returns the current thread CRT-error pointer (`thread+0x20`), loads CRT error `2`, and completes the original `CFD570` epilogue. All four retained placement/slot cases arrive at parent `0xCFD518` with return value `2`, the current 76-byte UTF-16 owner byte-exact and still live, and no parent cleanup executed. Four current-path cases reject 1,020 altered contracts; the inherited producer rejects 264 invalid API requests.

E011CW's older 74-byte release geometry remains excluded. No new camera Start, reboot, kernel build, production change, or rear runtime is used.

NEXT **E011FA** qualifies the parent ownership flag and exact 76-byte cleanup pointer before allowing the `0xCFD528 -> 0xCB1650` release path.
