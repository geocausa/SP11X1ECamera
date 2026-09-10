# E003i-DX — generation-tagged parent CQ gain feed

Status: **PASS (offline IPC + preserved DT replay; no camera runtime).**

DX joins the already-live native AEC/CQ parent with DW's residual-ISP-aware IQ producer without duplicating AEC state.

The helper creates a dedicated pipe before the producer fork. After each successful native AEC result and successful DB schedule queue for G1..G3, the audit thread publishes exactly one 24-byte little-endian record:

`{magic='IGF1', version=1, bytes=24, generation, logical_request, isp_gain_float_bits, reserved=0}`

The record enforces `request == generation + 3`, so G1/G2/G3 map to request4/5/6. The Python producer consumes records strictly in generation order and rejects bad magic/version/size, wrong generation/request, EOF, non-positive/invalid float, or a bounded wait timeout. It never substitutes a default gain in live mode.

Only the producer receives the pipe read end. Only the parent audit path retains the write end. SIGPIPE is ignored at process level so a dead producer becomes a handled `EPIPE` fail-closed error rather than killing the helper asynchronously.

The sensor-control scheduler, DQBUF release law, IMX681 clustered write, AWB hold, LSC/Tintless and capsule framing are unchanged.

No camera runtime is performed by the DX verification gate.
