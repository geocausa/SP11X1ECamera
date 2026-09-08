# E003i CB — Windows AEC ADRC / dark-boost tail

Status: **PASS (static/offline)** once `verify-cb.py` passes.

CB closes the remaining arithmetic/trigger tail between the final target aggregators and the phase-2 Short/Long `AdjRatio` publications for uninterrupted ordinary `DefaultSequence`.

The DLL's trigger-control enum names ID 8 **Lux** and ID 14 **Gyro**. BG independently proves trigger-bank key `(9,8)` is the live AEC LuxIndex. CB does not rely on a writer-level semantic claim for bank `(9,14)`: CA's selected `ADRCLuxFaceCap` method-2 program has only one outer `0..1000` region, so the scoped output is invariant to that first coordinate. The second coordinate is the proven Lux trigger, and its inner curve is therefore the active ordinary dependency:

- Lux `<=210`: `1.6`;
- `210..260`: Windows float32 interpolation `1.6 -> 1.5`;
- `260..300`: `1.5`;
- `300..320`: Windows float32 interpolation `1.5 -> 1.4`;
- `>=320`: `1.4`.

The Short tail is:

- `3:66 AdjRatioShort = 3:9 / 3:10`;
- `3:67 ADRCGain = MIN(Windows method-2 ramp(3:66), 9:54 ADRCLuxFaceCap)`;
- BZ then gives `3:11 = 3:9 / 3:67`.

The nominal `1 -> 1000` method-2 ramp must **not** be replaced by algebraic `clamp(x,1,1000)`: at input `123.5f`, Windows instruction ordering produces `0x42f70001` while direct `123.5f` is `0x42f70000`.

The Long tail is:

- `3:157 DRCGainRemainder = 8.0 / 3:67`;
- `3:68 AdjRatioLong = 3:12 / 3:9`;
- `3:69 DarkBoostGain` is MIN of a Lux/`3:68` method-2 program and a Lux/`3:157` method-2 program.

Because `3:67 <= ADRCCap <= 1.6`, `3:157 >= 5.0`. Its method-2 branch is therefore safely above the competing Long branch, whose maximum is `2.0`; the MIN always selects the Lux/`3:68` program on this default domain. The surviving method-2 program itself remains authoritative and is not algebraically collapsed: even interpolation between numerically equal child values can change one ULP.

No camera module load, stream, sensor write, MMIO, Windows boot, or reboot is used.
