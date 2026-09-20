E004hs OFFLINE ORIGINAL SPMI COMMON CONTROLLER FULL DIRECT-CALLER AUDIT PASS (2026-09-20): SP7 remote debugger setup was blocked BEFORE any NEW Windows boot/KD session; E004hs LIVE OBSERVER WAS NOT RUN, protected Golden remains original a668186f-df85-4238-9983-f7b28455ec84. Original SHA-pinned qcspmi8380.sys provider publishes THREE callback slots: interface+28 standalone READ at SPMI+13a0, interface+30 direct WRITE at +1660, interface+38 masked READ-MODIFY-WRITE at +1920. Scanning ALL original SPMI executable sections found EXACTLY FOUR direct calls to shared controller+64d8: standalone read +15b4 (w0=1), direct write +1870 (w0=0), masked read +1b38 (w0=1), masked write +1b70 (w0=0 only after prior success). Common entry arg convention original w0 operation, w2 bus, w3 SID, w4 assembled register address, x5 data pointer, w6 data length; distinct from incoming callback registers. Synthetic timer WRITE span filter 1..256-byte overlap ee3e..ee41 tested, but no proof original lengths cannot exceed 256 or other indirect/driver/firmware paths absent. 51 original ARM64 mutation negatives + 22 synthetic filter checks PASS, original E004hr evidence scope pinned. No first idle 0x93 writer, live controller request, real silicon completion or independent physical current/pulse/host-fault cutoff demonstrated. New shared-controller live trace proposal explicitly UNEXECUTED, do not treat as log or stale KD session. Linux IR/flash/PAM OFF, E004fs/E004ge gate BLOCKED. See E004hs README.

E004hr FRESH EARLY ORIGINAL WINDOWS/SP7 KD ALTERNATE SPMI MASKED-RMW OBSERVER COMPLETE (2026-09-20): original SPMI module load at uptime 11.792s base fffff8037e280000 and PMIC base fffff8037e220000; persistent +1920 w2 low16 ONE-REGISTER timer address ee3e..ee41 conditional trap, independent one-shot +1924 alternate unfiltered control, separate +1664 direct-write control all armed BEFORE device initialization. +1664 direct positive HIT naturally 15.973s x2=0x00019246 x4=1 non-timer. Neither +1924 alternate one-shot nor +1920 timer predicate hit; both original alternate breakpoints remained ACTIVE/UNCONSUMED at final manual pause uptime 66.474s. Thus NO observed alternate callback entry in selected bounded window with direct positive, NOT proof it was never used, no full legacy/context-derived coverage, NO first 0x93 timer writer, silicon completion, optical pulse/current/independent fault-off. Original 10047-byte SP7 KD log SHA 70bbb26c0b13ea575d88c6954ad9eeb909ef2bcabd98fbfe8ae3b97886a8000f archived ZIP SHA a445f4e059e2feb58d6d990412430e71b755f9b821c70d554c85ff7b4611cfd3; verifiers + 23 mutation negatives PASS; breakpoints/load events cleared, log closed, KD stopped. Windows normally returned to NEW independently guarded Golden boot a668186f-df85-4238-9983-f7b28455ec84, saved v19c, EFI order unchanged, camera idle, native IR/flash/PAM OFF. This one-use E004hr is CONSUMED: DO NOT REPEAT alternate idle nonhit. Next genuinely DISTINCT offline trace actual PMIC consumers of interface +0x38 or future common SPMI controller +0x64d8 real controller-write observer with correct operation/address/count and positive control. See E004hr README.

E004hq ORIGINAL LIVE SPMI ALTERNATE MASKED RMW CALLBACK GAP OFFLINE PASS (2026-09-20): after consumed E004hp early filtered timer-range watch of ONLY original qcspmi8380+1660 returned zero matches but separate natural non-timer control, NEW OFFLINE audit found original SPMI provider's NEXT +0x38 slot points to distinct original callback qcspmi8380+1920; prior ORIGINAL E004hn byte-preserved LIVE Windows interface dump independently shows PMIC+3d040=[live SPMI+1660] and adjacent PMIC+3d048=[live SPMI+1920]. SHA-pinned original ARM64 +1920 code accepts caller packed selector w2, requested masked value w3, mask w4; on its successful one-byte controller READ at +1b38, synthesizes (old & ~mask)|(new & mask) at +1b54..+1b64 then calls controller +64d8 directly at +1b70 for WRITE, NO direct SPMI+1660 call. E004hp's +1660/+1664 breakpoints CANNOT see these +1920 controller writes; crucially +1920 w4=MASK NOT byte count, so original span filter cannot be copied to that callback. This identifies installed alternate WRITE-CAPABLE path/observer gap, NOT an observed +1920 entry, actual ee3e..ee41 transaction, requested 0x93, first-writer, bus completion or physical off. Original provider/consumer/archive immutable verifier plus 48 negative tests PASS, NO new Windows/KD/PMIC/SPMI/camera/emitter/Golden/login actions; independent guarded Golden boot e32d34ba-a422-44cb-a60b-4ff28b583bab, native IR/PAM OFF, E004fs/E004ge physical gate BLOCKED. Next distinct early observer must separately classify +1920 masked read-then-write and +1660 plain writer, or monitor validated common controller+64d8 without misreading w4. See E004hq README.

E004hp FRESH EARLY WINDOWS/SP7 KD TIMING-SPAN WATCH WITH INDEPENDENT CALLBACK CONTROL COMPLETE (2026-09-20): Pre-load kernel KD 10.950s, real original SPMI load 11.771s (base fffff80359180000), PMIC base fffff80359120000. Armed PERSISTENT conditional SPMI+1660 software entry filter for any 1..256-byte packed-selector LOW16 address span intersecting timer 0xee3e..0xee41; separate ONE-SHOT unfiltered original SPMI+1664 same-function control armed before device init. CONTROL genuinely HIT at 16.819s: x2=0x00019246, x4=1 non-timer 0x9246. IMPORTANT control action mistakenly used invalid combined-register WinDbg syntax, temporarily stopped kernel; manually read actual x2/x4/LR with separate valid register commands, resumed. Captured LR at +1664 after PAC signed, DO NOT claim exact unhashed PMIC return. At separate manual break uptime 30.921s, persistent filter still active; corrected its initially malformed combined-register ACTION syntax (condition unchanged) to separate r commands+immediate gc, resumed. Final manual pause uptime 58.415s showed SAME persistent filtered SPMI+1660 breakpoint ACTIVE, zero original timer-span hit markers in window; this ONLY bounds non-observation at selected callback/low16 address span, does NOT establish 0x93 first-writer, no other writes, original silicon completion, or physical current/pulse/host-fault off. All debugger BPs/load events cleared, log closed, SP7 KD stopped; Windows normal reboot to independently VERIFIED NEW Golden Linux boot e32d34ba-a422-44cb-a60b-4ff28b583bab, v19c kernel/GRUB/EFI order and camera idle unchanged. Original SP7 KD log 12707 bytes, raw SHA 74d5d5b73cc29a96e6fcc7be73dd4b3f02ffe68144bfd6a9e3d5827ae1405472 and archive ZIP SHA a3ec537cd31f8d03f8c764828321584e5feac68482a96533f3d934965a8a8942, no key. Verifier and 28 original evidence/Golden scope negative mutations plus 26 synthetic overlap/invalid-input filter cases PASS. This one-time E004hp is CONSUMED: no rerun of same selected SPMI timer no-match observer. Original idle timer 0x93 source UNKNOWN; native Linux IR/flash and PAM/login OFF, E004fs/E004ge independent optical/electrical cutoff gate BLOCKED. Next seek independent alternate/pre-OS/reset writer or actual timer transaction with original full bus/SID/span and completion, and validate all short debugger action syntax before any live arming. See E004hp README.

E004ho FRESH EARLY WINDOWS/SP7 KD SOFTWARE SPMI POSITIVE CONTROL PASS (2026-09-20): original SP7 KD preboot armed qcspmi8380+0x1660 one-shot at original SPMI DRIVER LOAD uptime 11.809s (before normal device init); real callback HIT during natural Windows boot at uptime 16.243s, whereas prior E004hn armed late at 35.654s and had no idle hit through 85.089s. NEW ORIGINAL call metadata: x2 packed selector 0x00019246 (software bus nibble 0, SID nibble 1, start address 0x9246), x4 ONE byte, LR original qcpmic8380+0x23bec. Live Windows PMIC+0x23ba8..+0x23be8 and hash-pinned original ARM64 image verify masked ONE-byte write call path, w1 prepared zero; w1 itself NOT captured at SPMI entry, no buffer/value logged. Demonstrates first natural non-timer SPMI software callback positive control and WHY postinit hook can miss early activity; does NOT capture a timer address ee3e..ee41, first idle 0x93 writer, controller status/silicon completion or optical/electrical/autonomous off. Only transient software code breakpoint, no manually issued camera/flash/PMIC/data-write action. SP7 original 12007-byte KD log raw SHA fdf6a5118cecce073046cfc8382141d2e9b4d4cf2a0aec74a612683fc2af2e39 archived, all breakpoints cleared/log closed/KD stopped. Windows normal reboot to NEW independently verified Golden boot 842c0fe1-499b-4eff-88ba-bc5392edddcd; kernel 7.1.5-sp11-render-parity-v4+, saved GRUB v19c, EFI order preserved and BootNext empty, camera idle. Verifier and 33 in-memory evidence/OEM negatives PASS; native IR/flash and PAM/login OFF, E004fs/E004ge physical gate BLOCKED. E004ho CONSUMED; next distinct early scoped timer-range observer must have separate real positive control, actual bus/SID/span and nonstall cleanup. See E004ho README.

E004hn LIVE SP7 KDNET / SP11 Windows read-only SPMI interface ID PASS and bounded idle nonhit (2026-09-20): NEW distinct Windows boot, fresh PMIC base fffff8033de40000 at kernel uptime 11.819s, PMIC interface +3d010 ALL ZERO at initial module load. At uptime 35.654s, SPMI base fffff8033dea0000 loaded; real PMIC+3d040/+0x30 interface slot = fffff8033dea1660 = actual qcspmi8380+1660, verified by live in-memory ARM64 disassembly. CONFIRMS original E004hl static SPMI bus-facing raw-write callback really installed after Windows normal startup. A single bounded idle one-shot software breakpoint at qcspmi+1660 was armed after init; at manual stop uptime 85.089s breakpoint remained ARMED and last event manual interrupt: NO observed callback entry or positive control during this limited interval; cannot infer earlier first writer, bus traffic, 0x93 origin, actual SPMI completion or optical safety. The temporary software breakpoint may patch code while armed; NO manual debugger data/PMIC register writes, Camera preview or flash action. Cleared all BPs/exception load filters, closed original 12,995-byte SP7 KD trace (raw SHA 81cf7b9e0655a98902e3f54a1973a1d3a8134077b6a6065a469c96148f059643), stopped SP7 KD; normally rebooted Windows to independently verified NEW GOLDEN Linux boot de81c0ac-01e1-4fcd-a473-744b5791ffcc, v19c kernel/GRUB/EFI unchanged and camera idle. Trace ZIP+verifier and 15 in-memory negative tests PASS; E004hn is CONSUMED, do not repeat its no-hit idle watch. Native Linux emitter/PAM OFF; E004fs/E004ge independent physical current/irradiance/pulse/host-fault cutoff gate BLOCKED. Next genuine high-signal observation: distinct EARLY SPMI observer with non-timer positive control from before driver setup and full SID/address-span/return correlation; do not claim idle first-writer before trace. See E004hn README.

