#!/usr/bin/env python3
"""E004jr: bounded NONIMAGE media topology diagnostic for a future unique candidate.

Offline --from-file replays previously accepted saved media-ctl topology.
--live is for an already isolated, camera-capable candidate only; it does
not load modules, set media links, open video nodes, stream or power sensors.
All live topology text and failure stderr remain root-private.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import time

REQUIRED = ("ov13858 ", "imx681 ", "msm_csiphy1",
            "msm_csid0", "msm_vfe0_rdi0", "msm_vfe0_video0",
            "msm_csiphy2", "msm_csid1", "msm_vfe1_pix", "msm_vfe1_video3")
MAX_MEDIA_NODES = 8
MAX_TOPOLOGY_BYTES = 128 * 1024
MAX_ATTEMPTS = 30
MAX_SECONDS = 8.0


def topology_report(raw: str) -> dict:
    """Structure-only verdict. Do not claim this proves correct media routing."""
    ents = re.findall(r"^- entity \d+: (.*?) \(\d+ pads?, \d+ links?", raw, re.M)
    missing = [p for p in REQUIRED if not any(e.startswith(p) if p.endswith(" ")
               else e == p for e in ents)]
    present = [p for p in REQUIRED if p not in missing]
    devnodes = sorted(set(re.findall(r"device node name (/dev/(?:video|v4l-subdev)\d+)",
                                    raw)))
    return {"entities_seen": len(ents), "required_present": present,
            "required_missing": missing, "required_complete": not missing,
            "video_node_count": len([d for d in devnodes if d.startswith("/dev/video")]),
            "subdev_node_count": len([d for d in devnodes if d.startswith("/dev/v4l-subdev")])}


def private_dir(path: Path) -> Path:
    if path.is_symlink() or not path.is_dir():
        raise ValueError("E004JR_OUTPUT_MUST_BE_EXISTING_PRIVATE_DIRECTORY")
    s = path.stat()
    if os.geteuid() != 0 or s.st_uid != 0 or stat.S_IMODE(s.st_mode) != 0o700:
        raise PermissionError("E004JR_LIVE_NEEDS_ROOT_OWNED_MODE0700_DIRECTORY")
    return path


def checked_write(root: Path, filename: str, contents: str) -> None:
    if not re.fullmatch(r"[a-zA-Z0-9._-]+", filename):
        raise ValueError("E004JR_UNSAFE_FILENAME")
    name=root/filename
    fd=os.open(name,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
    with os.fdopen(fd,"w",encoding="utf8") as out:
        out.write(contents)


def safe_media_name(p: Path) -> bool:
    return bool(re.fullmatch(r"media\d+",p.name))


def inspect_live(root: Path) -> dict:
    root=private_dir(root)
    started=time.monotonic()
    last=[]
    for attempt in range(1,MAX_ATTEMPTS+1):
        if time.monotonic()-started >= MAX_SECONDS:
            break
        entries=sorted(p for p in Path("/dev").glob("media*")
                       if safe_media_name(p))[:MAX_MEDIA_NODES]
        if not entries:
            last=[{"status":"no_media_nodes"}]
            time.sleep(.15)
            continue
        reports=[]
        for m in entries:
            remaining=MAX_SECONDS-(time.monotonic()-started)
            if remaining <= 0:
                reports.append(({"device":str(m),"status":"diagnostic_budget_exhausted"},"",""))
                break
            record={"device":str(m)}
            try:
                cp=subprocess.run(["media-ctl","-d",str(m),"-p"],capture_output=True,
                                  timeout=min(1.5,remaining),check=False)
                stdout=cp.stdout[:MAX_TOPOLOGY_BYTES].decode("utf8","replace")
                stderr=cp.stderr[:4096].decode("utf8","replace")
                record.update({"returncode":cp.returncode,
                               "stdout_bytes":len(cp.stdout),
                               "stderr_bytes":len(cp.stderr),
                               "stdout_truncated":len(cp.stdout)>MAX_TOPOLOGY_BYTES,
                               "stderr_truncated":len(cp.stderr)>4096})
                record.update(topology_report(stdout))
                if (record["required_complete"] and cp.returncode==0 and
                        not record["stdout_truncated"]):
                    checked_write(root,"ACCEPTED-MEDIA-GRAPH.txt",stdout)
                    checked_write(root,"ACCEPTED-MEDIA-STDERR.txt",stderr)
                    checked_write(root,"DISCOVERY.json",json.dumps(
                        {"status":"complete","attempt":attempt,**record},
                        sort_keys=True,indent=2)+"\n")
                    return {"status":"complete","attempt":attempt,**record}
                reports.append((record,stdout,stderr))
            except (OSError,subprocess.TimeoutExpired) as exc:
                record.update({"status":"media_ctl_failed",
                               "error_type":type(exc).__name__})
                reports.append((record,"",str(exc)[:4096]))
        last=[r for r,_,_ in reports]
        if time.monotonic()-started >= MAX_SECONDS or attempt==MAX_ATTEMPTS:
            for i,(_,out,err) in enumerate(reports):
                checked_write(root,f"MEDIA-{i}-LAST-STDOUT.txt",out)
                checked_write(root,f"MEDIA-{i}-LAST-STDERR.txt",err)
            break
        time.sleep(.15)
    result={"status":"incomplete","attempts":attempt if "attempt" in locals() else 0,
            "elapsed_ms":int((time.monotonic()-started)*1000),"observed":last}
    checked_write(root,"DISCOVERY.json",json.dumps(result,sort_keys=True,indent=2)+"\n")
    return result


def main() -> int:
    parser=argparse.ArgumentParser()
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--from-file",type=Path)
    group.add_argument("--live",action="store_true")
    parser.add_argument("--out-dir",type=Path)
    args=parser.parse_args()
    if args.from_file:
        if args.out_dir:
            parser.error("offline --from-file cannot create live output")
        result=topology_report(args.from_file.read_text(errors="replace"))
        print(json.dumps({"source":"archived_text_only",**result},sort_keys=True))
        return 0 if result["required_complete"] else 2
    if args.out_dir is None:
        parser.error("--live requires a pre-existing private --out-dir")
    result=inspect_live(args.out_dir)
    print("E004JR_MEDIA_GRAPH_DIAGNOSTIC="+result["status"]+
          " DETAILS_PRIVATE="+str(args.out_dir/"DISCOVERY.json"))
    return 0 if result["status"]=="complete" else 1


if __name__=="__main__":
    raise SystemExit(main())
