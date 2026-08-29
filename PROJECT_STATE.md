## E003h ACTIVE — Linux steady-state module-input materializer built unreachable; IQ input-provider boundary next — 2026-08-29

The project target remains strict same-machine Windows parity, not merely a working raw stream. Static decoding of the exact installed Windows sensor/ISP binaries and the E003g MMIO oracle has now closed several lifecycle and format gaps. The SHA-pinned IMX681 sensor data defines stream-on/off as exactly `0x0100=0x01` / `0x0100=0x00` with zero delay; group hold `0x0104` is separate. CSID1 Windows RX is exactly `RX_CFG0=0x11300000`, `RX_CFG1=0x00000001`. The current Linux CSID680 path omitted the C-PHY type bit and Windows' reproducible bit-28 field; a static-only patch now computes the exact Windows RX_CFG0 for one-trio CSIPHY2 C-PHY and builds cleanly with Golden vermagic. It has **not** been deployed.

Windows VFE1 is a real ISP path: CSID1 IPP crops/measures the 3840x2640 RAW10 sensor mode to 3840x2160, then VFE1 emits FULL Y 2560x1440, FULL C 2560x720, DS4 320x180, DS16 80x45 and statistics clients. Current Linux VFE680 explicitly supports only RDI; its generic PIX mapping is invalid for PIX and would route line 3 through WM27/LTM_STATS. Therefore a Linux RDI frame can at most be a diagnostic transport proof and **cannot satisfy parity**.

Static disassembly of the exact installed `qccamisp8380.sys` (SHA-256 `64463b4d...17c21c`) mechanically establishes ISP-internal lifecycle ordering: **CDM start -> IFE start -> initial IFE/SFE/CSID config packets -> CSID start** and **CSID stop -> IFE stop -> CDM/remaining core stop**. The prior two-pass KD oracle proves ISP completion precedes IMX681 stream-on/off. A new four-cycle same-machine MIPI oracle closes the remaining placement gap: every start is **ISP_START_DONE -> MIPI_START_ENTER -> MIPI_START_DONE -> SENSOR_STREAM_ON_APPLY**. On stop, `ISP_STOP_DONE` always precedes both sensor-off and MIPI-stop, while Windows deliberately exhibits no total order between sensor-off and the MIPI stop interval: sensor-off was observed before MIPI entry, between MIPI entry/done, and after MIPI completion. The 8,600-byte raw log is SHA-256 `09a9b0aa...ef224` and a deterministic parser enforces this partial order. The X1E-only static `0010` candidate therefore remains valid: it corrects VFE->CSID teardown to **CSID -> VFE -> existing CSIPHY -> sensor tail**; that tail is an observed-valid Windows serialization, not a claimed Windows requirement. The patch builds cleanly with Golden vermagic and has not been deployed.

A new static-only `0011-x1e-csid1-ipp-windows-parity.patch` now closes the CSID1 IPP representation gap. On X1E, CSID source pad 4 is separated from the RDI virtual-channel bitmap and selects the dedicated IPP block while remaining CSI VC0. The candidate is fail-closed to the accepted front tuple (CSID1 + CSIPHY2 + one-trio C-PHY + SRGGB10 3840x2640), programs the stable same-machine Windows IPP configuration (`CFG0=0x802b2000`, `CTRL=1`, `CFG1=0x7241`, 3840x2160 crop/measure), uses the published IPP RUP/AUP mask `0x10001`, and leaves rear RDI0/VC0 behavior unchanged. Restore/apply/rebuild reproducibility is PASS; `qcom-camss.ko` SHA-256 is `ff02c59f...0f90b` with Golden vermagic and zero diagnostics. It has **not** been deployed.

VFE1 FULL memory layout is now mechanically resolved from the E003g Windows MMIO oracle. Clients 0/1 are **TP10 UBWC**, not linear NV12: `PACKER_CFG=0x0b` decodes as TP10, Windows uses 3584-byte stride, Y/C metadata sizes are exactly `0x6000`/`0x3000`, frame increments are exactly metadata plus TP10 data (`0x4f2000`/`0x279000`), and the two live address sets prove one contiguous `Y_META -> Y_TP10 -> C_META -> C_TP10` surface. The total 2560x1440 surface is `0x76b000` bytes. In Linux V4L2 terminology the matching opaque format family is `V4L2_PIX_FMT_QC10C`. Current CAMSS has no QC10C/UBWC VFE path. Qualcomm's public VFE680 source also confirms IFE top configuration is supplied through CDM rather than synthesized by the kernel driver.

The same-machine Windows initial IFE startup byte oracle is now **closed**. The main DEVICE_START `0x803` capture preserves all four descriptor-0 CDM streams (`175222` bytes, SHA-256 `a22f94b6...e86e762a`) and decodes exactly with zero unknown opcodes: 278 commands, 2131 register writes and 46 DMI commands. Packet 3 independently matches the E003g live VFE1 values at `+0x24` and `+0x90`, pinning the CDM base to VFE1 `0x0ac71000`. The register stream reaches `VFE1+0xbe70`; **2015** startup writes lie outside the current upstream X1E `0x4000` aperture.

A final bounded same-machine Windows patch/DMI oracle closes all 46 DMI references too. Raw capture `E003H_IFE_PATCH_DMI_EXACT_20260828.log` is 5,832,792 bytes, SHA-256 `71904380...bffc7`. Exact installed-`qccamisp8380.sys` ARM64 disassembly proves the Windows packet payload/patch layout and 24-byte patch records. The deterministic resolver proves **46/46 patch records = 46/46 DMI commands**, every destination is the exact DMI address field in the proper command-buffer slot, every patched IOVA is `source_iova + src_offset`, and every `encoded_length + 1` payload byte is captured. The source 128 KiB window is identical across all four startup hits (SHA-256 `bbb9dc35...69d9a`), the maximum referenced end is exactly `+0x1bccc`, and the references reduce to 21 exact register/selector/payload groups and **16 unique payload byte strings**. Supporting captures also prove descriptor 1 is the CSID1 IPP command stream and descriptor 2 is not the DMI source allocation. The public Qualcomm VFE680 kernel map does not name these pixel-IQ DMI offsets, so semantic names are intentionally not guessed.

The VFE1 static ownership/aperture pass is now mechanically closed. Across 695 unique startup register offsets, 650 are single-valued and 45 vary only between startup packets; no offset changes value within a packet. Five offsets independently known from the two-pass Windows live oracle are explicitly classified `runtime_volatile_do_not_freeze`. The initial-CDM corpus contains zero writes in the public VFE680 BUS range (`0xc00..0x2988`), proving buffer-client programming is a separate path. Maximum observed VFE1 access is `+0xbe70`, so the exact required byte span is `0xbe74`, page-rounded `0xc000`. The same-machine Denali VFE0->VFE1 base spacing is exactly `0xf000`, historical Denali used `0xf000` for both VFE apertures, and that span covers the complete Windows corpus. Static `0012` therefore overrides only Denali VFE0/VFE1 sizes to `0xf000`; the DT build passes and the before/after DTBs differ by exactly two bytes, the two size cells. No other X1E board is changed.

The Windows VFE1 BUS oracle is now closed through the dynamic address writer. The prior three-session capture proves session order **BUS static config -> BUS enable -> ISP_START_DONE -> BUS disable**. The focused same-machine follow-up then identifies the actual dynamic writer as `qccamisp8380` RVA **`0x1dd20`**, not `0x27920`: its image write site at `0x1dea4` programs each client `IMAGE_ADDR +0x04`, and its FULL metadata site at `0x1dee8` programs `META_ADDR +0x40`. The exact repeated address order is **FULL Y -> FULL C -> DS4 -> DS16 -> AEC_BE -> RS -> BHIST -> AWB_BG -> TL_BG**; FULL enable/disable internally toggles **WM0 then WM1**. A lifecycle capture proves the first complete nine-client IOVA set occurs **after BUS enable and before `ISP_START_DONE`**, with later complete sets repeating per frame. The same capture shows the values changing across frames, and the derived oracle explicitly rejects freezing either Windows IOVAs or observed Windows ring strides. `0x27920` remains a request/command-buffer builder but is superseded as the address-writer target.

Static `0017-x1e-vfe1-pix-bus-unreachable-recipe.patch` now represents those mechanics without making them reachable. It accepts only caller-supplied Linux `dma_addr_t` allocations, derives the proven QC10C Y/C metadata/data offsets, configures clients in Windows resource order, toggles FULL WM0->WM1, writes the initial dynamic addresses, and exposes a separate per-frame update helper. It never embeds a captured Windows IOVA or Windows ring stride. The helpers are retained only through a private `__used` table: binary inspection finds exactly three ABS64 relocations from that table to `prepare/update/stop`, no runtime relocation/reference to the table, and no VFE ops reference. The existing X1E VFE1 PIX `-EOPNOTSUPP` gate still fires before stream lock/IRQ/output programming. Build and forward/reverse reconstruction pass with Golden vermagic and zero compiler diagnostics; module SHA-256 is `44b9233d...783ef`, patch `55e88685...b2d5e`, inspector `db54f0fe...bd09d`, inspection JSON `92715605...262e`. No CAMSS module was loaded and no camera runtime occurred.

