# E003i BI — Algorithm001 history exposure coordinate

Status: **PASS (static/offline + prior live AB2 memory evidence)** — closes the semantic producer of BH's formerly abstract F−3 `history_reference` scalar.

## Exact identity

On the ordinary front path, Algorithm001's history baseline is:

**the F−3 S1 lane's convergence-derived `log1.03` exposure coordinate.**

The mechanical propagation is:

`RunControl selected lane +0x10 coordinate -> rich arbitration +0x18 -> saved history lane +0x10 -> Algorithm001 F−3 read`.

BH's 0x10 payload-header correction is essential here. `GetInternalFrameHistory` returns the 0x1b0-byte payload, whose seven 0x28-byte lane records begin at payload `+0x10`. Algorithm001 indexes `payload + 0x28*lane` and reads `+0x20`, which is therefore lane-relative `+0x10`.

## Producer

`RunControlArbitration` stores the compact converged linear exposure into the selected lane at `+0x18`, converts it to float, divides by the active table base exposure, applies the double logarithm and the shared reciprocal `log(1.03f)` scale, and stores the resulting float coordinate at selected lane `+0x10`.

AX already proves core arbitration snapshots selected lane `+0x10` into rich output `+0x18`; `runEndOfFrame` then copies rich `+0x08..+0x2f` into the saved lane, preserving that coordinate at saved lane `+0x10`.

## Lane identity and live cross-check

The committed AB2 debugger capture records `w20=3` at Algorithm001's history lookup. The independently proven internal enum-to-string map names lane 3 **S1**.

The same AB2 S1 history record contains:

- coordinate bits `0x4365acdd` = `229.6752471923828` at lane `+0x10`;
- retained linear exposure `0x01fc4ec3` = `33,312,451` at lane `+0x18`.

AQ/AR prove the active T681 base exposure is `37,516`. The analytical relation

`log(33,312,451 / 37,516) / log(1.03f)`

rounds to the exact captured coordinate bits `0x4365acdd`.

This supersedes AB's old wording that the history field itself was Lux. Lux is the **Algorithm001 output** after the measured-luma correction is added to this exposure coordinate.

## Scope

BI closes field identity, lane identity, temporal selection, and one live bit-exact coordinate/exposure pair. It does not claim that Python/libm reproduces the proprietary Windows logarithm implementation bit-for-bit for every possible input; a full native arbitrary-input log-coordinate oracle remains a separate precision gate.

No live camera, sensor, module, or MMIO operation is performed.

Reproduce:

```sh
./verify-bi.py | tee VERIFY-RESULT.txt
```
