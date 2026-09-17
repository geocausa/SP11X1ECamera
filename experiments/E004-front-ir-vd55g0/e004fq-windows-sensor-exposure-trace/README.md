# E004fq — bounded Windows VD55G0 exposure/strobe write trace

Status: **PREPARED / NOT YET CONSUMED**.

E004fp closed the live PMIC register-level flash trigger configuration. The remaining pre-emitter question is the sensor-side exposure/strobe envelope used during a normal Windows IR preview.

This experiment is read-only observation. It does not change exposure, gain, flash current, protected properties, firmware, PMIC state, sensor registers, or Linux illumination.

## Static authority

The exact Surface VD55G0 package is SHA256 `e574db7eb28231d3fa4f5eee5c1861919125d8ec7a753fc7a0708606e1f1a794`. Its first-start configuration programs:

- `0x044c = 0x02` (manual exposure mode under ST's public register naming),
- `0x044d = 0x00` (unity analogue gain code),
- `0x044e..0x044f = 100` coarse-exposure lines,
- `0x0468 = 0x02` (GPIO1 strobe mode),
- `0x046d = 0`, `0x046e = 0` (zero strobe-edge shifts).

The package's sensor-driver header carries the coarse-integration register address `0x044e`; its optional `strobeStartAddr` and `strobeWidthAddr` leaves are empty. This is consistent with using the VD55G0's own strobe GPIO envelope rather than programming an independent strobe-width register.

ST UM2829 Rev 2, section 18, describes `STROBE_MODE` as the integration-time envelope and states that `STROBE_START_DELAY` / `STROBE_END_DELAY` shift its two edges in signed line units. Therefore the Surface zero-delay configuration makes GPIO1 follow the sensor integration envelope, subject to the actual exposure selected for each frame. Public ST material is semantics/reference authority; same-machine Windows remains parity authority.

The exact installed `surfacecamauxsensor8380.sys` is SHA256 `e5b6b064f39cf239ab07e22ca2434e3c08c93b691dc7d27cebb90861226efa75`. E004d proved `SubmitSeqCmd` builds an 8-byte internal write element, loads its register into `w0` and data into `w1`, then calls register-write helper RVA `0xa350`. E004fq uses that exact helper only as an observer.

## Live contract

One fresh Windows boot only. On SP7 KD:

1. resolve the fresh `surfacecamauxsensor8380` module base;
2. run the generated dry validation while idle and remain broken;
3. arm one breakpoint at `base + 0xa350`;
4. auto-resume every hit and print only writes in these bounded groups:
   - `0x0200..0x0202` lifecycle;
   - `0x044c..0x0451` exposure/gain;
   - `0x0458..0x0459` frame length;
   - `0x0467..0x046e` GPIO/strobe controls;
5. run one normal `Surface IR Camera Front` preview, maximum 12 acquired frames / five seconds;
6. no control SETs and no saved images;
7. break once after capture, remove the breakpoint, verify an empty breakpoint list, and resume;
8. reboot normally back to protected Golden and verify saved default, empty one-shot state and no camera activity.

The observer caps matching events at 128. A command/parser error aborts the capture. No same-boot stream retry.

## What constitutes useful evidence

A changed write to `0x044e/0x044f` during the preview establishes the Windows-requested coarse exposure value for that frame path. If Windows leaves the InitialConfig value at 100 lines, that is also useful but must be stated only within the bounded capture. Frame arrival plus successful teardown is supporting execution evidence; it is not an electrical measurement of light output.

E004fp already showed no PMIC timer-register access in its bounded 12-frame preview. E004fq does not reinterpret that absence as global proof. Native Linux illumination remains disabled until this sensor-side observation is closed and the resulting bounded activation contract is reviewed.
