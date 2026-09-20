#!/usr/bin/env python3
"""E004hz: uninstalled, OFFLINE-ONLY, all-or-nothing HLOS diagnostic transaction.

Unlike the E004hi streaming client, do not expose any provisional output to
the caller before the exact DONE marker, clean stdout EOF, and child exit 0.
No camera, PMIC, LED, liveness, consent, enrollment, PAM or login API. The
caller owns input and returned buffers; this is not a secure image erase.
"""
from pathlib import Path
import importlib.util

HERE=Path(__file__).resolve().parent
SPEC=importlib.util.spec_from_file_location(
    "sp11_original_offline_stream",HERE/"sp11-offline-stream-client.py")
if SPEC is None or SPEC.loader is None:
    raise ImportError("original offline stream transport not found")
_original=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(_original)
MAX_FRAMES=_original.MAX_FRAMES

class TransactionFault(Exception):
    """Terminal offline session failure; no user pixels or scores in errors."""

def process_offline_frames(binary,frames,max_seconds=30.0):
    """Return (tuple[processed NV12], non-auth diagnostic) ONLY after commit.

    The input must be an already-bounded tuple of 1..16 immutable byte
    frames, not an arbitrary generator that may stall or never terminate.
    Keep the original C/IPC worker unchanged; no live capture or login path.
    """
    if type(frames) is not tuple or not 1<=len(frames)<=MAX_FRAMES:
        raise TransactionFault("offline transaction invalid frame container/count")
    count=len(frames)
    if any(type(frame) is not bytes or len(frame)!=_original.FRAME_LEN or
           frame[_original.YLEN:]!=bytes([128])*(_original.FRAME_LEN-_original.YLEN)
           for frame in frames):
        raise TransactionFault("offline transaction invalid frame shape/chroma")
    outputs=[]
    stream=None
    try:
        stream=_original.OfflineStream(binary,count,max_seconds=max_seconds)
        for idx,frame in enumerate(frames,1):
            outputs.append(stream.accept(idx,frame))
        receipt=stream.finish()
        if (stream.state!="complete" or
            receipt.get("status")!="complete" or
            receipt.get("frames_checked")!=count or
            receipt.get("login_or_unlock_authorized") is not False or
            receipt.get("autonomous_hardware_cutoff_proven") is not False):
            raise TransactionFault("offline transaction invalid completion receipt")
        return tuple(outputs),receipt
    except Exception:
        # No partial images are exposed; clear our references on failure.
        outputs.clear()
        if stream is not None and stream.state=="collecting":
            try:
                stream.cancel()
            except Exception:
                pass
        raise TransactionFault("offline transaction rejected; zero outputs committed") from None
