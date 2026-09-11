# E003i-GL — twenty-four-generation gain-feed publisher

Status: **PASS OFFLINE G1..G24 publisher / no camera runtime.**

GL extends GF by exactly one bounded validation change: accepted generation upper bound 21 -> 24. ABI, request identity, float-bit publication and error handling are unchanged. The real C source must accept G1..G24 and reject G25.