E004hm ORIGINAL SPMI CONTROLLER MMIO COMMAND+STATUS OFFLINE PASS (2026-09-20): SHA-pinned OEM qcspmi8380.sys provider callback +1660 decodes caller selector and calls original controller helper +64d8 via +1870 with original payload/count. The original helper writes controller data MMIO at +674c/+6788, command MMIO at +67e0, then finite host CPU polling initial counter 0x190 at +6818, controller status reads at +684c/+6854, routes explicit status/errors and returns original code via +6b54 -> provider+1874/+18e4. This newly maps exact software request→MMIO/status boundary; does NOT prove real SPMI payload delivery/physical PMIC register update, first actual timer idle 0x93 writer, autonomous hardware timer, emitted IR current/irradiance/pulse/host-fault cutoff. Exact original ARM64 instruction audit and 79 in-memory mutation negatives PASS. No new Windows/KD/camera/SPMI/PMIC/LED/Golden/PAM activity; native IR OFF. Next separately-authorized genuinely different live read-only SPMI+1660 positive control followed by +64d8 address-span/return status (early enough for first-writer question); do not reuse consumed traces or confuse finite host poll with autonomous emitter fault-off. See E004hm README.

E004hl SPMI PROVIDER CALLBACK IDENTITY OFFLINE PASS (2026-09-20): original hash-pinned qcspmi8380.sys+3e38..3f38 builds genuine 0x70-byte WDF interface output buffer at sp+110 and stores function qcspmi8380.sys+1660 at buffer+30 (sp+140; neighbor slot+38 points +1920). Original PMIC WDF query targets same GUID 72c96e71-eb2d-48e3-99ac-9894a59f9c4c into PMIC+3d010, raw writer +23f24 loads callback at PMIC+3d040 / interface+30 and calls at +23f3c. SPMI candidate callback+1660 saves packed original selector w2, source x3, count w4; original +177c..1788 extracts SID bits16..19, addr high8, addr low8, bus bits20..23. This resolves ORIGINAL STATIC callback identity below PMIC raw writer, but neither proves WDF live query succeeded nor records a genuine Windows +1660 entry/hardware transaction or first 0x93 timer writer. 33 in-memory original-code mutations rejected; NO new Windows/KD/camera/SPMI/PMIC/emitter/login actions. Golden unchanged, native IR OFF, E004fs/E004ge physical optical/electrical cutoff gate BLOCKED. Next independent read-only lower-layer positive-control runtime observer, only under fresh separately staged authorization; do not repeat consumed PMIC idle no-hit traces. See E004hl README.

E004hk ORIGINAL PMIC↔SPMI SOFTWARE BUS INTERFACE OFFLINE PASS (2026-09-20): original hash-pinned qcpmic8380.sys and qcspmi8380.sys share real 16-byte GUID 72c96e71-eb2d-48e3-99ac-9894a59f9c4c; PMIC+3938..3974 queries WDF interface with GUID PMIC+37058, 0x70-byte output struct PMIC+3d010; original SPMI+3ef8..3f38 builds compatible descriptor with GUID +a1d8. PMIC original RAW helper +23dc8 packs normalized SID|(bus<<4) and 16-bit register into w2 at +23ed8/+23edc, then calls x15=[PMIC+3d040] with x0=[PMIC+3d030] handle, x3 original payload, w4 length at +23f3c. Verified original four raw BL callers +23a04/+2fc54/+303b4/+32c2c. Sample bus0 SID1 0xee3e -> selector 0x0001ee3e is SYNTHETIC decoder fixture, NOT actual Windows SID or physical emitter wiring. No live SPMI interface binding/dynamic transport callback, actual timer address write, first idle 0x93 origin, hardware current/pulse/cutoff established. 32 in-memory GUID/opcode/selector negatives PASS. No new Windows/KD/Camera/PMIC/LED/Golden/PAM action; native IR OFF. Separate read-only downstream live interface context/function inspection would be needed before arming an OBSERVER, not an emitter. E004fs/E004ge independent physical safety gate remains BLOCKED. See E004hk README.

E004hj SAME-SESSION real SP11 ARM64 OFFLINE controlled comparison PASS (2026-09-20): six rotation-balanced trials each of three transport modes, every mode exact original maintained HLOS pixel output + strict full-range NV12 bridge + real pinned YuNet/SFace on SAME repeated OpenCV public grayscale ROI (144 measured ephemeral public features), 1 OpenCV/OMP/OPENBLAS CPU thread. Median FIRST public model feature: original 8 separate process launches 107.275 ms, original 8-frame whole batch 347.804 ms, NEW uninstalled E004hi provisional stream 79.675 ms. Median total all 8 model features/worker exit: single 879.877 ms, whole batch 637.374 ms, stream 815.174 ms. Stream total MAX of n6 958.828 ms > single MAX 901.262 ms; nearest-rank p95 at n6 equals maximum, no statistical tail/real camera FPS guarantee. Thus stream has lower observed median first/total than single starts here but not proven consistent; original batch achieves lower observed median total at expense of first result. All eight model outputs byte-parity original C and stream DONE/exit0, no native IR image/freshness/liveness/accuracy/auth/watchdog. Offline verifier, six timing negatives and 16 scope negatives PASS. No Windows/KD/camera/PMIC/LED/Golden/PAM action; native emitter OFF. Original PMIC idle 0x93 first writer UNKNOWN; E004fs/E004ge physical optical/electrical gate remains BLOCKED. See E004hj README.

E004hi OFFLINE FUNCTIONAL PASS on real SP11 ARM64 (2026-09-20): NEW uninstalled `src/sp11-camera-hlos-worker/sp11-offline-nv12-stream.c` and bounded no-auth stream client wrap EXACT original eight-file HLOS C pixel core. 8 strict immutable sequential neutral-NV12 public OpenCV visible-light ROI frames sent one by one; byte-identical original C one-frame output each; all 8 actual pinned YuNet/SFace (1,128) features finite in RAM. Prior outputs PROVISIONAL; exact DONE/count/EOF/child-exit0 needed before session is complete. Malformed first inputs produce no output; malformed late input/excess after first can produce prior provisional frame but NO DONE and invalidates WHOLE session; caller-fault terminal no rearm. 9 original C negative cases, 8 client runtime terminal-fault cases, 12 constructor/deadline negatives PASS; original model/pixel/source hashes pinned. One NOT paired streaming trial: first public feature 139.614 ms, eighth 1091.276 ms, DONE/clean exit 1093.439 ms; NO CLAIM of perf advantage vs prior benchmarks, real camera throughput, actual IR face, liveness, auth, enrollment or autonomous host-fault watchdog. No Windows/KD/camera/PMIC/LED/Golden/PAM modifications, native IR OFF. PMIC idle 0x93 first writer UNKNOWN, E004fs/E004ge physical gate BLOCKED. Next gather same-session paired stream vs original single/batch costs before choosing transport. See E004hi README.

E004hh PASS real ARM64 offline (2026-09-20): compared UNMODIFIED maintained original HLOS C `--frames 8` whole-batch input validation/output-after-all-eight with eight separate maintained C process launches, then SAME pinned YuNet/SFace/strict NV12 bridge on 64 repeated-identical public grayscale demo-frame model extractions in four alternating paired runs. Original C single vs batch output BYTE-IDENTICAL, truncated or overlong eight-frame input nonzero exit and ZERO stdout. Median 8-frame HLOS CPU wall: 8 separate 362.453 ms vs one batch 278.794 ms; median time FIRST public model feature separate 82.220 ms vs batch 344.158 ms (batch withholds all eight outputs); median all 8 features separate 817.692 ms vs batch 634.121 ms. n=4 each p95 nearest rank = measured maximum, no extrapolated streaming FPS, NIR image quality, freshness, liveness/auth or actual secure controller/watchdog. Original model/image/embeddings NOT committed; verifier+6 malformed timing and 13 negative scope cases PASS; no new Windows/KD/camera/PMIC/LED/Golden/IR/PAM activity. First PMIC idle 0x93 writer still unknown; E004fs/E004ge remain BLOCKED. Next isolated bounded persistent streaming worker needs explicit frame/error framing to improve BOTH first result and throughput, or distinct first-timer-owner research. See E004hh README.

E004hg PASS on real SP11 ARM64 (2026-09-20): no-emission CPU benchmark of ACTUAL maintained HLOS C subprocess -> full-range NV12 bridge -> pinned original YuNet/SFace OpenCV 4.12, 2 warmups + 8 repeated same PUBLIC visible-light gray ROI. OMP/OPENBLAS/OpenCV all 1 CPU thread. One-time model object init 53.465 ms; 8-trial medians maintained HLOS C launch/process/output 47.888 ms, strict bridge 1.616 ms, actual YuNet+SFace 58.846 ms, total sequential 109.328 ms; nearest-rank p95 total 111.321 ms (at n=8 this equals observed MAX). ru_maxrss entire testing Python process 188172 KiB, NOT production model memory. No real camera cadence, fresh independent frames, native NIR darkness, liveness, accuracy or login demonstrated; each trial replays same public fixture, outputs no pixels/features/scores. Result and original source hashes plus verifier and 6 negative timing tests PASS. No Windows/KD/camera/PMIC/LED/Golden changes, native IR/PAM OFF. Next optimize bounded per-frame host C process overhead with isolated persistent worker, or pursue separate OEM first 0x93 writer; do not claim 60fps or authentication. See E004hg README.

E004hf PASS OFFLINE (2026-09-20): ORIGINAL OEM alternate flash-start function flash+48c8 direct called at exactly +6638 (general 12-byte configuration/context path) and +6a20 (separate branch requiring context byte +88 zero and +81 one). That start explicitly requests current -> timer helper flash+4dd0 -> strobe; normal subtype-0 direct dispatch DOES NOT exhaust lifecycle. The ORIGINAL FLASH TIMER HELPER itself supplies FIXED 1270 ms (0x4f6) for two logical sources if enabled, encoded by PMIC four-channel callback to BYTE 0xfe; disabled requests produce 0x00. Thus it does not directly produce the Golden idle 0x93 as a new requested byte, but earlier/indirect/firmware writes or retained state remain possible. 19 in-memory PE mutation negatives PASS, no new Windows/KD/camera/PMIC/emitter/login actions. First 0x93 writer UNKNOWN; E004fs/E004ge independent physical gate BLOCKED; protected Golden unchanged, native IR/PAM OFF. Next distinct lead look for alternative caller-supplied timer requests or pre-driver/firmware reset defaults, not repeat fixed-helper or subtype0 direct tracing. See E004hf README.

E004he PASS OFFLINE (2026-09-20): combine E004hd LIVE Windows PMIC four-channel table +39470/+90 -> +285c0 with original SHA-pinned flash/PMIC ARM64: subtype-0 direct command sequence current 0x802f0fb0 -> PMIC+270c0, trigger input 0x802f0fcc -> +27f20, trigger mode 0x802f0fd0 -> +281e0, strobe 0x802f0fc8 -> LIVE handler+285c0. Timer helper flash+4dd0 sends distinct IOCTL 0x802f0fac -> PMIC+26d50 through table+28, and original flash type-0 direct branch does NOT call timer helper; only two original direct timer-helper calls +4938 alternate configuration and +5b2c type-2. This consolidates already known E004fi/fl/gi with NEW E004hd in-memory handler identity. It does NOT rule out indirect/earlier/pre-OS timer writes, establish first writer of idle 0x93, or prove optical/electrical autonomous off. PE verifier and 19 in-memory negative tests PASS; NO NEW Windows/KD/camera/PMIC/LED actions, native IR/PAM OFF, Golden unchanged. See E004he README. Next focus genuinely distinct first timer-register writer/firmware origin or offline fail-closed face worker, not repeating OEM subtype0 static map.

