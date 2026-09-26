# E007q — rear GTM clean producer handoff

Parent Git: `e0c37ce1` (E007p clean TMC141 family-2 producer PASS).

Status: **COMPILE-ONLY PASS**.

## Goal

Bind the now-clean rear TMC141 → GTM131 producer into the existing non-submitting rear DMI materializer.

The adaptive math remains in userspace. The kernel-side checkpoint accepts exactly one request-tagged 2048-byte GTM wire payload and routes it through the already-accepted E007i → E007f → E006g path.

## End-to-end clean producer

`rear-gtm-runtime.py` composes:

1. semantic TMC141 inputs: TUNE / RUNTIME / COMMON / CTRL / FACE;
2. E007p clean TMC141 family-2 SRC/DST/COEF;
3. the accepted clean GTM backend;
4. one 2048-byte Titan680 GTM DMI payload.

Private validation against the accepted E007j rear oracle proves **15/15 GTM requests byte-exact**.

Captured Windows TMC knots are correspondence/final-oracle data only and are never producer inputs.

## Kernel handoff

`camss-e007q-rear-gtm-handoff.inc` adds one request-tagged GTM state:

- exact request id;
- explicit valid bit;
- exactly `E006G_GTM_BYTES` (2048) payload bytes.

Validation rejects:

- stale/mismatched request ids;
- missing GTM state;
- missing remaining stable-family producer.

LSC/Tintless remains bound through E007i; BFStats remains bound through E007f; the still-open stable DMI families remain explicit upstream dependencies.

## Build result — PASS

The full rear register/DMI provider chain through E007q compiled in an isolated accepted CAMSS source copy.

- private end-to-end GTM validation: 15/15 accepted E007j requests exact;
- W=1 warnings/errors: 0;
- qcom-camss.ko: 13,774,432 bytes;
- SHA-256: `cf644fa17cdd66c6d9878d49e5032b73ca34a2c6e562e3a44e6fd189156d1754`;
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- retained symbols: `e007q_rear_gtm`, `e007q_rear_validate_request`, `e007q_rear_prepare_dynamic`, `e007q_rear_fill_slot`, `e007q_rear_gtm_handoff_recipe`;
- install/load/camera/DMI/RT-CDM submission: none.

## Safety

This experiment is compile-only.

It does **not**:

- load a module;
- access a Linux camera;
- write MMIO;
- submit DMI;
- submit RT-CDM;
- authorize native rear Linux ISP runtime.

## Next

After compile PASS, perform a first-native-frame blocker audit rather than continuing to close every parity corner case indiscriminately.
