#!/usr/bin/env python3
"""Independent request-to-BPC trigger semantics. No camera or hardware access."""
from pathlib import Path
import importlib.util, math, struct
HERE = Path(__file__).resolve().parent

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

S = load("bpc_interval_ae", HERE.parent / "e011ad-rear-bpcabf411-trigger-interval-selector" / "selector.py")

def f32(value):
    try:
        value = struct.unpack("<f", struct.pack("<f", value))[0]
    except (OverflowError, struct.error):
        raise ValueError("outside finite binary32 domain") from None
    if not math.isfinite(value):
        raise ValueError("finite binary32 input required")
    return value

def gain_slot(sensor_mid_override, node_context, snapshot_context, input_context):
    """Source precedence; contexts are resolved semantic inputs, not inferred from outputs."""
    if type(sensor_mid_override) is not bool:
        raise ValueError("explicit sensor-mid override required")
    contexts = (node_context, snapshot_context, input_context)
    if any(type(x) is not int or x not in (0, 1, 2, 3) for x in contexts):
        raise ValueError("unknown request context")
    if sensor_mid_override:
        return "mid"
    if 3 in contexts:
        return "short"
    if 1 in contexts:
        return "mid"
    if 0 in contexts:
        return "long"
    raise ValueError("native unsupported context retains prior gain; no new gain produced")

def produce_triggers(*, gains, sensitivities, drc_gain, sensor_mid_override,
                     node_context, snapshot_context, input_context,
                     request_id, qll_short_override=False):
    """Ordinary type IDs [2,5,1]; AEC fields are caller-owned semantic inputs."""
    if type(request_id) is not int or request_id < 1:
        raise ValueError("request identity required; cold initialization is a separate boundary")
    if qll_short_override is not False:
        raise ValueError("IPE QLL override not admitted by this IQSetupTriggerData domain")
    if set(gains) != {"short", "mid", "long"} or set(sensitivities) != {"short", "mid"}:
        raise ValueError("exact AEC semantic fields required")
    gains = {key: f32(value) for key, value in gains.items()}
    sensitivities = {key: f32(value) for key, value in sensitivities.items()}
    drc_gain = f32(drc_gain)
    if any(value < 0 for value in (*gains.values(), *sensitivities.values(), drc_gain)):
        raise ValueError("negative AEC semantics unsupported")
    slot = gain_slot(sensor_mid_override, node_context, snapshot_context, input_context)
    # Native FSUB/FABS is binary32, FCVT then compares against binary64 1e-6.
    denominator = sensitivities["short"]
    ratio = 1.0 if abs(denominator) < 1e-6 else f32(sensitivities["mid"] / denominator)
    return {"request_id": request_id, "gain_slot": slot,
            "typed": ((2, drc_gain if drc_gain > 1.0 else 1.0),
                      (5, ratio), (1, gains[slot]))}

def produce_bpc(authority, modes, **request):
    """No captured scalar, region, common output or register word is an input."""
    triggers = produce_triggers(**request)
    result = S.produce(authority, modes, triggers["typed"][2][1])
    result["request_id"] = triggers["request_id"]
    result["typed_triggers"] = triggers["typed"]
    result["gain_slot"] = triggers["gain_slot"]
    return result

def startup_common(authority, modes, request1, request2):
    """Three source semantic states for the C binder; no materializer ID invention.

    The cold Default region is independently invariant across all six leaves.
    It does not depend on an assumed initial gain or the observed zero vector.
    """
    if request1.get("request_id") != 1 or request2.get("request_id") != 2:
        raise ValueError("exact startup source requests 1 and 2 required")
    cold = S.AC.cold_seed(authority)
    first = produce_bpc(authority, modes, **request1)
    second = produce_bpc(authority, modes, **request2)
    return {"source_request_id": (0, 1, 2),
            "common": (cold["state"], first["state"], second["state"])}
