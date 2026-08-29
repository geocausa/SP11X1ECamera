# E003h RT-CDM period_cfg two-value contract — static/unreachable

Date: 2026-08-29

## Result

The remaining VFE1 startup `period_cfg +0x8c` transport contract is narrower than the four packet-local holes retained by `0020`. Across four independent same-machine Windows starts/captures, packet 0 always carries one start-dependent value while packets 1, 2 and 3 carry one identical shared value. The exact values vary between starts, so neither value is a Linux constant.

The Windows KMD pass-through proof already establishes that these values are populated before the IFE `0x803` processor reaches the captured handler and are not changed by its downstream helper. For the Linux kernel transport layer, the correct fail-closed interface is therefore **two opaque upstream caller inputs mapped onto four command-buffer patch sites**, not four unrelated caller inputs and not a guessed formula.

`extract_rtcdm_period_cfg_contract.py` hash-pins the accepted startup-ownership oracle and producer capture and enforces this two-value relation across all four observed starts. Derived oracle: `rtcdm-period-cfg-contract-oracle.json`.

## Linux `0021`

`0021-x1e-rtcdm-period-cfg-two-value-contract-unreachable.patch` refines only the retained private corpus materializer:

- two logical caller values;
- four `period_cfg` patch sites;
- packet 0 consumes logical value 0;
- packets 1/2/3 consume logical value 1;
- valid mask becomes two bits;
- no captured Windows period value is embedded;
- no MMIO, IRQ, FIFO submission, VFE op or stream connection is added.

`materialize_rtcdm_period_cfg_owned.py` reconstructs both independent Windows command variants with this two-value mapping and still decodes exactly 278 commands, 2,131 ordinary register writes and 46 DMI commands. `inspect_rtcdm_period_cfg_contract.py` independently checks the source relation, binary retention/isolation and Golden vermagic.

## Build/static proof

- patch SHA-256: `2f30286f01e6214c6af4fdf1e8908837ae3db39cb4a68075584fc2732b689636`
- contract extractor SHA-256: `5a3232054bab9fb1b97f0aa47d55dc4d4db53d5b26afa6925c2c2520ace7be24`
- contract oracle SHA-256: `0e6128140b6126845ca2656977f7cc137b1a32e6063b51497d3e808db29fed0d`
- static materializer SHA-256: `0b2ef49b06e1a4500657f29b222e7777669dfcb0abcc4aaca0a57e5c36de925e`
- static materialization JSON SHA-256: `aacc1b92dea07069ff7980526b87262d52bb2cea4dbb14437f9cc97d3fd2dadb`
- inspector SHA-256: `12b88a54d80c2d5fd53167324d6be655791cd223dffed98a2a2e2ffc33950d0d`
- inspection JSON SHA-256: `169cf024d87e2f9a4ec620fb15be657767d8e01dd87da0b47ebe9c11375e37c3`
- built module SHA-256: `6f29ccec021c0f2a6662bf9f7b27ec799d842ce14e1e235be3794e050dc6b921`
- source SHA-256: `6b0b0fce4481b26620a3a1f4ae82157d87a309131da8b26747ce655b66cd4a0c`
- Golden vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

Forward/reverse reconstruction passes. Strict checkpatch has zero code/style checks; only mail-patch metadata is absent. The module was not loaded and no Linux camera runtime occurred.

## Boundary

The kernel-side command transport no longer needs the upstream arithmetic that creates the two values; it needs an explicit caller contract for them. A later integration layer must obtain them from an equally proven upstream source rather than synthesize or freeze observed Windows values.

The next safe engineering step is a **private unreachable front-start orchestrator** that composes the already-proven static layers while keeping those two values explicit inputs. It must remain disconnected from probe/VFE/media paths and must not submit RT-CDM FIFO0, enable VFE1 PIX, transmit IMX681 or attempt a frame.
