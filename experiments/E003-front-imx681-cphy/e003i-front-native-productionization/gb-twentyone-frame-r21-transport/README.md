# E003i-GB — twenty-one-frame R21 transport

Status: **offline transport candidate / no GB camera runtime.**

GB extends the proven FT eighteen-frame transport by exactly three frames. The buffer cycle continues with frames 19..21 on buffers 2,3,0; steady IQ slots continue 0,1,0; and the requeue window extends from 14 to 17 completed sequences.

The AEC/TL_BG collector covers G1..G21. CQ gain publication remains bounded to G1..G18 because GA consumes G2..G18 for R5..R21. Physical sensor writes remain exactly the existing G1/G2/G3 sources released at completed G2/G3/G4.

Acceptance regenerates the complete transport lineage, builds CAMSS with W=1, builds the helper with -Werror using the real FZ gain publisher, and unit-tests G1..G21 scheduling with exactly three sensor writes.
