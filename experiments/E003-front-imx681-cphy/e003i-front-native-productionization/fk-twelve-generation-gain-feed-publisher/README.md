# E003i-FK — twelve-generation C gain-feed publisher

Status: **PASS_OFFLINE_G1_G12_C_PUBLISHER / no camera runtime.**

FK extends FC's exact 24-byte gain-feed ABI from G1..G9 to G1..G12 for bounded R13..R15 continuation. The only C source delta is the accepted generation upper bound 9 -> 12. Request identity remains request = generation + 3; G13 is rejected.
