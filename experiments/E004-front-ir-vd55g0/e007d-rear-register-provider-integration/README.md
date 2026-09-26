# E007d — rear register-provider integration

Parent Git: `db081152` (E007c PERIOD_CFG compile PASS).

Status: **COMPILE-ONLY PASS**.

## Goal

Join the complete register-provider set into one non-submitting rear integration object.

E006m/E006j intentionally used one opaque context pointer for all callbacks. Individual concrete providers, however, each own a different semantic state type. E007d supplies the missing adapter layer rather than duplicating any producer algorithm.

## Integration model

`e007d_rear_register_state` aggregates:

- scalar/bank state;
- BPC/ABF calculated-output state;
- BFStats25 calculated-output state;
- geometry/MNDS/CST/BC/small-IQ state;
- BHist/RS and three Bayer-grid stats states;
- packet-aware PERIOD_CFG state.

Thin wrappers route the E006j steady and E006m startup callback tables to the correct sub-state.

Split producer families are merged explicitly. For example BPC/ABF bank selectors are resolved by E006z and its calculated words by E007a.

PERIOD_CFG deliberately fails closed through the old packet-blind E006m scalar callback. All integrated startup fills go through E007c's packet-aware wrapper.

## Build result — PASS

The full E006/E007 provider chain plus E007d integration compiled in an isolated accepted CAMSS source copy.

- E007d structural verifier: PASS;
- W=1 warnings/errors: 0;
- qcom-camss.ko: 13,724,400 bytes;
- SHA-256: `12d23af05b87193d407322d68d8d01f3efff52851cd32b808bacbf1fcf060e95`;
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- retained integration symbols: `e007d_rear_fill_startup`, `e007d_rear_fill_steady`, `e007d_rear_validate_register_integration`, `e007d_rear_register_integration_recipe`;
- install/load/camera/DMI/RT-CDM submission: none.

The register side is now not only 714/714 provider-complete but also **composed behind one non-submitting integration API**.

## Boundary

This checkpoint integrates **register production only**. E006g DMI payload callbacks remain a separate upstream interface because live LSC/Tintless, GTM/TMC, BF ROI/gamma and other DMI/state producers are not all complete.

No RT-CDM command is submitted and no camera path is touched.
