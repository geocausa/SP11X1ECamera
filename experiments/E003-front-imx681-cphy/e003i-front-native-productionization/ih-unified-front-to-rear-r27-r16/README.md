# Camera IH — same-boot front -> neutral -> rear R27/R16

Status: **PASS live front -> neutral -> rear / Golden restored / candidate retired**.

IH is the independent reverse-direction companion to passed IG. It uses the same exact IB unified DTB and module authority under a fresh one-shot identity.

One consumed attempt is permitted:
1. Verify all four mutable rear/front route links are neutral.
2. Consume the attempt before any route mutation.
3. Run exactly one 27-frame front production stream with shadow post-G3 policy.
4. Require front runtime suspend after close and verify front-only routing.
5. Explicitly disable both front mutable links and verify a fully neutral topology.
6. Enable only the rear route and run the accepted rear sequence: one exact color-bar frame plus 16 normal frames.
7. Require rear runtime suspend and final rear-only routing.
8. No same-stream or same-boot retry; return directly to Golden, archive, retire.

Passing IH together with IG closes the bidirectional same-boot route-handoff proof. It does not by itself prove indefinite camera switching or the parked brighter-scene post-G3 native-feedback gate.

The exact IH candidate is now installed under /boot/sp11-7.1.5-camera-ih-front-to-rear-r27-r16. Golden remains the saved default and next_entry is empty. Installed-unarmed state must be committed and pushed before arming.

## Live result

IH passed the independent reverse same-boot handoff exactly once. The candidate began neutral, consumed before the first route mutation, ran one front R27 production stream, observed front runtime suspend, explicitly disabled both front mutable links, verified fully neutral topology, enabled rear-only, then captured the exact accepted OV13858 color-bar frame plus 16 normal frames and observed rear runtime suspend. Final route state was rear-only. Front delivered 27/27 frames with fresh generation 1, 24 producer generations / 23 requests, startup writes G1..G3 only, zero post-G3 native writes, four hardware control transactions, clean STREAMOFF and clean kernel health. No retry occurred.

Candidate boot ID d55aca5c-519c-42a6-afcf-b24da423a80f; Golden return boot ID c19b139c-41a7-431c-9ca8-09773203a9ca. The candidate is retired. Final archive manifest SHA256: 4c988c514992ec69e92449aaf66e7eb90cc35365d735c54ae2d2fda5fcd4c0ea.

Together, IG and IH now prove both rear -> neutral -> front and front -> neutral -> rear bounded same-boot route handoffs under the exact unified IB DTB. This closes bidirectional bounded handoff, but not indefinite switching/soak or the parked brighter-scene native-feedback gate.
