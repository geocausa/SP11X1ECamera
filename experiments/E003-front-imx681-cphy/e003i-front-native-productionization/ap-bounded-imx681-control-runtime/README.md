# E003i-AP — live AM sensor controls with AO paired-stats audit

Status: **PASS — bounded live non-default IMX681 control + AO paired-stats audit closed.**

AP is not an AN retry. AN proved the exact AM group-held sensor transaction live and its producer submitted both R5 and R6, then the parent pinned because its old TL_BG-first/3A-second one-shot audit straddled a latest-snapshot publication boundary. AN returned Golden without retry.

AP changes only the parent capture helper to AO. AO starts a 3A-first -> TL_BG target-generation collector before STREAMON, stores generations 1..6 in memory, and writes evidence after all six frames. AM, Z/Y CAMSS, front-only DTB, template-free R4 and the deadline-hardened producer are unchanged.

Acceptance requires cached controls FLL 3554 / exposure 3500 / analogue 0x040 / global digital 0x0110, the exact AM `ret=0` transaction, six QC10C frames, AO paired generations 1..6, live R5/R6 submissions, clean kernel health, no same-boot retry and mandatory Golden return.

## AP executed result

AP consumed exactly one candidate boot. The pre-stream cache held FLL `3554`, exposure `3500`, analogue code `0x040`, and global digital code `0x0110`. At STREAMON the AM driver emitted the exact group-held hardware transaction with `ret=0` (twice during control restore/setup).

The AO collector started before STREAMON and captured matching `(generation, source_seq, slot)` identities for generations 1..6. The unchanged producer completed and submitted R5 `93096dc3...1073f` from G2 and R6 `4c13fefa...89c15` from G3. Six QC10C frames completed in order, STREAMOFF succeeded, and the kernel-health scan was clean. SP11 then returned to the saved Golden entry with `next_entry` empty and no camera modules loaded. No same-boot retry occurred.

The initial post-run Python verifier contained a schema-only bug: it looked for top-level `r5_submitted`/`r6_submitted`, while the producer records `submitted_live=true` on the G2/G3 rows. Correcting that verifier against the already-completed evidence passes without another stream.

This closes the bounded live sensor-control transport. It does **not** claim continuous AEC yet; the producer still uses the bounded fixed Lux-history seed. The next gate is request-local continuous AEC state/output feeding the now-live-proven AM sensor controls.