The Windows VFE1 completion ownership is now closed without overfitting the observed interrupt order. Five front cycles repeat `VIDEO(0x03) -> AEC_BE_BHIST(0x0d) -> TINTLESS_BG(0x0e) -> AWB_BG(0x10) -> RS(0x12)`, but exact `qccamisp8380.sys` disassembly proves helper RVA `0x26460` selects an **independent FIFO by group index** (`0,5,6,7,9`) and advances that queue's own count/read index. Therefore cross-group order is observational, not a required dependency. VIDEO owns FULL Y/C plus DS4/DS16; AEC_BE+BHIST share one group; TL_BG, AWB_BG and RS each own distinct groups. Raw completion log SHA-256 is `1e3e810a...b77ec`; extractor `461899f4...c8162`; oracle `696f476a...763f9`.

Static `0018-x1e-vfe1-pix-buffer-ownership-unreachable.patch` now models that ownership with two frame slots and **five independent group FIFOs**. Each slot keeps one caller/vb2-owned QC10C surface plus seven separate coherent Linux auxiliary allocations using the exact Windows `FRAME_INCR` payload sizes, not Windows ring spacing. Begin enqueues the slot into all five group FIFOs and produces the Linux IOVA bundle; each event pops only its own FIFO. VIDEO may return the userspace buffer immediately, but the slot is reusable only after all five group bits retire in any cross-group order. No Windows IOVA/ring stride is frozen, no `0017` BUS helper is called, no live ISR/`vfe_buf_done`/VFE ops path is modified, and the PIX `-EOPNOTSUPP` gate remains intact. Build/reconstruction pass with Golden vermagic and zero compiler diagnostics; module SHA-256 `7d88c0d6...e5010`, patch `fb1d0ace...c924f`, inspector `1f91e87f...27d2e`, inspection JSON `bc8bf641...b7dcf`. No runtime occurred.

Cross-capture normalization now closes RT-CDM **command/data materialization** without importing captured allocation geometry. Comparing the original four Windows main-CDM streams with the later exact patch/DMI capture proves that, after zeroing all 46 DMI IOVA words, the only newly exposed cross-capture command difference is public VFE680 `period_cfg +0x8c`. Combined with the five offsets already proven live-volatile (`+0x3b70`, `+0x3d78`, `+0x3d7c`, `+0x3d80`, `+0x3d84`), the four normalized templates contain exactly 66 holes: 46 DMI addresses plus 20 explicit dynamic register values. Once those holes are zeroed, both independent Windows captures are byte-identical packet-for-packet. `extract_rtcdm_corpus_materializer.py` SHA-256 is `3f02b586...72faf`; derived oracle SHA-256 is `1d1b753e...38cdc`.

Static `0019-x1e-rtcdm-corpus-materializer-unreachable.patch` mirrors that model without embedding any captured command/payload arrays. The caller must provide four normalized templates, the 16 exact DMI payload blobs, all 20 dynamic values and a full valid mask. Linux allocates its own `0x4000` main arena as four 4 KiB slots plus a compact `0x3a00` 64-byte-aligned DMI arena; Windows' `0xa000` command spacing and source-window offsets are deliberately not reproduced. All DMI commands are rewritten to Linux DMA addresses. A user-space proof reconstructs both independent Windows variants at synthetic Linux addresses and decodes both to exactly **278 commands / 2,131 ordinary writes / 46 DMI commands**. The kernel materializer is retained only by a private `__used` table with exactly two ABS64 helper relocations and no reference to the table itself; it adds no MMIO, IRQ arm, FIFO0 commit, VFE op or stream connection. Build/reconstruction and all deterministic inspectors pass with Golden vermagic; module SHA-256 `f783550d...3ae66`, patch `5e6f557e...25a2`, inspector `1264822d...2ea2`, inspection JSON `f0a4fc0f...b62e`. No runtime occurred.

The DMI execution architecture is now mechanically closed too. A bounded same-machine diagnostic first rejected importing the older Qualcomm VFE17x direct LUT-dump recipe: while native Windows kept VFE1 live, `DMI_CFG=0x101` at VFE1 `+0x4708` read back as `1`, but both candidate data ports remained zero and did not expose the known nonzero selector-1 payload. A second same-machine KD oracle then hit the exact Windows acquire-copy point and proved **`SW CDM = 0x00`**, hit the **hardware-CDM** branch, and never hit the software branch. The exact KMD resource mappings plus KD PTEs place `RT_CDM_0` at physical `0x0ac25000` and `RT_CDM_1` at `0x0ac26000`; both report `HW_VERSION=0x20010000` (CDM v2.1). During the native front stream only RT_CDM1 FIFO0/current-BL fields carry a command list, while RT_CDM0 BL fields and RT_CDM1 FIFO1/2/3 base+length remain zero. The archived POST sample, taken after normal StopAsync **and dispose/session teardown**, returns both RT-CDM windows to the `0x80000000` powered-off sentinel; it was not sampled exactly at the `0x805` boundary. Therefore direct guessed VFE680 DMI MMIO replay is no longer an acceptable parity architecture: Linux must provide equivalent **RT_CDM1 hardware execution** (or separately prove an exactly equivalent hardware interface).

The RT-CDM interrupt resource is now mechanically closed too. A controlled restart of only the same-machine Windows Spectra ISP device hit the exact `qccamisp8380.sys` RT-CDM registration routine during WDF `PrepareHardware`. RT_CDM0 registered as class 3 / instance 0 with raw firmware GSI `488` (`0x1e8`); RT_CDM1 registered as class 3 / instance 1 with raw firmware GSI **`319` (`0x13f`)**. The focused 7,428-byte UTF-16 KD oracle is SHA-256 `0f4b3027...6cbf1b` and a fail-closed parser rejects any byte change. The SP11 CAMSS DT itself supplies the namespace cross-check: its existing `GIC_SPI` cells 464..469 map exactly to Windows ISP GSIs 496..501, proving `GSI = DT SPI cell + 32` here. Therefore Linux RT_CDM1 must use **`GIC_SPI 287` (`0x11f`)**, not the Windows translated vector and not a guessed neighboring camera IRQ. Windows ISP returned `Started/OK` after the controlled restart, and Golden was then restored byte-exact.

Static `0013-sp11-rtcdm1-inert-resource.patch` establishes the first Linux RT_CDM1 representation without creating hardware behavior. It appends only the Denali MMIO tuple `0x0ac26000/0x1000` and `GIC_SPI 287` resource/name pairs, leaving every existing CAMSS tuple in order; generic Hamoa/other X1E boards are untouched. The helper is optional and X1E-only, requires the exact physical base/4 KiB span, resolves the named IRQ and maps the aperture, but performs **zero RT-CDM MMIO reads/writes**, does not request the IRQ, allocates no command memory and exposes no submit API. CAMSS builds cleanly with Golden vermagic (`qcom-camss.ko` SHA-256 `7bdb7e43...052ad`). Denali DT before/after is 215173 -> 215217 bytes; decompiled structural diff changes only `reg`, `reg-names`, `interrupts`, and `interrupt-names` by appending `rt_cdm1`, with after SHA-256 `bbe48a77...0304b`. Forward/reverse patch dry-runs pass. No runtime occurred.

Static `0014-sp11-rtcdm1-disabled-irq-dma-scaffold.patch` closes the next Linux scaffolding layer without authorizing hardware execution. RT_CDM1's proven IRQ is registered with `IRQF_TRIGGER_RISING | IRQF_NO_AUTOEN`, exactly following CAMSS's disabled-at-probe CSID/CSIPHY pattern. There is **no arm API and zero assignments of `irq_armed=true`**, so the compiled FIFO0-only ISR is unreachable. Its status model is compile-time pinned to the Windows live mask `0x00070007`; Qualcomm v2.1 is used only to name the matching reset/inline/BL-done/invalid/overflow/AHB-error bits and status/clear registers. A caller-sized coherent DMA arena is allocated only on explicit future request, independently rejects addresses above 32 bits, and is zeroed on allocation and before free. There is still no FIFO base/length/store/config write, IRQ-mask write, reset/core/FE write, core-enable write, or submit API. CAMSS builds cleanly with Golden vermagic (`qcom-camss.ko` SHA-256 `0a3f1e64...ce9a10`); Denali DT remains byte-identical to `0013` at SHA-256 `bbe48a77...0304b`. No runtime occurred.

The exact same-machine Windows RT-CDM1 write ordering is now statically pinned by `extract_rtcdm_init_order.py` against `qccamisp8380.sys` SHA-256 `64463b4d...17c21c`. Open/init is **IRQ0 mask 1 -> reset command 9 -> bounded reset wait -> DMB -> CORE_CFG 0x11f**. DEVICE_START is now fully ordered **CDM -> IFE -> initial IFE/SFE/CSID packets -> CSID**, and RT-CDM start itself is **IRQ0 mask 0x00070007 -> DMB -> CORE_EN 1**. Dynamic FIFO0 commit is **base -> encoded length/tag/arb -> store 1** and remains per-request state. DEVICE_STOP is **CSID -> IFE -> CDM**; the CDM stop path directly masks IRQ0 to zero but no `CORE_EN=0` write is proven. A bounded mapped-base store sweep finds no direct software store to live `FE_CFG +0x20=0x07ff000f` or `FIFO0_CFG +0x5c=0x01000000`; that is negative evidence only, not proof of reset ownership. Extractor SHA-256 is `399a7a6e...6629`; derived JSON SHA-256 is `489f47f4...e927`. The Windows one-shot returned to byte-exact Golden with empty `next_entry` and repository divergence `0 0`.

