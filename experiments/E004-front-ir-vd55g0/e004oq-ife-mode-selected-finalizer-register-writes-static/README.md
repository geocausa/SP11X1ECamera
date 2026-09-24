# E004oq — original IFE stop finalizers perform mode-specific register writes, not proven DMA retirement

**2026-09-24; parent E004op Git `7f24b418d9296aeaf01ec09cf84fc9d54723ee32`.** Exact original same-SP11 `qccamisp8380.sys` ARM64 SHA pinned; private image read-only, no camera runtime, Windows boot, KD, firmware installation or protected Golden mutation. Evidence tier **S/static** only. Target Windows oracle: rear OV13858 3840×2160 VideoRecord, but its selected IFE mode/base and BF `0x0F` event are unobserved. Native Linux slices **L1 exclusive shared-core ownership, L2 per-mode VFE control, L3 interrupt/DMA buffer lifetime**.

## Finalizer producer → selected receiver → original register writes

E004op independently showed that the IFE per-resource stop helper calls a selected finalization interface at context `+0x6B690` (RVA`0x27340–0x27358`), then sets software progress-pending flag `+0x171` and signals one of two software event objects. **E004oq resolves the previously unidentified original finalizer implementations and all instructions in their bounded bodies:**

| Original code/data [S] | What the original code directly performs | What is not established |
| --- | --- | --- |
| Mode state `+0x6B678` read/compare `0x19FA8–0x19FB0`; producer `0x19FEC–0x1A004` | Conditional pointer selection stores **RVA0x1D2B0 for zero-state** and **RVA0x1BE80 for nonzero-state** into IFE context field `+0x6B690`. Both are actual original ARM64 PE function entries, not inferred names. | Which mode or physical VFE1 register-window instance live Windows rear VideoRecord selected. |
| Entire nonzero-state finalizer **RVA0x1BE80–0x1BEE8** | Writes to original context `+0x140` register base at offsets **`+0x24`, `+0x28`**, uses helper `0x1C958` for software bookkeeping and writes to selected context `+0x150` register window **`+0x18` and `+0x8`**, then returns. | Hardware VFE/WM stopped, complete IRQ drain or safe in-flight DMA buffer release. |
| Entire zero-state finalizer **RVA0x1D2B0–0x1D338** | Writes original context `+0x140` register base **`+0x34`, `+0x38`**, calls the same bookkeeping helper, writes selected context `+0x150` window **`+0x18`, `+0x1C`** and conditionally **`+0x8`**, then returns. | That this path is live rear VFE1/WM16, or that these writes constitute a hardware DMA stop acknowledgement. |
| Entire 14-instruction helper **RVA0x1C958–0x1C98C** | Uses a context mode field, calculates/stores context mapping and software status, and returns. It contains no hardware-status poll, DMA wait or interrupt acknowledgement. | That an independent hardware-driven IRQ/stop path does not exist elsewhere. |
| IFE stop loop consumer `0x27358` and later progress flag `0x2738C` | Selected finalizer callback returns before the stop helper records software pending-progress; E004op's subsequent event stages remain distinct. | End-to-end physical WM16 quiescence, buffer ownership release or Windows profile selection. |

These callbacks provide **real mode-dependent original register-control operations**; they are stronger evidence than simply finding a pointer or naming a Windows selector. However, neither complete bounded callback contains an explicit hardware stop-status poll, interrupt/DMA wait or safe buffer-retirement proof. Other source/runtime hardware-completion mechanisms may exist. An original mode-dependent control write cannot be blindly copied to a shared Linux front/rear pipeline, and an IFE callback return or later `KeSetEvent` alone does **not** authorize a native CAMSS DMA free or PIX owner transition.

## Verification and next precise gate

`PYTHONDONTWRITEBYTECODE=1 python3 verify.py` checks original ISP SHA, **94 individual exact ARM64 instruction anchors** including the entire two selected finalizer bodies and entire bookkeeping helper, **two original PE function entries**, E004op's conservative interface-call contract and **14 fail-closed negative mutations**. `RESULT.json` contains only source-derived scalar RVAs/offsets and explicit unknown/false gates. No original driver executable, bulk disassembly, optical image, DMA address, firmware, KD credential/log or proprietary tuning is exported.

**Next falsifiable investigation:** source-map the original `+0x140` and `+0x150` register windows against the actual active IFE instance, and independently trace the **post-write hardware VFE bus/WM16 status, IRQ acknowledgement and per-generation image/statistics DMA completion**. Only a permitted same-session Windows rear4K observation can prove the selected mode, whether BF event0x0F and FIFO8 actually occur, and the true safe ownership handoff. Do not retry/bypass the blocked KD debugger launch; do not treat source-compiled experimental rear Linux ISP as arm-approved.

**Runtime remains unchanged:** protected Golden, working front 27-frame native PIX, rear RAW/software-4K fallback and IR privacy untouched; new Linux rear hardware-ISP candidate remains runtime-DENIED.
