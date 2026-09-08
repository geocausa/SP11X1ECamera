# Static / composition proof

Required committed ancestry:

- BX `7bb370f`: optional SafeAgg candidate zero state and six-active reduction;
- BY `11ededf`: bit-exact native method-11 point aggregation;
- BZ `5258e86`: `SafeAdjRatio 3:9 = SafeTarget 3:8`;
- CC `e6d9e55`: bit-exact native ADRC/DarkBoost tail;
- CD `64572b7`: effective shared Safe weight is exact absolute `0.001f`.

CE does not reproduce those primitives. It fixes their Windows ordering and composes them behind one integration-facing API.

Safe method-11 point order is exactly:

`Frame -> SatPrev -> DarkPrev -> Brighten -> ExtremeColor -> Illuminance`.

Short and Long each put the shared Safe point first, followed by their dedicated preview point, matching the serialized tuning order.

The verifier uses an independent numpy float32 instruction-order model rather than calling BY/CC as its oracle. Native compilation includes all three C sources with `-fno-fast-math -ffp-contract=off`.

The known BY single-point weighted-mean trap remains `0x4344a49c`, proving that composition has not replaced method-11 with a weighted-average shortcut.
