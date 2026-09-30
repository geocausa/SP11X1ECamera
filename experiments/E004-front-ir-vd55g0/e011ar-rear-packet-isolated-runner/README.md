# E011AR — packet-isolated Linux runner handoff

Parent: a48adb34c012287e8b8dd767cab3e0670ee512be.
Status: BUILD-ONLY PASS; native rear hardware runtime remains DENIED.

The E011AM composer produces four independent E008o semantic records, but the archived E008k/E008n runner still accepts one shared register/DMI state. E008o explicitly rejected wiring that old shape to hardware. This checkpoint implements the missing packet-isolated handoff in a new unreachable runner and consumed wrapper. Archived providers and protected Golden remain unchanged.

The runner validates the sealed four-record set, materializes each record into its own Linux-owned E008l command arena, and copies the resulting four submission descriptors. All materialization finishes before shared-owner acquisition and before command exposure. No shared register/DMI pointer or packet-id override exists in the new request. The caller must exclusively own the semantic set and arena throughout the transaction. These checks do not establish the provenance of otherwise valid caller policy inputs.

The wrapper atomically consumes its identity, validates the semantics and route, allocates command backing and invokes the new runner. It never rematerializes hardware-exposed commands. Any pre-exposure failure can release never-exposed commands; every exposure requires reboot, including success. Successful command release requires stopped RT-CDM, both frame ledgers complete, owner released and output mappings intentionally pinned. Unknown exposure pins commands until reboot. No exposed output mapping is freed or reused.

A lifecycle audit also found that the archived runner records successful RT-CDM/BUS/CSID/CSIPHY/sensor starts after each call. A partially failing start could therefore miss its emergency stop. The new runner marks each possible exposure before its attempt. An RT-CDM open/start failure now takes the emergency stop/pinned-owner path, and partial BUS/source starts receive stop attempts. Stop attempts do not prove hardware stopped; fault paths retain mappings/PM and mark the owner unsafe.

Validation:
- Actual runner and wrapper C execute against host-only fault-injected lifecycle providers under GCC and Clang ASan/UBSan: 4,091 assertions each, 58 failing lifecycle operations, 15 semantic negatives, two allocation failures, four command-exposure failures, and rejection of a second invocation.
- The exact runner preflight function executes with the real E008o/E008l/E007y composer. Its output packets are compared privately against the pinned corpus: 510,045 assertions per sanitizer compiler, zero semantic differences in phases 0/1/2/3, unchanged BF/BPC/LSC/GTM/GIC and statistics parity. Six new preflight negatives preserve submission descriptors.
- Fresh isolated ARM64 W=1 build: zero warnings/errors; module 14,820,448 bytes, SHA-256 5545aaff892fb87eade9be4e1168f391b6cc76dab9ccd88aa213fec4b0f31604. Exact protected-Golden vermagic; PiMaster verifier and separate Fabric hash/vermagic check pass.
- The host lifecycle providers are simulations. They do not prove live IRQ, DMA, IOMMU, timeout, sensor or stop behavior.
- No module installed/loaded, runtime entry point, Linux camera start, MMIO/submission, reboot or system sleep. Golden remains idle on boot c0e263ed-7319-4f69-8f10-4d51f20cd1a1.

Run verify.py for lifecycle/module checks; verify-private.py performs the private full composer comparison on SP11. Originals and packet bytes stay private on SP11. build-once.py and prepare.py are consumed: do not rerun them or reuse the isolated build directory.

Open gates are unchanged: deterministic caller-policy initialization (cold AEC weights/AWB retained BG, RS count/offset authority), explicit inactive cold gamma, and independent same-generation WM16 IRQ/consumed-IOVA/DMA/IOMMU retirement validation. Runtime authorization stubs remain -EOPNOTSUPP. Persistent output-DMA free/reuse is a later gate; this disposable runner pins output DMA until reboot.

Next: finish the startup policy producer and perform a final integrated preflight audit before preparing any separately guarded hardware observer/proof. Do not attach a V4L2/autostart path or activate this build.
