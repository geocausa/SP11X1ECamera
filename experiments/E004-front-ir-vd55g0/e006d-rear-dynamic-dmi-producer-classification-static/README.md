# E006d — rear dynamic DMI producer classification and same-session GIC alias closure

Parent Git: `9c634951` (E006c result).

Status: **STATIC/OFFLINE PASS**. No Linux camera runtime was performed. Raw Windows source windows remain private on SP7 and are not committed.

## Why

E006c proved that two consecutive healthy rear 4K steady `0xAC8` requests contain 16 DMI payload identities, of which four vary request-to-request:

- `0x4308 selector1`, 884 bytes
- `0x4308 selector2`, 884 bytes
- `0x4708 selector1`, 512 bytes
- `0x5A08 selector1`, 2048 bytes

The question is whether these are four independent runtime producers or fewer underlying state machines.

## Exact module mapping

The already accepted Surface/Titan680 command mapping identifies:

- `0x4308` = **LSC411** DMI
- `0x4708` = **GIC311** DMI
- `0x5A08` = **GTM131** DMI

Existing exact-binary producer work is reused only for architecture/algorithm provenance; E006c remains the authority for this rear runtime session.

## Same-session rear GIC alias proof

The exact Surface `IFEGIC311Titan680::CreateCmdList` anomaly had already been source-locked: the GIC dword offset is passed to `WriteDMI` as a byte offset, so the wire `0x4708` range aliases current LSC source bytes rather than the separately calculated logical GIC LUT.

E006d verifies that relationship directly on both private E006c AC8 source windows.

For each request:

- LSC0 source begins at relative `0x400` and runs to `0x774`;
- LSC1 begins at relative `0x774`;
- wire GIC begins at relative `0x62e` and is 512 bytes;
- therefore wire GIC is:
  - `0x62e..0x774`: 326 bytes from LSC0 tail;
  - `0x774..0x82e`: 186 bytes from LSC1 head.

Private byte comparison on SP7 returned exact equality for both requests:

- AC8 sample0 GIC/alias SHA-256:
  `5fee246a1d6bc874d435c92c08b22f06e8b1a44f5a392d6f0eb9b093ce00febc`
- AC8 sample1 GIC/alias SHA-256:
  `0f2d74f58b30842a8eb7ce1d85670d8adef35b829c48def976e52bc0f36953d8`

Thus E006c's changing `0x4708` payload is **not a third independent dynamic producer**. It follows the current LSC source exactly.

## Dynamic producer classification

The four changing wire identities reduce to **two independent request-time producer families**.

### 1. LSC / Tintless

`0x4308 selector1` and `selector2` are current LSC wire payloads.

The repo already contains an exact OV13858 rear mode-1 Surface Tintless request5→request6 replay, including exact persistent-state carry and byte-exact output meshes. That proves the Surface rear/shared Tintless state machine and its stateful request-to-request nature.

For current E006c, do **not** substitute historical request5/6 bytes. The proof establishes the producer algorithm/state boundary, not current request state.

`0x4708 selector1` is derived from those same current LSC bytes by the proven wire alias.

### 2. GTM / TMC

`0x5A08 selector1` is the 0x800-byte GTM131 LUT.

The repo already contains an exact Surface GTM131 producer replay: TMC generation-5 request data plus exact ARM64 adaptive/Titan680 setting math reproduces observed GTM output byte-for-byte. E006c confirms that the rear steady GTM payload is request-varying, so Linux must produce it from current request/TMC state rather than freeze one captured LUT.

## Consequence for rear materializer

A correct rear Linux materializer must be split into:

- command topology / wrapper structure;
- payloads shown stable for the relevant variant;
- a **stateful LSC/Tintless producer** for current `0x4308` selector1/2;
- `0x4708` generated as the exact Surface LSC wire alias;
- a **request-time GTM/TMC producer** for `0x5A08`.

The 12 AC8 identities that were stable across two consecutive requests are only **AC8 stability candidates**. They are not promoted to globally static templates until A98/8F0/steady-658 cross-variant evidence is captured.

## Remaining gates

Still missing:

- steady A98 source window;
- steady 8F0 source window;
- true steady 658 source window (request generation >=4);
- cross-variant classification of the currently stable AC8 identities;
- current-session Linux-native LSC/Tintless state producer integration;
- current-session Linux-native GTM/TMC producer integration;
- guarded rear RT-CDM materializer integration;
- runtime completion/retirement validation before native rear processed ISP authorization.

Native rear Linux ISP remains **DENIED**.

### Next

Use a fresh, longer, fully auto-continue SP7→SP11 Windows capture for only A98 / 8F0 / steady-658. Require request generation >=4 for 658 so startup cannot satisfy the gate. In parallel, reuse the accepted rear Tintless and GTM producer implementations as the design basis for a rear materializer skeleton, but keep it unreachable/unloaded until the missing cross-variant corpus is closed.
