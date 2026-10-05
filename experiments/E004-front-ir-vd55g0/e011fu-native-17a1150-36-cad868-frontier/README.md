# E011FU: native `0x17A1150=36` read to `0xCAD868` frontier

Status: **PASS_NATIVE_17A1150_36_READ_TO_CAD868_FRONTIER**.

E011FU resolves the writable runtime cell at RVA `0x17A1150` with a bounded SP7 KDNET process-context measurement on the front-camera Windows oracle. The 8-byte value is `36` (`0x24`) both after front initialization/before reader Start and again in the same process/module context after a successful front NV12 1920x1080 reader Start. This rejects the older E011DY loader-model zero as native runtime authority; no exact native `0x6BD8C` instruction breakpoint is claimed.

That native value is then joined into the source-exact four-case replay. The original `0x6BD8C` 8-byte load executes and produces `x0=36`; the inherited formatter tuple remains exact at untouched `0x6BD90`, where execution stops before the call to `0xCAD868`. Across four placements, 2,356 altered current-path contracts plus the inherited 264 producer-API mutations are rejected.

This checkpoint used one front-camera Start and one controlled Windows-oracle round trip, returned to verified Golden Linux, and used no rear Start or kernel build. NEXT **E011FV** enters `0xCAD868` only under this exact qualified call contract. Native rear runtime remains denied.
