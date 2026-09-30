# E011AU — bgStatsConfigV1 retained-BG initialization writer

Status: STATIC EXACT WRITER FOUND; LIVE SOURCE QUALIFICATION PREPARED.

E011AT proves the real AWBSetParameter callback at RVA 0x68C090 receives quad=1 and preserves all 92 retained BG bytes. Original ARM64 now closes the immediately upstream code path: CreateAWBAlgorithm at RVA 0x681D80 calls configuration parser RVA 0x686A50 from RVA 0x682224 for the matching input descriptor. That parser resolves the literal bgStatsConfigV1 through lookup helper 0x6F39F8, receives the selected record at lookup result+0x120, zeros actor+0xFB744 for 92 bytes, populates the record, and copies source+0x20 to actor+0xFB798 at RVA 0x688290. The parser range is 0x686A50..0x688848.

The SetParam wrapper RVA 0x681C40 only validates wrapper/parameter pointers, writes wrapper+0x34 to thread state, resolves wrapper+0x28 -> actor -> vtable+0x08, and dispatches. It has no retained-record write. Combined with E011AT, the cold initializer is now localized to the pre-Start CreateAWBAlgorithm configuration path rather than SetParam/GetParam2/publication.

The live observer is intentionally armed before MediaCapture.InitializeAsync. It targets the CreateAWBAlgorithm call, the exact post-lookup point and the post-population point; it will compare the selected bgStatsConfigV1 source against the retained actor record. The FrameServer service must be started and user-mode CDB attached with the deferred breakpoint before PREINIT.GO is released. One camera Start/Stop remains the maximum for the fresh identity.

No kernel debugger, BCD change, Linux camera runtime, production source change or native rear activation is authorized. Raw code, process bytes and captures remain private on SP11. The exact numeric profile/value is still pending live qualification; do not hardcode quad=1 from static control flow alone.
