# E011HW — CAD940 return-26 caller path to cleanup frontier

Reusing accepted E011FX caller registers, four exact placements terminate the output at caller `SP+0x47f`, take the return-code branch, set `w19=26`, and take the nonnegative branch to `0xCAD9A4`. Execution stops before cleanup setup.
