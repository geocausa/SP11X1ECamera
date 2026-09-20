#!/usr/bin/env python3
"""E004iu: fail-closed OFFLINE rear RAW10 -> NV12 fast-preview wrapper.

Rebuilds a disposable C helper per offline invocation; this compile/setup
cost is NOT included in the per-frame conversion timing. No media/V4L2/IR.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
EXAMPLE=ROOT/"experiments/E004-front-ir-vd55g0/e004dz-canonical-package-rgb-handoff/runtime-output/rear-colorbar.raw"
EXAMPLE_SHA="6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346"
REAR_BYTES=14321824
NV12_BYTES=3110400

def digest(path:Path)->str:
    with path.open("rb") as f:
        return hashlib.file_digest(f,"sha256").hexdigest()

def inspect_source(source:Path,reference_colorbar:bool,frames:int=1)->str:
    if type(frames) is not int or not 1 <= frames <= 27:
        raise ValueError("offline batch must contain between 1 and 27 frames")
    if reference_colorbar and frames!=1:
        raise ValueError("reference colour bar mode requires exactly one frame")
    if source.is_symlink() or not source.is_file() or source.stat().st_size!=REAR_BYTES*frames:
        raise ValueError("only a complete regular non-symlink rear packed-Bayer frame")
    if source.resolve()!=EXAMPLE.resolve():
        if not source.resolve().is_relative_to(Path("/tmp")):
            raise ValueError("non-reference optical input must be a private /tmp file")
        parent=source.parent.resolve()
        if parent == Path("/tmp") or parent.stat().st_uid!=os.getuid() or parent.stat().st_mode&0o077:
            raise ValueError("optical input requires an owned private /tmp parent")
    actual=digest(source)
    if reference_colorbar and (source.resolve()!=EXAMPLE.resolve() or actual!=EXAMPLE_SHA):
        raise ValueError("reference colour bar source/checksum changed")
    return actual

def inspect_destination(output:Path)->None:
    parent=output.parent.resolve()
    if parent == Path("/tmp") or not parent.is_relative_to(Path("/tmp")):
        raise ValueError("output needs a caller-owned private directory below /tmp")
    if output.exists() or output.is_symlink():
        raise FileExistsError("never replace an existing output")
    if not parent.is_dir() or parent.stat().st_uid!=os.getuid() or parent.stat().st_mode&0o077:
        raise ValueError("output parent must be an owned private directory")
    if output.resolve(strict=False).parent != parent:
        raise ValueError("output parent changed unexpectedly")

def convert(source:Path,output:Path, *, reference_colorbar:bool=False,
            sanitizer:bool=False,frames:int=1, runner=subprocess.run):
    source_sha=inspect_source(source,reference_colorbar,frames)
    inspect_destination(output)
    if not shutil.which("gcc"):
        raise RuntimeError("gcc unavailable for offline C helper")
    with tempfile.TemporaryDirectory(prefix="sp11-e004iu-build-",dir="/tmp") as td:
        scratch=Path(td)
        binary=scratch/"rear-fast"
        flags=["-std=c11","-Wall","-Wextra","-Werror","-pedantic",
               "-fno-omit-frame-pointer"]
        if sanitizer:
            flags+=["-O1","-g","-fsanitize=address,undefined"]
        else:
            flags+=["-O3"]
        runner(["gcc",*flags,str(HERE/"rear_fast.c"),"-lm","-o",str(binary)],
               capture_output=True,text=True,check=True,timeout=45)
        # Only a new, exclusive output filename; compiled C unlinks on failure.
        proc=runner([str(binary),"--input",str(source),"--output",str(output),
                     "--frames",str(frames)],
                    capture_output=True,text=True,check=True,timeout=35)
    marker=re.fullmatch(
        r"E004IU_OFFLINE_REAR_NV12_BYTES=([0-9]+) FRAMES=([0-9]+) CONVERSION_MS=([0-9.]+) "
        r"AVG_CONVERSION_MS=([0-9.]+) BATCH_IO_AND_CONVERSION_MS=([0-9.]+) "
        r"SOURCE=pgAA_4076x2806 OUTPUT=NV12_1920x1080 "
        r"COLOUR_CALIBRATED=NO LIVE_CAMERA=NO",proc.stdout.strip())
    if not marker or int(marker.group(1)) != NV12_BYTES*frames or int(marker.group(2))!=frames:
        output.unlink(missing_ok=True)
        raise ValueError("unrecognized fast converter result or incorrect batch length")
    if not output.is_file() or output.is_symlink() or output.stat().st_size!=NV12_BYTES*frames:
        output.unlink(missing_ok=True)
        raise ValueError("incomplete or invalid NV12 output")
    if digest(source)!=source_sha:
        output.unlink(missing_ok=True)
        raise ValueError("source changed during offline processing")
    os.chmod(output,0o600)
    return {"experiment":"E004iu",
       "source_fourcc":"pgAA","source_geometry":"4076x2806",
       "source_stride_bytes":5104,"source_bytes":REAR_BYTES*frames,
       "frames":frames,
       "source_sha256":source_sha,
       "accepted_reference_colorbar":reference_colorbar,
       "output_fourcc":"NV12","output_geometry":"1920x1080",
       "output_bytes":NV12_BYTES*frames,"output_sha256":digest(output),
       "c_conversion_ms_excluding_compile_and_disk_io":float(marker.group(3)),
       "c_average_conversion_ms_excluding_compile_and_disk_io":float(marker.group(4)),
       "c_batch_io_and_conversion_ms_excluding_compile":float(marker.group(5)),
       "c_average_batch_io_and_conversion_ms_excluding_compile":float(marker.group(5))/frames,
       "preview_method":"nearest 2x2 GRBG colour-tile; approximate BT.601 full range",
       "full_demosaic":False,"colour_calibrated":False,
       "live_camera_used":False,"live_30fps_pipeline_proven":False,
       "standard_application_endpoint_created":False}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input",type=Path,required=True)
    parser.add_argument("--output",type=Path,required=True)
    parser.add_argument("--reference-colorbar",action="store_true")
    parser.add_argument("--frames",type=int,default=1)
    parser.add_argument("--sanitizer",action="store_true")
    args=parser.parse_args()
    print(json.dumps(convert(args.input,args.output,
         reference_colorbar=args.reference_colorbar,sanitizer=args.sanitizer,frames=args.frames),
         sort_keys=True))

if __name__=="__main__":
    main()
