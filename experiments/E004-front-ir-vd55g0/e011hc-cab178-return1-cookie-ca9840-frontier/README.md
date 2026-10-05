# E011HC — CAB178 return 1 through cookie check to CA9840 frontier

Four opaque-cookie axes execute `0xCAB62C`, setting helper return value `1`, then run the original `0x11F0` cookie checker using the accepted E011GL/E011FZ frame contract. All axes take the successful comparison path; the failure target is never executed. The saved `CAB178` frame is restored and original `0xCAB658` returns to `0xCA9840` with `w0=1`.

Execution stops before `0xCA9840`. E011HD qualifies the caller branch and retained source pointer reload, stopping before `0xCA984C` reads the unqualified byte at RVA `0x1370762`.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
