# E003i-GI — fresh bounded twenty-four-frame R5–R24 live candidate

Status: **staged offline / unarmed / no GI stream yet.**

GI is the fresh live successor authorized by the closed R24 chain:

- FY: calibrated AWB selector.
- GD: one bounded Windows stream provides combined AWB + Tintless/LSC authority through R24.
- GE: R22..R24 offline continuation is deterministic and Windows-authorized.
- GF: compiled CQ gain publisher accepts G1..G21 and rejects G22.
- GG: live-capable producer composes R5..R24 from G2..G21.
- GH: 24-frame transport collects G1..G24 and consumes IQ through R24.

The helper runs one bounded 24-frame stream with buffer cycle 0,1,2,3 repeated six times. CQ gain publication stops after G21 because G21 produces R24; G22..G24 are collector-only generations. Physical IMX681 writes remain exactly G1/G2/G3 released after completed G2/G3/G4.

GI is one-shot: one stream attempt per candidate boot, no same-boot retry. Raw evidence must be archived before a whole-machine Golden return. It does not claim unrestricted or continuous AEC.
