# E003i-FT — bounded eighteen-frame R18 transport

Status: **offline candidate / no FT camera runtime.**

FT extends FM's already-live-proven fifteen-frame ownership chain by exactly three steady frames: frame/request 16 on IQ slot1/video3, 17 on slot0/video0, and 18 on slot1/video1.

The helper extends paired TL_BG/3A auditing to G1..G18 and CQ gain publication only through G15 for FS R5..R18. The delayed physical sensor-write schedule remains exactly G1..G3 released at completed G2/G3/G4.

Acceptance requires CAMSS W=1, helper Werror, exact ownership/requeue checks through frame 18, G1..G18 scheduler completion, and exactly three physical sensor writes.
