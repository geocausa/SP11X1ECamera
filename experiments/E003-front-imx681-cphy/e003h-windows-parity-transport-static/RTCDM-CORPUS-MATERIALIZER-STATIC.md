# E003h RT-CDM command-corpus materializer — static/unreachable

Date: 2026-08-29

## What this closes

The four same-machine Windows IFE startup command lists are already captured and decode to exactly 278 CDM commands, 2,131 ordinary VFE1 register writes and 46 DMI commands. The final patch/DMI oracle also reduces those 46 DMI references to 16 unique payload byte strings.

`extract_rtcdm_corpus_materializer.py` now compares the original initial-CDM capture with the later independent patch/DMI capture. After replacing the 46 captured DMI IOVA words, the only additional cross-capture command-byte difference is public VFE680 `period_cfg +0x8c`. The earlier ownership oracle separately proved five VFE offsets live-volatile between two same-machine Windows snapshots: `+0x3b70`, `+0x3d78`, `+0x3d7c`, `+0x3d80`, `+0x3d84`.

Accordingly the normalized command templates contain exactly **66 zero holes**:

- 46 DMI address fields;
- 20 dynamic register-value fields: four `period_cfg +0x8c` values, four `+0x3b70` values, and four values each for `+0x3d78/+0x3d7c/+0x3d80/+0x3d84` in packets 0..2.

The initial and later Windows streams become byte-identical after those holes are normalized. Their normalized SHA-256 values are:

- packet 0: `931d3a5ab8367bd0ec472eaa2bc56f9dec18bb70ebc2820c3b6693b38890c164`;
- packet 1: `7188c948ca65bae654c716a187d03f4e1bd4b2cfc3ccc761fbfd3748aef9bdb7`;
- packet 2: `ad3862424022169a49672682edf52032d626e329a5428c77e033e21b88732cc8`;
- packet 3: `233973ed415bf3cbd4d58bc890fcb34f494448daf5a736a60cdbcc099d0db487`.

## Linux-owned layout

The materializer deliberately does **not** reproduce Windows allocation geometry.

- main arena: `0x4000`, four Linux 4 KiB slots; packet lengths remain exact `0xe94`, `0xe34`, `0x904`, `0x4e8`;
- DMI arena: `0x3a00`, containing the 16 unique payloads packed at deterministic 64-byte alignment;
- Windows `0xa000` command-slot spacing is not used;
- Windows DMI source-window offsets are not used;
- every DMI command address is rewritten to the Linux coherent DMI arena.

`materialize_rtcdm_corpus.py` validates this architecture without hardware. It materializes both independent Windows variants at synthetic Linux DMA bases and decodes both outputs back to exactly 278 commands / 2,131 ordinary writes / 46 DMI commands. The DMI arena is identical for both variants; only the explicit dynamic register inputs differ.

## Kernel `0019`

`0019-x1e-rtcdm-corpus-materializer-unreachable.patch` mirrors that model in `camss.c` without embedding any captured command or payload byte arrays.

The caller must provide:

- four normalized command templates with every DMI/dynamic hole already zero;
- all 16 exact payload blobs with exact lengths;
- all 20 dynamic values;
- `dynamic_valid = GENMASK(19, 0)`.

The kernel helper rejects non-zero normalized holes, allocates separate 32-bit coherent command/DMI arenas, copies the normalized inputs, patches only the 46 Linux DMI addresses and 20 caller values, and exposes the four Linux command DMA/length pairs in the private corpus object.

There is **no** call to RT-CDM open/start/FIFO0/stop, no MMIO, no IRQ arm, no VFE operation and no stream connection. The helper pair is retained only by a private `__used` table. Object relocation inspection finds exactly two ABS64 relocations from that table to `materialize` and `release`, with no relocation/reference to the table itself.

## New boundary

The command/data materialization mechanics are no longer the blocker. The remaining inputs that cannot be frozen are the dynamic startup values themselves: `period_cfg +0x8c` and the five prior live-volatile register offsets. Their same-machine Windows production semantics must be recovered before a full unreachable start orchestrator can claim parity. Until then, do not substitute captured constants.

No module was loaded and no RT-CDM FIFO0 submission, VFE1 PIX enable, sensor transmission or frame occurred.
