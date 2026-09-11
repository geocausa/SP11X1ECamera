# E003i-GN — twenty-seven-frame R27 transport

Status: **offline transport candidate / no GN camera runtime.**

GN extends the proven GH twenty-four-frame transport by exactly three frames. Frames 25/26/27 continue on buffers 0/1/2, steady IQ slots 0/1/0, and the requeue window extends from 20 to 23 completed sequences.

The AEC/TL_BG collector covers G1..G27. CQ gain publication remains bounded to G1..G24 because GM consumes G2..G24 for R5..R27. Physical sensor writes remain exactly G1/G2/G3 released at completed G2/G3/G4.
