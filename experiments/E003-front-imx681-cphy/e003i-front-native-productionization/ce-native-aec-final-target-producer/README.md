# E003i CE — native final AEC target producer

Status: **PASS (native/offline)**.

CE composes the already-proven native Windows method-11 primitive (BY), the corrected effective final-aggregator weights (CD), SafeAgg identity from BZ, and the native ADRC/DarkBoost tail (CC) into one ordinary/default producer API.

Inputs are the eight active analyzer scalar/confidence publications plus Lux:

- SafeAgg active order: Frame, SatPrev, DarkPrev, Brighten, ExtremeColor, Illuminance;
- Short dedicated candidate: ShortSatPrev;
- Long dedicated candidate: LongDarkPrev.

The five optional SafeAgg analyzers are not public inputs because BX proves their value/confidence slots remain exact zero in uninterrupted DefaultSequence.

CE performs:

1. method-11 over the six active Safe candidates -> `3:8 SafeTarget`;
2. exact Safe identity `3:9 SafeAdjRatio = 3:8`;
3. method-11 over `[SafeAdjRatio @ 0.001f, ShortSatPrev @ confidence]` -> `3:10 ShortTarget`;
4. method-11 over `[SafeAdjRatio @ 0.001f, LongDarkPrev @ confidence]` -> `3:12 LongTarget`;
5. CC -> ADRC cap, `3:66/67/11`, `3:157/68/69/13`.

The order of the six Safe points is intentionally fixed to the Windows tuning order because method-11 float accumulation is order-sensitive. The shared Safe weight is CD's exact absolute `0.001f`, not Frame confidence.

The verifier independently models method-11 and the CC float32 tail, then compares the compiled CE+BY+CC native implementation across 72 boundary cases and 8,192 deterministic ordinary finite cases. BY's weighted-mean 1-ULP trap remains exact through the complete composed producer.

No camera module load, stream, sensor write, MMIO, Windows boot, or reboot is used.
