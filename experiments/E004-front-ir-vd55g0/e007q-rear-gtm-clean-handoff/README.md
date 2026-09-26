# E007q — rear GTM clean producer handoff

Parent Git: `e0c37ce1` (E007p clean TMC141 family-2 producer PASS).

Status: **STAGED / COMPILE-ONLY**.

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
