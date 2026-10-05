# E011FZ — opaque security-cookie producer to `CA94E8` frontier

E011FZ executes the current `0xCA6294 -> 0x11D0` security-cookie producer with four distinct opaque cookie fixtures. All four execute the same six original producer instructions and the same 38-instruction current path through `CA6280`; only the encoded cookie stack word changes according to the exact `SP - cookie` formula. The live process cookie value is not claimed and the file-image cookie is not substituted as native authority.

The deterministic `CA6280` setup resumes at `0xCA6298` and is qualified through `0xCA6344`, then stops before `0xCA6348 -> 0xCA94E8`. No camera Start, reboot, rear runtime, or kernel build is used. NEXT is E011GA.