A second fail-closed exact-binary ownership oracle now closes the optional CGC ambiguity and strengthens the FE/FIFO result. Windows allocates the CDM object as exactly `0xa40` bytes and zeroes the entire object before initialization, maps RT-CDM once into object `+0x48`, and keeps the command-parser target in the distinct object `+0x838` field. The `CGC_CFG +0x14=7` path is guarded by object byte `+0xa38`; the exact executable has exactly one fixed-offset access to that byte (the guard read), no direct store overlaps it, and later bulk-memory operations target other subobjects. The normal Windows object lifecycle therefore leaves the guard zero and the optional CGC write is **statically not taken**. After the mapping/alias/helper/parser census, no in-binary CPU write path exists for live `FE_CFG +0x20=0x07ff000f` or `FIFO0_CFG +0x5c=0x01000000`; positive reset/hardware origin timing is still not proven. Extractor SHA-256 is `d25da738...b1e7`; derived JSON SHA-256 is `4c01a857...7b7c`.

A third fail-closed exact-binary/live-log oracle now separates stream stop from final power collapse. Windows `DEVICE_STOP 0x805` remains **CSID -> IFE -> CDM** and the CDM command's only direct RT-CDM write is `IRQ0_MASK +0x30 = 0`; there is no proven `CORE_EN=0` or reset write. Later camera control `0x80e` invokes manager/session delete: per-block CDM associations are released, the CDM software object is closed without any access to its RT-CDM MMIO field `+0x48`, then CSID and IFE receive explicit `POWER_OFF` and converge on the same reference-counted platform power-off helper. The platform callback runs only when the component use count reaches zero. The prior all-`0x80000000` POST dump is therefore correctly scoped to post StopAsync/dispose/session teardown and is consistent with this later power-collapse layer, not a hidden CDM shutdown-register sequence. Extractor SHA-256 is `3bf8189e...f805`; derived JSON SHA-256 is `75711e2c...39b8`.

A fourth same-machine two-cycle KD oracle now positively closes `FE_CFG` / `FIFO0_CFG` timing. After cycle 1 stop/dispose, RT_CDM1 `+0x00..+0x7f` is uniformly the powered-off `0x80000000` sentinel. On cycle 2, at exact resource-map return RVA `0x1849c` and again at the pre-first-MMIO boundary RVA `0x187a0`, **before the front CDM object writes any RT-CDM register**, Windows already reads `HW_VERSION=0x20010000`, `FE_CFG +0x20=0x07ff000f`, and `FIFO0_CFG +0x5c=0x01000000`. The FE/FIFO values remain unchanged through reset completion and `CORE_CFG=0x11f`, then return to the sentinel after cycle 2 teardown. This is positive proof that the values are restored by the pre-CDM-object platform/power-up/hardware layer, not programmed by the front CDM object. The ultimate source (firmware vs hardware reset/default) remains intentionally unnamed. Raw log is 18,444 bytes SHA-256 `4d54bca3...076bb`; extractor SHA-256 `16f283a0...4243`; JSON SHA-256 `7ab8eab8...ea3b`.

Static `0015-sp11-rtcdm1-windows-static-recipe.patch` now closes the Linux RT_CDM1 **representation** gate without authorizing execution. It adds a read-only exact preflight for `HW_VERSION/FE_CFG/FIFO0_CFG`, then privately encodes the Windows open/init (`IRQ0_MASK=1 -> RST_CMD=9 -> reset-done <=500 ms -> DMB SY -> CORE_CFG=0x11f`), start (`IRQ0_MASK=0x70007 -> DMB SY -> CORE_EN=1`), FIFO0 (`BASE -> observed encoded LEN -> STORE=1 -> BL-done wait`) and stream-stop (`IRQ0_MASK=0`) mechanics. The five helpers are retained only through a private `__used` data table; binary relocation inspection proves there is no code reference to that table, so no probe/media/stream path can reach the recipe. FE_CFG/FIFO0_CFG are never written, the CGC path is absent, and no `CORE_EN=0` is invented. CAMSS builds cleanly with Golden vermagic; `qcom-camss.ko` SHA-256 is `0c2f3df7...440d9`, patch SHA-256 `32661bf7...9514`, inspector SHA-256 `07338c37...d72a`, inspector JSON SHA-256 `23f9f601...a346`. Denali DTB remains byte-identical at `bbe48a77...0304b`. No module load or runtime occurred.

The VFE1 PIX **format/surface/completion representation** is now statically closed too. Exact installed-Windows KMD disassembly mechanically maps **TOP status1 bit0 -> event 3 -> `IFE VIDEO buf done`**, and pins `TOP_MASK0=0x0007f051` plus `BUS_MASK0=0xd0000000`; the fail-closed completion extractor SHA-256 is `04d54dce...9409`, JSON SHA-256 `c8436846...573c`. Combining that with the two-pass BUS/layout oracles closes one composite VIDEO/FULL surface: 2560x1440 `V4L2_PIX_FMT_QC10C`, one V4L2 DMA plane, 3584-byte stride, total `0x76b000`, with internal offsets `Y_META=0`, `Y_TP10=0x6000`, `C_META=0x4f2000`, `C_TP10=0x4f5000`; FULL is WM0+WM1 while DS4/DS16 and stats clients remain separate auxiliary outputs. Static `0016-x1e-vfe1-pix-qc10c-static-contract.patch` exposes that format **only on X1E IFE1 PIX**, retains exact Windows FULL/DS/stats/mask/event values as unreferenced read-only contract data, and returns `-EOPNOTSUPP` before stream lock/IRQ/output programming on VFE1 PIX. IFE0, both Lite instances and the existing VFE680 RDI WM functions are unchanged. CAMSS builds cleanly with Golden vermagic; module SHA-256 `97fd2dd9...855b`, patch SHA-256 `4e0cbba5...ab03`, inspector SHA-256 `af5b43ac...6f51`, inspection JSON SHA-256 `cb2d5ae3...fe10`. No module load, VFE1 PIX MMIO, RT-CDM submission, sensor transmission or frame occurred.

The `period_cfg +0x8c` kernel transport contract is now narrowed one step further without inventing its upstream arithmetic. Across four independent same-machine Windows starts/captures, packet 0 carries one start-dependent value while packets 1/2/3 always carry one identical shared value; the values themselves change between starts. The existing KMD pass-through proof shows they arrive already populated and are not modified by the downstream IFE handler. Static `0021-x1e-rtcdm-period-cfg-two-value-contract-unreachable.patch` therefore replaces four unrelated caller values with **two opaque upstream caller inputs mapped to four packet sites** (`0 -> value0`, `1/2/3 -> value1`). No observed Windows value is embedded. The two-value materializer still reconstructs both independent startup variants as exactly 278 commands, 2,131 ordinary writes and 46 DMI commands. Patch SHA-256 `2f30286f...89636`; contract oracle `0e612814...fed0d`; inspection JSON `169cf024...e37c3`; Golden-vermagic module `6f29ccec...6b921`. Runtime remains untouched.

A bounded same-machine Windows cross-order capture now closes the missing placement between the four initial IFE `0x803` packets and VFE1 BUS setup. Before the first `ISP_START_DONE`, Windows executes **packet0 -> packet1 -> nine BUS static configs -> eight resource enables -> one complete nine-client initial address set -> packet2 -> packet3**. Combined with the already-accepted manager order, the host contract is **RT-CDM start -> IFE resource start -> packet0 -> packet1 -> BUS prepare -> packet2 -> packet3 -> CSID1 start -> ISP_START_DONE**; MIPI/CSIPHY and IMX681 stream-on remain later. Raw cross-order log SHA-256 is `c32acebd...42963`; extractor `e0cd5d69...913ad`; oracle `b495cc83...acce6`.

Static `0022-x1e-front-start-orchestrator-unreachable.patch` encodes that result only as a retained contract/validator. It pins the exact X1E front tuple, the `0021` period map `{0,1,1,1}`, Linux-only preparation markers, and the ten host lifecycle stages while explicitly setting hardware execution false and excluding MIPI/sensor start. The validator can call only the fail-closed corpus-input validator; it does not call RT-CDM write/FIFO helpers, VFE1 BUS helpers, CSID stream helpers or VFE stream paths. Binary inspection finds one ABS64 relocation from the private recipe to the validator and no relocation to the recipe itself. Build/reconstruction pass with Golden vermagic; patch SHA-256 `1bf7d406...7e190`, module `d845b027...ac8c8`, inspector `aa434869...8ba47`, inspection JSON `dc4a86ae...c700a`. No module was loaded and no runtime occurred.

Post-`ISP_START_DONE` scheduling remains closed. The accepted two-session KD timeline proves one complete nine-client address bundle before `START_DONE`, a **second complete bundle after `START_DONE` but before the first completion cycle**, then a refill bundle after that first cycle. Exact `qccamisp8380.sys` call-graph anchors retain the software order **IFE Epoch0 -> complete BUS IOVA update -> queued RT-CDM BL consume/program -> completion retirement**. Static `0023` recorded that scheduler as read-only data and remains non-executable.

