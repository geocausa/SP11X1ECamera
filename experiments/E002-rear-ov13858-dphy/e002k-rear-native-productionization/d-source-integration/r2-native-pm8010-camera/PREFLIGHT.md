# E002k-D-R2 — native PM8010 camera integration

Status: PREPARED / NOT YET BOOTED

## Question

Can the already-accepted E002k-C rear camera path operate unchanged when its temporary camera-specific RPMh provider is replaced by the kernel's native PM8010-M provider accepted in D-R1?

## Single architectural change

Starting from the exact accepted E002k-C DT:

- add native `qcom,pm8010-rpmh-regulators` PMIC ID `m`;
- expose LDO1/LDO5/LDO6 with the R1-accepted parent topology;
- retarget sensor `dvdd` -> LDO1, `avdd` -> LDO5, `dovdd` -> LDO6;
- remove the entire `microsoft,sp11-camera-rpmh-regulators` node and its stale symbols.

The accepted E002k-C `ov13858.ko` is byte-identical. The initrd differs only in provider handling: it no longer contains or loads the custom provider module and instead waits up to 5 seconds for built-in `regulators-8` before loading the unchanged sensor/V4L2 modules.

## Reproducibility

- kernel SHA-256: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`
- initrd SHA-256: `ead0535023220b7e4761acbb8ed43386d759e0801febd2e61bf41080f9f828f7`
- DTB SHA-256: `c91d65eb85e70d6d999aaee16a9695f382a2cac7e78d95607111f0e23e8ced52`
- unchanged accepted OV13858 module SHA-256: `4fce94b28b2c38825433cc18971eea396745695b0ed21f6d87e59e502a700a0a`
- independent initrd A/B builds: byte-identical
- independent DTB A/B builds: byte-identical
- DTC warning count: 30 -> 30
- custom regulator compatible absent from candidate DTB

## Runtime acceptance

R2 must reproduce accepted E002k-C behavior:

1. native PM8010 provider bound before sensor module;
2. OV13858 native identity/profile bind succeeds;
3. zero custom RPMh provider module/device;
4. internal test-pattern frame SHA-256 exactly `6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`;
5. test pattern disabled and 16 normal full frames stream with sequences 0..15 near 30 fps;
6. clean sensor/clock/regulator teardown;
7. Wi-Fi/audio remain healthy;
8. Golden remains saved GRUB default.
