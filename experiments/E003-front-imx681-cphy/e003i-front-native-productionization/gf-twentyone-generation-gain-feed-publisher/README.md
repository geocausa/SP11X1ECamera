# E003i-GF — twenty-one-generation gain-feed publisher

Status: **PASS OFFLINE G1..G21 publisher / no camera runtime.**

GF extends FZ by one bounded validation change: accepted generation upper bound 18 -> 21. ABI, request identity, float-bit publication and error handling are unchanged. The real C source must accept G1..G21 and reject G22.
