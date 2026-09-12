# E003i-HA — native cap-release one-write policy

Status: **PASS OFFLINE / no camera runtime / no synthetic gain escalation.**

GZ showed why GY did not reveal the production feedback threshold: native Short convergence is hard-censored by the Windows-derived preview cap from G3 through G27. HA therefore stops trying to provoke the controller with synthetic gain steps and defines the first production-native later-write gate.

For any source after G3, HA allows exactly one native control tuple only when all of the following are true:

1. no later native write has already been applied;
2. the native Short convergence is **strictly below** `E003I_PREVIEW_CAP_MAX=6133333088`;
3. the cap output exactly equals the unconstrained convergence value, proving the cap did not modify it;
4. the native IMX681 tuple differs from the last successfully applied tuple.

Otherwise the source remains shadow-only. The policy never manufactures or enlarges a sensor-control delta. G1..G3 remain owned by the already-proven startup path.

Replay of immutable GY evidence proves HA would have allowed **zero** later writes there because the cap stayed active. Synthetic unit cases prove a below-cap changed native tuple is accepted once, then every later tuple is suppressed after the one-write latch.

This closes the decision policy only. It does not authorize a live run by itself. The next integration gate must carry the native AEC convergence/cap result to the exact DQBUF release boundary and preserve the one-write latch.
