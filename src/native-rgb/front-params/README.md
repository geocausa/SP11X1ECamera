# Typed front scalar qualification

The optional overlay follows the qualified NV12 queue and frame-associated
statistics overlays. All module flags default false. One private startup R4
profile still enters through the development bootstrap control, is parsed and
kept in kernel-owned memory. Further raw capsules are rejected. This does not
close startup firmware/configuration, dynamic tuning-table updates or the final
product request API.

Every later request supplies a 64-byte pointer-free, little-endian typed packet:
request sequence, per-frame overlay mask, four Bayer0 Demux Q10 gains, four PDPC
Q12 ratios and relative B/R white-balance Q10 gains. Unknown/reserved/unused fields,
out-of-range scalars and uncoupled WB/PDPC updates reject before mutation.
The overlay applies to the startup defaults for this request; omitted modules
reset to those defaults rather than retaining an earlier per-frame overlay.
The kernel owns packing, addresses, all16 alternating DMI bank selectors, DMA
binding and CDM framing. Userspace supplies no commands, IOVAs or register offsets.

The same kernel packer passes1979 sanitizer checks and matches92 independently
qualified private fixed-IQ fixtures byte-for-byte. The real libcamera libipa
encoder forwards quantized values through this shared schema, with unchanged
outputs on invalid input. These are helpers, not a completed pipeline or IPA.

Fresh params01 tests80 paired frames and84 typed requests5..88. Five malformed
or forbidden-control cases must reject without damaging the provider sequence.
Requests32..63 apply a2x Bayer gain, then return to defaults; settled output
luminance must rise and fall. This measures typed control reaching hardware,
not AE/AWB convergence or Windows image quality. It preserves all ownership,
completion, CDM receipts, safe-stop and Golden protections. Original profile,
statistics and pixels stay private on SP11. Retire the one-use identity after
an attempt; never rearm it.

Hardware params01 passed80 pairs at30.006fps,84 typed requests and all5 negative
cases. Measured Bayer-gain response:3.458 ->7.146 ->3.456. All405 ownership checks
passed; explicit stop, neutral graph, standby and Golden return verified. Identity
is consumed and retired; never rearm. See the derived PARAMS-01 evidence.
