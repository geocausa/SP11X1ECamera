# E003i-U — corrected TL_BG ABI bounded runtime package

Status: **runtime PASS; Golden return verified**.

U changes only the userspace-visible TL_BG snapshot dimension relative to S: the corrected E003i-T module advertises a 32-byte header plus `0xF000` raw Titan680 bytes, total **`0xF020` / 61,472 bytes**. The accepted S six-frame order, R4-before-STREAMON timing, live same-fd R5/R6 submissions, front-only DT/sensor assets, one-shot boot hardening, one-invocation rule and mandatory Golden return are unchanged.

The helper requires every TL_BG header to advertise exactly `0xF000`, persists six `0xF020` snapshots, and still requires final generation 6. Offline parsing after Golden return must consume the entire raw payload with no legacy zero tail.

## Result

U passed one bounded runtime with the corrected `0xF020` snapshot ABI. All six `0xF000` raw payloads parse through stage N, have 768 populated records, are generation-unique, and contain no legacy zero tail. R4-before-STREAMON plus live same-fd R5/R6 and the accepted six-frame ordering also passed. Request-ID inference remains forbidden.
