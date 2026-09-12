# Camera IH — same-boot front -> neutral -> rear R27/R16

Status: **installed / not armed / no runtime**.

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
