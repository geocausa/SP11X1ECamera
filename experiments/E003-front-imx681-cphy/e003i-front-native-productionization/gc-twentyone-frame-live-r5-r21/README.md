# E003i-GC — fresh bounded twenty-one-frame R5–R21 live candidate

Status: **staged offline / unarmed / no GC stream yet.**

GC is the fresh live successor authorized by the closed R21 chain:

- FY: calibrated AWB selector reproduces the live Windows selector object and Windows AWB through R21.
- FW: one bounded Windows stream provides combined AWB + Tintless/LSC authority through R21.
- FV: R19..R21 offline continuation is deterministic and Windows-authorized.
- FZ: compiled CQ gain publisher accepts G1..G18 and rejects G19.
- GA: live-capable producer composes R5..R21 from G2..G18.
- GB: 21-frame transport collects G1..G21 and consumes IQ through R21.

The helper runs one bounded 21-frame stream. Its DQBUF cycle is:

`0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0,1,2,3,0`

CQ gain publication stops after G18 because G18 produces R21. G19..G21 are collector-only generations. Physical IMX681 writes remain bounded to exactly G1/G2/G3 released after completed G2/G3/G4.

GC is one-shot: one stream attempt per candidate boot, no same-boot retry. Raw evidence must be archived before a whole-machine Golden return. It does not claim unrestricted or continuous AEC.
