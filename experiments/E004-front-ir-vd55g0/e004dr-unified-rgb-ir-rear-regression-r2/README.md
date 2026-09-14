# E004dr — fresh rear RGB regression retry after E004dq verifier bug

Status: **PREPARED OFFLINE / NOT INSTALLED / NOT ARMED**.

E004dq's camera runtime behavior completed successfully, but that one-shot is formally failed and retired because its post-runtime verifier attempted a normal-user read of a CAMSS module parameter declared `0400` and raised `PermissionError`. No same-boot retry occurred.

E004dr is a fresh candidate. It preserves E004dq's three-camera DTB, exact-lineage IR-gated CAMSS module, sensor modules, rear route/configuration, color-bar capture, eight-frame normal capture, nonstream requirements for front/IR, and no-retry policy.

The sole runtime-code correction is in `verify-live.py`: the root-only `e004j_ir_dphy_windows_parity` parameter is read using `sudo -n cat` instead of `Path.read_text()`. The rear camera runtime script itself is otherwise byte-equivalent after substituting the experiment path.

Acceptance remains: exact rear color bar `6987a736...`, sequences 0..7 at ~30 fps, final neutral route, all three sensors suspended before/after, no CSIPHY0 parity-selection marker, no front stream, no IR stream, no receiver harness, no illumination, no Linux SecureISP, clean kernel, Golden return and retirement.
