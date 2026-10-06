# E011HV — CA6280 cookie/epilogue return to CAD940 frontier

Four opaque-cookie axes pass the original `0x11F0` check, restore the CA6280 saved frame, and return at `0xCA63FC` to `0xCAD940` with `w0=26`. Execution stops before caller code. E011HW reuses accepted E011FX caller registers and qualifies the immediate caller branch path.
