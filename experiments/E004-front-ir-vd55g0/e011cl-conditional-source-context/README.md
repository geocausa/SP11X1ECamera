# E011CL original conditional source context

Status: **PASS, bounded source-only prefix**. Base: `1ccf55cf404d893473bcfa98f81f6ce5c4664637`.

Hypothesis: original instructions after the accepted E011CK comparison return select a source-derived scene-change context and make exactly six inner-object stores through the stop before `0x36DE04`. Original `0x36CBA0` entry and the entire inherited prefix execute first. The new conditional portion is 428 bytes. All 24 cases pass: three pinned same-SP11 sources, four owned placements and two variants (unmodified or explicit six-field destination poison). Numeric callbacks execute originals; no new numeric/TLS success stub is admitted.

The independent model reads serialized `aecxscenechangedetector` metadata and `scdBank` records. Counts differ across sources: 3/3/4. A 144-byte serialized record expands to a guarded 176-byte owned record, giving 528/528/704-byte arrays. Every record's first 12 scalar bytes and source `SCDName` buffer are checked against serialized source data. Flag and name matching independently select record 1. The original search visits records 0 and 1; the actual X24 selected pointer, X0 metering-name/X1 bank-name comparison arguments and retained selected+8 field match the model.

The scene-change module is the actual 352-byte module in primary core cache 37; metering is the actual 624-byte module in cache 31. Their payload source IDs match the typed source metadata. Metering's name is the actual guarded 7-byte buffer retained at module+368. Its full serialized upstream producer and the full bank/metering payloads are not newly qualified.

| Original store site | Inner offset | Bytes | Independent value |
| --- | --- | --- | --- |
| `0x36DC78` | 555728 | 4 | Matched-context flag 1 |
| `0x36DC84` | 555752 | 4 | Selected serialized record's field+8 |
| `0x36DC8C` | 555760 | 8 | Actual metering module+360 |
| `0x36DD24` | 555768 | 4 | Typed metering source ID |
| `0x36DD30` | 555772 | 4 | Typed scene-change source ID |
| `0x36DDD8` | 555776 | 8 | Unsigned 64-bit all-ones sentinel |

All 144 store chunks are checked by site, offset, width and value. An independently predicted entire 606264-byte inner delta and whole-arena comparison reject any other object, gap or guard change. This portion allocates/releases nothing. The exact source read receivers at `0x36DC7C/36DD1C/36DD28` are verified. The tested inner+91908 flag is zero; the stop is before the original `0x7AC38` call. Alternate nonmatching and nonzero-flag branches are not qualified.

Inherited checks pass: 360 independent 152-byte records, 2880 statistics initializers, 584 core initializers, 1032 core-cache lookups plus 48 additional module lookups. Whole mapped image/native heap/serialized source and exact caller/TLS deltas remain checked. Statistics+40 and mode+91952 are retained; the 72-byte outer is unchanged, public output is zero and the owned single-thread lock is held. This is not proof of concurrent lock behavior, final publication, whole return or attachment lifetime through return.

Four rejected matrix attempts remain private: schema-label mismatch (two), comparison-pointer argument reversal (one), and a fixed three-record assumption (one). The accepted verifier uses exact `SCDName`, original X1 selected-bank argument and source-derived variable count. Failed checker runs are excluded, not hardware camera failures.

A static original-reference scan identifies enclosing pdata entry `0xCB3260` and stores to the missing CRT globals `0x16A2A50/58`. Candidate targets `0xCB75E0/CB1650/CBA4B0` still need dynamic source/default/OS ownership proof. The prior second CRT-lock extension and null-global `0xCC6140` read remain excluded. No guessed locale, null mapping or CRT success substitute is accepted.

Changed files are this six-file experiment and eight continuation/readiness documents. No production C, kernel, deployment, camera Start, reboot or optical test. Golden boot/payload hashes and historical checkout state match `GUARD-SAFE.json`. Original DLL/tuning/source strings/instruction text and optical evidence remain private on SP11. Rollback: retain E011CK and this source-only record; Golden is untouched.

Next: **E011CM**, source-only CRT initialization/global/locale/OS ownership before final output/outer-inner publication, whole return and balanced lock release. Full bootstrap/preflight/RS count/whole-frame offset and independent enabled WM16 IRQ/consumed IOVA/DMA/IOMMU retirement/optical gates keep native rear runtime denied. Optional AI/effects/HDR/catalogue remain deferred.
