# E003i-HE — production integration inventory

Status: **PASS OFFLINE / no camera runtime.**

The experimental front-RGB stack is technically much further ahead than its repository shape suggests. R27 capture/IQ, IMX681 control transport, native AEC composition, continuous scheduling and the fail-closed cap-release gate all have durable authorities. The integration problem is now largely one of **consolidation and lifecycle engineering**, not discovering the basic camera pipeline again.

HE identifies the main production gap: there is no stable `src/`/production package. The final CAMSS source and final capture helper are still generated through long experiment transform chains; the GM IQ producer dynamically imports many earlier experiment modules; boot/install scripts are intentionally machine/path-specific one-shot harnesses. This is excellent for evidence-driven reverse engineering, but it is not yet a maintainable camera stack.

The next safe step is deliberately boring: create a stable front-IMX681 source bundle containing **byte-identical proven sources plus a provenance manifest**, without changing behaviour and without running the camera. Only after that bundle is reproducible should we remove experiment-directory imports, absolute workspace coupling, add stable media discovery/installation, and start repeated-stream robustness testing.

Post-G3 native sensor feedback remains a separate parked gate. The production bundle must keep later native writes fail-closed until HD's brighter-real-scene condition is available and proven.
