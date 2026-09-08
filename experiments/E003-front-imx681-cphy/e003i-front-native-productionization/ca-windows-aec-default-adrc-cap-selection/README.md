# E003i CA — default ADRC cap selection

Status: **PASS (static/offline)** once `verify-ca.py` passes.

CA identifies Triggers bank `9:54` mechanically as `ADRCLuxFaceCap`, the output of ADRCCapSA arithmetic op0. The operator is enum 13 `CondSmaller`, with A=`SceneAnalyzer 3:36` (FaceSA confidence), B=`0.0001f`, C/D trigger operands, and output `Triggers 9:54`.

BX already proves `3:36` remains zero in uninterrupted ordinary `DefaultSequence`, because FaceSA is absent and its slot is constructor-zero with a unique writer. The DLL executor implements enum 13 as `A < B ? C : D`; therefore the scoped default path always selects C.

The selected C terminal table is pinned here (`1.6`, `1.5`, `1.4` over its three configured regions), but CA intentionally does not yet claim the complete method-2 two-trigger mapping. That mapping is the next boundary.
