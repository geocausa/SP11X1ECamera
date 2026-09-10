# E003i-DY — bounded sensor + residual-ISP Demux AEC one-shot

Status: **PREPARED_UNEXECUTED.**

DY is a fresh disposable one-shot candidate built after DT's six-frame sensor-side pass and DV/DW/DX's offline residual-ISP closure.

Its camera transport and safety envelope remain the already-live-proven DT path:

- six front frames only;
- exact DQBUF order and paired TL_BG/STATS3A generations 1..6;
- native DN-capped AEC;
- at most three group-held IMX681 writes, released after completed G2/G3/G4;
- CY/DU-proven write-after-N -> statistics-N+2 effect law;
- Windows-valid AWB HOLD_PREVIOUS behavior;
- dynamic LSC/Tintless and template-free R5/R6 IQ;
- one helper invocation, no same-boot retry, fail-closed camera handling and mandatory Golden reboot.

The single new integration variable is the already-closed CQ residual ISP gain. DX publishes the parent native-AEC/CQ float bits through a generation-tagged 24-byte pipe to the IQ producer. DW/DV then regenerate only Titan680 Demux/BLS registers 0x3b70 and 0x3b74 for R5<-G2 and R6<-G3. No duplicate AEC computation and no guessed/default live gain are allowed.

The live verifier does not expect fixed gain values or capsule hashes: illumination can differ from DT. Instead it requires each parent DX_AEC_ACCEPT ISP bit-pattern to equal the producer gain-feed bit-pattern for the same generation, recomputes Demux/BLS with DV, and checks the actual R5/R6 capsule module bytes.

Even a successful DY run proves only the bounded six-frame sensor + post-sensor Demux gain integration. Unrestricted continuous AEC remains outside this checkpoint.
