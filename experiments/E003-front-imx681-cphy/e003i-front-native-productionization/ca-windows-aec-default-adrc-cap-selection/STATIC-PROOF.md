# Static proof

- ADRCCapSA is analyzer 60 and immediately precedes SafeAggSA in `DefaultSequence`.
- op0 output descriptor is `bank9:data54`, description `ADRCLuxFaceCap`.
- op0 enum 13 is `CondSmaller`; its operands are A=`DB(3:36)`, B=`Fixed(0.0001f)`, C/D method-2 trigger operands.
- `RunOneArithMeticOperator` resolves A/B/C/D in order to s11/s12/s13/s14.
- Enum-13 body `fcmpe s11,s12; fcsel s10,s13,s14,lo` proves `A<B ? C:D`.
- BX proves FaceSA confidence `3:36` stays zero in uninterrupted DefaultSequence. Hence `0 < 0.0001` and C is selected.
- Selected C terminal values are pinned from tuning, while the generic method-2 trigger-source mapping is deferred.