E004hd COMPLETE (2026-09-20): fresh read-only Windows/SP7 KD live pointer ID SUCCESS. Early OEM PMIC driver base fffff803477a0000 loaded kernel uptime 10.807s, module-global +3b8d8 ZERO. At uptime 26.746s during passive normal Windows idle, same global equals live module+39470, and dereferencing its +90 slot equals live module+285c0 (original OEM four-channel flash callback); original target instructions disassembled on SP11 Windows. This NOW CONNECTS E004hc original flash IOCTL 0x802f0fc8 +7378 indirect dispatcher to the REAL Windows idle handler target, not merely an offline guessed table. E004hd did NOT execute the IOCTL/callback, issue a PMIC write or find first writer of Golden idle timer 0x93, and provides no emitted-light/electrical cut-off evidence. Original 10284-byte SP7 KD log SHA 72d567f1f679d307d59519376e5da56b4f39436aea2f06a254f4506e6afe332a byte-for-byte archived, verifier and 12 negative tests PASS. KD cleared/stopped and Windows normally restarted into independently verified protected Golden Linux new boot 9fe8087b-9476-4ea1-9d26-fda7b59c9828, original kernel/GRUB/EFI and camera idle. Linux emitter/PAM OFF; E004fs/E004ge physical gate BLOCKED. Next distinct lead analyze subtype-0 OEM flash normal lifecycle and first timer writer through this confirmed handler, do NOT repeat E004hd read-only pointer watch.

E004hc complete (2026-09-20): exact SHA-pinned OEM qccamflash8380.sys and qcpmic8380.sys share 16-byte interface GUID 20952871-af3d-4a8a-9e47-cb346507b95b; original flash IoGetDeviceInterfaces obtains PMIC endpoint device object at global +2a7d0, sends original four-byte command IOCTL 0x802f0fc8 via IoBuildDeviceIoControlRequest/IofCallDriver. PMIC original IOCTL dispatcher at +71e0 matches SAME literal +7c10, branches +7378, checks 4-byte input and invokes indirect per-object handler at offset +0x90. Do not conflate this path with E004ha generic write callback +32b70: target of IOCTL +0x90 remains to be recovered and original 0x93 timer writer remains UNKNOWN. Original PE + 19 in-memory negative tests PASS, no new Windows/KD/camera/PMIC/LED; Golden unchanged, native IR and PAM OFF. Next inspect actual PMIC IOCTL +0x90 handler-object construction, not re-run idle callback no-hit watch. See E004hc README.

E004hb completed (2026-09-20): distinct Windows/SP7 early KD live original PMIC callback addresses +2f918, +2fdd0, +32b70. Three ba e1 breakpoints exceeded available processor-0 debug resources; no three-breakpoint observation occurred. After manually clearing them, TWO hardware watches (+32b70 generic writer, +2f918 general descriptor) remained armed from Windows uptime 11.791s through 34.451s, with zero actual callback hit markers but NO positive control. Type-0x4a descriptor +2fdd0 was not monitored during the bounded run. Do not infer callbacks never execute or timer has no writer. All KD hooks cleared, SP7 KD stopped, original 10463-byte log SHA 9a92d9ff07fd4d9876385edb05a8e9978f15774fdba24e941d3898b3fc645b9d archived and ten negative tests pass. Windows normal reboot returned protected Golden boot 91e918f6-a800-4a6a-9511-78cbc275a07c; unchanged GRUB/EFI, camera idle, native IR and PAM OFF. Next identify request that actually activates exported PMIC generic table, not another same idle breakpoint watch. See E004hb README/RESULT.

E004ha complete (2026-09-20): original OEM PMIC generic writer +32b70 appears at true callback table +3a510; code +2f918 / +20304 exposes four-function table head +3a4f8 and code +2fdd0 / +2021c exposes two-function suffix +3a508 on 0x4a descriptor path. Original writer accepts u16 address/u8 length and calls raw-write +23dc8. Offline verifier and 12 negative tests pass. Runtime invocation and first timer writer remain unobserved; Golden unchanged, native IR off. See E004ha README.

E004gz complete (2026-09-20): original PMIC raw write bypasses +2fc54 and +303b4 cannot overlap timer registers by original ARM64 address arithmetic. Remaining generic 16-bit address write at +32c2c is indirectly exported via genuine data callback slot +3a510; dispatch owner and 0x93 writer still unknown. Offline verifier and 11 negative tests passed; no devices operated. Golden remains protected, native IR off. See E004gz README.

**2026-09-20 E004gy LOWER-LEVEL ORIGINAL PMIC RAW-WRITE HARDWARE KD POSITIVE CONTROL / GOLDEN RETURN PASS:** Fresh SP7 KD -d -bonc first pause SP11 Windows uptime 10.935s before qcpmic8380.sys loaded; second pause 11.756s original PMIC live base fffff80220520000. ba e1 hardware execute original raw-write helper +23dc8 fired uptime 17.902s, w2=4716 length w4=1; original caller lr fffff80220543a08 = masked helper return +23a08. Initial KD r x30 register alias error AFTER actual trap manually resolved using r lr and kb 6, then hardware bp rearmed with verified simple .printf auto-continue. 26 corrected hardware raw entry records, all 1-byte and all caller +23a08, no logged raw-write span overlapping timer ee3e..ee41. Other original raw-write direct callers 2fc54,303b4,32c2c NOT observed in this bounded Windows boot; original timer first-writer/0x93 source remains UNKNOWN. Manual final KD pause uptime 42.472s confirmed ba e1 still active, all breakpoints cleared and log closed; Windows normal reboot returned protected Golden new boot 836f28b9-850a-486a-9742-7152ebbe23e2, unchanged kernel/GRUB/EFI, no BootNext, camera-idle guard PASS, SP7 KD stopped. Original 12263-byte SP7 log SHA 0b072371f455a8aaa253582fcba3a8af2d85ffd58e9b1c920a5da103f6cf945b byte-for-byte archived; original verifier and 10 negative tests PASS. No new camera preview/manual PMIC writes/fault injection/native IR/PAM or Golden modification. E004fs/E004ge physical hardware safety still BLOCKED. Next analyze bypass caller lifecycle or firmware initialization, do not repeat E004gy identity.

**2026-09-20 E004gy NEW LOWER-LEVEL OEM RAW PMIC WRITE HARDWARE KD PREPARED NOT EXECUTED:** E004gx confirmed true ba e1 original PMIC masked helper hardware traps (104 post-rearm records, no timer address w2). Pinned OEM ARM64 executable scan found raw write helper qcpmic8380+23dc8 has four original BL callers: 23a04 from masked helper and THREE direct bypass candidates 2fc54,303b4,32c2c. A block write can overlap ee3e..ee41 even if starting earlier; new fresh SP7 KD -d -bonc will hardware ba e1 raw write early boot and log start w2/length w4/link caller for positive and timer-overlap evidence, no camera/PMIC manipulations, then return Golden. Original E004gx consumed, physical emitter E004fs/E004ge remains BLOCKED.

**2026-09-20 E004gx EARLY WINDOWS HARDWARE PMIC EXECUTE BREAKPOINT SUCCESS / GOLDEN RETURN PASS:** SP7 KD -d -bonc paused SP11 Windows at uptime 10.934s before original qcpmic8380.sys appeared; second pause uptime 11.756s loaded original PMIC base fffff8028a000000. Hardware execute `ba e1 qcpmic8380+23968` (original masked register helper) armed. ACTUAL hardware trap at uptime 17.847s, nonemitter w2=4716 mask ff requested ff, caller qcpmic8380+2bd60: establishes positive control independent of prior software/bu hooks. Initial complex KD callback-command parser error occurred AFTER real trap; manually inspected and rearmed same hardware bp with simple raw-register .printf/auto-continue. Corrected hardware callback logged 104 post-rearm hardware helper-entry records (the first recorded entry may be the resumed originally paused invocation) across 36 address arguments, zero w2=ee3e..ee41. Does NOT prove absence before first hook, on other paths/cores/firmware, or origin of idle 0x93; does NOT demonstrate software bp missed actual timer request. Manual final KD pause uptime 22.176s verified hardware bp active, cleared all KD bps and closed original original SP7 log. SP11 Windows normal reboot returned protected Golden Linux new boot ad449a21-86c0-4194-b8a5-e297d750226a; original kernel, saved GRUB FullIO, EFI BootOrder, empty next_entry/BootNext, camera idle guard PASS. Original 13931-byte SP7 KD SHA ba6161d368be4d946e35c82064be2e16f0e87b50ea660e222c685ec1bb620de4 archived and positive 9 negative verifier checks PASS. No Camera/PMIC write/fault injection/native IR/PAM/Golden change. E004fs/E004ge physical gate still BLOCKED. Next genuinely different low-level PMIC write/transport caller analysis, not another same-helper watch.

**2026-09-20 E004gx DISTINCT EARLY WINDOWS PMIC HARDWARE BREAKPOINT PREPARED, NOT EXECUTED:** Audio project notes software INT3 boot bps missed GPIO writes twice; HARDWARE ba e1 immediately caught them (original audio 04-gpio-pinctrl.md). New E004gx will boot Windows once with fresh SP7 KD -d -bonc and set actual ba e1 on original qcpmic8380+23968 as soon as live PMIC image is loaded, logging first few non-emitter generic helper hits as a positive control and filtering timer w2=ee3e..ee41. No software bp no-hit inference, no camera/PMIC writes/fault injection; archive original evidence, normal return Golden. Previous E004gw consumed, native IR/PAM remains off; E004fs/E004ge physical gate blocked.

**2026-09-20 E004gw FRESH PERSISTENT PRELOAD KD TIMER-WRITER WATCH PASS, FIRST TIMER WRITER STILL UNKNOWN:** A NEW SP7 KD -d -bonc on SP11 Windows paused at uptime 10.948s before qcpmic8380.sys loaded. PERSISTENT deferred bu /w conditional original qcpmic8380+23968 generic masked-write helper filter w2=ee3e..ee41 set at FIRST pre-load KD break; second pause 11.770s confirmed actual PMIC base fffff803037c0000 and resolved active bp at fffff803037e3968. Windows boot/idle resumed without OEM preview; final KD pause at uptime 50.272s independently confirmed same filtered bp STILL ACTIVE, with ZERO actual timer-helper hit markers in original KD transcript. This bounds absence only at THIS OEM masked-helper entry during the post-resolution ~38.5s interval; neither earlier boot 0–11.770s nor PMIC DriverEntry pre-hook nor other firmware/low-level writers excluded; actual source of prior Golden idle 0x93 remains UNKNOWN. All KD breakpoints explicitly cleared, log closed, SP7 KD stopped; Windows normally restarted into protected Golden boot e305fe1c-0bd9-407d-bf8c-e56a19354b7e (unchanged kernel/GRUB/EFI, camera-idle guard PASS). One E004gw Windows boot consumed, old E004gv/gt/gs/gb identities not repeated. Original 14502-byte SP7 KD SHA 1c6d5a603f00c0b5d53f316abcb686a6d9b3b7f30a9542d30b17f997fb3c25a2 byte-for-byte archived; E004gw verifier and 11 negative tests PASS. No Windows camera/PMIC writes/fault injection, no Linux LED/PAM/Golden change. Physical E004fs/E004ge safety BLOCKED; next alternative low-level/firmware timer-owner analysis, not same debugger hook.

**2026-09-20 E004gw DISTINCT PERSISTENT DEFERRED PMIC TIMER-WRITER EARLY KD PREPARED, NOT EXECUTED:** After E004gv first early KD (boot PMIC unloaded at 10.839s then loaded at 11.659s, but one-shot conditional absent at end), plan new one-time Windows/KDNET with symbolic PERSISTENT address-filtered bu /w at qcpmic8380+0x23968 armed at INITIAL break BEFORE PMIC load. Must prove unresolved->resolved and persistent active hook at teardown, or actual marker for w2 ee3e..ee41, else cannot infer no write. No Camera/PMIC writes/LED/fault injection; Windows normal reboot and independent Golden verify. E004gv prior ID CONSUMED, physical E004fs/E004ge BLOCKED. See E004gw README/PREPARED.

