# Camera IB — unified current-Golden rear+front DTB

Status: **PASS / offline only**.

IB constructs the first deterministic combined rear+front camera DTB without replacing the protected Golden system. The starting artifact is the proven HV DTB, itself derived from the exact current Golden tree. IB makes only the IA-authorized camera changes: remove the front-isolation `status="disabled"` from OV13858, add the accepted rear sensor/CAMSS `port@1` endpoint pair, and replace the front five-entry CAMSS fwspec with IA's conservative 11-specifier union. Front `port@2`, RT-CDM1, front VFE apertures and every other HV CAMSS resource remain byte-exact.

The resulting DTB contains 1,437 nodes: all 1,402 Golden nodes plus 35 camera nodes. Every pre-existing Golden property is byte-exact. Relative to HV, the only common-node changes are the rear status removal and CAMSS `iommus`; four rear route nodes are added. Rear sensor/port semantics match E002k-D-R3 after phandle remapping, while the front route is copied unchanged. Both endpoint pairs and camera symbols resolve correctly.

The build is deterministic at SHA256 `5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321`, and DTC emits exactly the same pre-existing warnings as HV with no graph regression. **No runtime is authorized by IB.** Next is a rear-first unified-DTB regression candidate prepared offline and checkpointed before any installation or boot.
