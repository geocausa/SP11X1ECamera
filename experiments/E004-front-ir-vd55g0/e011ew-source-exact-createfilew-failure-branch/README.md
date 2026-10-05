# E011EW: source-exact CreateFileW failure branch

Status: **PASS_SOURCE_EXACT_CREATEFILEW_FAILURE_TO_GETLASTERROR_FRONTIER**.

E011EW closes the exact file-open result without overstating the debugger evidence. E011EV already fixed the original `CreateFileW` arguments and 76-byte UTF-16 path. On the same bounded Windows boot, `C:\data\test\camxoverridesettings.txt` and its parent directory were absent, and an exact Win32 `CreateFileW` call with the source arguments returned `INVALID_HANDLE_VALUE` with `ERROR_PATH_NOT_FOUND` (3). The exact camera callsite breakpoint itself was **not** observed because FrameServer rehosted during MediaCapture initialization; that limitation remains explicit.

Four retained placements replay the original source using only that qualified OS result. Original `0xCFD658` takes the invalid-handle branch at `0xCFD678`, clears the claimed lowIO record active bit at `0xCFD6F0`, and stops at `0xCFD6FC` before `GetLastError`. The record lock remains held under the inherited owned lock model. 952 altered contracts reject.

The bounded Windows reference used three front-camera Starts in total; rear-camera Starts remained zero. SP11 completed the controlled Windows/Linux round trip and is back on Golden Linux. No kernel build, production-C or PM change was made.

NEXT **E011EX** qualifies the exact `GetLastError` result (authority value 3) and continues the original cleanup/error path only while ownership remains exact. Native rear runtime remains denied.
