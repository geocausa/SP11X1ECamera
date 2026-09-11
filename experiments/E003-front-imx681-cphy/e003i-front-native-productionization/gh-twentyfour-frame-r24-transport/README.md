# E003i-GH — twenty-four-frame R24 transport

Status: **offline transport candidate / no GH camera runtime.**

GH extends the proven GB twenty-one-frame transport by exactly three frames. Frames 22/23/24 continue on buffers 1/2/3, steady IQ slots 1/0/1, and the requeue window extends from 17 to 20 completed sequences.

The AEC/TL_BG collector covers G1..G24. CQ gain publication remains bounded to G1..G21 because GG consumes G2..G21 for R5..R24. Physical sensor writes remain exactly G1/G2/G3 released at completed G2/G3/G4.
