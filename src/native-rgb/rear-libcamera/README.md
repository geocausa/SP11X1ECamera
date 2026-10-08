# Rear libcamera public request qualification

Isolated standard libcamera pipeline for two rear 4K NV12 requests using exported/imported DMA-BUF application buffers. Kernel hardware ISP produces all pixels. The handler does not map pixels, implement a software ISP, or provide a camera daemon.

The candidate remains finite and uses the private compiler-bound startup profile. It proves application request transport and lifetime, not continuous capture, independent rear IPA, adaptive IQ, exposure timestamps or Windows quality parity. Maintained front pipeline/IPA sources are unchanged.

Continuous work must replace the fixed 16-entry completion history with a consumed event queue and establish live buffer retirement before releasing any mapping while hardware runs. Existing rear retirement only authorizes full-stop release; never substitute false stop proofs to recycle a live mapping.
