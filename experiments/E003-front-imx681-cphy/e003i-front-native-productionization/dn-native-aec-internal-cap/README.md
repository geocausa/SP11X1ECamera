# E003i DN — native internal exposure cap

Base: 9203815 plus the DM reference evidence. This additive offline experiment closes the saved DB attempt4 G4 overflow in the observed preview domain. It does not yet establish continuous live AEC.

## Change

Windows PopulateOutput calls internal CapExposure before T681 arbitration; DJ omitted it. DN independently implements that arithmetic in native-internal-cap.c, preserving float32 operation order, unsigned min/max, conditional Short rescaling, history snapping, ordered Short/Long/Safe/S1..S4, and the predictive-gain limit.

The generic API takes explicit limits and branch/history inputs. The ordinary preview adapter uses DM's observed bounds (37,516..6,133,333,088) and compact+0x98=0. It **returns -2 without modifying output** if the rescaling prelude is eligible, because bank9:data10 has not yet been bound to a proven native producer. It must not invent a zero/one value for that input. The generic arithmetic is implemented and tested for both branches; the runtime binding is intentionally narrower.

DN copies the DJ request loop into this experiment and inserts the cap between convergence and arbitration. Original convergence remains visible in diagnostics, capped output has its own field, and retained history uses capped PredGain. The DJ baseline and CH rejection policy remain unchanged. No hardware-facing helper or boot image is switched to DN.

## Evidence

- 18/18 ordinary Windows pre/post pairs match exactly, including 11 cap-changing pairs.
- 423 cases match original pinned ARM64 cap arithmetic, including 30 rescaling cases and 5 history snaps. The emulator models the established external history lookup/log10f primitives and runtime log1.03 scale; it is not a full Windows process replay.
- The exact SHA-pinned DB G1..G4 captures compile and replay through the DN request loop and unchanged CU/CV/control dependencies with strict warnings and floating-point flags.
- G1..G3 retain their original sensor controls.
- G4 changes from CV -142 to success: cap 6,133,333,088; T681 retained exposure 6,133,332,579; FLL7116 / exposure7108 / analogue960 / digital1471.
- Invalid input and unbound branch conditions preserve cap output. CV error handling preserves caller recurrence and output; CH still rejects 6,133,333,273 under ordinary policy.

Run `python3 verify-dn.py`. It requires the pinned local DriverStore DLL, archived captures, Python Unicorn, and a C compiler. Source dependencies are checked against 8bc6598. The live DM parser is rerun rather than blindly trusting fixture JSON.

## Limits

The saved G4 arithmetic failure is closed offline. No new Linux hardware run occurred, and no claim is made that brightness tracks control writes. DB's full-tuple write-to-statistics association remains unresolved. Keep the accepted delay unchanged until measured. The conditional branch input and ordinary bounds/compact-state invariance need further producer evidence before a general preview controller claim.
