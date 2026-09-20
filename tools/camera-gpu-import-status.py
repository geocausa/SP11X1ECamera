#!/usr/bin/env python3
"""Query Mesa/EGL DMA-BUF formats; no camera access, buffer import or rendering.

Advertised support is a prerequisite, never proof of QC10C layout compatibility.
"""
import argparse
import ctypes as C
import json
import os
from pathlib import Path

QCOM_COMPRESSED = 0x0500000000000001

def configure(lib, name, result, args):
    fn = getattr(lib, name)
    fn.restype = result
    fn.argtypes = args
    return fn

def probe(node):
    egl = C.CDLL("libEGL.so.1")
    gbm = C.CDLL("libgbm.so.1")
    ptr, integer, boolean = C.c_void_p, C.c_int, C.c_uint
    ints = C.POINTER(integer)
    create = configure(gbm, "gbm_create_device", ptr, [integer])
    destroy = configure(gbm, "gbm_device_destroy", None, [ptr])
    proc = configure(egl, "eglGetProcAddress", ptr, [C.c_char_p])
    initialize = configure(egl, "eglInitialize", boolean, [ptr, ints, ints])
    query = configure(egl, "eglQueryString", C.c_char_p, [ptr, integer])
    terminate = configure(egl, "eglTerminate", boolean, [ptr])
    def extension(name, result, args):
        address = proc(name.encode("ascii"))
        if not address:
            raise RuntimeError("EGL entry point unavailable: " + name)
        return C.CFUNCTYPE(result, *args)(address)
    fd = os.open(node, os.O_RDWR | os.O_CLOEXEC)
    device = display = None
    initialized = False
    try:
        device = create(fd)
        if not device:
            raise RuntimeError("GBM device unavailable")
        platform = extension("eglGetPlatformDisplayEXT", ptr, [boolean, ptr, ints])
        display = platform(0x31D7, device, None)
        major, minor = integer(), integer()
        if not display or not initialize(display, C.byref(major), C.byref(minor)):
            raise RuntimeError("EGL GBM initialization failed")
        initialized = True
        extensions = (query(display, 0x3055) or b"").decode().split()
        if "EGL_EXT_image_dma_buf_import_modifiers" not in extensions:
            raise RuntimeError("EGL DMA-BUF modifier query not advertised")
        formats = extension("eglQueryDmaBufFormatsEXT", boolean, [ptr, integer, ints, ints])
        modifiers = extension("eglQueryDmaBufModifiersEXT", boolean,
                              [ptr, integer, integer, C.POINTER(C.c_uint64), C.POINTER(boolean), ints])
        count = integer()
        if not formats(display, 0, None, C.byref(count)) or not 0 <= count.value <= 4096:
            raise RuntimeError("invalid format count")
        capacity = count.value
        values = (integer * capacity)()
        if not formats(display, capacity, values, C.byref(count)) or not 0 <= count.value <= capacity:
            raise RuntimeError("format enumeration failed")
        rows = []
        for value in list(values)[:count.value]:
            n = integer()
            if not modifiers(display, value, 0, None, None, C.byref(n)) or not 0 <= n.value <= 4096:
                raise RuntimeError("modifier count failed")
            capacity = n.value
            mods, external = (C.c_uint64 * capacity)(), (boolean * capacity)()
            if capacity and (not modifiers(display, value, capacity, mods, external, C.byref(n)) or not 0 <= n.value <= capacity):
                raise RuntimeError("modifier enumeration failed")
            rows.append({"fourcc": (value & 0xffffffff).to_bytes(4, "little").decode("ascii", errors="replace"),
                         "fourcc_hex": hex(value & 0xffffffff),
                         "modifiers": [{"value": hex(mods[i]), "external_only": bool(external[i])} for i in range(n.value)]})
        def compressed(name):
            return any(row["fourcc"] == name and any(int(m["value"], 16) == QCOM_COMPRESSED for m in row["modifiers"]) for row in rows)
        return {"render_node": str(node), "egl_vendor": (query(display, 0x3053) or b"").decode(),
                "egl_version": f"{major.value}.{minor.value}", "formats": rows,
                "compressed_nv12_advertised": compressed("NV12"),
                "compressed_p030_advertised": compressed("P030"),
                "qc10c_import_tested": False,
                "qc10c_conversion_proven": False}
    finally:
        if initialized:
            terminate(display)
        if device:
            destroy(device)
        os.close(fd)

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--render-node", type=Path, help="default: all /dev/dri/renderD* nodes")
    args = ap.parse_args()
    nodes = [args.render_node] if args.render_node else sorted(Path("/dev/dri").glob("renderD*"))
    results = []
    failed = not nodes
    for node in nodes:
        try:
            results.append(probe(node))
        except (OSError, RuntimeError) as exc:
            failed = True
            results.append({"render_node": str(node), "query_error": str(exc)})
    print(json.dumps({"schema": "sp11-camera-egl-import-capabilities-v1", "query_complete": not failed,
                      "camera_opened": False, "image_imported": False, "gpu_render_submitted": False,
                      "devices": results}, indent=2))
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
