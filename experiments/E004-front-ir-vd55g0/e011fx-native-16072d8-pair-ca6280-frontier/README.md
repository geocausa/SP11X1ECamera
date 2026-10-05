# E011FX — native `0x16072D8` pair to `CA6280` frontier

A bounded same-boot SP7 KDNET front-camera measurement established the current 16-byte dependency at `0x16072D8`: the first qword remains image-relative to RVA `0x1607180`; the second qword is stable, nonzero and not image-relative. Its absolute Windows value is intentionally redacted from public artifacts, and the older file-initial second pointer RVA `0x1607650` is explicitly rejected as current native authority.

Four source-exact placements execute the original `0xCAD8C8` load and the current branch/store prefix through `0xCAD938`. The pair is copied intact to `SP+0x28`, the one-byte owner flag `1` is stored at `SP+0x38`, and the qualified register state reaches `0xCAD93C -> 0xCA6280` with the exact current argument tuple. `CA6280` is not executed here.

This checkpoint uses one front reader Start from the completed native measurement and records two Windows oracle excursions since E011FW base (the second was a reconstruction-only reboot with no camera Start). No rear Start or kernel build occurred, Golden Linux is restored, and native rear runtime remains denied. NEXT is E011FY.
