# E003i-HN — snapshot-generation reset + rebuilt package authority

HN implements the minimal HM fix: both front-PIX exported snapshot reset functions now zero their generation counter under the same lock that clears payload/source/slot/valid state. No sensor-control policy, CSID programming, runner ordering, producer contract, or userspace capture logic changes.

The offline gate requires two logical sessions to start at generation 1, two byte-identical production builds, unchanged non-CAMSS artifacts, Golden vermagic, deterministic package staging, real-topology launcher discovery, and byte-exact R5..R27 producer output. No camera runtime is authorized by HN.
