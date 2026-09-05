# E003i-W — request/statistics selection + LSC trigger oracle

Status: **prepared; Windows oracle not yet executed**.

Purpose: close the two remaining inputs before any dynamic Linux-generated R5/R6 LSC substitution:

1. exact request-frame -> selected Tintless statistics identity;
2. the ordinary request-local LSC trigger/interpolation state.

The oracle deliberately does **not** use parser hit count as request identity. It uses pointer identity.

On one gated SP11 Windows cycle, the exact SHA-pinned `QcDeviceMFT8380.dll` is observed at:

- `TitanStatsParser::ParseTintlessBGStats` RVA `0x5f09d0`: log parsed output pointer (`x3`) and raw pointer (`x1`);
- `IQInterface::LSC411CalculateSetting` RVA `0x88e1e8`: log request frame `qwo(x1+0x1ff8)`, selected Tintless stats pointer `poi(x0+0xa0)`, and the request trigger block at `x1+0x2080`;
- optional redundant `TintlessAlgorithmWrapper::Process` RVA `0xc95fd0`: log `x2` stats pointer.

A request/statistics mapping is accepted only when the LSC-selected stats pointer exactly equals a parser output pointer from the same live process. Numerical delay is derived from those request-labelled matches, never assumed from priming order.

Trigger fields use the already-proven Surface `ISPIQTriggerData` layout, including AEC gain/lux, CCT, DRC, lens position, LED state, geometry and black level. The Windows stream is kept atomic: no values from an older matched-trigger stream are spliced into this oracle.

Safety: direct-Windows EFI BootNext only; persistent Golden remains unchanged. SP11 returns to Golden after the oracle. No Linux camera runtime is performed by W.
