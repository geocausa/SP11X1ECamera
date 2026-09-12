# Camera IG — same-boot rear -> neutral -> front R16/R27

Status: **PASS live rear -> neutral -> front / Golden restored / candidate retired**.

IG is the first cross-camera same-boot proof under the unified IB DTB. It follows IF's neutral-route ownership contract and uses a fresh one-shot identity.

One consumed attempt is permitted:
1. Verify all four mutable rear/front route links are neutral.
2. Consume the attempt before any route mutation.
3. Enable only the rear route and run the accepted rear sequence: one exact color-bar frame plus 16 normal frames.
4. Require rear sensor runtime suspend after close.
5. Explicitly disable both rear mutable links and verify a fully neutral topology.
6. Run exactly one 27-frame front production stream with shadow post-G3 policy.
7. Require front HY-equivalent acceptance and prove the rear route stayed disabled.
8. No same-stream or same-boot retry; return directly to Golden, archive, retire.

Passing IG proves rear -> front switching only. The reverse front -> rear direction still requires a separate IH one-shot before whole-stack/default promotion.

The exact IG candidate is now installed under /boot/sp11-7.1.5-camera-ig-rear-to-front-r16-r27. Golden remains the saved default and next_entry is empty. Installed-unarmed state must be committed and pushed before arming.

## Live result

IG passed the first same-boot cross-camera handoff exactly once. The candidate boot began with all four mutable route links neutral, consumed before the first route mutation, enabled rear-only, captured the exact accepted OV13858 color-bar frame plus 16 normal frames, and observed rear runtime suspend. It then explicitly disabled both rear mutable links and verified a fully neutral topology before launching one front R27 production stream. The front stream delivered 27/27 buffers with fresh generation 1, 24 producer generations / 23 requests, startup writes G1..G3 only, zero post-G3 native writes, four hardware control transactions, clean STREAMOFF and clean kernel health. Final route state was front-only. No retry occurred.

Candidate boot ID fb66ae54-96d6-45c1-80a8-f4dc9993c93d; Golden return boot ID a194bf45-4191-4326-9a20-fe6f7a6c384f. The candidate is retired. Final archive manifest SHA256: 09c8e7d29d34c8084125fc3a62fa2340d7db3e5366ac0a7d644f79865ae0a9a3.

IG proves the rear -> front direction only. A fresh independent IH one-shot must prove front -> neutral -> rear before same-boot bidirectional switching or whole-stack default promotion is accepted.
