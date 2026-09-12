# Camera IG — same-boot rear -> neutral -> front R16/R27

Status: **prepared / not installed / not armed / no runtime**.

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
