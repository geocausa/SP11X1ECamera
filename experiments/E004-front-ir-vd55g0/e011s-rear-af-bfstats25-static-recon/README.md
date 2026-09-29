# E011S — rear AF / BFStats25 static reconnaissance checkpoint

Parent Git: `41b72354` (E011R).

Status: **SOURCE-ONLY RECONNAISSANCE CHECKPOINT; LIVE REQUEST TRACE NOT STARTED.** Native rear ISP runtime remains denied.

E011R closed the rear AWBStatsControl producer -> request property -> IFENode consumer chain. E011S pivots to the remaining BFStats25 / AF first-frame semantic gate from E008p.

Pinned OEM source reconnaissance now maps the CAF entry points relevant to the next trace:

- `CamX::CAFStatsProcessor::Initialize` is at RVA `0x827940`.
- `CamX::CAFStatsProcessor::ExecuteProcessRequest` is at RVA `0x8288C0`.
- helper RVA `0x82D450` snapshots AF/HAF static settings from the settings object into the fixed 0xA0-byte block rooted at data RVA `0x176B640`; Initialize invokes this helper with mode 1.
- `CamX::CAFStatsProcessor::SetSingleParamToAlgorithm` is at RVA `0x82D820`.
- after the AF algorithm/HAF setup succeeds, Initialize calls SetSingleParamToAlgorithm with parameter `0x16`, then parameter `0x15` using the 0xA0-byte block at `0x176B640`.
- the parameter-0x15 block therefore gives a concrete source-side anchor for the AF bootstrap policy that must be related to E008r's unresolved packet-0 BF filter/coring/IIR/ROI semantics.
- the request execution path at RVA `0x8288C0` is the next live-trace container; no request-1 E011S live claim has been made yet.

The parameter-0x15 snapshot at RVA 0x82D450 includes multiple feature bits and copied setting groups from the global settings object; semantic names for the individual fields are not yet closed. Do not equate those fields with BFStats25 register fields until the consumer path proves the mapping.

Immediate next work:
1. decompile/xref the parameter-0x15 consumer downstream of the AF algorithm SetParam path and identify the exact structures that feed the first BFStats25 config;
2. recover the first-frame/packet-0 filter, coring, numeric IIR shifts and accepted ROI set required by E008r;
3. only after the static target is narrow, start a **fresh one-shot** Windows rear4K holder and a **fresh KDNET session**, then trap request ID 1 at the chosen CAF/BF producer-consumer boundary;
4. checkpoint only source-safe scalar relationships/stable RVAs; keep OEM bytes and raw debugger logs private.

Operational state at checkpoint:
- SP11 Windows and SP7 are online;
- repository is clean before this checkpoint;
- previous KDNET terminal `job_qK4sPUlE1b73bjuBzXCzvZ11` is stopped after transport retry exhaustion and must not be reused;
- no E011S live one-shot identity has been consumed by this checkpoint;
- no native camera module install/load or RT-CDM submit is authorized.