The new clean selector-2 oracle now closes the actual steady-state RT-CDM **command-list topology** and supersedes one narrower 0023 ownership inference. The hash-pinned Windows capture is 3,994,804 bytes SHA-256 `1e8dc967...4d9a7f` and contains exactly **179 batches / 894 BL records**: four startup batches followed by **175 steady Epoch0 batches**. Every steady batch has five BLs: 4-byte `CHANGE_BASE 0xf000`, one main IFE BL, 4-byte `CHANGE_BASE 0x57000`, a fixed 0x10-byte two-register BL, and a fixed 0x14-byte register+GEN_IRQ BL. The main IFE list has five real variants: `0x958` (8 samples, 56 commands/472 writes/14 DMI), `0x868` (42, 45/436/12), `0x83c` (46, 43/429/12), `0x6b8` (24, 35/352/8), and `0x5a4` (55, 22/315/2). The queue encoded length is **byte_count - 1**. Extractor SHA-256 is `d02f7faa...329a`; oracle SHA-256 `3bcf4efe...dce4`.

Within each main-BL variant, command topology is byte-identical across all samples. Every changing command dword is mechanically classified as either a DMI address field or a register-value field; normalization yields one exact template hash per variant. The clean oracle also proves Windows carries `period_cfg +0x008c` and `+0x3b70/+0x3d78/+0x3d7c/+0x3d80/+0x3d84` inside queued steady-state RT-CDM programs. Therefore 0023's earlier "no post-start software rewrite proven" wording is **superseded** for those identities. The retained rule is narrower and important: do not invent a separate Linux direct-MMIO/polling rewrite loop; these writes belong to the per-frame CDM command program.

Static `0024-x1e-epoch0-cdm-batch-contract-unreachable.patch` corrects the 0023 data object to `cdm_programmed_regs` plus `direct_mmio_rewrite_authorized=false`, and adds a retained five-variant Epoch0 batch contract. It embeds no Windows IOVA or raw command/payload array, explicitly leaves DMI payload bytes unclosed and FIFO0 submission unauthorized, and adds no executable helper. Build/reconstruction pass with Golden vermagic; patch SHA-256 `4b234a78...9f095`, module `1f88683b...dd9ad`, inspector `193eddc9...38afb`, inspection JSON `2f7bab80...8f90a`. CAMSS remained unloaded and no Linux camera runtime occurred.

The five steady-state DMI payload topologies are now hash-closed from local same-machine Windows evidence without committing raw payload bytes. The accepted 8,868-byte live mapping log is SHA-256 `f44d09f8...f3b0`; the local 15-slot source-ring and targeted `0x958`/`0x5a4` slot dumps remain untracked. Hash-only extractor `extract_vfe1_epoch0_dmi_payload_variants.py` is SHA-256 `824a99eb...0f13`; derived oracle `vfe1-epoch0-dmi-payload-variants-oracle.json` is SHA-256 `f4b4fbd7...b17a`. Representative samples cover all five variants (`0x958=2`, `0x868=10`, `0x83c=2`, `0x6b8=4`, `0x5a4=2`). `4308/1` and `4308/2` vary per frame in every multi-sample variant that carries them; `0x958` additionally varies `4708/1` and `5a08/1`. `0x83c` now has two dedicated samples: only `4308/1` and `4308/2` vary; its other ten carried DMI identities are invariant across both. Windows' `0x8000`/15-slot payload-ring geometry remains allocator evidence only, never a Linux constant.


The final steady-state tagging ambiguity is now closed too. Focused same-machine Windows trace `E003H_VFE1_GENIRQ_REQUEST_CORRELATE_20260829.log` (26,760 bytes, SHA-256 `7a182c14...974c`) captures **246 GEN_IRQ tags `1..0xf6`** and **245 selector-2 Epoch0 request identities `2..0xf6`**. After the two already-proven primed tags, every tag `N` immediately precedes consumed `requestId=N`; all observed `subRequest=0`. Fail-closed extractor `extract_vfe1_genirq_request_tag.py` is SHA-256 `157d566b...4f9e`; oracle SHA-256 `ddbc97e3...5ab6`. Therefore steady BL4 `GEN_IRQ userdata = low32(requestId)` for the accepted front stream and must remain request-derived in Linux, not a free-running CDM counter. A second dedicated `0x83c` DMI sample also closes its within-variant behavior: only `4308/1` and `4308/2` vary; the other ten identities remain byte-identical.

Exact KMD disassembly also corrects the prior "variant selector" wording. `DAL_ife_process_iq_packet` RVA `0x26838` derives active/changed groups from the incoming IQ packet (`0x28080`, `0x28168`, `0x267d0`) and processes changed groups through `0x28238`; record type is read from each upstream entry at `+0x8c`. There is no proven KMD five-way `0x958/0x868/0x83c/0x6b8/0x5a4` selector. Variant shape and frame-varying IQ payload values are therefore upstream IQ-producer inputs. Linux must not invent a kernel selector or freeze one captured sequence.

The upstream Windows producer is now mechanically identified as the registered **`QcDeviceMFT8380.dll` CamX DeviceMFT** from the exact Surface AVStream package. The INF hash is `4db3acab...62fcb`, DeviceMFT hash `c241b7fb...41c35`, and miniport hash `b97c4338...577ed`. Exact Titan680 command builders name every `0024` changing field: DemuxBLS141 owns `0x3b70/74`; PDPC311 `0x3d58/5c` and `0x3d78..84` plus DMI `0x3d08`; LSC411 `0x4358/5c` plus DMI `0x4308`; WB201 `0x456c/70`; GIC311 `0x4758/5c` plus `0x4708`; BPCABF411 `0x4958/5c` plus `0x4908`; GTM131 `0x5a58/5c` plus `0x5a08`; Gamma151 `0x5f58/5c` plus `0x5f08`; DSX101 `0xa058/5c`, `0xa258/5c` plus `0xa008/0xa208`. The same binary pins dependency families: LSC consumes AEC/AWB/calibration/tintless state, Gamma AEC/AWB, GTM TMC/AEC/DRC tone-mapping state, DSX geometry, PDPC sensor/PDAF state, WB white-balance gains, and DemuxBLS pixel-format/gain state. Extractor SHA-256 `85f8b405...9ba18`; oracle `cbd8908d...c03ef`. This closes producer **ownership/semantics**, not proprietary CamX algorithm reproduction.

Static `0025-x1e-epoch0-module-input-materializer-unreachable.patch` now closes the Linux **consumer/materialization** side without claiming those algorithms. It accepts only one of the five exact normalized `0024` main shapes plus exact per-module value/payload-valid masks, requires `subrequest=0`, derives BL4 `GEN_IRQ` from `low32(request_id)`, and repacks all DMI references into Linux-owned 4 KiB command + 12 KiB DMI arenas. No Windows main template, payload bytes, IOVA or ring geometry is embedded. Independent reconstruction with real normalized Windows samples but synthetic module values/payloads reproduces all five exact command/write/DMI counts. Forward/reverse source reconstruction is byte-exact; the private recipe has only two ABS64 retention relocations and no caller; VFE1 PIX remains fail-closed. Patch SHA-256 `75b88258...2ae68`, proof JSON `7c4b37c2...4b4bc`, inspection JSON `ae60274a5...41b46`, Golden-vermagic module `09abae83...b6c35`. CAMSS remained unloaded and no runtime occurred.

The four selector-2 batches immediately surrounding ISP start are now closed as a distinct **priming replay** phase rather than a second host-start submission. Each replay is byte-identical to its corresponding startup main stream after excluding only the already-proven `period_cfg +0x8c` replacement; packet0 receives value0 and packets1/2/3 share value1. The observed order is **replay0 -> replay1 -> ISP_START_DONE -> replay2 -> replay3 -> first steady 0x958**. Two DMI families are priming/startup-only in this front path: LCAC111 (`0x5408`, selectors 1/2) and BHistStats16 (`0xb208`, selectors 1/2). Extractor SHA-256 `28e305f2...18f08`; oracle SHA-256 `4d49864c...c1ef2`.

Runtime camera/image testing is now authorized. Golden remains the saved/default boot and will not be modified. The next experiment is a disposable, bounded first-frame candidate using private Linux DMA and the Windows-matched RT-CDM/VFE1 BUS/CSID1/CSIPHY2/IMX681 order with explicit teardown/rollback.

**Next action:** keep runtime blocked. Treat `0022/0023/0024/0025`, DMI topology, `GEN_IRQ=requestId`, and Windows producer/module ownership as closed. Next close the **module-input provider boundary**: determine which DemuxBLS/PDPC/LSC/WB/GIC/BPCABF/GTM/Gamma/DSX outputs can be derived from deterministic sensor/geometry/tuning state and which require live statistics/AEC/AWB/TMC/tintless feedback, including the Windows priming state before the first steady Epoch0 update. Do not freeze captured Windows outputs, claim CamX algorithm reproduction, create a caller for `0025`, arm RT-CDM IRQ/FIFO0, start CSID1 IPP/VFE1 PIX/MIPI, transmit IMX681 or attempt a frame.

Canonical handoff: `docs/runbooks/2026-08-28-e003h-windows-parity-static.md`.

## E003g ROUTE RESOLVED — same-machine Windows front route is CSIPHY2 -> CSID1 -> IFE1/VFE1 — 2026-08-28

A route-complete same-machine Windows oracle supersedes the earlier E003g CSID0/VFE0 hypothesis. Two independent `Surface Camera Front` WinRT reader cycles (`StartAsync=Success`, normal `StopAsync`) were captured by SP7 KDNET across `IDLE -> LIVE1 -> POST -> LIVE2 -> POST2` for the CSID wrapper, CSID0/1/2, VFE0/1 and CSIPHY2. The canonical raw log is `experiments/E003-front-imx681-cphy/e003g-windows-csid-vfe-oracle/raw/E003G_ROUTE_ORACLE_20260828.log`, 2,457,712 bytes, SHA-256 `fd8edcee46e794dffa0e2305331f19d4e9d2cd5b9ba5197484aa1cc7fa6c6fca`. Both post-stop states equal idle exactly.