**2026-09-20 E004gv FIRST EARLY KDNET BOOT-START PMIC LOAD WINDOW OBSERVED / GOLDEN RETURN PASS:** Fresh SP7 kd -d -bonc attached at SP11 Windows 26100 kernel uptime 10.839s with qcpmic8380.sys NOT loaded. After sxe ld:qcpmic8380; g, second debugger break at uptime 11.659s listed PMIC live base fffff80011fc0000, disassembled original generic PMIC masked-write helper RVA 23968 and armed conditional one-shot bp /1 /w for w2=ee3e..ee41. No actual timer-write hit marker. On final Ctrl-C at uptime 1:00.767 `bl` was empty: one-shot watcher could have been consumed by a nonmatching helper call; initial 0.82s PMIC load-to-hook gap also unobserved. FIRST WRITER / ABSENCE OF EARLY TIMER WRITES NOT PROVEN. Windows installed driver registry Start=0 Type=1 Group=Filter (boot-start). No OEM preview/PMIC writes/fault injection. All KD breakpoints disarmed, original 12536-byte SP7 KD log SHA 4c85099f3f02bb0b17c4fc5e15a22061ca1f84b14ca5dbd73f9e9e38c8af8e92 archived; 8 negative tests pass. Windows normal restart returned protected Golden boot 0f0b092e-538a-4391-a518-d7eab653f400, unchanged GRUB/EFI and idle camera guard PASS. E004gv consumed; next distinct E004gw pending persistent `bu /w` at INITIAL KD pause before PMIC image appears, with active-hook-at-teardown proof. Native LED/PAM OFF; E004fs/E004ge blocked.

**2026-09-20 E004gv FRESH EARLY KDNET PMIC-INITIALIZATION OBSERVATION PREPARED, NOT EXECUTED:** Original OEM qcpmic8380.inf SHA cd7ad772c04466f919928217b23e8d104b6fc67e5803205bb96998e643f31564 declares SERVICE_BOOT_START/Filter. E004gt original SP7 KD attached at Windows uptime 10.969 seconds, so prior postboot breakpoints structurally miss first ~11s. Distinct E004gv will try SP7 KD -d -bonc early connection and first module-load inspection, no OEM preview/fault injection/PMIC writes; if PMIC already loaded then report early initialization NOT observed and return Golden rather than claiming a timer-writer trace. One fresh Windows boot only, independent evidence, Golden rollback. No native LED/PAM change; E004fs/E004ge physical safety BLOCKED.

**2026-09-20 E004gu ORIGINAL WINDOWS PMIC TIMER-ORIGIN/PE-METADATA XREF AUDIT PASS (OFFLINE):** Fresh Ghidra of SHA-pinned OEM PMIC finds timer-register table 36d48 code xrefs 26e2c/26e60 (four-channel handler) and 27010 (single-channel handler); original ARM64 table reads and masked write-helper calls independently verified. Full 102 locally archived original Windows SYS binary scan finds the contiguous four ee3e..ee41 address DWORDs only in qcpmic8380.sys. Ghidra apparent extra timer-handler refs 364c4/364c8 are 438-entry PE GuardCF allowed-target METADATA, while 3faa0/3faa8 are .pdata UNWIND metadata, NOT extra runtime callback slots. Actual object dispatch pointers are 64-bit .data 39498/394a0 (previous E004gp). Four SHA-pinned relevant Windows drivers scanned across executable .text/PAGE/INIT: no direct literal MOV #0x93 in PMIC/PMICApps/flash; one at glink c740 is not evidence of a timer write. This does NOT exclude generic computed-address writes, driver/firmware/UEFI initial configuration, inherited timer state, or physical cutoff; early init owner remains UNKNOWN. E004gt original normal 8-frame preview 0/4 specific timer/config entry hits and E004fx consumed Golden idle 0x93 retained WITHOUT re-run. E004gu original PE/table/CFG/pdata verifier + 12 in-memory negative cases PASS. No Windows/KD/camera/PMIC/LED/GOLDEN/login change; E004fs/E004ge independent electrical/optical safety BLOCKED. See E004gu README/RESULT.

**2026-09-20 E004gt FRESH BOUNDED OEM WINDOWS TIMER-CALLER TRACE COMPLETE / GOLDEN RETURN PASS:** One distinct factory Windows Surface IR Front NV12 644x604 nominal 60fps preview collected exactly eight metadata-only frames in <1sec, successful StopAsync/Dispose, no pixels or templates saved. SP7 fresh KDNET live Windows PMIC base fffff8031b8a0000 / flash base fffff8031f940000 identified and original RVAs disassembled. Four one-shot automatic-continue hooks (PMIC timer4 26d50, timer1 26f30, flash timer wrapper 4dd0, flash config 48c8) all remain armed after capture: ZERO observed hits at those entries during bounded preview. DO NOT claim any actual timer setup / caller stacks, early initialization exclusion or hardware autonomy. Original SP7 KD raw SHA e10a1bc0c51085ba94dcd4a870c4adf739100294b62f55306dfdaba23bd994a0 and original Windows UTF16LE capture SHA aac4b8dfeb7df757623d7784cedf6b434272b45e72282ce80813febb17f48ec2 archived; offline evidence and eight negative tests PASS. All hooks disarmed, KD stopped, Windows normal reboot returned protected GOLDEN Linux new boot 6f958ff9-f46b-47c5-91ac-30a3a5b1aa47, GRUB/EFI unchanged, no camera processes/modules/nodes. E004gb/E004gs identities NOT repeated. Next focus alternative OEM timer default/early initialization ownership; physical emitter E004fs/E004ge remains BLOCKED; native Linux IR/PAM OFF.

**2026-09-20 E004gt NEW NORMAL OEM WINDOWS IR TIMER-CALLER TRACE PREPARED, NOT EXECUTED:** With E004gs PASS/golden-return e6cce90→7af8f4c committed, plan ONE separate normal manufacturer Windows 644x604 Infrared preview of at most 8 frame metadata/4 sec and fresh SP7 KDNET four one-shot auto-continue entry hooks on timer4/ timer1/ flash-timer helper/ flash config. This is distinct from consumed E004gb register writes/normal capture and E004gs passive no-camera diagnostic. First verify new actual Windows PMIC/flash module bases and ID; never use stale base, block on failed preflight. No manual LED override, firmware/PMIC writes, debugger fault injection, held strobe or pixel retention. Ensure finally StopAsync/Dispose, disarm KD only after preview stopped, archive fresh evidence and normal reboot to protected Golden. Native Linux emitter/PAM remain OFF, physical E004fs/E004ge unchanged. E004gt README/PREPARED.

**2026-09-20 E004gs FRESH PASSIVE WINDOWS KDNET TIMER BOOT COMPLETE, GOLDEN RETURN PASS:** SP11 one-shot booted Windows build 26100 ARM64 via direct EFI BootNext, SP7 KDNET attached to FRESH live qcpmic8380.sys base fffff8009ace0000 and qccamflash8380.sys base fffff8009f340000; direct live disassembly verified original timer4 RVA 26d50, timer1 RVA 26f30 and flash wrapper RVA 4dd0. Three one-shot read-only auto-continue hooks set AFTER Windows boot had 0 hits during passive idle with no intentionally initiated OEM camera preview; all breakpoints cleared and KD log closed. Therefore early boot timer programming / other dispatch is NOT excluded. Original SP7 transcript preserved byte-for-byte (10,792 bytes, SHA256 2d8f43c76e426b491f894184342f499cc5ad6dd2597295ee3a749555d35fb571), archived in E004gs and six negative verifier fixtures PASS. SP11 Windows normal restart returned GOLDEN Linux NEW boot bbb9ef1b-f1e5-4024-a636-44b5cc67c5a6; kernel, saved GRUB FullIO, EFI BootOrder, no BootNext, camera-idle guard PASS. Earlier E004gb consumed one-shot NOT repeated. No native IR, no Linux PMIC/flash, no PAM/login change; physical E004fs/E004ge remains BLOCKED. Next pursue distinct bounded E004gt Windows OEM camera-activation timer-only observer with separate fresh identity/record.

**2026-09-20 E004gs NEW WINDOWS-PASSIVE TIMER BOOT PREPARED, NOT YET EXECUTED:** User authorized fresh SP11 Windows reboot/SP7 KDNET. E004gs is separate from consumed E004gb and will initially perform no OEM camera preview, no LED/PMIC writes or fault injection: attach fresh KD to installed Windows PMIC, inspect loaded module/indirect four/single-channel timer callback initialization and PnP power state. Scope at most 64 read-only timer-callback hits if connection available; do not replay E004gb logs/capture. Persistent GRUB Golden saved_entry and EFI BootOrder preserved, only Windows Direct EFI one-time BootNext if all checks pass; after diagnostics clear all breakpoints, stop KD, boot back Golden and verify. Physical emitter current, irradiance/pulse and autonomous stuck-strobe off remain UNPROVEN; E004fs/E004ge stay BLOCKED. Preparation docs: E004gs README/PREPARED.

**2026-09-19 E004gr ACTUAL MAINTAINED HLOS C NV12→REAL YuNet/SFace ARM64 INTEGRATION PASS, IR/LOGIN OFF:** Added strict offline-only 644×604 full-range neutral NV12 grayscale→BGR image bridge that checks complete immutable batch/neutral UV and preserves exact Y luma without accidental OpenCV video-range black/white remapping. Recompiled actual original Windows-parity HLOS C processing worker in temporary directory; processed only pinned OpenCV Zoo public visible-light multi-person fixture crop converted to monochrome neutral NV12. Real processed output drives real pinned ARM64 YuNet one-face detection and SFace finite 128D feature in RAM. Same C worker on whole public group photo and synthetic blank fails closed at face probe (multiple/zero faces); short/long C frames and malformed UV/size/type rejected. Actual pixels change in C yet are copied without luma distortion in bridge; no imagery/templates/scores persisted. A public grayscale visible photo is NOT SP11 optical near-IR in darkness, identity/liveness, actual user enrollment or Windows Hello protected security parity. No camera/PMIC/Windows/KD, native emitter, PAM/login or Golden changes. E004fs/E004ge physical LED current/optical irradiance/actual pulse and autonomous fault-off remain BLOCKED. See E004gr README/RESULT.

**2026-09-19 E004gq REAL ARM64 OFFLINE YuNet + SFace INFERENCE PASS; NO NATIVE IR/LOGIN:** Used isolated /tmp Python 3.14 virtualenv (opencv-python-headless 4.12.0.88), official OpenCV Zoo SHA-pinned YuNet/SFace original ONNX weights and the official SHA-pinned public multi-person demo photo, all strictly OUTSIDE Git. Newly implemented userspace-only `sp11-offline-face-probe.py` loads actual neural nets and enforces exact-one-face extraction from properly bounded BGR frames, finite 128-element SFace features, and separate scalar diagnostic-only similarity with zero face-auth or login API. On SP11 AArch64, original YuNet rejects uniform zero-face synthetic 644x604 input and multiple faces in public photo; isolated public face crop gives single detection, aligned SFace in-memory 128D embedding and repeat-image self-consistency. Grayscale visible-light public crop also extracts a feature but is NOT near-IR optical/darkness parity or liveness proof. Invalid frames/features, swapped/unpinned/symlinked model files are rejected; OpenCV/model hashes pinned. Reproducible non-root /tmp-only asset installer and verification PASS. No user face, consented enrollment, unknown-person accuracy benchmark, spoof test, PMIC/camera, Windows/KD, IR light, Golden or PAM/login modification. E004fs/E004ge physical current, optical irradiance, emitted pulse and autonomous fault-OFF remain BLOCKED; see E004gq README/RESULT.

