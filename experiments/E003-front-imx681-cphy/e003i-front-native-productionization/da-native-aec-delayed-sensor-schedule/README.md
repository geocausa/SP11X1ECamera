# E003i DA — native AEC delayed sensor schedule

Status: **PASS (offline)**.

DA closes the scheduling contract needed before a native closed-loop live gate. It does not run the camera.

Windows W proves stats generation `G` owns request `F=G+3`. CX proves packet `F` is selected by the Windows sensor KMD at its `SOF=F-1` coordinate and synchronously walked into I2C submission. CY independently measures the Linux IMX681 sensor-side boundary: one atomic group-held write issued immediately after completed generation `N` first produces a strong BHist response in generation `N+2`.

Therefore the bounded Linux parity schedule is mechanical: compute the control tuple from stats `G`, retain it for one completed generation, issue it immediately after completion of `G+1`, and expect its first sensor-visible effect at `G+3`. `G+3` is the same logical request number W assigns to the originating Windows stats. DA does not claim that this algebra independently proves a Windows optical SOF label; it defines the Linux delayed-application schedule using the separately proven Windows request identity and measured Linux latch boundary.

The cold bootstrap is also exact. CP starts all exposure-history lanes at `33,333,332`; CH maps that to T681 `{gain=1,time=33,333,332}`, and CQ maps it to IMX681 `{FLL=3562,VBLANK=1402,exposure=3554,analogue=0,digital=0x0100,ISP=1}`.

A six-frame live gate can therefore remain bounded:
- G1/G2/G3 are captured under the cold bootstrap unless a previously scheduled tuple reaches its target;
- controls computed from G1 are issued after G2 and target logical G4/R4;
- G2 controls are issued after G3 and target G5/R5;
- G3 controls are issued after G4 and target G6/R6;
- no control derived from G4+ needs to be applied in the six-frame acceptance run.

CY's six diagnostic frames must **not** be replayed as one continuous native-AEC sequence: CY manually changed exposure after G1, so its later stats were not caused by CP/CV's earlier outputs. A local diagnostic replay confirmed that each retained CY payload is individually valid from cold state. The raw CY binaries are intentionally ignored rather than committed, so DA's clean-clone verifier does not depend on them. The earlier sequential G3 overflow is therefore recorded as a fixture/history mismatch, not used as a reason to invent out-of-table T681 behavior.
