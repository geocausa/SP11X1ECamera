# E004ds — front RGB production regression under unified RGB+IR authority

Status: **PREPARED OFFLINE / NOT INSTALLED / NOT ARMED**.

E004dp closed simultaneous three-camera bind plus Windows-exact CSIPHY0 receiver coexistence. E004dr then proved the accepted rear RGB path still streams byte/timing-exact under the same three-camera DTB and IR-gated CAMSS lineage.

E004ds is the independent front counterpart. It stages the exact accepted E004dn front production package (manifest SHA `60a34901...`) containing the Windows-fallback AWB port, but runtime-loads the exact-lineage IR-gated CAMSS module `862732b7...` instead of the package's baseline `7afe6ed0...` module.

One fresh one-shot may bind rear OV13858, front IMX681 and IR VD55G0, then execute exactly one accepted front R27 production launcher run with post-G3 policy `shadow`. Rear and IR must remain unstreamed. After the 27-frame front run, the front route is disabled and all three sensors must be runtime-suspended.

Acceptance requires: 27 dequeued front frames sequences 0..26, `STREAMON_OK_ASYNC`, `STREAMOFF_OK`, clean producer result with 24 rows, valid AWB selection modes, zero later native writes under `shadow`, final neutral route, no CSIPHY0 IR-gate selection marker, no rear stream, no IR stream, no illumination, no Linux SecureISP/protected-memory action, clean kernel, one attempt only, Golden return and retirement.
