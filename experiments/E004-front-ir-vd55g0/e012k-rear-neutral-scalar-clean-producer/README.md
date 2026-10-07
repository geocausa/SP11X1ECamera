# E012K — rear neutral scalar clean producer

Userspace source-locked Demux/BLS141 + PDPC311 + WB201 scalar producer for the exercised rear OV13858 startup path. It takes semantic 3A/BLS inputs and emits only the quantized state consumed by `e006z_rear_scalar_state`. No captured Windows register words or RT-CDM packet bytes are embedded.

Private validation consumes the retained E011X semantic trace and E006A corpus outside Git. The accepted startup phase mapping is pre-request state, request-1 state, request-2 state, then request-2 Demux hold.

Runtime/hardware submission is not introduced here.
