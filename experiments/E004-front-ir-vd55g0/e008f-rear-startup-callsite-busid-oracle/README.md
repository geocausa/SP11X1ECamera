# E008f — rear startup call-site and BUS-resource Windows oracle

Parent Git: 5fb0e6a3eda1a05cf0347dcc5820f8f42fed5cca (E008d).
Parent observation: E008e.

Status: WINDOWS ORACLE PASS / STARTUP CONTROL PLANE NARROWED / NO LINUX REAR ISP RUNTIME.

## Result

A second fresh same-SP11 OEM rear Color / VideoRecord / NV12 3840x2160
session was observed from the external SP7 debugger with more specific
auto-continue probes. It produced 88 valid 4K frame handles, stopped cleanly
and returned to protected Golden Linux.

The accepted safe event order is:

CDM804 -> IFE804 -> selector2@0x2491c -> batch0(count4) ->
BUS_CONFIG(all rear resources) -> BUS_SET(enable) -> initial addresses ->
selector2@0x2491c -> batch1(count6) -> CSID_START -> ISP_START_DONE ->
selector2@0x25ec8 / later count6 batches.

The exact installed qccamisp8380.sys is SHA-256
64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c.
Static ARM64 confirms both observed call sites invoke the same RT-CDM
dispatcher RVA 0x28480 with selector 2:

- pre-CSID call site RVA 0x2491c, preceded by mov w1,#2;
- Epoch0/steady call site RVA 0x25ec8, preceded by mov w1,#2.

The second site is the already source-locked Windows Epoch0 consume path. The
first site belongs to original function RVA 0x246f0, reached by the packet
dispatcher before CSID start; its exact semantic name remains deliberately
unpromoted until the next static correlation checkpoint.

## Live rear BUS identities

E008f resolves the ten rear outputs at the actual BUS callbacks:

- 0x3000 FULL, two planes;
- 0x3001 DS4;
- 0x3002 DS16;
- 0x301c AEC_BE;
- 0x3010 RS;
- 0x300f BHIST;
- 0x300e AWB_BG;
- 0x300c TL_BG;
- 0x300d BF / BAF.

All nine resources are enabled before the ten initial address writes. FULL
has two address calls (arg=0, arg=1); all other resources have one.

This is the first accepted live rear-4K execution evidence that resource
0x300d participates in BUS config/enable/address setup. Earlier E004oj
source analysis had identified 0x300d as BF but had explicitly not claimed
that its live rear branch executed. E008f closes that narrower live-selection
fact. It does not weaken E007z's exact-consumed-IOVA retirement rule.

## What remains

E008f closes the gross BUS/RT-CDM/CSID ordering question but does not by itself
map every count-6 batch to E007y's four startup packets, nor does it observe
the CSIPHY1/OV13858 stream-on boundary. The next checkpoint must correlate
RVA 0x2491c and the count4/count6 batches statically, then combine that with
the already accepted Linux physical-stream ordering. A new Windows boot is
not justified unless that static correlation leaves a specific unresolved
edge.

No pixel data, DMA contents or IOVA values are committed.
