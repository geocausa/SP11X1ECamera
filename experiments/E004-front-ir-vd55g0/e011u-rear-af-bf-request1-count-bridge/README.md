# E011U — rear AF/BF request-1 count bridge

Parent Git: `c7141132` (E011T). Evidence: pinned OEM static producer mapping plus fresh bounded OEM Windows request-1 live trace. Native rear ISP runtime remains denied.

## Exact producer mapping

Pinned `QcDeviceMFT8380.dll` SHA-256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

The OEM request property name table identifies `0x3000000E` as `PropertyIDAFStatsControl`; `IFENode::Get3AFrameConfig` RVA 0x741570 retrieves the adjacent AEC/AWB/AF/AFD stats-control group, including this AF property. Its BF branch checks the published AF BF record's ROI count at RVA 0x741C7C, property pointer +0x1C8C.

`CAFIOUtil::PublishOutput` RVA 0x817710 processes AF outputs and invokes `UpdatePropertyBFConfigOutput` RVA 0x819108 for output type 1 and `UpdatePropertyROIOutput` RVA 0x819418 for output type 2. Its ROI mapper destination is the internal BF record **plus four bytes** (CAF IO object +0x1401C). Source ROI config has a separate field at word index 1 and accepted copied-entry count at word index 2. The mapper writes source word 1 to mapper destination +0x1C8C, source word 2 to destination +0x1C88, and copies word-2 entries from 0x20-byte source ROI records to 0x24-byte destination records. Source entry +0x1C maps to destination +0x350 and is the per-record validity value. The mapper explicitly tests the copied validity when computing its bound; count alone cannot prove validity.

The same `PublishOutput` copies **0x1CC0 bytes** from the internal record *start* (CAF IO object +0x14018) to its request-indexed slot. Thus the mapper destination +0x1C88 becomes the copied BF record +0x1C8C, exactly the IFENode count field; copied entry validity is at BF record +0x354 (first), then +0x378 (second), with 0x24 stride. This four-byte shift is directly proved by the mapper call arguments and later memcpy source, rather than inferred from similar counts. A request-owned AFStatsControl output is consistent with the property table and IFENode input; direct live identity of the exact metadata allocation across the copy remains to be trapped.

`GetDefaultConfigFromAlgo` RVA 0x8274E0 provides a pre-request AF/BAF default path. `CAFStatsProcessor::ExecuteProcessRequest` RVA 0x8288C0 calls the AF processing and CAF IO publication path for request 1. The separate AF/HAF settings SetParam 0x15 arm at RVA 0x619910 feeds `af_haf_set_setting_info` RVA 0x622020; it is not the ROI field writer.

## Fresh E011U-0757A live trace

A new atomic holder identity E011U-0757A was consumed once. Its private script SHA-256 is `aee8abd9c4d1b7af51d7f1114a0ce80083eb80cf17c58e1f27e87ef5a54d43fb`. Fresh SP7 KDNET session connected, then local ARM64 CDB observed the FrameServer user-mode boundary. The raw transcript and host pointers stay private on SP11.

Before the first observed `CAFStatsProcessor::ExecuteProcessRequest`, `UpdatePropertyROIOutput` received source header words **1, 0, 25** and a zero-initialized destination count pair. Its return left destination +0x1C88 = **25**, +0x1C8C = **0**. The first two sampled destination ROI validity fields (+0x350 and +0x374) were **1**. This is the pre-request default ROI mapping, not proof that all 25 published request ROIs are individually valid.

The CAF Execute breakpoint then carried request ID **1**. A later ROI mapper hit within that request again had source words **1, 0, 25**, destination copied count **25** and the first two sampled validity fields **1**. At the request-1 IFENode BF consumer, the published BF record had +0x1C88 = **0** and +0x1C8C = **25**, with request ID **1**. The four-byte publish shift explains this exact pair; the normal nonzero path was selected. The observed order is pre-request mapper, CAF request-1 entry, request-1 mapper, then IFENode count consumer. Source and live observations together close the **count** mapping across AF output and IFENode for request 1. The 25 entries' individual validity, exact metadata allocation identity and a separately occurring packet-0 hardcode event are still open.

Breakpoints were cleared, StartAsync succeeded, 970 valid 4K handles were acquired, Stop passed, CDB detached, and the fresh KDNET job was stopped. No native module install/load or RT-CDM submit occurred.

## Next

Use a fresh one-shot to trap the CAF IO per-request 0x1CC0 copy and the AFStatsControl metadata boundary, verify all 25 validity flags and the request ID on both sides, then isolate packet-0 hardcode timing if it occurs separately. Do not replay E008s's already source-closed packet-0 filter/coring, -3/0 IIR shifts, centered 5x5 ROIs or packet1+ normal 3/3 shifts. Neutral-3A, LSC/GTM and VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement remain separate gates.
