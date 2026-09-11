# E003i-GP — GO control/statistics timing authority

Status: **PASS OFFLINE / read-only analysis of immutable GO evidence / no camera runtime.**

GP turns the consumed GO R27 stream into an explicit timing contract for the continuous-control pivot. It does not invent later sensor writes. It proves what the existing live run actually measured and separates that from the next scheduler hypothesis.

The current established algebra is:

- stats/control source generation `G`
- logical request/effect generation `G+3`
- physical sensor write gated immediately after completed video generation `G+1`
- sensor pipeline write-to-effect delay `+2` generations

GO directly exercised this law for G1/G2/G3 only. Those three writes began within 0.2 ms of their DQBUF gate, finished before the following DQBUF, and had 10.34–14.93 ms observed margin before the next completed frame. No later physical write occurred, so continuous writing remains unproven.

For a finite 27-frame replay, sources G1..G24 are the only sources whose logical effect G+3 remains inside the captured G1..G27 window. That gives the next offline scheduler an exact bounded target: queue G1..G27, but release only G1..G24 after G2..G25. This is an offline design target, not authorization for live hardware.
