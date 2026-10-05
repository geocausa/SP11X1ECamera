# E011GF — selected CA9718 case to 1370761 read frontier

Four source-exact placements execute the selected original parser case at `0xCA9718..0xCA9728`, then its branch to common resume `0xCA9848`. The case owns exactly the expected receiver mutations: `+0x38 = u8 0`, `+0x28 = u64 0`, `+0x30 = u64 0xffffffff`, and `+0x4c = u8 0`.

The common-resume load at `0xCA9848` executes and still selects retained source-pointer RVA `0x1370761`. The bounded source harness observes no source-memory read during the case/resume step and stops with PC at `0xCA984C`, before the signed one-byte read from `0x1370761`.

E011GG must separately source-qualify the exact pinned byte at `0x1370761` before executing that read. GF does not claim that byte, downstream parser state, a complete parser iteration, CA94E8/CA6280 return, or native rear runtime. No camera Start, reboot, rear runtime, or kernel build is used.
