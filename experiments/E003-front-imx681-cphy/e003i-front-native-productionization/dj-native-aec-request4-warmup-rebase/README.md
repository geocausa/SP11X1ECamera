# E003i DJ — request-4 warm-up state rebase

Status: **PASS candidate; verify with `verify-dj.py`.**

DB exposed a temporal startup bug, not a T681 bug. Linux statistics generation G owns Windows request G+3, but CP began G1 with Windows request-1 state. That collapsed three real Windows warm-up history records into one synthetic start record and let the recurrence run away until G3 Short exceeded the ordinary policy-0 T681 range. DG/DH proved Windows rejects that over-range target too, so CH must not clamp it.

DJ preserves CU's public local law (`G1 == frame_id 0`) and rebases only the internal history coordinate by +3. It retains CN's distinct synthetic start record, then seeds the three real warm-up records proven by DC/DI: requests 1..3 retain 33,312,452 in every exposure lane and have exact PredGain `0x3f800000`. AB22 independently pins the cold request-4 entry Lux to `0x4365acdd` after request 1 begins at `0x4365b24a`.

Thus local G1/request4 sees h1=request3, h2=request2 and h3=request1. G2/request5 sees request4/request3/request2, and later local frames continue normally. The external generation identity and CU stats envelope are unchanged.

`verify-dj.py` compiles the full CU→CV chain with warnings-as-errors and replays the exact archived STATS3A G1/G2/G3 bytes from failed DB attempt2. The former G3 `-142` disappears without any T681 change. Verification is offline only: no device, ioctl, module, sensor, MMIO, boot or camera runtime is touched.
