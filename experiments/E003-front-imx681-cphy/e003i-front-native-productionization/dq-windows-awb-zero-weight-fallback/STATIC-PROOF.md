# DQ static proof

## Pinned functions

- `CSAAGWV1` accumulator: `0x1806d0dc0..0x1806d0f70`, SHA256 `df0ecd1018d5d941e57df6bb956f290747c0444ecf8bc033945003bfbea18a5a`
- `CSAAGWV1` finalizer: `0x1806d1090..0x1806d1920`, SHA256 `375d2b6544312f9d8c371360343b0258e4c16354bc92379d2821aaec3b0c9f33`
- `CAWBMain::RunWBROIBased` fallback owner: `0x180692848..0x180693058`, SHA256 `aa03f830c5a7f8b549cf29de5d84c3f5c630d3d376194671610ce432a60aa869`

## Aggregate zero handling

Critical ARM64 at `0x1806d10ac`:

```
ldr   s18,[x19,#0x58]
fcmp  s18,#0.0
b.eq  0x1806d10d0
ldp   s17,s16,[x20,#0x4c]
fdiv  s17,s17,s18
fdiv  s16,s16,s18
stp   s17,s16,[x20,#0x4c]
b     0x1806d10d4
0x1806d10d0: stur xzr,[x20,#0x4c]
```

The zero branch stores one zero 64-bit value over adjacent float X/Y.

## Higher-level fallback

Critical ARM64 at `0x180692c9c`:

```
ldp   s8,s9,[sp,#0x20]
fcmpe s8,#0.0
b.le  0x180692d7c
fcmpe s9,#0.0
b.le  0x180692d7c
...
# only the positive path writes the new decision point to persistent state
```

The fallback block owns the production log string:

`CID:[%d] Computed Decision Point rg : %f, bg :%f, previous AWB gains will be used`

After either fallback branch, execution joins the common copy-forward block without replacing the previous persistent decision state.

## Conclusion

Aggregate AGW weight zero is a valid no-update frame. The caller must preserve previous AWB state. Returning a fatal producer error, or applying the normal startup 60/40 temporal filter to a fabricated `(0,0)` fresh target, is inconsistent with Windows.
