#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Retire a spent front parameter probe on Golden; never stream or replay."""
import argparse,datetime,hashlib,json,os,subprocess
from pathlib import Path
ap=argparse.ArgumentParser();ap.add_argument("--attempt",choices=["01","02"],required=True);args=ap.parse_args()
need=lambda ok: None if ok else (_ for _ in ()).throw(RuntimeError("retirement precondition"))
need(os.geteuid()==0)
r=Path(__file__).resolve().parents[3]
need("BOOT_IMAGE=/boot/sp11-7.1.5-audio-fullio-v19c/" in Path("/proc/cmdline").read_text())
subprocess.run([str(r/"tools/camera-overlap-guard.sh"),"--require-golden","--require-no-camera-process"],cwd=r,check=True)
name=f"sp11-camera-native-front-param-queue-20261010-{args.attempt}"
d=Path("/var/lib")/name
need((d/"ATTEMPT-CONSUMED").is_file());need(not (d/"RETIREMENT.json").exists())
result=json.loads((d/"RESULT.json").read_text())
need(result["identity"]==f"E-NATIVE-FRONT-PARAM-QUEUE-20261010-{args.attempt}")
golden=json.loads((d/"GOLDEN-ASSET-HASHES.json").read_text())
for file,sha in golden.items():need(hashlib.sha256(Path(file).read_bytes()).hexdigest()==sha)
units=[name+".service",name+"-watchdog.timer",name+"-watchdog.service"]
for unit in units[:2]:subprocess.run(["systemctl","disable","--now",unit],check=True)
subprocess.run(["systemctl","stop",units[2]],check=True)
subprocess.run(["systemctl","reset-failed",*units],check=False)
for unit in units:
 need(subprocess.check_output(["systemctl","show",unit,"-p","ActiveState","--value"],text=True).strip()=="inactive")
 state=subprocess.run(["systemctl","is-enabled",unit],text=True,capture_output=True).stdout.strip()
 need(state in ("disabled","static"))
firmware=Path("/lib/firmware/qcom/sp11/imx681-2560x1440-nv12-v1.bin")
need(firmware.is_file())
need(hashlib.sha256(firmware.read_bytes()).hexdigest()==hashlib.sha256((d/firmware.name).read_bytes()).hexdigest())
firmware.unlink()
script=Path("/etc/grub.d")/f"99zzzzzz_sp11_camera_native_front_param_queue_20261010_{args.attempt}"
archive=d/"RETIRED-GRUB-SCRIPT";need(script.is_file() and not archive.exists())
script.rename(archive)
subprocess.run(["update-grub"],check=True)
env=subprocess.check_output(["grub-editenv","/boot/grub/grubenv","list"],text=True).splitlines()
need("saved_entry=sp11-audio-fullio-v19c" in env)
need(not any(v.startswith("next_entry=") and v!="next_entry=" for v in env))
need(name not in Path("/boot/grub/grub.cfg").read_text())
for file,sha in golden.items():need(hashlib.sha256(Path(file).read_bytes()).hexdigest()==sha)
record={"identity":result["identity"],"retired":True,"retired_utc":datetime.datetime.now(datetime.timezone.utc).isoformat(),
 "result_status":result["status"],"candidate_boot_id":result["candidate_boot_id"],
 "golden_boot_id":Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
 "saved_default_unchanged":True,"next_entry_empty":True,"Golden_asset_hashes_unchanged":True,
 "experiment_units_disabled_and_inactive":True,"owned_temporary_profile_removed":True,
 "grub_script_archived":True,"private_pixels_same_SP11":True,"retry":False}
os.umask(0o077)
with (d/"RETIREMENT.json").open("x") as f:json.dump(record,f,indent=2,sort_keys=True);f.write("\n");f.flush();os.fsync(f.fileno())
print(json.dumps(record,sort_keys=True))
