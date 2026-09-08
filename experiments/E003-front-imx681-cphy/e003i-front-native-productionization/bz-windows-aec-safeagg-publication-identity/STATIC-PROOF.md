# Static proof

- SafeAggSA arithmetic operator 2 is the final bank-3:data9 publication.
- Its compact record is `enabled=1`, operation enum `2`, with A=`DB bank3:data8`, B/C/D=`Fixed +1.0f`, output=`bank3:data9`.
- The DLL operation-name table at `0x18169dac0` maps enum 2 to `MUL::(AxB)x(CxD)`.
- `RunOneArithMeticOperator` dispatches enum 2 to `0x1803c91cc`; the body uses three scalar `fmul` instructions for `(A*B)*(C*D)`.
- `UtilGetOperand` proves method 0 is fixed (`ldr s16,[operand+4]`) and method 1 is DB (`GetData` from descriptor `+8`).
- Therefore the final SafeAgg arithmetic is `(DB(3:8)*1.0f)*(1.0f*1.0f)`, so `3:9` is the method-11 scalar unchanged in the finite scoped domain.