The wrapper proves only CSID1 has `OUTPUT_IFE_EN` (`+0x000=0x1`, `+0x004=0x101`, `+0x008=0x1`). CSID1 is the active receiver block and its IPP `CFG0=0x802b2000` mechanically decodes as enabled VC0 / CSI-2 DT `0x2b` RAW10 / 10-bit decode. Windows IPP crop/measurement is 3840x2160 (`x=0..3839`, `y=0..2159`) from the established 3840x2640 sensor mode. VFE0 has zero live non-zero/non-sentinel dwords; VFE1 has 217 and contains active FULL Y/C, DS4, DS16 and statistics bus clients. Qualcomm's published CSID680/VFE680 tables are used only for register naming/layout; same-machine Windows remains the behavioral oracle.

**Current boundary:** the physical front route is now proven as `IMX681 -> CSIPHY2 -> CSID1 -> IFE1/VFE1`. E003f's VFE0 power call remains valid historical evidence that sufficient host CAMNOC/CPAS context was needed to exercise CSIPHY2, but it was not proof that VFE0 is the Windows front output route. Linux `camss-vfe-680.c` explicitly supports only RDI output today, so the first native transport experiment must preserve the proven CSID1/VFE1 instance selection while using Linux's supported RDI path rather than copying Windows FULL/DS/statistics programming. No first-frame Linux patch has been accepted yet.

**Historical next action at E003g:** keep byte-exact FullIO v19c Golden as the saved default. Audit and minimally adjust the E003d/e/f media graph and any hard-coded host-power selection so the front mode0 path reaches CSID1 and VFE1 instead of CSID0/VFE0. Derive/build the smallest bounded CSID1 -> VFE1 RDI diagnostic candidate with explicit timeout, fail-closed teardown and rollback; do not call that diagnostic Windows parity.

Canonical handoff: `docs/runbooks/2026-08-28-e003g-route-resolved.md`.

## E003f ACCEPTED — host-powered CSIPHY2 C-PHY receiver parity — 2026-08-27

E003f-R3 passed the receiver electrical gate. After exact Golden/candidate preflight, the one-shot `sp11-camera-e003f-r3-cphy-receiver` booted with the corrected 8 KiB CSIPHY2 DT resource and patched CAMSS srcversion `1D2912B8FF127D1F3D94704`. The SHA-checked verifier added only normal VFE0/IFE/CAMNOC/CPAS host power around CSIPHY2; it made no CSID stream or sensor/CCI/MODE_SELECT call. CSIPHY2 power-on succeeded at a 400 MHz timer rate and the live comparison matched **121/121** Windows final C-PHY registers with zero mismatches (`CTRL5=0x02`, `CTRL6=0x01`, `CTRL7=0x7a`). Stream-off cleared CTRL5/6, VFE0 power_count returned to zero, and IMX681 remained runtime-suspended/usage 0 with reset-low, front MCLK/rails inactive and no sensor/CCI messages in the R3 window. Rear camera, Wi-Fi, FullIO audio and G6 touch remained healthy. Normal reboot restored byte-exact FullIO v19c Golden: Image `bca0a336...428a`, initrd `ac3ba64b...b66d`, DTB `2fcfa738...6d00`, saved default Golden and empty `next_entry`. E003g starts static-only: derive the exact front CSID/VFE/RDI route and smallest bounded sensor-stream lifecycle before any MODE_SELECT=1 or frame attempt.

## E003e ACCEPTED — IMX681 Windows mode0 programmed in standby — 2026-08-27

The front IMX681 accepted the exact same-machine Windows init (364 writes) plus 3840x2640@30 mode0 (68 writes) while MODE_SELECT remained 0 before and after all 432 writes. Readback verified C-PHY/RAW10/one-trio timing, crop, output size and PLL2; fixed transmitter metadata reports 1.2 GHz V4L2 link frequency for the 2.4 GHz C-PHY symbol rate. A direct sensor harness proved the mbus values and `s_stream(1)=-EOPNOTSUPP`; IMX681 PM, MCLK4, CSIPHY2/timer, front rails and reset all returned/stayed idle. Rear camera, Wi-Fi, FullIO audio and G6 touch stayed healthy, and normal reboot restored byte-exact FullIO v19c Golden. CCI adapter numbers and Wi-Fi IP/MAC are dynamic across boots, so future tooling must discover them. Next is E003f: receiver-only C-PHY electrical activation with the sensor still in standby and streaming blocked.

## E003d ACCEPTED — IMX681 one-trio C-PHY idle graph — 2026-08-27

The accepted native IMX681 now appears in `/dev/media0` with an ENABLED+IMMUTABLE link to `msm_csiphy2` using one zero-based CSI-2 C-PHY trio. The exact Windows-derived X1E C-PHY table is compiled into candidate CAMSS, but a direct sensor-only `s_stream(1)` test still returned `-EOPNOTSUPP`; MCLK4, CSIPHY2/timer, both front rails and reset therefore remained electrically idle. Rear camera, Wi-Fi, FullIO audio and G6 touch stayed healthy. Normal reboot restored byte-exact FullIO v19c Golden. Next is E003e: exact Windows IMX681 3840x2640@30 mode0 programming in standby, still with MODE_SELECT prohibited and no PHY streaming.

## E003c ACCEPTED — native IMX681 V4L2 bind-only gate — 2026-08-27

The front Sony IMX681 now binds under a native V4L2 sensor driver on CCI1/master1 and passes both the SP11 Windows/platform identity (`0x0004 = 0x0aff`) and Sony silicon identity (`0x0016 = 0x0681`). E003c intentionally contains no sensor write path and no front endpoint. A separate test-only harness called the bound V4L2 `s_stream(1)` callback directly and proved `-EOPNOTSUPP`; runtime PM then remained suspended with usage 0, MCLK4/front rails/CSIPHY2 disabled and GPIO237 reset-low. Golden was restored byte-exact with Wi-Fi/audio/touch healthy. Next is E003d: add the C-PHY graph and X1E80100 receiver programming while keeping streaming blocked.

## E003b ACCEPTED — front IMX681 electrical identity — 2026-08-27

Linux one-shot E003b reproduced the same-machine Windows front-camera electrical lifecycle on CCI1/master1 and read IMX681 register `0x0004 = 0x0aff` at address `0x10`. MCLK4, LDO3_M and LDO7_B returned disabled, GPIO237 returned reset-low, CSIPHY2 stayed unused with no front media link, and Wi-Fi/audio/touch/rear-camera health remained intact. The machine then returned to byte-exact FullIO v19c Golden with empty `next_entry`. Next is E003c: native IMX681 V4L2 bind only, still no front CSI endpoint or streaming.

## E003 STARTED — front IMX681 / C-PHY static integration phase — 2026-08-27

Rear OV13858 production integration is closed by E002k-D-R3. R3 booted one-shot on the exact FullIO v19c Golden Image with the maintained reconciled DTB and production OV13858 module, reproduced the accepted color-bar SHA-256 `6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`, streamed 16/16 4076x2806 RAW10 frames at 29.9504 fps, and tore down cleanly. The machine was then returned to Golden; Golden kernel/initrd/DTB hashes remain exact and Wi-Fi/audio/touch are healthy. Source audit proves the production base is `.golden-v33-repro/src` plus exactly three intentional source-file differences; `.golden-v33-delta-replay/src` contains later audio drift and is not a production base.

Phase D now begins as E003 front IMX681. Existing same-machine Windows oracle evidence proves CCI1/master1, CSIPHY2, MCLK4 19.2 MHz, reset GPIO237, LDO3_M 1.8 V + LDO7_B 2.8 V, Linux slave address 0x10, ID register 0x0004 expected 0x0aff, and CSI-2 C-PHY (`0x0111=3`). E003a is static/compile-only: audit the current C-PHY CAMSS series against the exact true Golden source and derive a clean front sensor/power plan before any powered runtime.

## E002k-D-R2 ACCEPTED — native PM8010 rear camera — 2026-08-27

The temporary camera RPMh shim is retired. Accepted E002k-C camera bytes with only the provider swapped to stock `qcom,pm8010-rpmh-regulators` reproduced the exact hardware color-bar SHA `6987a736...f09346` and 16/16 normal frames at ~30.065 fps. Native LDO6/LDO1/LDO5 returned disabled/users 0 after streaming; no custom provider existed; Wi-Fi/audio remained healthy. Next is compile-only maintained-source integration in the isolated exact-Golden tree.

## E002k-D-R2 prepared — native PM8010 camera integration — 2026-08-27

R2 starts from exact accepted E002k-C camera bytes and replaces only the temporary camera RPMh shim with the R1-accepted native PM8010-M provider. Sensor standard supplies now point to native L6/L1/L5; the accepted OV13858 module is byte-identical. Initrd no longer contains the custom provider module and waits for built-in `regulators-8`. Runtime acceptance requires the known color-bar SHA plus 16-frame stability.

## E002k-D-R1 ACCEPTED — native PM8010-M provider — 2026-08-27

