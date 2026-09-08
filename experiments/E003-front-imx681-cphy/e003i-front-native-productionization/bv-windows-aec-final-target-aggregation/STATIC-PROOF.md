# BV static proof

Pinned evidence:

- DLL SHA-256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`
- tuning SHA-256 `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`

The analyzer-array record is tuning entry 3592, 52 records x `0x8c`. `verify-bv.py` parses the default sequence and the three aggregate records directly.

Each analyzer record points to an arithmetic-operator array. Every operator is `0xd0` bytes. Its output descriptor is the final six words; the verifier requires an enabled bank-3 output to each SI data ID used by the aggregate calculators. This mechanically joins calculator input IDs to their producers.

For the final three analyzers the same arithmetic arrays prove:

- SafeAggSA -> bank 3 data 9;
- ShortAggSA -> bank 3 data 11;
- LongAggSA -> bank 3 data 13.

The target component fields independently require method 11 and target publication IDs 8/10/12.

The DLL method-11 proof uses the signed 13-entry jump table rooted at `0x1803f0c94`, with dispatch base `0x1803f07a8`; entry 11 resolves to `0x1803f0978`. The method-11 body has the positive-weight filter, boundary vector construction, constants 0/256, sort helper, weighted interval scan and duplicated final scalar store at `0x1803f0b74`.

BD is fresh-run to retain the exact S1 SI arithmetic and result exposure-type mapping. BF is fresh-run to retain the metering-target -> convergence -> T681 join. BU is fresh-run to retain the narrowed native ordinary-preview convergence consumer.
