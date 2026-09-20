#!/usr/bin/env python3
"""Actual ARM64 worker and stock GStreamer round-trip; synthetic pixels only."""
import importlib.util
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[3]
EXP = ROOT / "experiments/E004-front-ir-vd55g0"
HLOS = ROOT / "src/sp11-camera-hlos-worker"
def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def main():
    preview = load(HLOS / "sp11-offline-preview.py", "preview")
    hi = load(EXP / "e004hi-failclosed-offline-hlos-stream-transport/verify_stream.py", "hi")
    hg = load(EXP / "e004hg-arm64-hlos-yunet-sface-bounded-perf/benchmark_offline.py", "hg")
    with TemporaryDirectory(prefix="sp11-desktop-preview-") as tmp:
        folder = Path(tmp)
        worker = hi.compile_stream(folder / "worker", hg)
        solo = hg.compile_worker(folder)
        y = 644 * 604
        frames = tuple(bytes([v]) * y + bytes([128]) * (y // 2) for v in (40, 90))
        expected = b"".join(hg.real_hlos_once(solo, frame) for frame in frames)
        source, output = folder / "input.nv12", folder / "preview.y4m"
        source.write_bytes(b"".join(frames))
        assert preview.export_preview(source, output, worker, 30) == 2
        decoded = folder / "decoded.i420"
        cp = subprocess.run(["gst-launch-1.0", "-q", "filesrc", "location=" + str(output),
                             "!", "y4mdec", "!", "filesink", "location=" + str(decoded)],
                            capture_output=True, text=True, timeout=30)
        assert cp.returncode == 0, cp.stderr
        raw = decoded.read_bytes()
        # GStreamer aligns each I420 plane row to four bytes (322 -> 324 for UV).
        strides = (644, 324, 324)
        shapes = ((644, 604), (322, 302), (322, 302))
        packed = bytearray(); cursor = 0
        for _ in frames:
            for stride, (width, height) in zip(strides, shapes):
                for _ in range(height):
                    packed.extend(raw[cursor:cursor + width]); cursor += stride
        assert cursor == len(raw), (cursor, len(raw))
        assert bytes(packed) == expected, "stock player changed processed pixels"
        original = output.read_bytes()
        try:
            preview.export_preview(source, output, worker, 30)
        except FileExistsError:
            pass
        else:
            raise AssertionError("existing preview replaced")
        assert output.read_bytes() == original
        for name, data in [("short", b"x"), ("trailing", b"".join(frames) + b"x"),
                           ("chroma", frames[0][:y] + bytes([129]) * (y // 2))]:
            bad = folder / (name + ".nv12"); bad.write_bytes(data)
            target = folder / (name + ".y4m")
            try:
                preview.export_preview(bad, target, worker, 30)
            except Exception:
                pass
            else:
                raise AssertionError("invalid offline input accepted")
            assert not target.exists()
    print(json.dumps({"status": "PASS", "synthetic_frames": 2,
          "actual_native_worker": True, "stock_gstreamer_decode_pixel_exact": True,
          "existing_output_preserved": True, "invalid_inputs_without_output": 3,
          "camera_runtime": False, "ir_illumination": False, "authentication": False}, indent=2))

if __name__ == "__main__":
    main()
