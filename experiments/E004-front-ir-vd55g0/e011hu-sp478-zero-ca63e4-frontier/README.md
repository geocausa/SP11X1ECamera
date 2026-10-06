# E011HU — SP+0x478 zero through CB1650 fast path

The accepted frame slot is zero. Original `0xCB1650` takes its zero fast path and resumes at `0xCA63E0` with `w0=26`; execution stops before `0xCA63E4`. E011HV closes the cookie/epilogue return to `0xCAD940`.
