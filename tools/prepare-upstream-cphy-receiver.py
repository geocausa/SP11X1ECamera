#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Apply the pinned receiver series to the qualified candidate17 kernel source."""
import argparse, pathlib, hashlib, json, os, shutil, subprocess, sys
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def checked(root, name, expected):
    p=root/name
    assert not p.is_symlink() and p.resolve().is_relative_to(root), name
    assert (sha(p) if p.exists() else None)==expected, name
def main():
    if sys.flags.optimize:
        raise RuntimeError('Run source admission without Python -O')
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--parent-source',type=pathlib.Path,required=True)
    ap.add_argument('--output',type=pathlib.Path,required=True)
    a=ap.parse_args(); parent=a.parent_source.resolve(); out=a.output.absolute()
    bundle=pathlib.Path(__file__).resolve().parents[1]/'src/upstream/receiver/cphy-x1e-20261012'
    m=json.loads((bundle/'manifest.json').read_text())
    assert parent.is_dir() and not out.exists() and not out.is_symlink()
    assert not out.resolve().is_relative_to(parent) and not parent.is_relative_to(out.resolve())
    assert not out.resolve().is_relative_to(bundle.parents[3]), 'output inside repository'
    for p,pin in {**m['parent_source_sha256'],**m['unchanged_parent_source_sha256']}.items():
        checked(parent,p,pin)
    for name,pin in m['patch_sha256'].items(): checked(bundle/'patches',name,pin)
    shutil.copytree(parent,out,copy_function=os.link,symlinks=True,ignore=shutil.ignore_patterns('.git'))
    # Detach every changed old file before patching a hardlink clone.
    for p,pin in m['parent_source_sha256'].items():
        if pin is not None:
            q=out/p; data=q.read_bytes();q.unlink();q.write_bytes(data)
    for name in m['patch_sha256']:
        subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(bundle/'patches'/name)],cwd=out,check=True)
    for p,pin in {**m['output_source_sha256'],**m['unchanged_parent_source_sha256']}.items():
        checked(out,p,pin)
    for p,pin in {**m['parent_source_sha256'],**m['unchanged_parent_source_sha256']}.items():
        checked(parent,p,pin)
    print(json.dumps({'ok':True,'changed_files':len(m['output_source_sha256']),'unchanged_files':len(m['unchanged_parent_source_sha256']),'output':str(out),'installed':False}))
if __name__=='__main__':
    try: main()
    except (AssertionError,OSError,subprocess.CalledProcessError) as e:
        print('Receiver preparation rejected: '+str(e),file=sys.stderr);sys.exit(1)
