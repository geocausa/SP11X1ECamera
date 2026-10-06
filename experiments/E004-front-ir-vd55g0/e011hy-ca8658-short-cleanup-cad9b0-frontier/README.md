# E011HY — CA8658 short cleanup to CAD9B0 epilogue frontier

The original CAD868 setup stores qualify cleanup object bytes `+0x28=1`, `+0x30=0`, and `+0x38=0`. Four exact placements execute `0xCAD9A8 -> 0xCA8658`; those bytes select the short cleanup path, which returns at `0xCA8778` to `0xCAD9AC`. The caller then restores `w0=w19=26`.

Execution stops before the CAD868 epilogue at `0xCAD9B0`. E011HZ uses the unique source callsite `0x6BD90 -> 0xCAD868` to execute the epilogue/return and stop at `0x6BD94` before the caller instruction executes.

No camera Start, reboot, rear runtime, or kernel build is used. Native rear runtime remains denied.
