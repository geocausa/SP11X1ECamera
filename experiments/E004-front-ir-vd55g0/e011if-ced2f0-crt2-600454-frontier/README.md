# E011IF — joined CED2F0 CRT=2 return to 0x600454 frontier

The exact `0x600450` call instruction is executed, fixing architectural return `0x600454`. E011FO supplies the accepted same-thread CRT error value `2`, and E011FJ supplies the already-qualified complete `CED2F0` source return contract for that state. The resulting accepted return is `w0=2`.

Execution stops before `0x600454`. E011IG resumes the current second iteration and stops before the first global dependency read at `0x60046C`. Native rear runtime remains denied.
