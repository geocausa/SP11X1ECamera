# E003i-FG — R13–R15 continuation authority audit

Status: **PASS OFFLINE COMPOSABILITY / CONTENT AUTHORITY STILL OPEN.**

FG uses only the immutable FF attempt1 archive. It extends FD's existing composer offline across the unused FF continuation inputs G10/G11/G12, mapping them to R13/R14/R15. No camera module is loaded and no camera stream is possible through the probe CLI.

What FG proves:

- the extended offline producer reproduces live FF R5–R12 capsules 8/8 byte-exact
- R13/R14/R15 each compose as valid 41088-byte capsules
- R13/R14/R15 are deterministic across two independent offline runs
- GTM remains on EB's stable post-R6 output law in this trace

What FG also proves is important: post-R12 IQ is **not steady**. AWB registers continue changing request-to-request, and Tintless/LSC/GIC payloads continue changing through R15. Therefore the project must not justify R13+ live parity by simply reusing or freezing R12 content.

Windows-backed AWB/LSC content authority still ends at R12. FG deliberately marks R13–R15 as composable but not yet differential-authorized. No R13+ Linux live candidate should be created until that authority gap is closed.
