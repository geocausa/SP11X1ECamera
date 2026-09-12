# Camera IJ — bidirectional production-handoff acceptance decision

Status: **PASS / offline decision / no camera runtime**.

IG and IH now prove both bounded same-boot directions under the exact unified IB DTB and exact production module authority:

- rear -> explicit neutral topology -> front;
- front -> explicit neutral topology -> rear.

Both directions consumed exactly one fresh candidate, used no same-boot retry, observed source/target sensor runtime suspend, preserved the front shadow post-G3 policy, passed kernel-health checks, returned to protected Golden, and retired the candidate.

## Decision

The unified rear-RGB + front-RGB production handoff is **accepted as a bounded bidirectional production candidate**. The exact IB DTB and pinned CAMSS/IMX681/OV13858 module set are now the durable authority for future integrated RGB work. The neutral-route transaction is mandatory: close/suspend source, explicitly disable both source mutable links, verify all four rear/front mutable links neutral, then enable the target route.

This does **not** authorize replacing protected Golden or calling the full SP11 camera stack complete.

Persistent/default promotion remains blocked by three independent boundaries:

1. **Front IR / VD55G0 is still unproven on Linux.** A full camera-stack default cannot omit the Windows Hello/IR sensor path.
2. **Front post-G3 native feedback remains environment-blocked.** Production R27 is accepted with post-G3 policy shadow; the brighter diffuse-scene cap-release proof remains separate and no synthetic delta is authorized.
3. **Repeated alternating cross-camera switching has not been soaked.** IG and IH prove one bounded transition in each direction, not indefinite toggling.

Because IR is the largest missing functional block, the next highest-value work is E004 VD55G0 bring-up from the existing Windows oracle. A repeated alternating RGB switch soak may be added before final default promotion, but it should not delay initial IR authority/driver work.

Protected Golden remains unchanged and saved by default.
