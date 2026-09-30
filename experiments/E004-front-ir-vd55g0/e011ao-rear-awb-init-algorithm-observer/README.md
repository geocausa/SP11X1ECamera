# E011AO — bounded rear AWB algorithm initialization observer

Parent: 4bfea59895a680105681fd558b1a4bc2ae0ded0b. Fresh attempt E011AO-20260930-1250A.
Status PREPARED; no observation performed at preparation.

Hypothesis: initialization GetParam selector12 populates BG IO+0xCB4 including quad at+0xD08; its actual algorithm target identifies the next policy source. E011AN proves the descriptors preserve those bytes and only expose a writable destination.

Five bounded auto-continuing user-mode probes:
- initialization helper entry0x831510;
- algorithm call0x831964 and return0x831968, paired by thread and processor identity;
- Usecase AWBStatsControl publication0x831E00, filtered property0x5000001D and size0x80;
- AWB request consumer0x9FDF60.

Each path records at most four cases. Before/after pairing validates the actual BG descriptor destination/size; overlap or wrong return identity invalidates evidence. Private target-code/object/descriptor bytes and module metadata identify ownership without exporting originals. A positive bracket does not alone prove the first internal store or explain its policy.

The holder retains E011AK's atomic CreateNew entry, manual-only scheduled-task invocation, pre-enumeration/pre-initialization/start gates and30-second reader bound. It validates OEM rear Color VideoRecord NV12 3840x2160 frame handles without saving pixels.

Resolve probes to the actual loaded DeviceMFT owner before releasing initialization. If ownership cannot be established before initialization, do not label a late observation as an initialization trace. Clear user-mode breakpoints and detach before releasing resources when possible; audit exit and remove the task. Use no on-target kernel debugger or BCD changes.

Protected fallback: current Golden Linux boot b74c0760-83bb-421f-ac4d-1efa4e297294, kernel7.1.5-sp11-render-parity-v4+, saved FullIOv19c. A one-shot Windows GRUB entry leaves the saved default intact; normal Windows reboot returns Linux. No Linux camera activation, sleep, kernel deployment, MMIO or RT-CDM submission.

Original bytes, pointers and transcripts stay private on SP11. Source-safe aggregates only enter Git. Never reuse the identity once camera entry is consumed.
