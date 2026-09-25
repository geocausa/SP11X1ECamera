# E005o — live Windows rear4K BF/FIFO8/matcher vs independent VFE BUS7 probe

2026-09-25; parent E005n Git 7e7841dae68ceb5f56a8c040b08c97cbb905d240.

This was one bounded physical Windows-oracle run on the same SP11, with SP7 as the external kernel-debug host. SP11 never depended on its own paused kernel for debugger control. All kernel probes were auto-continuing and emitted anonymous marker strings only. Raw addresses, pointer values, DMA/MMIO values and the private KD log remain outside Git.

After the run every breakpoint was removed, the private debugger log was closed, the one-shot Windows camera task was unregistered, Windows was resumed, and a normal reboot returned SP11 to protected Golden Linux. Post-return overlap guard passed with saved_entry=sp11-audio-fullio-v19c, empty next_entry, no camera modules/nodes/processes and clean tracked Git state.

## Physical capture

The one-use interactive-user camera helper opened Surface Camera Rear / Color / VideoRecord / NV12 / 3840x2160. It completed an 8,026 ms session with 13 valid frame handles, StartAsync=Success and clean StopAsync=Success.

## Live debugger result

Exact marker lines were counted from the private SP7 KD log after excluding breakpoint-command text.

| Live predicate | Exact hits |
| --- | ---: |
| original BF event | 22 |
| BF group8 FIFO pop returned non-null entry | 22 |
| BF outstanding matcher returned non-null | 22 |
| WM16 consumed-status callback value nonzero | 42 |
| candidate OEM VFE BUS status reader A had comp-group7 bit7 | 0 |
| candidate OEM VFE BUS status reader B had comp-group7 bit7 | 0 |

This is the first bounded live rear4K run in which every observed BF event also had a non-null FIFO8 entry and non-null matcher return. That closes a major weakness in the earlier E004pq/E004ps evidence: the original software BF path is no longer only a branch/callback proof.

The same session also produced repeated nonzero WM16 consumed-status observations. This is useful but still not an independent DMA fence because the BF callback itself reads that status.

## Why BUS7=0 is not a hardware-failure conclusion

E005m independently established the Qualcomm VFE680 reference contract: WM16 = STATS_BAF, composite group 7, VFE BUS status0 BIT(7), and consumed address from WM16 ADDR_STATUS0.

For E005o two exact OEM functions that read the VFE-style BUS status words were probed after their status0 load. Neither exposed bit7 during the successful rear4K session.

That result is negative for those probe points only. It does not prove that WM16 DMA never completed. The successful rear4K stream, 22 live BF/FIFO/matcher events and 42 nonzero WM16 consumed-status observations mean the more conservative interpretation is that the true OEM IRQ aggregation/dispatch/clear path or comp-group representation has not yet been source-locked.

Do not substitute CSID BUF_DONE bit7 for this missing VFE BUS witness. They are separate interrupt domains.

## Still deliberately denied

E005o does not establish one FIFO8 queue object equals one independently completed WM16 DMA buffer, same-frame/same-generation correlation, true WM16 BUS interrupt ownership and acknowledgement, DMA/IOMMU quiescence and safe reuse, all six rear output groups retired, or authorization to remove the rear native ISP runtime denial.

The E005n Linux observer remains unloaded. Before another live experiment, statically resolve the OEM VFE BUS interrupt-status producer/ack path and its comp-group encoding. A new physical run should only be performed after that probe is source-locked.
