#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Losslessly archive retired front NV12 originals, on the same SP11 only.

No pixels, spatial metrics, or image-derived hashes leave this machine.
Remove redundant loose files only after complete original-byte verification.
"""
import argparse, datetime, fcntl, json, os, stat, subprocess, tarfile
from pathlib import Path

FRAME_BYTES = 5529600
FLOOR = 512 * 1024 * 1024
REPO = Path(__file__).resolve().parents[1]

def need(value, reason):
    if not value:
        raise RuntimeError(reason)

def free(path):
    v = os.statvfs(path)
    return v.f_bavail * v.f_frsize

def fingerprint(path):
    s = path.lstat()
    need(stat.S_ISREG(s.st_mode) and s.st_uid == 0, "root-owned regular original required")
    need(s.st_size == FRAME_BYTES, "unexpected original extent")
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("identity", choices=["02", "03", "04"])
    args = parser.parse_args()
    need(os.geteuid() == 0, "root only")
    subprocess.run([str(REPO / "tools/camera-overlap-guard.sh"), "--require-clean-tracked",
                    "--require-golden", "--require-no-camera-process"], check=True)
    d = Path("/var/lib/sp11-camera-native-control-response-20261007-" + args.identity)
    s = d.lstat()
    need(stat.S_ISDIR(s.st_mode) and s.st_uid == 0 and not s.st_mode & 0o077,
         "private root directory required")
    report = json.loads((REPO / ("docs/NATIVE-RGB-FRONT-CONTROL-RESPONSE-" + args.identity + "-20261007.json")).read_text())
    retired = report["candidate_retired"] if args.identity == "02" else report["consumed_retired"]
    need(retired is True and report["golden_assets_unchanged"] is True,
         "retirement and Golden proof required")
    need((d / "ATTEMPT-CONSUMED").is_file(), "consumed identity required")
    lock = (d / "camera.lock").open("a")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    archive = d / "PRIVATE-ALL320-NV12.tar.zst"
    record = d / "LOSSLESS-ARCHIVAL.json"
    need(not archive.exists() and not record.exists(), "archive identity already exists")
    originals = sorted(d.glob("frame-*.bin"))
    need(len(originals) == 320, "all320 originals required")
    fingerprints = {p.name: fingerprint(p) for p in originals}
    before = free(d)
    need(before > FLOOR, "not enough temporary archive space")
    os.umask(0o077)
    process = None
    verified = False
    try:
        with archive.open("xb", buffering=0) as destination:
            process = subprocess.Popen(["zstd", "-q", "-3", "-T2", "-c"],
                                       stdin=subprocess.PIPE, stdout=destination)
            with tarfile.open(fileobj=process.stdin, mode="w|", format=tarfile.PAX_FORMAT) as tar:
                for p in originals:
                    need(free(d) > FLOOR, "temporary archive reached free-space reserve")
                    need(fingerprint(p) == fingerprints[p.name], "original changed before archive")
                    tar.add(p, arcname=p.name, recursive=False)
            process.stdin.close()
            need(process.wait(timeout=60) == 0, "compression failed")
            os.fsync(destination.fileno())
        reader = subprocess.Popen(["zstd", "-q", "-d", "-c", str(archive)], stdout=subprocess.PIPE)
        seen = []
        try:
            with tarfile.open(fileobj=reader.stdout, mode="r|") as tar:
                for member in tar:
                    need(member.isfile() and member.name in fingerprints and member.size == FRAME_BYTES,
                         "unexpected archived member")
                    need(member.name not in seen, "duplicate archived member")
                    original = d / member.name
                    need(fingerprint(original) == fingerprints[member.name], "original changed before verification")
                    archived = tar.extractfile(member)
                    with original.open("rb") as source:
                        for offset in range(0, FRAME_BYTES, 1024 * 1024):
                            n = min(1024 * 1024, FRAME_BYTES - offset)
                            a, b = source.read(n), archived.read(n)
                            need(len(a) == n and a == b, "original-byte verification failed")
                        need(source.read(1) == b"" and archived.read(1) == b"", "extent mismatch")
                    need(fingerprint(original) == fingerprints[member.name], "original changed during verification")
                    seen.append(member.name)
            while reader.stdout.read(1024 * 1024):
                pass
            need(reader.wait(timeout=60) == 0 and set(seen) == set(fingerprints), "incomplete archive")
        finally:
            reader.stdout.close()
            if reader.poll() is None:
                reader.terminate(); reader.wait(timeout=10)
        need(all(fingerprint(p) == fingerprints[p.name] for p in originals), "original changed before disposition")
        verified = True
        retained = {originals[i].name for i in (0, 79, 159, 239, 319)}
        proof = {"status": "PASS_PRIVATE_LOSSLESS_ARCHIVE_BYTE_FOR_BYTE_VERIFIED",
                 "identity": "control-response" + args.identity,
                 "archived_native_frames": len(originals), "verified_native_bytes": FRAME_BYTES * len(originals),
                 "archive_bytes": archive.stat().st_size, "archive_path": str(archive),
                 "private_pixels_stayed_on_SP11": True, "image_hashes_exported": False,
                 "retained_original_names": sorted(retained), "redundant_uncompressed_frames_removed": 0,
                 "free_before_bytes": before, "utc": datetime.datetime.now(datetime.timezone.utc).isoformat()}
        with record.open("x") as f:
            json.dump(proof, f, indent=2); f.write("\n"); f.flush(); os.fsync(f.fileno())
        for p in originals:
            if p.name not in retained:
                need(fingerprint(p) == fingerprints[p.name], "original changed before removing redundant copy")
                p.unlink()
                proof["redundant_uncompressed_frames_removed"] += 1
        proof["free_after_bytes"] = free(d)
        temporary = d / "LOSSLESS-ARCHIVAL.json.complete"
        with temporary.open("x") as f:
            json.dump(proof, f, indent=2); f.write("\n"); f.flush(); os.fsync(f.fileno())
        os.replace(temporary, record)
        fd = os.open(d, os.O_DIRECTORY)
        try: os.fsync(fd)
        finally: os.close(fd)
        print(json.dumps({k:v for k,v in proof.items() if k != "retained_original_names"}))
    except BaseException:
        if process is not None and process.poll() is None:
            process.terminate(); process.wait(timeout=10)
        if not verified:
            archive.unlink(missing_ok=True)
        raise

if __name__ == "__main__":
    main()
