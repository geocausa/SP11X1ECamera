# E008n — rear consumed single-use wrapper

Status: **BUILD-ONLY PASS**.

E008n composes the E008l Linux command-DMA arena with the complete E008k rear transaction under a deliberately consumed one-shot identity. There is still no module parameter, probe hook, V4L2 callback or other runtime caller.

The wrapper consumes its identity with atomic_cmpxchg on the first invocation, allocates all four Linux command slabs, performs exact-route validation and full E007y materialization while the command set is still known unsubmitted, and then conservatively marks the complete command set hardware-exposed before entering E008k. This intentionally over-pins on any later failure so a partial RT-CDM FIFO fetch can never race command-memory free.

On a fully successful E008k return, RT-CDM stopped + both rear frames complete + shared owner released are required before E008l command memory is zeroed/freed. E008k output DMA remains intentionally pinned even on success, so every post-preflight return still requires reboot before any second camera attempt.

This is a disposable-transaction policy, not persistent runtime. It is intended to make the future first native rear proof fail closed: one attempt per module/boot identity, command DMA never freed after an uncertain hardware exposure, output DMA never reused, and Golden reboot required afterward.

## Build result

The fresh isolated E008n identity passed W=1 against the protected Golden headers. `qcom-camss.ko` is 14,682,720 bytes, SHA-256 `1b102acba82ce06acd6cacd347a9c4f36c14cafc3ef1f03ded9da322cc800cd9`, with exact Golden vermagic `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`. The build log contains zero warnings/errors. The module retains `e008n_rear_run_once_unreachable`, `e008n_rear_single_use_recipe`, `e008l_rear_command_alloc`, and `e008k_rear_run_unreachable`.

PiMaster and independent Fabric verification both pass. No install, module load, camera activation, RT-CDM runtime submission or reboot occurred.

## Runtime boundary

E008n closes the command-DMA lifetime and retry/reuse policy required for a first disposable rear-native proof. It still deliberately has no runtime call site and its authorization stub returns `-EOPNOTSUPP`.

A successful first proof may use the reboot-pinned output-DMA policy instead of ordinary post-stop free/reuse: no output mapping is reused, no second camera attempt is permitted in that boot, and a protected-Golden reboot is mandatory after every post-preflight return. Persistent runtime still requires a separate safe output-DMA free/reuse gate.

The next checkpoint is therefore a fresh guarded runtime candidate that wires exactly one explicit invocation path to this consumed wrapper, validates the rear route and Golden state before arming, records bounded evidence, and guarantees reboot-to-Golden recovery. The candidate must not introduce any ordinary V4L2/autostart path or weaken the one-shot identity.
