# E004dr — fresh rear RGB regression retry after E004dq verifier bug

Status: **PREPARED OFFLINE / NOT INSTALLED / NOT ARMED**.

E004dq's camera runtime behavior completed successfully, but that one-shot is formally failed and retired because its post-runtime verifier attempted a normal-user read of a CAMSS module parameter declared `0400` and raised `PermissionError`. No same-boot retry occurred.

E004dr is a fresh candidate. It preserves E004dq's three-camera DTB, exact-lineage IR-gated CAMSS module, sensor modules, rear route/configuration, color-bar capture, eight-frame normal capture, nonstream requirements for front/IR, and no-retry policy.

The sole runtime-code correction is in `verify-live.py`: the root-only `e004j_ir_dphy_windows_parity` parameter is read using `sudo -n cat` instead of `Path.read_text()`. The rear camera runtime script itself is otherwise byte-equivalent after substituting the experiment path.

Acceptance remains: exact rear color bar `6987a736...`, sequences 0..7 at ~30 fps, final neutral route, all three sensors suspended before/after, no CSIPHY0 parity-selection marker, no front stream, no IR stream, no receiver harness, no illumination, no Linux SecureISP, clean kernel, Golden return and retirement.

## Attempt 1 — PASS and retired

Fresh candidate boot `0c4bf47c-0dcf-4ff5-bde9-6e5c039189fe` passed the rear-only regression. The OV13858 color bar remained byte-exact (`6987a736...`), the normal stream produced sequences 0..7 at ~30.12 fps, routing returned to neutral, and rear/front/IR were suspended before and after. The IR-gated CAMSS parameter was armed, but its CSIPHY0 programming marker never appeared during the CSIPHY1 rear stream, proving the gate remained out of the rear path.

No front stream, IR stream, receiver harness, illumination, Linux SecureISP action or kernel fault occurred. SP11 returned to Golden boot `5e583b57-765c-4bc2-8ff7-4285ac776be8` and the candidate was retired.

The raw pass JSON/console retains an inherited `E004dq` schema/message prefix; this is cosmetic metadata from the copied verifier. The fresh E004dr candidate identity is independently fixed by its path, prep commit `156425c`, boot ID and GRUB ID. No E004dq candidate was reused.

Next gate: independently regress the accepted front RGB production R27 path under the same three-camera DTB/CAMSS lineage while rear and IR remain unstreamed.
