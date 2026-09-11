# E003i-FY — OTP-calibrated AWB selector replay

Status: **PASS — Windows selector object bit-exact and all known Windows AWB oracles replayed bit-exact through R21.**

FY supersedes FB for production use while preserving FB unchanged as historical evidence.

FX showed that the configured Windows `CSFStatDistV1` geometry is not built from the raw `refPtV1` coordinates. Windows first multiplies each reference point by the same-device **stored** `ComputeCalFactors` pair for that slot group, then constructs the boundary/search geometry. Those stored factors are reconstructed cleanly by EJ from shipped tuning plus the same 12 physical OTP bytes read natively by EK.

The three groups are:

- slots 0..3: RG `0x3f7ebcac`, BG `0x3f79a47c`
- slots 4..6: RG `0x3f7f2038`, BG `0x3f7a40d6`
- slots 7..9: RG `0x3f7f66ed`, BG `0x3f7b3bff`

After that pre-transform, FY reproduces the FX first-call Windows selector object exactly: 8/8 boundary lines, 8/8 search lines, and 8/8 boundary lengths at the float32 bit level.

The corrected selector then replays every available Windows AWB authority without request-specific fitting: EG 8/8, FA 9/9, FH 15/15, and FW 18/18 through R21.

FY adds no camera stream and performs no Linux camera runtime. Its inputs are the closed EJ/EK clean calibration chain plus the sealed FX object hash.