Provider-only one-shot passed: stock `qcom-rpmh-regulator` bound PM8010 ID `m` as `regulators-8`; LDO6_M 1.8 V, LDO5_M 2.8 V and LDO1_M 1.2 V all registered with zero users and no enable vote. Regulator summary confirms L6<-S4C, L5<-BOB1, L1<-S5J. No camera node was present; Wi-Fi/audio remained healthy. Next gate replaces the temporary camera RPMh shim in accepted E002k-C with these native regulators only.

## E002k-D-R1 prepared — native PM8010-M provider-only gate — 2026-08-27

A DT-only provider gate adds native `qcom,pm8010-rpmh-regulators` PMIC ID `m` under the Golden RSC, with no camera/CAMSS/CCI consumer. Upstream-backed X1 parents are L1/L2=`vreg_s5j_1p2`, L3/L4=`vreg_s4c_1p8`, L5=`vreg_bob1`, L6=`vreg_s4c_1p8`, L7=`vreg_bob1`. Only LDO1/LDO5/LDO6 children are exposed using non-fixed voltage ranges, with no boot-on/always-on/initial-mode vote. Candidate DTB SHA-256 `6291de3c0b4148735acec2f0a48b54a51208e2931b9898f7c91d90db6ac119b0`; kernel/initrd remain exact Golden. Runtime has not yet occurred.

## E002k-D prepared — source integration with native-PMIC split — 2026-08-27

Golden was mechanically reverified after E002k-C. Historical kernel worktrees are too contaminated for camera integration, so E002k-D will use a fresh writable copy of the exact Golden replay source. Linux already has native PM8010 RPMh-regulator support; live Golden simply lacks PMIC-M in DT. A saved SP11 baseline proves native PMIC-M and its L3/L4 and L5 input parents, but not L1/L2 or L6, so native-regulator replacement is isolated until those parents are proven rather than guessed. Driver and Denali rear-camera source integration can proceed independently.

## E002k-C ACCEPTED — rear profile no longer experiment-gated — 2026-08-27

The rear OV13858 now selects its proven 4076x2806@30 Surface profile solely from standard four-lane 592.8 MHz endpoint metadata; no `microsoft,e002*` property or stream gate remains. The deterministic color-bar SHA remains `6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`, and a 16-frame normal run completed seq 0-15 at 29.9575 fps with clean teardown, zero VAF votes and healthy audio/Wi-Fi. Next is source-level production integration and removal of temporary initrd/module scaffolding.

## E002k-C prepared — firmware-selected rear profile, no experiment gates — 2026-08-27

The candidate removes all four `microsoft,e002*` DT booleans and corresponding driver gate/validation state. The Surface 4076x2806 profile is selected from standard firmware endpoint metadata: four-lane D-PHY with a single 592.8 MHz link frequency. Generic OV13858 mode/540 MHz PLL tables are mechanically unchanged and devices without that firmware signature retain the upstream fallback. Candidate artifacts are reproducible; runtime has not yet occurred.

## E002k-B ACCEPTED — standard OV13858 supply bindings — 2026-08-27

The sensor now consumes standard `dovdd`, `dvdd`, and `avdd` supplies mapped to the same proven LDO6_M 1.8 V, LDO1_M 1.2 V and LDO5_M 2.8 V providers. LDO16_B/VAF is absent from the sensor node and had zero enable events. Native identity/streaming passed and the hardware color-bar frame remained byte-identical to E002j/E002k-A at SHA-256 `6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346`. Teardown and system health were clean. Next is removal of the remaining experiment-only mode/stream properties.

## E002k-B prepared — standard OV13858 supply bindings — 2026-08-27

E002k-B is a naming/binding-only conversion on top of accepted E002k-A: `dovdd` maps to the same LDO6_M/VIO 1.8 V provider, `dvdd` to LDO1_M/VDIG 1.2 V, and `avdd` to LDO5_M/VANA 2.8 V. LDO16_B/VAF is removed from the sensor DT node. Driver enable/disable order, voltages, mode, MCLK/reset and transport are unchanged. A reproducible DT builder yields byte-identical candidates and asserts all pre-existing non-supply sensor properties remain unchanged.

## E002k-A ACCEPTED — VAF separated from OV13858 — 2026-08-27

With the exact accepted E002h-r1 kernel/DT and only LDO16_B ownership removed from `ov13858`, native identity and full streaming passed with zero LDO16_B enable votes. The one-frame internal color-bar SHA-256 is exactly the same as E002j (`6987a736...f09346`). Therefore LDO16_B 2.9 V is not required by the rear sensor path and is classified as VAF/actuator power. Next: rename the remaining three consumers to standard `dovdd`/`dvdd`/`avdd` DT supplies without changing their rails/order/voltages.

## E002k-A prepared — separate VAF from OV13858 sensor power — 2026-08-27

Static QTI `sensorDriverData` classifies the rear sensor power-up as RESET -> VANA -> VDIG -> VIO -> MCLK -> RESET release; VAF is absent from power-up and explicitly disabled in power-down. With the board voltages this maps VIO=LDO6_M 1.8 V, VDIG=LDO1_M 1.2 V, VANA=LDO5_M 2.8 V, VAF=LDO16_B 2.9 V. E002k-A keeps the accepted E002h-r1 kernel/DT/mode/transport byte-identical and removes only LDO16_B ownership from `ov13858`. It will repeat identity plus the internal color-bar frame and require zero LDO16_B enable votes.

## E002j ACCEPTED — sensor-generated RAW10 integrity — 2026-08-27

Using the exact accepted E002h-r1 binaries, standard `V4L2_CID_TEST_PATTERN=1` produced one complete 4076x2806 packed-GRBG10 frame. Decoded RAW contains only levels 64 and 1023; all same-parity rows are bit-identical and Bayer-channel transition positions form deterministic vertical bars. Test pattern was restored to disabled and all camera power/clocks returned idle. This independently proves sensor-generated RAW10 packing/order through CSIPHY1 -> CSID0 -> VFE0 RDI0. Next: E002k productionize the rear path into standard/native bindings and driver logic.

## E002j prepared — sensor-generated RAW10 integrity gate — 2026-08-27

E002j is a control-only test on the exact accepted E002h-r1 binaries. No kernel/module/initrd/DT changes. It will enable the upstream OV13858 standard `V4L2_CID_TEST_PATTERN=1` (Vertical Color Bar Type 1), capture exactly one 4076x2806 packed-GRBG10 frame, validate vertical-band structure after RAW10 decode, restore test pattern to disabled, and verify electrical teardown.

## E002i-B ACCEPTED — standard rear exposure response — 2026-08-27

With gain and transport fixed, standard V4L2 exposure 100 -> 3000 lines produced a coherent RAW10 signal increase (full-frame mean 64.3415 -> 65.2285; central mean 64.3500 -> 65.3988) while both captures and teardown remained clean. The scene is close to black pedestal, so next E002j uses the sensor's standard test-pattern control as an optics-independent packing/data-integrity proof.

## E002i-A ACCEPTED — 16-frame rear stream stability — 2026-08-27

The byte-identical accepted E002h-r1 payload streamed sequences 0..15 with full 14,321,824-byte buffers at ~29.95 fps and clean PM/clock teardown. No drops or new kernel faults. E002i-B may now vary only standard exposure with gain/transport fixed.

## E002i prepared — rear short-stream stability, then exposure response — 2026-08-27

E002i reuses the accepted E002h-r1 kernel/initrd/module/DTB byte-for-byte. Phase A streams exactly 16 frames through the native 4076x2806 RAW10 route to `/dev/null` and checks sequence/timestamp/full-buffer stability plus clean teardown. Only after that passes will Phase B vary the standard V4L2 exposure control with gain and all transport settings fixed.

## E002h-r1 ACCEPTED — first native rear RAW10 frame — 2026-08-27

A one-cell DT correction (`csiphy1` MMIO size 0x1000 -> 0x2000) removed the reset Oops. The unchanged native pipeline `OV13858 -> CSIPHY1 -> CSID0 -> VFE0 RDI0 -> /dev/video0` then STREAMON'd successfully and dequeued sequence 0 with exactly 14,321,824 bytes of packed 4076x2806 GRBG10. Local frame SHA-256 `c025aaa5...`. RAW10 decoding yielded 11,437,256 non-constant pixels with a coherent dark-scene pedestal. Normal close returned sensor PM usage to 0 and MCLK/CSIPHY clocks to 0; Wi-Fi/audio remained healthy. First physical rear-camera frame transport is proven. Next E002i: bounded stream stability then standard exposure/gain response.

## E002h first stream BLOCKED / r1 prepared — CSIPHY1 MMIO window — 2026-08-27

The first E002h STREAMON Oopsed in `csiphy_reset()` before sensor streaming: sensor PM stayed suspended and MCLK1 stayed off while CSIPHY1 clocks enabled. Active DT mapped CSIPHY1 `0xace6000+0x1000`, but X1E CSIPHY uses `regs->offset=0x1000` and immediately writes at base+0x1000. Denali's own standalone PHY node and SM8550/8650 use a 0x2000 window. E002h-r1 changes only that one resource-size cell to 0x2000; kernel/initrd/module/mode/graph/stream permission are byte-identical.

## E002h prepared — first controlled native rear stream — 2026-08-27

E002h changes only the experiment permission boundary: one DT boolean `microsoft,e002h-allow-stream` plus an 11-line driver gate. The accepted 4076x2806 Surface mode, 592.8 MHz D-PHY link, 432732960 Hz VT pixel rate, power/reset/MCLK sequence, graph and unmodified X1E CAMSS remain unchanged. Read-only and hard-blocked E002g tests proved the native default path `OV13858 -> CSIPHY1 -> CSID0 -> VFE0 RDI0 -> /dev/video0` and active SGRBG10 propagation, with `/dev/video0` packed GRBG10 (`pgAA`) sizeimage 14321824. E002h will request exactly one mmap frame under an external timeout.

