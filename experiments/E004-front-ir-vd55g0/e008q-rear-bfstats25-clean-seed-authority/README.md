# E008q — rear BFStats25 clean seed authority

Parent Git: `73f9d649cd9eef97e51bd8fee98d8cf45766467f` (E008p).

Status: **STATIC AUTHORITY PASS / PARTIAL BF BOOTSTRAP CLOSURE / NO RUNTIME**.

## Purpose

E008p reduced the first native rear-frame gate to eleven semantic bootstrap
handoffs and deliberately put BFStats25 first because BF/WM16 participates in
the ten-WM completion contract. E008q closes the large tuning-derived portion
of that BF seed without replaying captured Windows command or DMI bytes.

The selected rear tuning authority is
`com.surface.tuned.rfc_ov13858`, SHA-256
`4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635`.
Its BAF tree contains the exact semantic sources used below.

## Gamma DMI

BAF preset symbol `0x1bc1` contains two valid 32-sample gamma curves. Curve 0
is the accepted normal rear BF gamma seed.

Private validation reads the retained E006b payloads only inside the validator.
The tuning-derived curve reproduces **4/4** available BC08 selector-2 payloads
(startup1, startup2, startup3 and steady_ac8) sample-for-sample. No captured
payload bytes are emitted or committed.

## Filter coefficients

BAF preset symbol `0x1bc4` contains four filter records of:

`enable + ten float coefficients + mode + init-state reference`.

The second record (index 1), converted with `round(coeff * 16384)`, exactly
reproduces the accepted normal rear BF Q14 coefficient state. Titan's A
register order is the source-locked permutation
`[0,1,2,7,3,4,5,6,8,9]`; the B register order is the native ten-value order.

This tuning derivation matches **34/35** retained complete BF register records.
The only non-match is startup packet0. Packets1/2/3 and every retained steady
record share the tuning-derived state. Packet0 is therefore a distinct
bootstrap phase and remains intentionally unresolved rather than copied.

## Coring / threshold tail

BAF preset symbol `0x1bc9` contains two 20-word coring records. The first
normal rear record provides 17 threshold lanes plus its scalar semantic field.
Those tuning semantics reproduce both BF tail blocks for the same **34/35**
accepted records; again only startup packet0 differs.

The additional final tuning field is recorded as tuning metadata but is not
promoted here as a Titan register producer.

## What this closes

For the normal rear state used from startup packet1 onward, clean selected
tuning now owns:

- BF gamma selector-2 samples;
- both Q14 filter coefficient groups;
- both coring/threshold tails.

Still open before a runtime-capable E008o semantic set exists:

- packet0's distinct initial BF filter state;
- exact feature-enable / LUT-bank policy;
- the two signed4 shift fields;
- generation of the 25-entry BF ROI table.

The next checkpoint should source-lock those remaining BF fields from the
pinned `BFStats25::CheckDependenceChange` / Titan680 implementation and the
rear AF tuning tree. A new Windows boot is not justified by E008q.

## Safety

Offline/static only. No module build/load, MMIO, RT-CDM submission, camera
activation, reboot, or native rear runtime. Private validation emits aggregate
match counts only.
