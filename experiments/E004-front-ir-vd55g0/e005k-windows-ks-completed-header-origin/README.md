# E005k — completed rear4K KS header and exact completion-number origin

Parent Git `428997fcd9d533d35039937ef06ad64f96681fa9` (E005j). SP11 returned to protected Golden Linux after a fresh, bounded **user-mode-only** Windows run. No KD, kernel WinDbg, kernel breakpoint, BCD change, OEM module replacement, or native rear ISP runtime occurred.

## Physical user-mode completion evidence

The private E005L run used CDB only against the Windows Camera FrameServer process. Rear `Surface Camera Rear / Color / VideoRecord / NV12 3840×2160` started and stopped cleanly, delivered 50 valid 4K frame handles in 5,032 ms, and sampled the Media Foundation completion owner immediately after `GetOverlappedResult`.

For the already-source-identified rear 4K **KS pin 2**, 24 sampled completed read headers were internally consistent:

- `KSSTREAM_HEADER.Size = 160`
- `FrameExtent = DataUsed = 12,441,600` bytes, exactly 3840×2160 NV12
- pre-submit `OptionsFlags = 0x5000` (`FRAMEINFO | METADATA`)
- post-completion `OptionsFlags = 0x25110`
- `FrameCompletionNumber = 1..24`, unique and sequential
- `DropCount = 0`
- metadata buffer size 8,130 bytes; completed metadata used 2,224 bytes

The simultaneous pin 3 companion stream likewise produced 76 sampled completed 1,048,576-byte headers with unique sequential completion numbers 1..76.

Only derived scalar evidence enters Git. Raw user-mode debugger logs, raw handles/pointers and proprietary binaries remain private.

## Exact Microsoft KS origin of `FrameCompletionNumber`

Installed `ks.sys` SHA256 `a6d9dc8239bff10d96adc3fc20c13aba98b0385cac417a0fd6a42e7127115e53`, version `10.0.26100.9444`, explains the post-completion mutation exactly. In the original installed binary, the internal stream-completion path at RVA `0x70bc`:

1. ORs `0x20000` (`KSSTREAM_HEADER_OPTIONSF_TRACK_COMPLETION_NUMBERS`) into `OptionsFlags`;
2. verifies the header is large enough for `KS_FRAME_INFO`;
3. increments a per-pin 64-bit counter at internal object offset `+0x240`;
4. writes that incremented counter at `header + 0x78`, exactly `KS_FRAME_INFO.FrameCompletionNumber`.

This reproduces the observed E005L transition from pre-submit `0x5000` / completion zero to completed `0x25110` / 1,2,3,...

**Therefore `FrameCompletionNumber` is Microsoft KS stream bookkeeping. It is not an independent ISP/WM16 DMA fence and must not be used as one.**

## Qualcomm AVStream distinction

Original `surfacecamavs8380.sys` SHA256 `b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed`, version `1.0.4258.7908`, makes the ownership boundary equally clear.

`CPin::CompleteFrame` starts at RVA `0x18830`. Its original instructions update `DataUsed` and OR only `0x110` (`TIMEVALID | DURATIONVALID`) into `KSSTREAM_HEADER.OptionsFlags`, then dispatch virtual slot `+0xc0`. It does **not** OR the `0x20000` tracking flag or populate `FrameCompletionNumber`.

All five concrete pin vtables present in the binary place `CPin::CompleteFrame` at slot `+0xb8`. The `CVideoPin` vtable from E005j is one of them and places `CPin::NotifyFrameCompleted` at `+0xc0`.

## GROUP0 image → pin completion chain tightened

The original AVStream driver now also source-locks the worker-class handoff around E005j:

- `CDispatchHandler::GetIspNotification` RVA `0x17798` parses ISP packets into a worker notification record.
- Parsed notification class **2** contains raw message IDs `0x15` and `0x16`, both explicitly logged as `IFE_MSG_ID_GROUP0_IMAGE`.
- `CDispatchHandler::OnIspNotification` RVA `0x17428` dispatches class 2 to `CCaptureFilter::ProcessIfeFrame` RVA `0x5488`.
- `ProcessIfeFrame` validates candidate pin buffers, logs `Completing frame for %s`, and calls virtual slot `+0xb8`.
- The concrete pin vtables resolve `+0xb8` to `CPin::CompleteFrame` RVA `0x18830`.

Thus the static chain is:

`GetIspNotification GROUP0_IMAGE → notification class 2 → OnIspNotification → ProcessIfeFrame → CPin::CompleteFrame → KS stream completion`

This strengthens E005j's source lock, but it still does **not** dynamically bind one live rear pin2 frame to one qccamisp FIFO8 group8 entry, a non-null WM16 outstanding object, an independent exact WM16 IRQ/ACK, or DMA/IOMMU quiescence.

## Boundary

E005k deliberately closes a tempting false shortcut: sequential KS completion numbers are useful user-mode stream bookkeeping but **not hardware completion evidence**. Native processed rear ISP remains **DENIED**.

The next admissible gate remains same-live-frame FIFO8 group8 → non-null WM16 identity plus independently trusted WM16 hardware completion/IRQ/ACK and DMA/IOMMU safe-stop. Kernel debugging remains prohibited on remote-only SP11; it can be reconsidered only with a separate live external debugger host such as recovered SP7.

Run:

`PYTHONDONTWRITEBYTECODE=1 python3 verify.py`
