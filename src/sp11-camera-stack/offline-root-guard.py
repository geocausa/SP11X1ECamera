#!/usr/bin/env python3
"""Guard bounded, unprivileged, OFFLINE camera-package scratch roots.

Additional non-concurrent preflight, NOT a security sandbox. Only
user-owned disposable /tmp roots are accepted; live / is out of scope.
"""
from pathlib import Path
import argparse
import os
import re
import stat

STATE=Path("var/lib/sp11-camera-stack/installed-camera-stack-manifest.sha256")
MANIFEST=Path("CAMERA-STACK-MANIFEST.sha256")
HASH_LINE=re.compile(r"([0-9a-f]{64})  (usr/[A-Za-z0-9_.+/-]+)\Z")

class RootGuardFault(Exception):
    """No raw paths, file contents, secrets or image pixels in errors."""

def need(ok,why):
    if not ok:
        raise RootGuardFault("OFFLINE_ROOT_GUARD_REJECTED "+why)

def scratch_root(path):
    raw=os.fspath(path)
    need(raw.startswith("/") and not any(p in ("", ".", "..") for p in raw.split("/")[1:]),
         "noncanonical root")
    root=Path(raw)
    need(len(root.parts)>=3 and root.parts[:2]==("/","tmp"),
         "root outside disposable /tmp")
    need(Path("/tmp").is_dir() and not Path("/tmp").is_symlink(),
         "temporary parent unavailable")
    current=Path("/tmp")
    for part in root.parts[2:]:
        current=current/part
        if current.is_symlink():
            raise RootGuardFault("OFFLINE_ROOT_GUARD_REJECTED symlink in root")
        if current.exists():
            info=current.lstat()
            need(stat.S_ISDIR(info.st_mode) and info.st_uid==os.getuid(),
                 "existing temporary root component not user-owned directory")
        else:
            need(not current.is_symlink(),"dangling root symlink")
    need(root.resolve()==root,"noncanonical temporary root")
    return root

def clean_relative(value):
    need(bool(value) and value.startswith("usr/") and
         "//" not in value and all(x not in ("", ".", "..") for x in value.split("/"))
         and bool(re.fullmatch(r"usr/[A-Za-z0-9_.+/-]+",value)),
         "unsafe manifest member")
    return Path(value)

def parse_manifest(source):
    need(source.is_file() and not source.is_symlink(),"manifest unavailable or symlink")
    data=source.read_bytes()
    need(1<=len(data)<=500_000 and b"\x00" not in data,
         "manifest size/encoding")
    try:lines=data.decode("ascii").splitlines()
    except UnicodeError:
        raise RootGuardFault("OFFLINE_ROOT_GUARD_REJECTED nonascii manifest") from None
    need(lines and len(lines)<=5000 and len(lines)==len(set(lines)),
         "manifest empty/duplicate/excessive")
    entries=[]
    for line in lines:
        match=HASH_LINE.fullmatch(line)
        need(match is not None,"invalid manifest checksum record")
        item=clean_relative(match.group(2))
        entries.append(item)
    need(len(entries)==len(set(entries)),"duplicate manifest target")
    return entries

def safe_existing_tree(root,entry):
    current=root
    for part in entry.parts:
        current=current/part
        if current.is_symlink():
            raise RootGuardFault("OFFLINE_ROOT_GUARD_REJECTED managed path symlink")
        if current.exists():
            kind=current.lstat().st_mode
            need(stat.S_ISREG(kind) if current==root/entry else stat.S_ISDIR(kind),
                 "unsafe existing managed path type")

def verify_package(package):
    need(package.is_dir() and not package.is_symlink(),"package unavailable/symlink")
    manifest=parse_manifest(package/MANIFEST)
    usr=package/"usr"
    need(usr.is_dir() and not usr.is_symlink(),"package usr tree missing/symlink")
    package_files=set()
    for entry in usr.rglob("*"):
        info=entry.lstat()
        if stat.S_ISDIR(info.st_mode):
            continue
        need(stat.S_ISREG(info.st_mode),"package contains symlink/special entry")
        package_files.add(entry.relative_to(package))
    need(package_files==set(manifest),"package file inventory != approved manifest")
    return manifest

def install(package,root):
    destination=scratch_root(root)
    items=verify_package(Path(package))
    for entry in items:
        safe_existing_tree(destination,entry)
    previous=destination/STATE
    if previous.is_symlink():
        raise RootGuardFault("OFFLINE_ROOT_GUARD_REJECTED previous manifest symlink")
    if previous.exists():
        for entry in parse_manifest(previous):
            safe_existing_tree(destination,entry)
    current=destination
    for part in STATE.parent.parts:
        current=current/part
        if current.is_symlink():
            raise RootGuardFault("OFFLINE_ROOT_GUARD_REJECTED state parent symlink")
        if current.exists():
            need(current.is_dir(),"unsafe existing state parent")
    for rel in ("installed-front-package-manifest.sha256","INSTALL-STATE.txt"):
        file=destination/STATE.parent/rel
        need(not file.is_symlink() and (not file.exists() or file.is_file()),
             "unsafe existing state file")
    return True

def uninstall(root):
    destination=scratch_root(root)
    previous=destination/STATE
    items=parse_manifest(previous)
    for entry in items:
        safe_existing_tree(destination,entry)
    for rel in ("installed-front-package-manifest.sha256","INSTALL-STATE.txt"):
        file=destination/STATE.parent/rel
        need(not file.is_symlink() and (not file.exists() or file.is_file()),
             "unsafe existing state file")
    return True

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("operation",choices=("install","uninstall"))
    parser.add_argument("paths",nargs="+")
    args=parser.parse_args()
    if args.operation=="install":
        need(len(args.paths)==2,"install expects package+scratch root")
        install(*args.paths)
    else:
        need(len(args.paths)==1,"uninstall expects scratch root")
        uninstall(args.paths[0])
    print("SP11_CAMERA_OFFLINE_ROOT_GUARD=PASS")
if __name__=="__main__":main()
