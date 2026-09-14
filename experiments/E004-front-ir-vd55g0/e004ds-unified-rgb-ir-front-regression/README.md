# E004ds — front RGB production regression under unified RGB+IR authority

Status: **PREPARED OFFLINE / NOT INSTALLED / NOT ARMED**.

E004dp closed simultaneous three-camera bind plus Windows-exact CSIPHY0 receiver coexistence. E004dr then proved the accepted rear RGB path still streams byte/timing-exact under the same three-camera DTB and IR-gated CAMSS lineage.

E004ds is the independent front counterpart. It stages the exact accepted E004dn front production package (manifest SHA `60a34901...`) containing the Windows-fallback AWB port, but runtime-loads the exact-lineage IR-gated CAMSS module `862732b7...` instead of the package's baseline `7afe6ed0...` module.

One fresh one-shot may bind rear OV13858, front IMX681 and IR VD55G0, then execute exactly one accepted front R27 production launcher run with post-G3 policy `shadow`. Rear and IR must remain unstreamed. After the 27-frame front run, the front route is disabled and all three sensors must be runtime-suspended.

Acceptance requires: 27 dequeued front frames sequences 0..26, `STREAMON_OK_ASYNC`, `STREAMOFF_OK`, clean producer result with 24 rows, valid AWB selection modes, zero later native writes under `shadow`, final neutral route, no CSIPHY0 IR-gate selection marker, no rear stream, no IR stream, no illumination, no Linux SecureISP/protected-memory action, clean kernel, one attempt only, Golden return and retirement.

## Attempt 1 — PASS and retired

Fresh candidate boot `76ea2b42-7589-4e28-bd9e-b08f1f0cc049` passed the front production regression under the three-camera authority. The accepted R27 launcher produced sequences 0..26, completed the provider-owned bounded 27-frame requeue, and the producer returned 24 PASS rows. All 24 AWB selections were ordinary `triangle` mode in this scene; no fallback row was needed. Post-G3 policy remained `shadow` with zero later native writes.

Rear and IR remained unstreamed. The IR-gated CAMSS parameter was armed but its CSIPHY0 programming marker did not appear during the front CSIPHY2/C-PHY run. Routing returned to neutral and all three sensors were suspended afterward. No illumination, Linux SecureISP action or kernel fault occurred.

SP11 returned to protected Golden FullIO v19c on boot `dba28692-7f66-49c5-b93d-a3d6cc5b0e2d`, and the candidate was retired.

Together with E004dr, both accepted RGB cameras have now independently streamed successfully under the same unified rear+front+IR DTB and IR-gated CAMSS lineage.