**2026-09-19 E004gp GHIDRA ORIGINAL PMIC INDIRECT TIMER CALLBACK TABLE AUDIT PASS (OFFLINE):** Recovered completed temporary Ghidra job after stream error, verified Golden and synchronized clean tracked Git baseline c54c7e38ae8f956915e365ea3d513d6525588a23. Hash-pinned OEM ARM64 qcpmic8380.sys places callback table at RVA 39470; original machine code 210f0–210f8 installs its pointer in an output structure (software variant tag 0203). Table slot 5 maps 4-channel timer handler RVA 26d50 (previously emulated in E004gh), slot 6 maps separate single-channel timer handler RVA 26f30, slot 18 maps module/channel enable RVA 285c0. Ghidra confirms single-channel callback also requests a nominal timer through a PMIC masked-write helper. It is UNKNOWN which callback the normal OEM IR preview invoked or whether firmware/hardware autonomously cuts off a continuously asserted/retriggered strobe. Offline original PE source/hash/table/instruction verifier and 10 negative mutations PASS; no proprietary original binary/decomp text committed, no camera/PMIC/Windows/KD/emitter/Golden/login change. E004fs/E004ge PHYSICAL current/irradiance/actual pulse/autonomous shutdown remain BLOCKED; see E004gp README/RESULT.

**2026-09-19 E004go OFFLINE HLOS ONE-SHOT SIGNAL-DIAGNOSTIC SESSION GATE PASS:** New isolated userspace-only aggregate-telemetry controller enforces one-shot IDLE→COLLECTING→COMPLETE transitions and non-rearmable FAULT/CANCELLED, bounded 1..16 strictly ordered frames, strict JSON/schema/range/UTF-8 validation including duplicate keys/nonfinite values/deep recursion, caller-injected monotonic tick/deadline handling and rejection of stale/duplicate/overlong requests. 1024 adversarial state/event sequences PASS; existing real C signal-metrics executable processes fresh synthetic uniform NV12 16-frame batch, then actual JSON passes bounded controller. Output is strictly diagnostic and asserts NO biometric auth/login/unlock, NO hardware-independent watchdog, NO emitter or camera I/O; frame pixels/templates never enter the controller. Real-face detection, matching, consent and liveness NOT tested. E004fs/E004ge physical emitter current/irradiance/pulse/autonomous OFF still BLOCKED; Windows/optical one-shots consumed, Golden untouched. See E004go README/RESULT.

**2026-09-19 E004gn PUBLIC QUALCOMM/LINUX PM8550 TIMER+FAULT SOURCE RECONCILIATION PASS (OFFLINE):** Verified public Qualcomm author driver/binding, PM8550 DT, 2025 torch current-clamp update, and pinned isolated local four-channel flash source. Source STATUS3 offset 09 (candidate SP11 SID1 flash-base ee00 -> ee09) contains per-channel timeout indication interpreted via `LED_FAULT_TIMEOUT`: conditional paired LED1 source1/source4 bits 0/6. Timer config source offsets 3e..41 and previous consumed E004fx idle bytes 93 only describe stored configuration. No live STATUS3 value, latch/clear-on-read behavior, stuck-strobe retrigger semantics, hardware-autonomous OFF, actual current or optical irradiance demonstrated; do NOT speculatively read or re-run consumed one-shots. External/public docs do not prove SP11 optical safety. Nine mutated-source/evidence offline negative tests PASS; IR emitter OFF, no camera/PMIC/Windows/KD/Golden/login mutation. See E004gn README/RESULT.

**2026-09-19 E004gm CROSS-PLATFORM ORIGINAL-INSTRUCTION VS UNINSTALLED LINUX C FAIL-CLOSED TEST PASS:** Following E004gl Ghidra proof that Windows may rearm after a prior OFF request reports failure, extracted and compiled the actual isolated Linux qcom_flash_strobe() source with existing *uninstalled* patches 0003/0004. New ASan/UBSan harness proves that an initial OFF error returns failure and makes NO new current/timer/module-enable/strobe-on request; attempts best-effort channel and module cleanup instead. If those mocked SPMI cleanup calls fail, the simulated hardware remains potentially ON despite software no-rearm (clearly reported unsafe). Normal path and preexisting E004fz six-fault-stage compiled C plus E004gl original Windows ARM64 fault tests PASS. Existing Linux patch already avoids this particular Windows protocol gap; NO new patch was needed or installed. This is only safer SOFTWARE request ordering, not current/irradiance/physical pulse or autonomous-off evidence. E004fs/E004ge remain BLOCKED, native IR LED OFF, E004gb consumed, no camera, PMIC, Windows/KD, Golden or login mutation. See E004gm README/RESULT.

**2026-09-19 E004gl GHIDRA OEM FLASH+PMIC DECOMPILE / ORIGINAL ARM64 START-STOP FAULT INJECTION PASS (NO HARDWARE):** SP11 already had Ghidra 12.0.4; hash-pinned original OEM Windows flash + PMIC PEs were independently decompiled by disposable headless Ghidra projects. Original Windows start RVA 48c8 follows current→timer→strobe-on but its *prior-active* branch requests OFF without checking the OFF return before continuing. Offline Unicorn actual Windows CPU execution reproduces that a mocked prior OFF failure still leads to subsequent current/timer/rearm requests and software success if later requests succeed; normal stop RVA 4828 retains active-state flag and reports failure if OFF helper reports failure. Seven exact-instruction VM scenarios plus eight input/hash negative fixtures PASS. No decompiled proprietary source or PE binary committed. This establishes a concrete software protocol weakness to avoid in native Linux (fail CLOSED after prior OFF error); it does NOT establish physical LED ON/OFF or PMIC fault autonomy. Ghidra confirms PMIC timer callback is indirectly dispatched and module ee46 precedes channel ee4e. Windows/KD, E004gb consumed normal capture, camera, PMIC, emitter and Golden NOT touched. E004fs/E004ge independent physical electrical/optical current, true pulse and host-fault/stuck-strobe OFF remain BLOCKED; see E004gl README/RESULT.

**2026-09-19 E004gk ORIGINAL WINDOWS ARM64 ADDITIONAL FLASH ON/OFF ROUTES CPU EMULATION PASS, NO NEW HARDWARE:** Full SHA-pinned Windows qccamflash8380.sys direct-call map locates auxiliary ON routine RVA 6db0 at caller 5900 and auxiliary OFF RVA 6e28 at callers 5924/5a44. Original CPU instructions in offline Unicorn VM (Windows logging/flash transport MOCKED) produce flash command 802f0fc8 ON payload [1,0,0,1], OFF [0,0,0,0]; injected transport failure makes both auxiliary callbacks return failure 1, without proving physical LED state. These are extra software request paths, NOT proof that normal preview, every suspend/remove path or host-crash executes them. Eight negative tests PASS; E004gb one-shot untouched, no Windows boot/KD/camera, PMIC, LED, Golden or login changes. E004fs/E004ge physical electrical/optical current, actual pulse and autonomous stuck-strobe/host-fault OFF remain BLOCKED. See E004gk README/RESULT.

**2026-09-19 E004gj OEM VD55G0 SENSOR STOP + LINUX RESET FALLBACK STATIC PASS, IR SAFETY STILL BLOCKED:** Hash-pinned exact Windows sensor package register-list entry 1880 contains 0x0202=0x01; the pinned ST naming reference calls that STOP_STREAM. This is an installed OEM stop-command candidate, NOT observed dynamic Windows stop execution or an electrical GPIO measurement. Current Linux native source independently uses 0x0202=1, polls command clear and SW_STBY, then asserts sensor reset and suspends on failure; normal stream start requires all GPIO selectors disabled 01,01,01,01. Nine tampered-package/source/semantics negative tests PASS. Linux software sensor reset or Windows OEM stop-command existence does NOT prove independent PMIC LED power cutoff in host freeze/bus failure/stuck strobe. No hardware, Windows/KD, PMIC, IR illumination, Golden or PAM changes. E004fs/E004ge remain BLOCKED; see E004gj README/RESULT.

**2026-09-19 E004gi PINNED WINDOWS FLASH TIMER DIRECT-CALL MAP PASS, NO NEW HARDWARE:** SHA-pinned qccamflash8380.sys ARM64 full .text direct-BL enumeration found exactly two direct callers of helper RVA 4dd0: separate configuration 4938 and dispatch subtype-2 5b2c. The observed normal subtype-0 dispatch 5b7c..5c64 has no direct timer-helper call; E004gh original Windows PMIC timer emulation shows callback semantics *if called*, not that a normal subtype-0 OEM preview called it. E004gb bounded no-timer-hook observation remains CONSUMED and was re-verified OFFLINE only. This does NOT exclude indirect/other timer writers, earlier initialization, existing active hardware timer or firmware autonomy. 12 negative cases PASS; no Windows/KD/camera, PMIC, IR emitter, Golden or login change. E004fs/E004ge independent real current/irradiance/physical pulse and autonomous-off gates BLOCKED; see E004gi README/RESULT.

**2026-09-19 E004gh original Windows ARM64 TIMER HANDLER CPU emulation PASS, HARDWARE STILL BLOCKED:** Ran SHA-pinned Windows qcpmic8380.sys instructions at RVA 26d50 inside offline AArch64 Unicorn VM, mocking only Windows logging and PMIC masked writes. Under explicit synthetic requests the handler encodes nominal 10ms→80, 200ms→93, 1280ms→ff; requested ee3e/ee41 for logical LED1 and ee3f/ee40 for other channels, plus an additional ee40 clear under this synthetic fixture. Five individually injected mocked-write failures confirm original paired-write error handling and abort before next logical LED. Archived consumed E004fx idle 93 matches the Windows *software encoding* for a nominal 200ms request; it does not prove active Windows timer state, electrical enforcement or physical optical pulse duration. E004gb Windows boot/KD/camera one-shot NOT repeated. Normal and negative offline tests PASS; no PMIC, camera, Windows boot, emitter or Golden mutation. E004fs/E004ge independent current/irradiance, true pulse and autonomous fault-off remain BLOCKED; see E004gh README/RESULT.

**2026-09-19 E004gg ORIGINAL WINDOWS ARM64 OFF-INSTRUCTION EMULATION PASS, NO HARDWARE:** Resumed after stream interruption and confirmed E004gf commit `55b026524e340dc597d7df83ffc9f3469c725ff3` synchronized on protected SP11 Golden. New offline Unicorn CPU execution maps byte-for-byte SHA-pinned Windows flash and PMIC ARM64 PEs into disposable in-memory VMs; intercepts only messaging and mocked PMIC helpers. Original flash OFF wrapper emits command 802f0fc8/payload [0,0,0,0]. Original PMIC callback requests ee46 mask 80 clear before ee4e mask 0f clear, and on a mocked failed FIRST request skips the second; second failure returns an error after both requests. LED1 ON fixture produces ee46=80 then ee4e=09. Nonzero flash-wrapper args revealed [0,1,0,1] packing, correcting an initial test expectation; all rerun negative tests PASS. Correlates, but does not REPEAT, consumed E004gb normal Windows KD evidence. This is REAL Windows CPU instruction emulation with MOCKED hardware services, NOT a Windows boot, real bus fault, actual LED off or independent timer/current/irradiance safety proof. No camera/Windows/KD, PMIC/emitter, boot, Golden or login modification. E004fs/E004ge stay BLOCKED; see E004gg README/RESULT.

**2026-09-19 E004gf Windows ARM64 STATIC + ARCHIVED-LIVE shutdown diagnosis PASS (NO NEW WINDOWS BOOT):** SHA-pinned installed `qccamflash8380.sys` + `qcpmic8380.sys` ARM64 disassembly confirms Windows type-0 OFF issues a mode command then an OFF command; the PMIC OFF callback requests module ee46 disable *before* channel-mask ee4e clear and short-circuits if the first write fails. Previously consumed E004gb live trace independently agrees with successful normal module-before-channel requests; its trace was only re-VERIFIED OFFLINE, not repeated. A four-case OFFLINE software fault model and eight static-instruction negative checks pass: failed module-off skips the channel-off request; neither static instructions nor a simulated bus failure measures the real electrical LED outcome. Uninstalled Linux rollback patch still does not guarantee autonomous fault-off. No camera, Windows, KD, PMIC, emitter, boot or Golden changes; E004fs/E004ge hardware safety gate remains BLOCKED. See E004gf README/RESULT.

