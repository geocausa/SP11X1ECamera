#!/usr/bin/env python3
"""E004ib: scratch-only unsafe package/root/manifest negative regression.

No live system root, camera, kernel, IR, firmware, GRUB or login mutation.
"""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import importlib.util
import os
import subprocess

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
STACK=ROOT/"src/sp11-camera-stack"
S=importlib.util.spec_from_file_location("e004ib_rootguard",STACK/"offline-root-guard.py")
assert S and S.loader
guard=importlib.util.module_from_spec(S)
S.loader.exec_module(guard)

def fail(call,why):
    try:call()
    except guard.RootGuardFault as e:
        assert str(e).startswith("OFFLINE_ROOT_GUARD_REJECTED"),why
    else:raise AssertionError("E004IB_NEGATIVE_FAIL_OPEN "+why)

def manifest(package,entries):
    (package/"CAMERA-STACK-MANIFEST.sha256").write_text("".join(
        hashlib.sha256(content).hexdigest()+"  "+name+"\n"
        for name,content in entries))

def run():
    count=0
    with TemporaryDirectory(prefix="e004ib-scratch-",dir="/tmp") as tmp:
        base=Path(tmp)
        pkg=base/"pkg"
        member=pkg/"usr/bin/camera-demo"
        member.parent.mkdir(parents=True)
        member.write_bytes(b"public-camera-package-standin")
        manifest(pkg,[("usr/bin/camera-demo",member.read_bytes())])
        root=base/"sandbox"
        assert guard.install(pkg,root) is True
        assert not root.exists(),"guard should never create destination"
        for bad in ("/","/home","/tmp","/tmp/../","/tmp/../etc",
                    str(base/"../outside"),str(base)+"/", "./sandbox",
                    str(base/"sandbox/../else")):
            fail(lambda bad=bad:guard.scratch_root(bad),"reject root "+bad)
            count+=1
        target=base/"real-target"
        target.mkdir()
        alias=base/"alias"
        alias.symlink_to(target,target_is_directory=True)
        fail(lambda:guard.install(pkg,alias/"sandbox"),"symlink in root")
        count+=1
        missing=base/"dangling"
        missing.symlink_to(base/"does-not-exist")
        fail(lambda:guard.scratch_root(missing),"dangling root symlink")
        count+=1
        manifest_path=pkg/"CAMERA-STACK-MANIFEST.sha256"
        original=manifest_path.read_bytes()
        for bad in (
            b"f"*64+b"  usr/../../etc/passwd\n",
            b"f"*64+b"  /usr/bin/camera-demo\n",
            b"f"*64+b"  usr//bin/camera-demo\n",
            b"f"*64+b"  usr/./bin/camera-demo\n",
            b"f"*64+b"  usr/bin/camera-demo\n"+b"f"*64+b"  usr/bin/camera-demo\n",
            b"f"*64+b"  usr/bin/camera-demo\x00\n",
            b"not-a-checksum  usr/bin/camera-demo\n",
        ):
            manifest_path.write_bytes(bad)
            fail(lambda:guard.install(pkg,root),"unsafe package manifest")
            count+=1
        manifest_path.write_bytes(original)
        extra=pkg/"usr/bin/extra-unlisted"
        extra.write_bytes(b"extra")
        fail(lambda:guard.install(pkg,root),"extra package payload")
        count+=1
        extra.unlink()
        member.unlink()
        member.symlink_to("/etc/passwd")
        fail(lambda:guard.install(pkg,root),"package payload symlink")
        count+=1
        member.unlink()
        member.write_bytes(b"public-camera-package-standin")
        state=root/"var/lib/sp11-camera-stack"
        state.mkdir(parents=True)
        (state/"installed-camera-stack-manifest.sha256").write_bytes(original)
        (root/"usr/bin").mkdir(parents=True)
        sandbox_member=root/"usr/bin/camera-demo"
        sandbox_member.write_bytes(member.read_bytes())
        # Synthetic managed install/uninstall through the actual maintained
        # uninstall-root.sh; unrelated scratch state must survive.
        (root/"etc").mkdir()
        (root/"etc/unrelated-sentinel").write_text("SENTINEL_UNCHANGED")
        outer=base/"outside-only"
        outer.write_text("OUTSIDE_UNCHANGED")
        assert guard.install(pkg,root) is True
        assert guard.uninstall(root) is True
        sandbox_member.unlink()
        (root/"usr/bin").rmdir()
        (root/"usr").rmdir()
        (root/"usr").symlink_to(target,target_is_directory=True)
        fail(lambda:guard.uninstall(root),"managed root usr symlink")
        count+=1
        (root/"usr").unlink()
        (root/"usr/bin").mkdir(parents=True)
        sandbox_member.write_bytes(member.read_bytes())
        (state/"installed-camera-stack-manifest.sha256").write_bytes(
            b"f"*64+b"  usr/../../etc/passwd\n")
        fail(lambda:guard.uninstall(root),"malicious prior manifest")
        count+=1
        (state/"installed-camera-stack-manifest.sha256").write_bytes(original)
        # A symlink at the *target* must also fail before rm can traverse it.
        sandbox_member.unlink()
        sandbox_member.symlink_to(outer)
        fail(lambda:guard.uninstall(root),"managed target symlink")
        count+=1
        sandbox_member.unlink()
        sandbox_member.write_bytes(member.read_bytes())
        assert guard.uninstall(root) is True
        actual=subprocess.run([str(STACK/"uninstall-root.sh"),str(root)],
                              capture_output=True,text=True,timeout=15)
        assert actual.returncode==0 and \
            "SP11_CAMERA_STACK_ROOT_UNINSTALL=PASS" in actual.stdout,actual.stderr
        assert (root/"etc/unrelated-sentinel").read_text()=="SENTINEL_UNCHANGED"
        assert outer.read_text()=="OUTSIDE_UNCHANGED"
        assert not sandbox_member.exists() and not state.exists()
        fail(lambda:guard.uninstall(root),"repeated uninstall absent manifest")
        count+=1
        refused=subprocess.run([str(STACK/"uninstall-root.sh"),"/"],
                               capture_output=True,text=True,timeout=10)
        assert refused.returncode!=0 and \
            "live root uninstall is intentionally forbidden" in refused.stderr
    assert count==24,count
    print("E004IB_OFFLINE_SCRATCH_CONFINEMENT_AND_MANIFEST_NEGATIVES_PASS",count)
    print("E004IB_ACTUAL_MAINTAINED_ROOT_UNINSTALL_SYNTHETIC_SANDBOX=PASS")
    print("E004IB_UNRELATED_SCRATCH_AND_OUTSIDE_SENTINELS_PRESERVED=PASS")
    print("E004IB_NO_LIVE_SYSTEM_ROOT_CAMERA_IR_BOOT_OR_PAM_MUTATION")
    return count
if __name__=="__main__":run()
