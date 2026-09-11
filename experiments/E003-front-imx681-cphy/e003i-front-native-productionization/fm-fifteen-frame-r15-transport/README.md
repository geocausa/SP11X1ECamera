# E003i-FM — bounded fifteen-frame R15 transport

Status: **offline candidate / no FM camera runtime.**

FM extends FE's already-live-proven twelve-frame runner by exactly three steady frames: frame/request 13 on slot0/video0, 14 on slot1/video1, and 15 on slot0/video2. The helper extends paired TL_BG/3A auditing to G1..G15 and CQ gain publication only through G12 for FL R5..R15. The delayed physical sensor-write schedule remains exactly G1..G3 released at completed G2/G3/G4.