## E002g ACCEPTED — native Surface rear mode semantics — 2026-08-27

Strict no-stream runtime exposes exactly one rear mode, 4076x2806 RAW10, with LINK_FREQ=592800000, PIXEL_RATE=432732960, HBLANK=412 and VBLANK=408. This computes exactly 30 fps at the pixel array while keeping CSI output throughput separate. E002e/e002f validation still passes, sensor/CSIPHY return to electrical idle, and system health is intact. Offline Windows-oracle comparison also proves the clean upstream+Surface reconstruction reaches identical final values for all 207 Windows-covered mode0 registers; the proprietary table remains local oracle evidence, not shipped source. Next gate is E002h first bounded transport activation.

## E002g prepared — native Surface rear mode semantics — 2026-08-27

Offline oracle equivalence proves the E002f clean reconstruction covers all 207 Windows mode-0 register addresses with identical final Windows-covered values after the normal final VTS write; only Linux's explicit `0x4503=0` test-pattern-disabled write is extra. E002g therefore keeps the clean upstream+Surface-delta implementation rather than embedding the proprietary table. Timing semantics are now split natively: LINK_FREQ=592.8 MHz / CSI output throughput=474.24 Mpixel/s, while the sensor-array VT PIXEL_RATE is 432,732,960 Hz from 4488 pixel clocks/line * 3214 lines * 30 fps. HBLANK=412 and VBLANK=408. E002g exposes only 4076x2806 on the SP11 experiment and retains the pre-power hard no-stream guard.

## E002f ACCEPTED — Surface rear mode0 programmed/read back in standby — 2026-08-27

The real OV13858 accepted the compact clean-room Surface profile in standby: PLL 05/00/f7, 4076x2806 output, line-length register 1122, static VTS 3208, MIPI timing 0x0d, then final QTI VTS 3214, with MODE_SELECT=0 before and after. Power teardown was clean; CSIPHY1/CSI1 timer never enabled; E002e controls and E002d graph remained unchanged. E002f is accepted. Next is E002g: resolve Surface 30-fps line-length/pixel-rate semantics before exposing the mode via normal V4L2 enumeration.

## E002f prepared — Surface rear mode0 standby programming — 2026-08-27

E002f composes a clean-room Surface mode0 program from a 12-register Windows-derived 592.8 MHz PLL, the unchanged upstream full-resolution common table, and a compact 24-register Surface delta. It validates 4076x2806, line length 1122, static VTS 3208, MIPI timing 0x0d, then writes/readbacks final QTI frame length 3214 while MODE_SELECT remains standby. The E002e pre-power stream guard remains intact and CSIPHY is never powered. Candidate module `d70cd770...`, initrd A/B `b23b757b...`, DTB `b669db40...`.

## E002e ACCEPTED — rear 592.8 MHz transport metadata — 2026-08-27

Automatic driver endpoint validation proved four-lane D-PHY at 592800000 Hz. Read-only V4L2 controls returned LINK_FREQ=592800000 and PIXEL_RATE=474240000, exactly matching the Windows QTI RAW10/four-lane transport. The immutable enabled OV13858->CSIPHY1 link remained present; sensor runtime PM stayed suspended/usage 0 and MCLK1/CSIPHY1/CSI1 timer enable counts stayed 0 after identity. No PLL/mode register array or stream operation was executed. E002e is accepted. Next is E002f: program the focused Windows Surface mode0 PLL/register delta in sensor standby, still with no stream/CSIPHY power.

## E002e prepared — rear 592.8 MHz transport metadata, hard no-stream — 2026-08-27

Exact Windows QTI mode data proves the Surface rear transport uses RAW10/four-lane D-PHY at 474.24 MHz pixel rate = 1.1856 Gbit/s/lane = 592.8 MHz DDR link frequency. Windows mode0 is 4076x2806 and differs from upstream full-res in only 19 of 199 shared final register values plus a small address delta. E002e intentionally changes no sensor PLL/mode register arrays: it adds 592.8 MHz endpoint/control metadata, validates four-lane D-PHY at probe, and installs a DT-selected stream guard before runtime-PM power-up. Candidate initrd A/B are byte-identical at `48517776...`; candidate DTB `0e25c28f...`.

## E002d ACCEPTED — native rear OV13858 -> CSIPHY1 graph — 2026-08-27

Read-only `MEDIA_IOC_G_TOPOLOGY` proved `ov13858 1-0010` pad0 -> `msm_csiphy1` pad0 with flags `0x3` (ENABLED + IMMUTABLE) and data-link type. Sensor remained runtime-suspended (usage 0), MCLK1/CSIPHY1/CSI1 PHY timer enable counts stayed 0, reset stayed asserted, and no rail activity occurred after boot identity. E002d is accepted. Next gate is E002e: reconcile Windows rear mode/lane timing with native OV13858 link-frequency/mode metadata, still with no stream operation.

## E002d prepared — rear OV13858 <-> CSIPHY1 graph only — 2026-08-27

E002d adds only reciprocal four-lane D-PHY endpoints between the accepted native OV13858 and CAMSS `port@1`, mechanically mapped by the exact X1E source to CSIPHY1 and independently proven by Windows routing. Host lanes are `<0 1 2 3>`, sensor lanes `<1 2 3 4>`, bus type explicitly D-PHY. No link frequency, mode, CSID/VFE route or stream is added. Local source proves async graph completion/media-link creation does not power or stream CSIPHY. Candidate DTB `ea55cafd...`; E002c-r1 kernel/initrd remain byte-identical.

## E002c-r1 ACCEPTED — native OV13858 bind / identity / runtime PM — 2026-08-27

E002c-r1 automatically loaded the accepted RPMh provider, exact V4L2 dependencies and patched native `ov13858` from initrd. The native driver bound to `1-0010`, upstream 24-bit identity passed, then all rails and MCLK tore down with runtime PM `suspended`, usage 0. Loaded sensor module srcversion `02C96088AA5798CD5A70BFE` proves the patched module was running. No sensor CSI endpoint existed and no stream occurred. E002c is accepted. Next gate E002d adds only rear four-lane D-PHY graph wiring to Windows-proven CSIPHY1.

## E002c-r1 prepared — packaging-only fix after manual native PASS — 2026-08-27

E002c r0 automatic loading failed before electrical action because Golden has no module `extra/` directory and r0 emitted only its nested `extra/e002c/`. Loading the exact same provider and patched native driver after full boot passed completely: native OV13858 bound, ID verified, runtime-suspended, rails/MCLK off, reset asserted. r1 changes only initrd packaging: emit the missing parent `extra/` and preserve real insmod errno. r1 initrd A/B are byte-identical at `d1e56f66...`; kernel, DTB and camera module bytes are unchanged.

## E002c prepared — native OV13858 bind only, no CSI — 2026-08-27

E002c now cleanly separates native sensor-driver ownership from transport. Starting from accepted r3g, the DT changes only the rear client compatible to `ovti,ov13858`; no endpoint is added. The exact upstream OV13858 source was adapted only to own Denali's proven four-rail/GPIO110/MCLK1 power lifecycle and runtime PM. The module builds with exact Golden v4 vermagic (`35c99b5...`). A Golden-based initrd containing the accepted RPMh provider, exact V4L2 dependencies and patched native driver was built twice byte-identically (`48e092c4...`). No E002c runtime boot has occurred yet.

## E002b-r3g ACCEPTED — rear OV13858 physical contact / identity — 2026-08-27

The strict A/B boot removed only `clk_ignore_unused pd_ignore_unused` and reproduced the permissive result: GPIO97 `0x00000244`, OV13858 ID `0xd855` at address `0x10`, clean reverse teardown, CAMSS nodes present, Wi-Fi/audio healthy. E002b is accepted. The r3f NACK root cause was the missing physical MCLK1 GPIO97 route. Next gate is E002c: native Linux OV13858/V4L2 bind plus the minimum rear CSI endpoint, with no streaming yet.

## E002b-r3g permissive runtime PASS — 2026-08-27

The one-variable GPIO97 correction changed the rear OV13858 from the r3f `-ENXIO` NACK to a valid `0xd855` chip ID at `0x10`. GPIO97 reads `0x00000244` exactly as Windows did; the unchanged r3f probe then completed and tore all rails/MCLK down cleanly. Wi-Fi, playback and capture remained healthy and Golden remained the saved default. This proves missing physical MCLK1 routing was the r3f NACK root cause. A strict one-shot with only `clk_ignore_unused pd_ignore_unused` removed is required before accepting the identity gate.

## E002b-r3g prepared — physical rear MCLK1 pad proven — 2026-08-27

A one-shot SP11 Windows KD session read X1E TLMM directly. Windows leaves GPIO97 at `0x00000244`: function 1 `cam_mclk`, 4 mA, no pull, output enabled. Golden/r3f Linux reads GPIO97 as `0x00000001`: GPIO/function 0, 2 mA, pull-down, output disabled. Qualcomm's 2026 Hamoa/X1E80100 pinctrl series independently maps `cam_mclk1_default` to GPIO97 and its camera overlay pairs that pinctrl with `CAM_CC_MCLK1_CLK`.

