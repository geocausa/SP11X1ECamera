# E008y — bounded, nonhalting AF trace oracle

Parent: E008x 0801142b2dc6c057a90723eb28c4049fa94cf358.
Slice L4/L5 AF statistics policy, rear color VideoRecord NV12 3840x2160.
Evidence: E008x offline shape [S], this run seeks original Windows runtime [P].

Question: can original user-mode tracing reveal the AF/BAF rectangle before BFStats25 adjustment, tagged to the first normal requests? Private packet1 and packet2 have the same 25 widths and heights but a uniform position shift on both axes; this alone does not attribute the producer.

The pinned same-SP11 DeviceMFT registers ETW provider {88c9b48e-2d10-41ce-8433-92b27d4a6a67} on process attach. AFIOUtil has a verbose BF ROI rectangle log and BAFLogicDriver has coordinate/grid logs, but their enable masks and event providers are not yet proven. Query provider/trace syntax on Windows, run a bounded 64 MiB circular ETW capture around one original rear4K holder, and check event/message counts first. No debugger attachment or on-target kernel stops. Do not modify OEM driver, tuning, firmware or kernel debug policy.

Keep ETL, decoded logs, Windows OEM data and optical material private on SP11. Commit only source-derived law and aggregate counts/booleans. If provider/capture fails or logs lack request-labeled AF stages, stop tracing and return to Golden; do not infer intermediate geometry from final DMI. Original holder is bounded with a single-use entry guard; direct remote launch avoids a persistent scheduled task. Ordinary Windows reboot returns Golden through persistent EFI order. Verify new Linux boot identity, saved Golden GRUB entry, empty next_entry, no camera nodes/modules/processes and repository state.

Runtime rear native ISP remains denied. This experiment does not change a driver or authorize rear ISP DMA.
