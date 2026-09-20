#!/usr/bin/env python3
"""E004jd: verify a disposable, fully staged *production* R4 camera package.

No device nodes, camera modules, GRUB or actual system installation are used.
The derived R4 binary is consumed only from the caller's local source.
"""
from pathlib import Path
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
ROOT=Path(os.environ.get("SP11_R4_PACKAGE_FIXTURE","/nonexistent-sp11-r4-package"))
VERIFY=REPO/"src/sp11-camera-stack/verify-package.py"
STAGE=REPO/"src/front-imx681/stage-package.sh"
R4REL="usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin"
R4SHA="1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa"
FULL_SHA="3f3bf8d3ea40a5045896f8ab3053bad14f09cc8fe3c328738905b33a5cf33c71"
FRONT_SHA="fef87066248193c1622671c519095ebaf7ca43d3348535d52a63a9e57bde3f17"

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def run(*args,timeout=25):
    return subprocess.run(args,capture_output=True,text=True,timeout=timeout)

class ProductionR4Package(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if not ROOT.is_dir() or not (ROOT/"CAMERA-STACK-MANIFEST.sha256").exists():
            raise RuntimeError("Run build-verify-offline.sh; the package must be a disposable /tmp fixture")
        if not ROOT.resolve().is_relative_to(Path("/tmp")):
            raise RuntimeError("Must only inspect /tmp staged package, never installed system files")

    def copied(self):
        t=tempfile.TemporaryDirectory(prefix="sp11-e004jd-negative-",dir="/tmp")
        self.addCleanup(t.cleanup)
        dest=Path(t.name)/"package"
        shutil.copytree(ROOT,dest,symlinks=True)
        return dest

    def test_accepted_hardware_authority_and_pinned_extended_manifest(self):
        self.assertEqual(digest(ROOT/"CAMERA-STACK-MANIFEST.sha256"),FULL_SHA)
        self.assertEqual(digest(ROOT/"FRONT-PACKAGE-MANIFEST.sha256"),FRONT_SHA)
        self.assertEqual(len((ROOT/"CAMERA-STACK-MANIFEST.sha256").read_text().splitlines()),51)
        self.assertEqual(len((ROOT/"FRONT-PACKAGE-MANIFEST.sha256").read_text().splitlines()),43)
        r4=ROOT/R4REL
        self.assertFalse(r4.is_symlink())
        self.assertEqual(r4.stat().st_size,41088)
        self.assertEqual(r4.stat().st_mode & 0o777,0o600)
        self.assertEqual(digest(r4),R4SHA)
        original=REPO/"src/front-imx681/userspace/iq/authority/r4-bootstrap.bin"
        self.assertEqual(digest(original),R4SHA)
        self.assertNotIn("r4-bootstrap.bin",
            run("git","-C",str(REPO),"ls-files","src/front-imx681/userspace/iq/authority/r4-bootstrap.bin").stdout)

    def test_actual_complete_package_verifier_requires_r4(self):
        p=run("python3",str(VERIFY),str(ROOT),"--require-r4")
        self.assertEqual(p.returncode,0,p.stdout+p.stderr)
        self.assertIn("PACKAGE VERIFY: PASS",p.stdout)

    def test_actual_packaged_front_launcher_dry_run_no_camera(self):
        launcher=ROOT/"usr/lib/sp11-front-imx681/bin/front-imx681-launcher.py"
        fixture=REPO/"experiments/E004-front-ir-vd55g0/e004dz-canonical-package-rgb-handoff/LOAD-MEDIA.txt"
        out=ROOT.parent/"MUST_NOT_CREATE_RELEASE_R4_DRYRUN"
        self.assertFalse(out.exists())
        p=run("python3",str(launcher),"--topology-file",str(fixture),
              "--media","/dev/media0","--build-dir",
              str(ROOT/"usr/lib/sp11-front-imx681/build"),
              "--output-dir",str(out),"--post-g3-write-policy","shadow")
        self.assertEqual(p.returncode,0,p.stderr)
        plan=json.loads(p.stdout)
        self.assertFalse(plan["execute"])
        self.assertEqual(plan["r4_sha256"],R4SHA)
        self.assertEqual(plan["discovery"]["proven_capture_fourcc"],"QC10C")
        self.assertEqual(plan["capture_command"][2],str(ROOT/R4REL))
        self.assertFalse(out.exists())

    def test_missing_sidecar_is_a_hard_verification_failure(self):
        p=self.copied()
        (p/R4REL).unlink()
        cp=run("python3",str(VERIFY),str(p),"--require-r4")
        self.assertNotEqual(cp.returncode,0)

    def test_corrupt_sidecar_is_a_hard_verification_failure(self):
        p=self.copied()
        target=p/R4REL
        value=bytearray(target.read_bytes())
        value[64]^=1
        target.write_bytes(value)
        cp=run("python3",str(VERIFY),str(p),"--require-r4")
        self.assertNotEqual(cp.returncode,0)

    def test_unlisted_package_file_rejected(self):
        p=self.copied()
        (p/"usr/lib/sp11-front-imx681/userspace/iq/authority/UNLISTED-TEST-ONLY").write_bytes(b"x")
        cp=run("python3",str(VERIFY),str(p),"--require-r4")
        self.assertNotEqual(cp.returncode,0)
        self.assertIn("omitted from full manifest",cp.stderr)

    def test_package_symlink_rejected(self):
        p=self.copied()
        (p/"usr/lib/sp11-front-imx681/userspace/iq/authority/SYMLINK-TEST-ONLY").symlink_to("r4-bootstrap.json")
        cp=run("python3",str(VERIFY),str(p),"--require-r4")
        self.assertNotEqual(cp.returncode,0)
        self.assertIn("symlink in staged package",cp.stderr)

    def test_source_never_embeds_ignored_binary_or_changes_golden(self):
        stager=STAGE.read_text()
        self.assertIn('R4_SRC="$ROOT/userspace/iq/authority/r4-bootstrap.bin"',stager)
        self.assertIn('install -m 0600 "$R4_SRC" "$R4_DEST"',stager)
        self.assertIn("FRONT_R4_BOOTSTRAP_SOURCE_MISSING_OR_DRIFTED",stager)
        self.assertIn("r4-bootstrap.json",stager)
        self.assertIn('git -C "$REPO" archive HEAD:src/front-imx681',stager)
        release=(REPO/"src/sp11-camera-stack/stage-full-package.sh").read_text()
        self.assertIn('python3 "$ROOT/verify-package.py" "$OUT" --require-r4',release)
        self.assertNotIn("modprobe ",stager)
        self.assertNotIn("grub-reboot",release)
        self.assertNotIn("ILLUMINATION_ON",release)

if __name__=="__main__":unittest.main(verbosity=2)
