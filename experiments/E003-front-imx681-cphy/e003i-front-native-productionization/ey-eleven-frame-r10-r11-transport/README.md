# E003i-EY — bounded eleven-frame R10/R11 transport

Status: **offline transport PASS target; no EY camera runtime.**

EY extends the already-live-proven ES/EV nine-frame runner to exactly eleven frames. Frames 10 and 11 repeat only the proven steady Epoch0/rebind/retire sequence, consuming R10 on frame10/slot1 and R11 on frame11/slot0. Userspace DQBUF order becomes 0,1,2,3,0,1,2,3,0,1,2 and completions through frame7 are requeued. Native AEC accepts G1..G11, CQ residual gain publication extends only through G8 for EX R5..R11, and physical sensor writes remain exactly G1..G3 at completed G2/G3/G4.

Offline acceptance requires deterministic transforms, CAMSS W=1, helper Werror with EW's real G1..G8 C publisher, and an 11-generation scheduler test with exactly three sensor releases. No camera stream is run by EY.
