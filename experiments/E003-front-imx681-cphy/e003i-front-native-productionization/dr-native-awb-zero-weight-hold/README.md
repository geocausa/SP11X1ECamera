# E003i-DR — native AWB zero-weight hold

Status: **PASS (offline differential; no camera runtime).**

DR changes only the previously undefined aggregate-AGW-zero branch of AD's native trigger core. DQ proves that Windows `CSAAGWV1` emits a `(0,0)` no-update decision when aggregate weight is zero and the higher CAWB layer retains previous AWB state.

Return contract:

- `0`: ordinary fresh AGW result, identical to AD.
- `1` (`E003I_TRIGGER_HOLD_PREVIOUS`): valid frame/Lux, but no fresh AWB target; the caller must keep its previous XY/CCT state.
- negative values: existing parser/model failures, unchanged.

On HOLD_PREVIOUS the C core still publishes measured luma, Lux, P01 count, valid weighted count and zero sum weight for evidence. Fresh AGW X/Y and fresh CCT are zero to make accidental use fail visibly. The stateful caller, not this stateless C primitive, owns the previous decision.

DR does not alter P01/P03/P04/P05 arithmetic, positive-weight behavior, the bounded AEC baseline, LSC, IQ composition, kernel code or camera runtime.
