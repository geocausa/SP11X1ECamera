# E004dh — Windows `FUN_18001c230` scalar closure

`FUN_18001c230` is the arithmetic core nested inside Windows SWASF `FUN_18001c3e8`.  It was called directly in the shipping `QcISPTrustlet8380.dll` after the normal SWASF module init.  The Windows binary is normative; the Ghidra decompile is explanatory only.

## Exact lane shape

The function consumes seven pointers to eight signed-16 samples plus two signed-16 tail samples.  It produces two 32-bit high-pass/intermediate values and two byte low-pass/control values.  The two lanes use horizontally shifted 7×7 windows: lane 0 reads columns 0..6 and lane 1 reads columns 1..7.

The apparent four `short` values printed by the first oracle are the little-endian halves of two signed 32-bit outputs.  This was confirmed by the `+4096/-4096` basis run.

## High-pass/intermediate kernel

The direct Windows +4096 basis exposes the exact signed kernel because Windows rounds after an 8-bit right shift:

```
 -7  -23  -41  -49  -41  -23   -7
-23  -73  -74  -53  -74  -73  -23
-41  -74   89  242   89  -74  -41
-49  -53  242    0  242  -53  -49
-41  -74   89  242   89  -74  -41
-23  -73  -74  -53  -74  -73  -23
 -7  -23  -41  -49  -41  -23   -7
```

The kernel sum is `-508`; the corresponding tail coefficient is `+508`, so a constant field cancels exactly.  Windows computes signed rounding shift by 8.

## Low-pass/control kernel

Using a zero baseline with ±4096 impulses exposes the exact second kernel because this path rounds after a 12-bit right shift:

```
 0   0   0   0   0   0  0
 0   9  23  31  23   9  0
 0  23  60  82  60  23  0
 0  31  82   0  82  31  0
 0  23  60  82  60  23  0
 0   9  23  31  23   9  0
 0   0   0   0   0   0  0
```

Its kernel sum is `912`; the tail coefficient is `112`, giving total DC gain `1024`.  With a constant input of 512 this yields `(512*1024)>>12 = 128`, exactly matching Windows.

The 48-byte post-init constant block at trustlet RVA `0x3c120` contains the unique coefficient set used to synthesize both matrices:

`[0,0,0,0, 9,23,31,60, 82,112,0,0, -7,-23,-41,-49, -73,-74,-53,89, 242,508,0,6144]` as signed little-endian 16-bit values.

## Scalar verification

`scaffold/sp11-swasf-c230.c` implements both two-lane filters with the Windows rounding shifts. `verify_c230_windows_basis.py` compiles that C as a shared object and compares it against **232 direct Windows oracle cases** (±256 around 512 and ±4096 around zero), including every row/column basis position and both tail inputs.

Current result: **232/232 byte/numeric outcomes match**.  A deterministic 4096-case random differential against the shipping Windows helper is also byte-exact.  The Windows and scalar aggregate SHA-256 values are both `f926c06b87b2679132cd9ac41b0a590578e712e353ce91732a646b584756d035`.  The nested C230 helper is therefore closed; the next task is the C3E8 wrapper/edge semantics.