**2026-09-19 E004ge physical illumination evidence gate — BLOCKED, PHYSICAL ACTION REQUIRED:** Rechecked Golden SP11 camera-idle state; SP11 USB inventory shows only root hubs, SP7 read-only PnP inventory only built-in cameras and no identifiable calibrated optical/electrical measurement instrument. No project dataset establishes the actual LED current/irradiance, optical pulse duration, autonomous host-halt/stuck-high/PMIC-failure OFF or exact hardware routing. E004ge adds an OFFLINE fail-closed five-category checklist, with negative tests PASS; even all asserted flags require independent expert measurement review, NEVER automatic emitter authorization. Qualified near-IR optical/electrical lab work on the exact SP11 is now the required physical action before Linux illumination. No new Windows/KD, camera, PMIC, emitter, reboot or login work; E004gb remains consumed, E004fs stays BLOCKED. See E004ge README/RESULT.

**2026-09-19 E004gd OFFLINE FULL-CHAIN IR TELEMETRY PASS:** After E004gc, independently reran all 16 immutable E004fe *sensor-generated pattern* RGB888 frames through the real RGB888→NV12 bridge, maintained HLOS parity worker and E004gc signal diagnostic on protected Golden with no device I/O. The processed buffer reproduces SHA256 `ea414ce89d3fdcf25f834baa3f8d13a1d04b25289ff34dba844a57986db655df`; every frame's six telemetry values match independent Python reference, and corruption in the last RGB/NV12 frame rejects the whole batch without partial output. Normal and ASan/UBSan tests PASS. These are generated patterns, NOT ambient optical images or faces; E004fu's optical buffers were not retained. E004gb/earlier identities remain consumed. No Windows/KD, camera, PMIC, emitter, login or reboot activity; E004fs physical current/irradiance, real pulse duration and autonomous host-crash/stuck-trigger shutdown remain BLOCKED. See `experiments/E004-front-ir-vd55g0/e004gd-offline-archived-pattern-telemetry/` README and pinned verifier.

**2026-09-19 E004gc OFFLINE HLOS signal diagnostics PASS:** A new strict 1..16-frame 644×604 neutral-NV12 diagnostic emits only aggregate per-frame luma, percentile, clipping and neighbor-contrast metrics after full-batch validation. Synthetic fixtures and ASan/UBSan PASS, existing HLOS Windows-oracle and 16-frame archived-pattern regressions PASS. This does not analyze E004fu's discarded optical frames and does not demonstrate face detection or recognition. No camera, LED, Windows, login/PAM or Golden mutation. See E004gc README/RESULT; E004gb is consumed; E004fs physical electrical/optical cutoff/current gate stays BLOCKED.

# SP11 Camera Linux Parity Handover — 2026-09-11 reconciled R27 frontier

**2026-09-19 E004gb Windows KDNET flash module/channel trace — PASS, CONSUMED, GOLDEN RETURNED:** Original KD dry and observer logs, Windows capture and single-use SP7 markers are archived byte-for-byte in `E004gb/evidence/ORIGINAL-WINDOWS-LOGS.zip` SHA256 `330afa1f20fc2714d8e8a172c6d754dbb4d32e5dc1a41e174825bb2c0eb0bfbf`. Live KD interpreter dry validated 11 target registers (including ee46 and ee4e), 8 excluded registers. During ONE normal bounded Windows OEM 12-frame IR preview, KD recorded 11 paired PMIC masked-helper read/write calls with return code 0: module ee46 00→80 then 80→00, channels ee4e 00→09 then 09→00, trigger pair ee4a/ee4d 01→05. No ee3e..ee41 timer register access hit these selected hooks in this session (NOT proof of timer state). These are Windows SOFTWARE helper requests and post-buffer values, NOT physical LED pulses, PMIC write readback, current/irradiance or independent fail-safe cutoff. Breakpoints cleared; SP7 KD stopped; SP11 rebooted into protected Golden boot `6ca88e8c-525b-4944-bffa-037a4337a01d` with original EFI BootOrder/GRUB FullIO entry, flash DT disabled and camera-idle guard PASS. `E004gb/verify_result.py` re-verifies original hashes and Golden return OFFLINE; `test_verify_result.py` rejects six tampered fixtures. **Never re-run E004gb or prior E004ga/E004fp/E004fr one-shot identities. Native Linux IR emitter OFF; E004fs physical optical safety/fault cutoff gate remains BLOCKED.** Next: independently establish current/irradiance, physical pulse width and autonomous host-crash/stuck-trigger shutdown; meaningful offline HLOS face-matching work can proceed separately without emitter or PAM/login installation.

**Historical E004gb preparation (superseded):** E004gb was subsequently completed, original evidence archived, and its one-shot identity consumed. Do NOT stage or repeat the Windows boot, KD hooks or OEM capture. See the current E004gb result above and the pinned offline verifier.

**E004ga Windows KDNET one-shot — ABORTED / CONSUMED, NO CAMERA PREVIEW (2026-09-19):** Live KD dry validation skipped BOTH required enable registers `ee46` and `ee4e`; earlier static checks did not execute WinDbg/MASM predicate semantics. No KD observer hooks armed, no OEM preview or new PMIC trace collected. SP7 KD breakpoints cleared, target resumed, Windows rebooted, KD job stopped. SP11 has returned to Golden boot `c017bcd7-4e86-45ed-8453-224646b6cc8e`, BootOrder/GRUB/camera-idle guard PASS; local HEAD matches origin. E004ga Windows identity is consumed and MUST NOT be rerun. SP7 original KD log SHA256 `3229becbccffc774c9b2a4026661278135fff1f6ab5dd36f557f52e75c8e4ace` (7539 B), located in SP7 E004GA stage; see E004ga/evidence/ABORTED.json and verify_abort.py. E004gb later passed live KD target/exclusion validation and completed; do not repeat either consumed experiment. E004fs IR emitter gate remains BLOCKED.


**E004ga fresh Windows KDNET enable/channel masked-RMW trace OFFLINE PREPARED / NOT ARMED (2026-09-19):** E004ga extends E004fp masked-PMIC observer with module enable `ee46` and channel mask `ee4e` alongside timers `ee3e..ee41`, triggers `ee4a..ee4d` and common `ee67` in a separately numbered normal OEM Windows IR preview (12 frames/5s, no images saved). Generator uses the FRESH installed qcpmic driver base and leaves target broken for dry/parser/breakpoint verification before explicit resume. Static test PASSED; no Windows boot or capture yet. Commit/push exact prepared E004ga scripts before BootNext and confirm SP7 KD+recovery, Golden clean/idle. Bounded Windows software requests are not independent optical safety authority; native Linux emitter remains off.\n\n**E004fz Linux flash error rollback (2026-09-19, OFFLINE PASS/UNINSTALLED):** The original isolated `qcom_flash_strobe()` could return from a fault after module-enable without a combined shutdown attempt. A new source-only patch `0004-qcom-flash-best-effort-error-disarm.patch` (after prior uninstalled `0003`) attempts channel disarm followed by module disable on all six failure stages, logs failures and preserves the initiating error. The actual modified C dispatcher passed ASan/UBSan fault injection including simulation of an SPMI bus failure with hardware potentially still ON, plus isolated Golden-kernel W=1 build. **A failed bus write can still leave emission ON; this patch is NOT an autonomous shutdown and must not be installed as an emitter-activation justification.** No physical current/pulse/irradiance or independent fault cutoff has been proven; E004fs remains blocked. KDNET/SP7 is available for a fresh, bounded Windows shutdown request/trace when useful, but is not a substitute for physical safety verification. See E004fz README and evidence/RESULT.json.\n\n**2026-09-19 E004fy read-only flash enable/trigger snapshot PASS, CONSUMED:** Six named idle PM8550/SID1 register bytes were read exactly once on protected Golden: module 0xee46=0x00 (bit7 clear); trigger selectors 0xee4a..0xee4d=0x01 each (Linux source software/level/active-high bits); channel mask 0xee4e=0x00 (all channels disabled). E004fx idle timer 0x93 configuration therefore did NOT imply an enabled flash output in this Golden state. Prior separate Windows E004fp preview observed selectors 0xee4a and 0xee4d change 0x01→0x05 for LED1 channels 1 and 4; do not attribute that transition to this idle Linux read. E004fy consumed before single bounded six-register passive observation, no PMIC writes, emitter or camera activation. Golden boot/EFI/GRUB/camera idle PASS; offline verifier `E004fy/verify_result.py` hash-pins evidence without re-reading hardware. **NEVER rerun E004fy.** E004fs optical current/pulse/independent host-fault shutdown still unproven; IR emitter stays OFF. KDNET/SP7 may be used for a separately staged Windows question when necessary.


**E004fx passive Golden timer-state read PASS / CONSUMED (2026-09-19):** One bounded 36-byte read of the precisely mapped PM8550 SID1 idle flash timer registers yielded `0x93` in all four `0xee3e..0xee41`. This is a config-byte observation only; the Windows handler would conditionally decode `0x93` as a nominal 200 ms request, NOT a measured LED pulse, physical cutoff or proof of an enabled module/channel. No PMIC writes, camera, flash driver installation, IR light or reboot occurred. Golden flash DT remains disabled, camera-idle and EFI/GRUB checks PASS. E004fx is consumed; NEVER re-run `read_once.py` or `prepare.py`. See E004fx `evidence/VERIFIED.json` and `verify_result.py`. Next distinct observation: module/channel enable and trigger registers; E004fs independent physical safety gate remains BLOCKED.

**E004fw Golden flash-PMIC mapping (2026-09-19):** Live read-only device-tree/SPMI metadata identifies the only flash-controller node as disabled PM8550 flash LED at SPMI `0-01`, base `0xee00`; the four-channel timer-register address candidates are `0xee3e..0xee41` on that controller. PMC8380 PMIC DT nodes on SIDs 3–6 are not the flash-controller parent. E004fw explicitly read NO PMIC register values and did not activate any hardware; 12 synthetic fail-closed mismatch tests pass. This does NOT prove physical wiring, timer state, safe LED power, or fail-safe shutdown. Next is a **fresh, narrowly bounded passive timer-register snapshot design** targeting the correctly identified node, without whole-regmap dumps or illumination. E004fs remains blocked.

**E004fv uninstalled source patch (2026-09-19):** The pinned original Linux PMIC timer encoder differs by one 10 ms step from the recovered Windows PMIC software handler. The new source-only patch 0003 aligns the Windows request→register-byte mapping across all 1271 allowed integer-ms values; actual patched C sanitizer tests and an isolated W=1 Golden-header module build passed. This is NOT a measured physical timer or independently safe LED cutoff: patch is NOT installed, IR emitter remains OFF, and E004fs hardware safety gate remains BLOCKED. See E004fv README/RESULT.json. The old text describing a 1270 ms encoded ceiling reflects where the uncorrected Linux formula first saturates; the Windows software handler maps 0xff to nominal 1280 ms, not a measured physical cutoff.

