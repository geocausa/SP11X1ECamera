# E003i DM — Windows internal CapExposure bounds

Base checkpoint: 9203815 (oracle plan), following DL 47f9691. One normal front-camera Windows capture completed on 2026-09-10; no exposure targets were injected.

## Result

PASS: 18 matched internal cap input/output records, requests 1..18. Requests 1..7 are unchanged; requests 8..18 clamp every lane to **6,133,333,088**. All seven request-local lower limits are 37,516; upper limits are 66,666,664 × 92 = 6,133,333,088. This is 184 below the serialized T681 endpoint 6,133,333,272. The common bounds field +0x230 is 37,516. Its wider upstream semantics are not established here.

Each sample has PredGain 0x3f800000 before and after, compact+0x98=0, and the separate controller cap flag=0. All samples bypass the conditional rescaling prelude independently of bank9:data10. That branch input was **not captured**; these observations do not establish its general value. The internal cap still changes 11 requests despite the separate controller flag remaining zero.

CDB cleared breakpoints and detached automatically. The holder reported START_STATUS=Success, STOP_PASS and DM_HOLDER_END. The limit literal `12` used CDB's hexadecimal radix, producing decimal 18 requests; this was still bounded and the completion marker confirms all 18. Future scripts should use explicit decimal radix.

Raw evidence is outside Git at:
`/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-dm/windows-internal-cap-20260910`.

Archive zip SHA256: `61b5a6f66da1bba079f51c6d8297c85dcda68092e421bd5570c37328a59ba327`.
Pinned DLL SHA256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

## Verification and rollback

`parse-dm.py ARCHIVE RESULT.json` validates all records, exact bounds, observed-domain tail arithmetic, capture completion and holder shutdown. RESULT.json contains derived values and raw-log hash, without process addresses.

SP11 returned normally to protected FullIO v19c Golden. GOLDEN-RETURN.txt verifies kernel, saved entry, empty next_entry and absent camera modules. No Linux camera candidate was installed or run by DM.

Continue at ../dn-native-aec-internal-cap/HANDOFF.md.