r3g is therefore a DT-only correction applied directly to the exact r3f DTB. It adds one GPIO97 `cam_mclk` state plus `pinctrl-0`/`pinctrl-names` on the existing rear probe node. Kernel, r3f initrd/probe module, rail/reset order, MCLK1 19.2 MHz, CCI0/master1 @ 400 kHz, address `0x10`, and the Windows-exact `0x300b -> 0xd855` transaction are unchanged. Candidate DTB SHA-256: `396259a06edffd4f9e0482480ef02201aa88acd98731db57fbb33358650a0b33`.

# Historical project-state snapshot — superseded by the newest sections above

**Snapshot date:** 2026-08-27
**Historical state ID:** E002g native Surface mode semantics accepted
**Golden remains:** SP11 Audio FullIO v19c

## Historical boundary at that snapshot

E002b-r3f booted stably and used the Windows-exact OV13858 ID transaction (`0x10`, FAST/400 kHz, register `0x300b`, 16-bit expected `0xd855`) on Windows-proven CCI0/master1. The first transfer still returned `-ENXIO`; teardown was clean and no crash occurred.

Live TLMM inspection exposed the strongest remaining omission: CCI GPIO103/104 are correctly muxed, but all X1E camera-MCLK capable GPIO96..99 are func0/unclaimed and the rear node has no MCLK pinctrl state. Before another powered probe, prove from Windows which physical pad carries `cam_cc_mclk1_clk`, then add only that pinctrl correction.

## E002b-r3e boundary and r3f preparation — 2026-08-27

r3e safely reached the first CCI transaction after the full rear power/MCLK/reset sequence, but returned `-ENXIO`. A one-shot Windows KD session plus the exact installed QTI sensor/platform blobs now confirm CCI0/master1, FAST 400 kHz, Linux address `0x10`, GPIO110/reset, MCLK1 19.2 MHz and the existing rail order. The Windows sensor configuration identifies using a 16-bit read at `0x300b`, expected `0xd855`; r3e instead used a generic three-byte read from `0x300a`.

E002b-r3f is prepared as a transaction-only correction. Its module and candidate initrd both build byte-identically across two clean builds. Golden is unchanged. The GRUB audit found no camera-blocking parameter; future accepted camera gates must, however, pass a second strict boot without `clk_ignore_unused pd_ignore_unused` so those permissive flags cannot mask missing DT ownership.

## Exact SP11 camera hardware

- rear RGB: OmniVision **OV13858**, `OVTID858`, `MSHW0491`;
- front RGB: Sony **IMX681**, `SONY0681`, `MSHW0490`;
- front IR/Hello: ST **VD55G0**, `SMO55F0`, `MSHW0492`;
- camera platform: Qualcomm **Spectra 695 / X1E80100**, Surface `MSHW0495`.

## Windows-derived board routing

The exact installed `CAMP_PCFG_MSHW0495.bin` and `qccamplatform8380.sys` were decoded/reversed. The driver parser proves the packed platform connection fields and the flattened CCI-master split.

| Sensor | CCI route | Receive PHY | Physical mode |
|---|---|---|---|
| OV13858 rear | **CCI0 master1** | **CSIPHY1** | 4-lane D-PHY |
| IMX681 front | **CCI1 master1** | **CSIPHY2** | **1-trio C-PHY** |
| VD55G0 IR | **CCI0 master0** | **CSIPHY0** | to be finalized later |

Front IMX681 C-PHY is independently proven by Microsoft's own sensor register program: `CSI_SIGNALING_MODE (0x0111) = 3`, with Linux CCS definitions independently identifying value 3 as CSI-2 C-PHY.

Windows MIPI-CSI MMIO resources line up with upstream X1E CSIPHY0/1/2/4 and CSITPG blocks, so Windows is using the same receive fabric Linux models.

## Rear OV13858 first-target facts

Windows power/resources:
- reset GPIO **110**;
- MCLK **cam_cc_mclk1_clk @ 19.2 MHz**;
- LDO6_M 1.8 V;
- LDO1_M 1.2 V;
- LDO5_M 2.8 V;
- LDO16_B 2.9 V;
- exact D0/D3 order/delays are in E001 `power-map.md`.

Probe:
- Linux 7-bit slave address **0x10**;
- ID register **0x300b**;
- expected ID **0xd855**;
- Qualcomm FAST CCI mode.

Transport:
- VC0 / RAW10;
- four lanes (`laneAssign=0x3210`);
- Windows route **CCI0 master1 -> CSIPHY1**;
- 474.24 MHz RAW pixel rate => **1.1856 Gbit/s per lane**, **592.8 MHz link frequency**;
- Microsoft's PLL is not mainline's stock 540/270 MHz OV13858 profile (`0x0300=0x05`, `0x0301=0`, `0x0302=0xf7`, `0x0303=0`).

Therefore E002 must not simply wire the generic mainline OV13858 mode and call it parity. Reuse the upstream driver infrastructure, but introduce/audit an SP11 Windows-derived mode/link profile.

## Reuse boundary

Reuse upstream Linux:
- X1E CAMSS;
- CCI;
- D-PHY/CSID/VFE/media-controller infrastructure;
- generic OV13858 driver architecture.

Derive Surface-specific behavior from Windows:
- board routing;
- power/reset/regulator sequencing;
- MCLK;
- sensor modes/PLL/link frequency;
- front C-PHY extension;
- later privacy LED/IR illumination and image-quality parity.

## Remaining Windows parity observations

Not blocking rear E002:
- exact runtime `settleTimeNS` value used by Windows receiver;
- privacy LED transition timing/ownership;
- whether any specialized profile changes receiver routing.

Keep them on the parity backlog; do not guess them into Linux.

## Historical next action at that snapshot — completed/superseded

**E002b-r3f — Windows-exact rear OV13858 identity transaction.**

Reuse the accepted r3d DT/power route byte-for-byte and change only the r3e identity transfer to a 16-bit read at `0x300b`, expecting `0xd855`. First test permissively; if it passes, repeat without `clk_ignore_unused pd_ignore_unused`. Do not add/start CSI streaming until this identity lifecycle is proven.


## E002b-r1 accepted — isolated camera regulator providers

The first E002b attempt exposed a regulator-provider isolation bug: adding PM8550-B LDO16 into the existing Golden `regulators-0` provider caused that whole provider to fail registration, cascading into audio and Wi-Fi deferrals. This was not a missing-kitchen DTB.

E002b-r1 fixes the architecture by registering PM8550-B LDO16 and PM8010-M LDO1/LDO5/LDO6 in separate camera-only RPMh provider devices with no registration-time voltage constraints. The one-shot r1 boot passed with Wi-Fi, playback, capture and CAMSS intact; all four new camera rails remained at 0 users / 0 mV.

Next gate: E002b-r2 rear OV13858 identity probe. The probe module must be candidate-initrd-only; the shared Golden `/lib/modules` tree must not be modified. No CSI endpoint or streaming is allowed in r2.

## 2026-08-29 — RT-CDM startup dynamic ownership narrowed; 0020 remains unreachable

The `0019` 20-hole policy was intentionally conservative and is now superseded by a narrower same-machine Windows proof. Hash-pinned KMD entry/return capture proves `qccamisp8380+0x26838` leaves `period_cfg +0x8c` and the five previously live-volatile register identities unchanged in all four startup packets. Three in-stream MMIO samples then separate startup programming from live hardware state: `+0x8c` reads back zero, `+0x3b70` remains stable during the bounded samples, and `+0x3d78..+0x3d84` mutate continuously.

Crucially, the 16 non-period words are identical in both independent Windows startup command corpora and in the fresh KMD entry capture. Zeroing only the 46 DMI address words plus the four `+0x8c` words makes the independent command streams byte-identical. They are therefore exact **startup-template data**, not materializer caller-dynamic patches; their later live behavior must not be inferred from their startup value. The new ownership extractor SHA-256 is `4309c598eed431cb6d0e83461ce4cf917195ec90a6fd1c9123487a3d76f113e3`; oracle SHA-256 is `402510679bae860f801166bd7ff36834ca8284650aa29d64f1c08d7c6afda856`.

Static `0020-x1e-rtcdm-startup-dynamic-ownership-unreachable.patch` refines `0019` without rewriting it: the private materializer now has exactly four caller dynamic values, all `period_cfg +0x8c`, with valid mask `GENMASK(3,0)`. The 16 invariant startup words remain in the exact caller-provided normalized templates. Refined static materialization still decodes both independent variants to 278 commands / 2,131 ordinary writes / 46 DMI commands. Patch SHA-256 `147b89961803f3812c10dfd6f89cc00a4273d077514fc39756e5eb78f2d2d86e`; inspection JSON `a589a5546342bb9ad127bc6b5b880071cb1be35bdc8327524b7e521eb48f4add`; module `ccafdf9e94ec6e5e1609bb5e36ec8c1f6bb97055d8e6a4ce80a09c3cecd73d2f`. Build diagnostics are zero, forward/reverse reconstruction passes, strict checkpatch has zero code/style checks, and CAMSS remained unloaded.

**Next:** keep runtime blocked. Close the upstream production/value rule for the four start-dependent `period_cfg +0x8c` words and define how the later live-mutating `+0x3b70/+0x3d78..+0x3d84` state participates in a private unreachable start/update orchestrator. Do not convert their captured startup values into live-state assertions. No FIFO0 submission, VFE1 PIX enable, IMX681 transmission or Linux front frame is authorized.
