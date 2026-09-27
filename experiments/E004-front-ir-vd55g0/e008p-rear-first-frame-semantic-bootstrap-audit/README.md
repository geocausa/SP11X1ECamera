# E008p — first rear-frame semantic bootstrap audit

Parent Git: `08693d573c956fb22e1df5c8600fe6765c2d53e8` (E008o).

Status: **OFFLINE AUDIT PASS / NO RUNTIME**.

## Finding

E008o fixed the structural problem that the four startup packets cannot share one
mutable register/DMI state.  This audit now separates the remaining state into
two classes: clean providers whose semantic inputs are already self-contained,
and packers/handoffs that still need an explicit first-frame seed.

The transport/control path is no longer the immediate blocker.  The remaining
gate is a **semantic bootstrap object** for each of the four packets.

## Already clean for a first proof

The following do not require another Windows boot or captured-value replay:

- startup bank/phase policy (E006z/E008o);
- PERIOD_CFG from ordinary non-HFR `numBatchedFrames=1` (E007w);
- rear 4K crop/round-clamp + MNDS geometry (E006p/E006q);
- CST12 and the disabled BC101/small-IQ families (E006r/s/t);
- stable PDPC-zero, LSC selector3, Gamma151, BPC/ABF411 and DSX101 DMI
  generators (E007s/t/u/v);
- packet0 BHist DMI zero priming (E007x).

## Explicit seed handoffs still required

A packer is not the same thing as a producer.  The current chain still expects
caller-owned semantic state for:

- Demux / PDPC AWB ratios / WB gains (E006z);
- BPCABF411 calculated register state (E007a);
- BFStats25 calculated register state (E007b);
- BFStats25 25-ROI + 32-sample gamma DMI policy (E007e);
- BHist, RS, AEC_BE, Tintless_BG and AWB_BG initial statistics geometry/policy
  (E006u/v/w/x/y);
- request-tagged LSC selectors 1/2, where E007h is a clean producer but still
  needs a first-frame lux/CCT/Tintless input state;
- request-tagged GTM, where E007p/q are clean producers but still need initial
  TMC semantic runtime/common/control inputs.

This does **not** mean full live 3A must be finished before the first processed
frame.  E007r's conclusion still stands: long-run AEC/AWB/AF convergence,
upper-AEC LSC and broad scene coverage are later parity work.  What is required
now is one deterministic, clean, source-bounded seed for the first four packet
states.

## Private startup sanity check

A private aggregate-only comparison of the retained E006a startup corpus was
used to test the assumption that one packet state could be reused.  No values or
packet bytes were emitted.  Across registers present in all four startup MAINs,
35 registers vary; this includes packet bank state and all 29 BFStats25 words.
That independently confirms the packet isolation introduced by E008o and rules
out a single frozen bootstrap object.

## Next

Build the first-frame seed producer in layers.  Start with the statistics/AF
bootstrap because BF/WM16 is part of the ten-WM completion contract and cannot
simply be omitted.  Then close neutral AEC/AWB scalar state and generate
request-tagged LSC/GTM seeds through the already-clean E007h/E007p/q algorithms.
Only after E008o materializes all four packets from those seeds should the
consumed runtime wrapper be recomposed.

No Linux camera access, MMIO, module load, RT-CDM submit or reboot occurred.
