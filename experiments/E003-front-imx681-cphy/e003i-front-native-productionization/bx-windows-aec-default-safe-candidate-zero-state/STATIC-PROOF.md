# BX static proof

- Constructor block `0x1803a9294..0x1803a92e0` zeros `object+0x7d08` for `0x5dc0 = 1000*24` bytes.
- SceneAnalyzer slot accessor `0x1803c4c88` returns `object + 0x7d08 + dataID*24` for IDs 0..999.
- `SetDataSceneAnalyzer` at `0x1803d64f8` stores 16+8 bytes into exactly the same slot.
- Pinned tuning's DefaultSequence excludes FaceSA/TouchSA/DepthSA/TrackerSA/SaliencySA.
- Whole-analyzer output census shows the SafeAgg value/confidence IDs for each of those five analyzers have no other writer.

Thus initialized zero is invariant for those ten SceneAnalyzer-bank publications while DefaultSequence remains uninterrupted.
