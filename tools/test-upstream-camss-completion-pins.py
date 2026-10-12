#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Verify real completion-tool rejection of altered reference and patch inputs."""
import argparse
from pathlib import Path
import shutil
import subprocess
import tempfile
import json

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parent", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    args=parser.parse_args()
    repo=Path(__file__).resolve().parents[1]
    prefix=Path("drivers/media/platform/qcom/camss")
    names=["camss-csid-680.c","camss.c","camss-vfe.c","camss.h","camss-vfe.h","camss-csid.h"]
    results=[]
    for case in ["parent_changed","parent_missing","parent_symlink","candidate_changed","header_changed","patch_changed"]:
        with tempfile.TemporaryDirectory(prefix="camss-completion-pin-") as directory:
            work=Path(directory)
            tool=work/"tools/test-upstream-camss-completion.py"
            tool.parent.mkdir()
            shutil.copyfile(repo/"tools/test-upstream-camss-completion.py",tool)
            patch=work/"src/upstream/camss/patches/0005-camss-validate-completion-routing.patch"
            patch.parent.mkdir(parents=True)
            shutil.copyfile(repo/"src/upstream/camss/patches"/patch.name,patch)
            for key,source in [("parent",args.parent),("candidate",args.candidate)]:
                target=work/key/prefix
                target.mkdir(parents=True)
                for name in names:
                    shutil.copyfile(source/prefix/name,target/name)
            path=work/"parent"/prefix/"camss-vfe.c"
            if case=="parent_missing":
                path.unlink()
            elif case=="parent_symlink":
                actual=path.with_name("copy.c")
                path.rename(actual)
                path.symlink_to(actual.name)
            else:
                if case=="candidate_changed":
                    path=work/"candidate"/prefix/"camss.c"
                elif case=="header_changed":
                    path=work/"candidate"/prefix/"camss-vfe.h"
                elif case=="patch_changed":
                    path=patch
                path.write_text(path.read_text()+"\n/* independent pin rejection fixture */\n")
            result=subprocess.run(["python3",str(tool),"--parent",str(work/"parent"),"--candidate",str(work/"candidate")],capture_output=True,text=True)
            expected="missing or symlink source" if case in ["parent_missing","parent_symlink"] else "changed pinned source"
            if result.returncode==0 or expected not in result.stderr:
                raise RuntimeError(case+": incorrect rejection")
            results.append({"case":case,"status":"PASS","reason":expected})
    print(json.dumps({"status":"PASS","reference_rejections":results,"hardware_access":False},indent=2))

if __name__=="__main__":
    main()