**E004fs source-level timer review (2026-09-19):** Hash-pinned Linux isolated flash driver code programs timer before arm but defaults to 1000 mA (versus Windows' observed 700 mA request), advertises up to 1280 ms while clamping the 7-bit encoded maximum to 1270 ms, and has 10 ms timer granularity. Windows' 1955 exposure lines under the *separate Linux* clock would hypothetically be 17.0494 ms, not an observed pulse. No PMIC timer readback, physical current/irradiance, or autonomous stuck-strobe/host-crash shutdown proof exists; **emitter activation remains blocked**. Offline checker `e004fs-emitter-timing-timeout-offline-review/verify_timeout_readiness.py` and six negative-path tests pass. Do not treat an E004fs offline PASS as emitter authorization.

**E004fu 2026-09-19 result:** Fresh one-shot test_pattern=0 ambient optical capture passed 16/16 RGB888 bridge-to-HLOS frames, clean stop/suspend/kernel and Golden return. Output remains very low contrast (steady mean 38.6–39.7/255); no usable face image or biometric matching proved. Image buffers and image hashes were not retained, and the temporary candidate was retired. E004fu is consumed; emitter remains OFF. See E004fu README, numeric RESULT.json and verify_result.py.

> **Current frontier — 2026-09-19 / E004fu live unilluminated optical HLOS capture PASS but low-contrast image; Golden restored, E004fs emitter authority next:** Native Linux IR remains unilluminated. E004fr recorded 114 contiguous sensor register writes during one 12-frame Windows IR preview, including 16 coarse-exposure programming groups (32 through 1955 lines) and frame-length values of 1955/2000 lines. KD and Windows original reports are archived with hash-checked offline verification. This is software write-observation evidence, not an electrical pulse-width/current measurement or proof of PMIC fail-safe timeout. E004fq remains a separately consumed, aborted attempt. The unsigned HLOS IR worker has only offline pixel-processing and archived-pattern format-bridge validation, not face authentication.


**Latest E004fq/E004fr update (2026-09-19):** E004fq Windows one-shot idle target/skip validation passed, but its generated breakpoint callback was rejected by KD's `Malformed string` parser before any camera capture. No IR preview or sensor write trace was collected. KD breakpoints were cleared, SP11 rebooted to protected Golden Ubuntu, unchanged boot order and camera-idle overlap guard verified. E004fq is consumed and cannot be retried. E004fr subsequently passed on a separate fresh Windows boot: KD accepted the observer, 12 IR frames acquired, 114 contiguous sensor register writes recorded, and SP11 returned to protected Golden. The current gate is E004fs offline pulse/current/PMIC timeout review before considering a bounded Linux emitter experiment; Linux emitter remains OFF. The independent HLOS bridge and IR pixel worker have now also passed **E004ft: one fresh live 16-frame generated-pattern camera capture processed in ordinary Linux userspace**, with clean camera stop, sensor suspension and Golden return. This establishes live camera-to-worker transport only, **not** unilluminated optical quality, liveness, face authentication or IR emitter safety. E004ft is consumed and retired; do not reuse it.

## Current continuous-control frontier — GV consumed/adjudicated PASS

GT limited redundant-write policy and GU helper integration are durable. GV then consumed exactly one fresh R27 stream. Six control ioctls G1..G6 succeeded, but because G4..G6 were bit-identical to current G3, V4L2 `cluster_changed()` suppressed those three before driver `.s_ctrl`. Thus the live run produced only bootstrap + G1..G3 sensor transactions and **no new post-G3 hardware write**.

The initial verifier expected one hardware transaction per successful ioctl and stopped on that incorrect assertion. After immediate archive, protected Golden return and candidate retirement, the verifier was corrected offline. The immutable evidence passes as `PASS_CAPTURE_GV_REDUNDANT_IOCTL_DEDUPE_R27`. No same-boot retry occurred.

GY then consumed exactly one fresh R27 one-shot and **PASSed**. A guarded G4 sentinel changed only digital gain 1471→1472 (+0.06798%), produced exactly one new post-G3 IMX681 hardware transaction, and G5..G26 stayed shadow-only. Golden return and retirement passed; no retry. The later native AEC tuples G5..G27 did not move, so GY proves transport/lifecycle but not production-native changed feedback.

GZ then closed offline response-threshold analysis: the tiny GY signal is below normal luma variability, and production native control is cap-censored G3..G27. HA closes a fail-closed one-native-write policy and HB integrates it at the exact DQBUF release boundary.

HC then consumed exactly one fresh R27 observer stream and returned **PASS_NO_CAP_RELEASE**. All eligible G4..G24 sources remained cap-active; G25/G26 were forced shadow by the evidence horizon; no post-G3 native write was issued. Hardware evidence is exactly bootstrap + startup G1..G3. STREAMOFF, kernel health, Golden return and candidate retirement passed with no retry.

HD closes that offline strategy. GO/GS/GV/GY/HC all end deeply cap-censored (>8× cap at G27), so merely extending the same static scene is not evidence-based. Windows DM proves a genuine below-cap ordinary preview regime (R7 ~0.917× cap; R8 first clamp), but not a transferable numeric lux threshold.

The next post-G3 native feedback live attempt therefore requires a **fresh identity plus a substantially brighter diffuse real scene**; HC must never be reused and no synthetic sensor delta is authorized. Until that physical condition is available, continue production integration and repeated-stream robustness work offline/safely.

HE/HF/HG/HH/HI/HJ production consolidation and bounded RGB handoff remain accepted without Golden promotion. **Front IR is now natively live through E004fe, and E004fn closes the normal Windows flash request sequence.** Linux has stock-libcamera capture and 16/16 processed monochrome frames; Windows requests 700 mA on logical LED1, selector 0, hardware/level/active-high trigger mode, arm then disable. Illumination on Linux remains unauthorized pending register-level PMIC and pulse-policy evidence.

**Next gate: E004fq actual VD55G0 sensor-exposure/strobe-envelope and PMIC-timer authority.** E004fp is consumed PASS and Golden-restored. The PMIC register writes are now live-proven; next determine the physical sensor exposure/strobe relationship and whether any separate timeout/timer programming is active or required. Prefer static authority first and keep native Linux illumination off.

---

## RECONCILED CURRENT FRONTIER — authoritative over the historical handoff below

Reconciled 2026-09-11 after a possible UI/turn overlap. Machine/Git/evidence state is authoritative, not visible chat chronology.

- durable checkpoint: `6985bb6f5993232df3483000581196e2a370acdc` (`camera: close R25-R27 offline authority`)
- branch: `experiment/e003-front-imx681-cphy`; local and origin matched at reconciliation
- GC: consumed Linux R5-R21 live PASS; archive manifest revalidated
- GI: consumed Linux R5-R24 live PASS; 24 QC10C frames; archive manifest revalidated
- GJ: consumed one-stream Windows R4-R27 combined AWB + Tintless/LSC PASS; 24/24 AWB bit-exact and 24/24 LSC byte-exact; archive manifest revalidated
- GK: offline R25-R27 PASS at `6985bb6`; R5-R24 regresses 20/20 against GI and R25-R27 is deterministic 3/3
- safe machine state at reconciliation: protected FullIO v19c Golden, empty `next_entry`, no camera nodes/modules, no camera process

GL, GM and GN are durably closed and pushed. GO then completed exactly one fresh R5..R27 Linux stream and **PASSed**: 27 QC10C frames, native AEC G1..G27, producer/IQ R5..R27, exactly three physical sensor writes, clean STREAMOFF and kernel health. SP11 returned to protected Golden and the GO candidate was retired.

After a GO PASS, stop mechanically extending R30/R33/etc. Pivot to continuous delayed sensor-control feedback, control-to-statistics timing, repeated/long streaming, production integration, then VD55G0 IR bring-up.

Continuous-control work is now closed through GP timing authority PASS, GQ continuous two-slot ring scheduler PASS, GR continuous helper integration PASS, and **GS live shadow scheduler PASS**.

GS consumed exactly one R27 stream: G1..G26 scheduler releases all hit their exact live boundaries, only G1..G3 performed physical sensor ioctls, G4..G26 produced 23 shadow releases, and kernel evidence contains exactly one bootstrap plus three real control transactions. STREAMOFF, Golden return and candidate retirement all passed.

Current frontier beyond the historical block: GY changed-transport PASS; GZ cap-censor analysis PASS; HA one-native-write policy PASS; HB helper integration PASS; HC prepared/unarmed/prearm PASS. The next live action is one HC observer stream only after its exact candidate is durably committed/pushed.

Before every meaningful mutation run `tools/camera-overlap-guard.sh` and inspect the intended stage path. If unexpected evidence exists, audit it first. Any one-shot attempt that may have started is consumed until proven otherwise. Never same-boot retry and never reuse a consumed identity.

The older FU/R18 handoff below is retained as historical evidence only.

---

## Resume command / first instruction for the next chat

Continue SP11 Camera from this HANDOFF on branch `experiment/e003-front-imx681-cphy`.

Current durable live-result checkpoint immediately before this handoff:

`aeb1b0df8876f54714380a028104dd50eddc6d2e`
(camera: record FU eighteen-frame live pass)

First verify the exact Git + Golden state below.

SP11 is reserved for Camera. Do not touch HostFabric work.

Do not reuse consumed one-shot identities. FU is consumed and retired.

Do not jump directly to unrestricted continuous streaming. The new frontier is bounded authority/work beyond R18.

---

## 1. Exact durable Git state

Repository:

`/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera`

Branch:

`experiment/e003-front-imx681-cphy`

Durable live-result checkpoint:

`aeb1b0df8876f54714380a028104dd50eddc6d2e`

Origin matched this checkpoint immediately before rewriting HANDOFF.

Important recent checkpoints:

- `c30a37a` — close Windows R18 Tintless/LSC authority
- `6328e59` — authorize bounded R16–R18 IQ content
- `7ed9347` — stage G15 publisher and R18 producer
- `767248e` — stage authorized eighteen-frame R18 transport
- `d572679` — stage FU eighteen-frame live candidate
- `9718a59` — make FT result repeatable
- `aeb1b0d` — record FU eighteen-frame live pass

Many old untracked historical artifacts across E002/E003 remain intentionally. Do not mass-clean them.

---

## 2. Exact current SP11 machine state

Hostname:

`SP11X1e`

OS/kernel:

- Ubuntu 26.04 LTS
- `7.1.5-sp11-render-parity-v4+`
- ARM64 / aarch64

Current boot is protected persistent Golden Linux.

Golden boot ID after FU:

`5c74a60a-e805-45b6-bdd5-983d66aaad6a`

Golden kernel cmdline boots from:

`/boot/sp11-7.1.5-audio-fullio-v19c/`

GRUB environment:

`saved_entry=sp11-audio-fullio-v19c`
`next_entry=`

Current Golden state:

- candidate qcom_camss absent
- candidate imx681 absent
- ov13858 absent
- no /dev/video*
- no /dev/media*

FU candidate boot artifacts are retired:

- `/etc/grub.d/99zv_sp11_camera_e003i_fu_eighteen_frame_r5_r18` absent
- `/boot/sp11-7.1.5-camera-e003i-fu-eighteen-frame-r5-r18` absent
- FU menu ID absent from generated grub.cfg
- Golden saved_entry unchanged

---

## 3. Windows/component authority through R18

### FH — recovered Windows AWB authority through R18

Status:

`PASS_RECOVERED_WINDOWS_R4_R18_AWB_15_OF_15_BIT_EXACT`

FH provides AWB/GainAdj differential authority through R18.

### FP — fresh Windows R4–R18 Tintless/LSC oracle

FP performed exactly one fresh Windows front-camera stream and captured R4..R18:

- Tintless stats: 0x12bec bytes/request
- trigger: 0x100 bytes/request
- final LSC staging: 0x18a0 bytes/request
- 15 entry hooks
- 15 post-stage hooks

Sequential native clean-room replay:

`15/15 byte-exact LSC0/LSC1/LSC2/GIC`

Bank parity:

`1,0,1,0,1,0,1,0,1,0,1,0,1,0,1`

FP returned Golden cleanly.

FP Windows evidence ZIP SHA256:

`f20d931b92cabb2533aaeea9cd205b63af21ee9cbc7791c91a07a52961393197`

FP Linux archive:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fp/windows-r4-r18-20260911`

FP final archive MANIFEST.sha256 file SHA256:

`290c0b238ff26e6f21f42626a6b40f8e18154a9ae18b1a22890eba8448c028a2`

### FQ — R16–R18 authority join

FQ combines:

- FO deterministic R16–R18 composition from immutable FN G13/G14/G15 continuation inputs
- FH Windows AWB authority through R18
- FP Windows Tintless/LSC authority through R18
- EB post-R6 stable GTM law

Status:

`PASS_OFFLINE_R16_R18_CONTENT_AUTHORIZED`

This is component differential authority, not a same-scene whole-capsule Windows oracle.

---

## 4. Offline bounded R18 stack

### FR — G1..G15 compiled C gain publisher

Status:

`PASS_OFFLINE_G1_G15_C_PUBLISHER`

Properties:

- exact existing 24-byte ABI
- request = generation + 3
- G1..G15 accepted
- G16 rejected
- only source delta from FK is upper bound 12 -> 15

gain-feed.c SHA256:

`c8b03597649ec5e1a6e5b62110eb61ab7cd6a29073a3ecdcf9194f439b410627`

### FS — live-capable R5..R18 producer

Status:

`PASS_OFFLINE_R5_R18_AUTHORIZED_INTEGRATION`

Offline proof:

- source: immutable FN G1..G15 paired stats + CQ gains
- R5..R15 reproduce the real FN live capsules 11/11 byte-exact plus key metadata
- R16..R18 match FQ-authorized hashes exactly
- two independent FS runs are deterministic
- live-capable scheduler/control/submission path preserved

Authorized R16–R18 capsule hashes:

- R16: `78b40962f9eb72a27a674050278c5cf309eff4f2d635952bd7e3e52e83188588`
- R17: `553803b3575bcebdd1dbbdf71bf68db8a82326a8a3dea3706cf2f674af120012`
- R18: `0b8e01730173acd8efe18ff4f459d450a98e436531b29c486531862eeaac9427`

### FT — eighteen-frame transport

Status:

`PASS_OFFLINE_EIGHTEEN_FRAME_TRANSPORT`

Proof:

- CAMSS W=1 PASS
- helper Werror PASS
- 18-frame buffer cycle:
  `0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1`
- paired AEC/stats generations G1..G18
- CQ gain publisher generations G1..G15
- IQ consumption requests R5..R18
- physical sensor-write schedule remains exactly sources G1/G2/G3 at boundaries G2/G3/G4
- scheduler unit test PASS G1..G18 with exactly 3 writes
- no FT camera runtime

Pinned generated source hashes:

- CAMSS:
  `a096493ae74fc3a22945f71f670f8777f0ea375bd3ad667c7451c96116d2ef6c`
- helper:
  `24c87150ae6ee447440fe544cb8af1cec27e33d70fc0f70b198b4b7d9f5f23ce`
- schedule header:
  `092c1b1dfaaa09ede3b9b492fc4173915d64f7b6c3d7e7439576314129e3c6cf`

Important verifier note:

FT originally recorded a temporary-path-dependent qcom-camss.ko hash in RESULT.json. That non-authoritative field was removed. Two consecutive FT verifier runs now produce byte-identical RESULT.json with SHA256:

`915acb4d3130abb7a2cd2606ab13738f1c71f9734523d25516bbcd6cef7a5aa5`

---

## 5. FU live result — consumed PASS, never reuse

Directory:

`experiments/E003-front-imx681-cphy/e003i-front-native-productionization/fu-eighteen-frame-live-r5-r18`

Durable pass record:

`ATTEMPT1-PASS.json`

Retirement record:

`RETIRE.txt`

Status:

`PASS_CAPTURE_FU_EIGHTEEN_FRAME_R5_R18`

Candidate HEAD:

`9718a59497a4b0783e358857167bbba4eba6cc28`

Candidate boot ID:

`3bb74578-1f93-4125-9b11-9b1a75efa4a2`

Exactly one FU camera stream attempt occurred.

No same-boot stream retry occurred.

The helper-consumed guard was created before streaming.

Helper result:

`HELPER_RC=0`

Transport result:

- exactly 18 QC10C frames
- DQBUF order:
  `0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1`
- native AEC accepted G1..G18
- paired TLBG + STATS3A captured G1..G18
- R5..R18 composed and submitted live
- kernel IQ consumption observed through R18
- STREAMOFF_OK
- bounded eighteen-frame kernel completion observed

Physical sensor writes:

exactly 3

Schedule:

- G1 released after completed G2 -> expected effect G4
- G2 released after completed G3 -> expected effect G5
- G3 released after completed G4 -> expected effect G6
- no later physical writes

Producer deadline:

all R5..R18 pipelines < 33.333333 ms

Maximum:

`28.516746 ms`

R18 live:

- capsule SHA256:
  `6714b533f3c866d41ceda8de69b1fd29ca3da6fa28d6ff775851c02ed2dc6ca2`
- AWB calibration slot 5
- AWB triangle 25

Kernel health:

PASS

FU does not claim unrestricted continuous AEC or an infinite scheduler.

---

## 6. FU external evidence

Archive:

`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fu/attempt1-pass-eighteen-frame-20260911T1822`

Final archive MANIFEST.sha256 file SHA256:

`a02b7b0916c1a5b56e2ce2d0555ff1ccd2904193bf63d7edf9448a54868a6d9b`

Compact evidence hashes:

- ATTEMPT1-PASS.json:
  `2ba823f10acb589ad4c849072a9b8b0be6ae17654675f83453d23098bd09c1a4`
- RUN.txt:
  `86186682b8f9c1bbef70436506979c01ca3cba9b1d5984ef9bf9602051b3cffb`
- LIVE-RESULT.json:
  `89d415282c23c0b5fbcdcd46f248b6c359c1839c24e6c0824e46f416033b0189`
- producer RESULT.json:
  `cbd3cb7f8c39f1f46fcfef91e5cdb446ae98cc8292c180e6df17e44c35c6465d`
- DMESG.txt:
  `0d31c7f8296c4c2e685d13166314c923f38c160e8dd012ebcb94e35d397e66b4`
- HELPER-CONSUMED.marker:
  `063171e5d17ed7b2889cf78eeec394a6c110e88a1b70a5d3eb5aa02c16b4d73f`
- GOLDEN-RETURN.txt:
  `02bcd593c27c4c4b843dbb326399fff584e0fc025b86ffc4a36cdda6478bd659`
- RETIRE.txt:
  `37edcf38af1ba7cd632d47478eb08f398dad6db2421e4bf9a3975ff6c6928c12`

---

## 7. Fresh continuation inputs now available

FU captured paired Linux statistics through G18.

FS consumed G1..G15 for R5..R18.

Therefore FU preserves fresh continuation inputs not yet consumed by the live IQ producer:

- G16 STATS3A/TLBG -> natural source for R19
- G17 STATS3A/TLBG -> natural source for R20
- G18 STATS3A/TLBG -> natural source for R21

Native AEC also produced CQ residual ISP gain observations through G18 in RUN.txt.

Use the immutable external FU archive as the source. Do not modify archived evidence in place.

---

## 8. Current authority boundary beyond R18

AWB/GainAdj:

- FH Windows differential authority stops at R18.
- R19..R21 are not yet Windows-authorized.

Tintless/LSC:

- FP Windows clean-room differential authority stops at R18.
- R19..R21 are not yet Windows-authorized.

GTM:

- EB's post-R6 stable output law remains available, but any new use must record that inference explicitly.

Producer mechanics:

- fresh Linux continuation inputs G16..G18 exist.
- the current production algorithms can be exercised offline.
- this does not authorize R19..R21 content by itself.

Therefore **both AWB/GainAdj and Tintless/LSC authority must be extended beyond R18 before any R19..R21 Linux live candidate is created.**

Do not silently extrapolate FH or FP past R18.

---

## 9. Recommended next frontier — bounded R19..R21 offline/Windows authority first

Suggested sequence:

1. Create an offline-only continuation/composability stage from immutable FU G16/G17/G18:
   - G16 -> R19
   - G17 -> R20
   - G18 -> R21
2. Prove deterministic composition and preserve exact regression to the real FU R5..R18 live capsules.
3. Extend Windows AWB/GainAdj authority through R21.
4. Extend Windows Tintless/LSC authority through R21.
   - Prefer one fresh bounded Windows stream only if the existing proven hooks can safely collect the needed evidence together.
   - Otherwise keep AWB and Tintless/LSC as separate bounded one-stream authority captures.
5. Join R19..R21 component authority explicitly.
6. Only after authority closes:
   - extend compiled C gain publisher through G18
   - extend live-capable producer through R21
   - extend bounded transport to 21 frames
   - verify everything offline
   - create a fresh one-shot Linux live identity
7. Still do not jump directly to unrestricted continuous/infinite streaming.

Suggested next labels if free:

- FV — offline R19..R21 continuation/composability
- FW — Windows AWB authority through R21
- FX — Windows Tintless/LSC authority through R21
- FY — R19..R21 authority join
- FZ — G1..G18 compiled publisher
- GA — R5..R21 producer
- GB — twenty-one-frame transport
- GC — fresh one-shot twenty-one-frame Linux live candidate

Verify labels are unused before creating them.

---

## 10. Closed / historical stages — do not rewrite history

Important closed stages include:

- EM — PASS_OFFLINE_R7_R9_COMPOSITION
- EN — historical R5-R9 producer integration; preserve its stale-publisher verifier gap
- EL — PASS_OFFLINE_JOIN
- ES — PASS_OFFLINE_NINE_FRAME_TRANSPORT
- EJ/EK — front AWB OTP source proven natively on Linux
- EB — Windows GTM authority / post-R6 stable law
- ED — Windows Tintless/LSC authority through R12
- FH — recovered Windows AWB authority through R18
- FI — Windows Tintless/LSC authority through R15
- FJ — R13–R15 content authority join
- FK — G1..G12 C publisher
- FL — R5..R15 producer
- FM — fifteen-frame transport
- FN — consumed live PASS through R15
- FO — R16–R18 continuation/composability
- FP — consumed Windows R4–R18 Tintless/LSC PASS
- FQ — R16–R18 content authority join
- FR — G1..G15 C publisher
- FS — R5..R18 producer
- FT — eighteen-frame transport
- FU — consumed live PASS through R18

Consumed Linux one-shot identities include:

EA / EO / EQ / ER / ET / EV / EZ / FF / FN / FU

Never reuse a consumed identity.

---

## 11. Safety rules that remain mandatory

- Golden default is sacred:
  `saved_entry=sp11-audio-fullio-v19c`
- candidate boots must be one-shot via next_entry / grub-reboot
- one camera stream attempt per candidate boot maximum
- on any failure: preserve evidence, no same-boot stream retry, whole-machine reboot to Golden
- never reuse consumed candidate identities
- every new live attempt needs a fresh identity
- preserve raw external evidence and checksums
- do not mass-clean historical untracked artifacts
- do not claim continuous AEC from bounded tests
- do not touch HostFabric work in this continuation
- do not extend Linux live IQ past the proven content-authority boundary without a fresh offline/Windows authority gate

---

## 12. Human summary

The Linux front-camera stack now has a successful bounded live run through **R18**.

FU completed eighteen real QC10C frames, captured paired 3A/TLBG through G18, submitted dynamic IQ R5..R18, performed only the original three delayed physical IMX681 writes, cleanly STREAMOFF'd, passed kernel-health validation, and returned to Golden. The consumed candidate was retired.

Fresh continuation inputs G16/G17/G18 now exist for natural R19/R20/R21 work. The blocker is no longer Linux transport or producer mechanics; it is authority beyond R18. Both Windows AWB/GainAdj and Windows Tintless/LSC differential authority currently stop at R18.

The next safe move is therefore offline R19..R21 continuation plus bounded Windows authority extension before another Linux live candidate.
