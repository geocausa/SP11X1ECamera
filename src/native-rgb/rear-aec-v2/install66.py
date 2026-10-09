#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Install verified one-use rear diagnostic boot assets; never arm or reboot."""
import hashlib,json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];PROJECT=ROOT.parents[1]
BUILD=PROJECT/"02-kernel/native-rgb-rear-generation-20261010-67"
PRIVATE=ROOT.parent/"private/NATIVE-REAR-GENERATION-20261007-73"
LIBBUILD=PROJECT/"02-kernel/libcamera-native-rgb-rear-v4l2-20261010-21"
D=Path("/var/lib/sp11-camera-native-rear-generation-20261010-66")
B=Path("/boot/sp11-7.1.5-camera-native-rear-generation-20261010-66")
G=Path("/etc/grub.d/99zzzzzz_sp11_camera_native_rear_generation_20261010_66")
S=Path("/etc/systemd/system/sp11-camera-native-rear-generation-20261010-66.service")
T=Path("/etc/systemd/system/sp11-camera-native-rear-generation-20261010-66-watchdog.timer")
W=Path("/etc/systemd/system/sp11-camera-native-rear-generation-20261010-66-watchdog.service")
F=Path("/lib/firmware/qcom/sp11/rear-generation-20261010-66.bin")
ID="sp11-camera-native-rear-generation-20261010-66"
MARKER="sp11_camera_native_rear_generation_20261010_66=1"
GOLDEN=Path("/boot/sp11-7.1.5-audio-fullio-v19c")
EXPECTED_GOLDEN={
 "vmlinuz-7.1.5-sp11-render-parity-v4+":"bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a",
 "initrd.img-7.1.5-sp11-fullio-v19c":"ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d",
 "x1e80100-microsoft-denali-sp11-fullio-v19c.dtb":"2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00"}
def run(args):return subprocess.check_output([str(x) for x in args],text=True)
def sudo(*args):return run(["sudo","-n",*args])
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def copy(source,dest,mode="0600"):sudo("install","-m",mode,source,dest)
def write(text,dest,mode="0700"):
 temp=BUILD/(dest.name+".install-input");assert not temp.exists();temp.write_text(text);copy(temp,dest,mode)
def main():
 run([ROOT/"tools/camera-overlap-guard.sh","--require-clean-tracked","--require-golden","--require-no-camera-process"])
 for path in [D,B,G,S,T,W,F]:
  assert subprocess.run(["sudo","-n","test","!","-e",str(path)]).returncode==0
 assert ID not in sudo("cat","/boot/grub/grub.cfg")
 result=json.loads((BUILD/"build-result.json").read_text())
 assert result["status"]=="PASS_REAR_GENERATION_SOURCE_BUILD_NOT_INSTALLED"
 assert result["statistics_wire_format"]=="QXA2" and result["statistics_wire_bytes"]==82016
 assert result["all_DMA_lifetime_and_stop_sources_byte_identical"] is True
 for relative,entry in result["modules"].items():
  assert sha(BUILD/relative)==entry["sha256"]
  assert run(["modinfo","-F","vermagic",BUILD/relative]).strip()==entry["vermagic"]
 for relative,digest in result["staged_sources"].items():assert sha(BUILD/relative)==digest
 baseline=PROJECT/"02-kernel/native-rgb-rear-generation-20261007-73"
 # Verified baseline qualification is retained; changed transport is tested separately.
 reports=[p for p in baseline.glob("*hosted-*.json") if p.name not in ["AE-parser-hosted-02.json"]]
 assert len(reports)>=35
 for p in reports:assert json.loads(p.read_text())["status"].startswith("PASS")
 assert json.loads((BUILD/"source-stop-order-hosted-01.json").read_text())["status"]=="PASS_ACTUAL_EARLY_SOURCE_STOP_ORDER_AND_FAILURE_PINNING"
 for cc in ["gcc","clang"]:assert json.loads((BUILD/(cc+"-statistics-copy-admission.json")).read_text())["status"]=="PASS_REAR_STATISTICS_COPY_ADMISSION"
 hosted=json.loads((PROJECT/"02-kernel/rear-aec-v2-hosted-20261010-01.json").read_text())
 assert hosted["status"]=="PASS_COMPACT_AEC_V2_IDENTICAL_KERNEL_USER_PACKER_AND_DECODER"
 assert len(hosted["results"])==8 and hosted["kernel_and_user_algorithm_identical"] is True
 assert json.loads((BUILD/"runtime-v2-hosted-01.json").read_text())["status"]=="PASS_COMPACT_AEC66_RUNTIME_RECEIPTS_AND_PRESERVED_LIFECYCLE"
 for name,digest in EXPECTED_GOLDEN.items():
  assert sudo("sha256sum",GOLDEN/name).split()[0]==digest
 dtb=PROJECT/"02-kernel/native-pipeline-20261007-05/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb"
 assert sha(dtb)=="3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb"
 ir=ROOT/"src/sp11-camera-stack/authority/sp11-vd55g0-production.ko"
 assert sha(ir)=="4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72"
 profile=PRIVATE/"profile-output/p0-input-0.bin";assert profile.is_file()
 library=json.loads((LIBBUILD/"build-result.json").read_text())
 assert library["status"]=="PASS_REAR_PUBLIC_LIBCAMERA_TRANSPORT_BUILD_NOT_INSTALLED"
 assert len(library["tests"])==7 and all(v["result"]=="OK" for v in library["tests"])
 assert library["statistics_wire_format"]=="QXA2" and library["statistics_wire_bytes"]==82016
 assert library["private_optical_identity"]==66
 assert sha(ROOT/"src/native-rgb/rear-aec-v2/capture-ae66.cpp")==library["capture_ae_source_sha256"]
 assert sha(ROOT/"src/native-rgb/rear-aec-v2/rear-private-optical-v11.h")==library["capture_optical_header_sha256"]
 for relative,digest in library["built_outputs"].items():assert sha(LIBBUILD/relative)==digest
 for relative,digest in library["staged_sources"].items():
  assert sha(PROJECT/"06-camera/reference/libcamera-native-rgb-rear-v4l2-20261010-21"/relative)==digest
 probe=LIBBUILD/"capture-ae"
 identity=json.loads(run([probe,"--identity-check"]))
 assert identity==dict(status="PASS_PRIVATE_OPTICAL_COMPILE_BOUND_IDENTITY",candidate_identity=66,hardware_access=False)
 assert library["private_optical_identity"]==66
 analyzer=ROOT/"src/native-rgb/rear-aec-v2/analyze-private-optical-v11.py"
 assert sha(analyzer)==library["optical_analyzer_sha256"]
 assert json.loads(run(["python3",analyzer,"--identity-check"]))==dict(status="PASS_PRIVATE_OPTICAL_ANALYZER_IDENTITY",candidate_identity=66,hardware_access=False)
 run([probe,"--help"])
 sudo("install","-d","-m","0700",D,D/"modules",D/"lib",D/"private-optical",D/"private-statistics",D/"lib/ipa",D/"lib/proxy")
 sudo("install","-d","-m","0755",B,F.parent)
 pairs=[
  (LIBBUILD/"src/ipa/camss-x1e-rear/ipa_camss_x1e_rear.so",D/"lib/ipa/ipa_camss_x1e_rear.so","0600"),
  (LIBBUILD/"src/ipa/camss-x1e-rear/ipa_camss_x1e_rear.so.sign",D/"lib/ipa/ipa_camss_x1e_rear.so.sign","0600"),
  (LIBBUILD/"src/libcamera/proxy/worker/camss_x1e_rear_ipa_proxy",D/"lib/proxy/camss_x1e_rear_ipa_proxy","0700"),
  (ROOT/"src/native-rgb/rear-v4l2/live-control-proof.py",D/"live-control-proof.py","0600"),
  (ROOT/"src/native-rgb/rear-aec-v2/analyze-private-optical-v11.py",D/"analyze-private-optical.py","0700"),
  (probe,D/"capture","0700"),
  (LIBBUILD/"src/libcamera/libcamera.so.0.7.0",D/"lib/libcamera.so.0.7","0600"),
  (LIBBUILD/"src/libcamera/base/libcamera-base.so.0.7.0",D/"lib/libcamera-base.so.0.7","0600"),
  (ROOT/"src/native-rgb/rear-aec-v2/run66.py",D/"run-once.py","0700"),
  (ROOT/"src/native-rgb/rear-v4l2/ae-control-proof.py",D/"ae-control-proof.py","0600"),
  (ROOT/"src/native-rgb/rear-generation/route-contract.py",D/"route-contract.py","0600"),
  (ROOT/"experiments/E004-front-ir-vd55g0/e004mg-private-optical-rgb-visual-one-shot/discover-unified.py",D/"discover-unified.py","0600"),
  (BUILD/"camss/qcom-camss.ko",D/"modules/qcom-camss.ko","0600"),
  (BUILD/"imx681/imx681.ko",D/"modules/imx681.ko","0600"),
  (BUILD/"ov13858/ov13858.ko",D/"modules/ov13858.ko","0600"),
  (ir,D/"modules/sp11-vd55g0.ko","0600"),
  (profile,F,"0600")]
 assets=[]
 for source,dest,mode in pairs:
  copy(source,dest,mode);assets.append(sha(source)+"  "+str(dest))
 for name in ["vmlinuz-7.1.5-sp11-render-parity-v4+","initrd.img-7.1.5-sp11-fullio-v19c"]:
  copy(GOLDEN/name,B/name,"0644");assets.append(EXPECTED_GOLDEN[name]+"  "+str(B/name))
 copy(dtb,B/dtb.name,"0644");assets.append(sha(dtb)+"  "+str(B/dtb.name))
 command=shlex.split(Path("/proc/cmdline").read_text())
 assert any(x.startswith("BOOT_IMAGE=/boot/sp11-7.1.5-audio-fullio-v19c/") for x in command)
 blacklist=[]
 for x in command:
  if x.startswith("modprobe.blacklist="):blacklist+=x.split("=",1)[1].split(",")
 command=[x for x in command if not x.startswith(("BOOT_IMAGE=","sp11_entry=","modprobe.blacklist="))]
 command+=["sp11_entry=7.1.5-sp11-camera-native-rear-generation-20261010-66",MARKER,
  "modprobe.blacklist="+",".join(dict.fromkeys(blacklist+["qcom_camss","imx681","ov13858","sp11_vd55g0","vd55g0"]))]
 uuid=run(["findmnt","-n","-o","UUID","/"]).strip();assert uuid=="33e842b7-0434-4749-b03a-299bdcdb8b9f"
 grub=f"""#!/bin/sh
exec tail -n +3 $0
menuentry 'SP11 rear generation proof - one use' --id '{ID}' {{
 load_video
 set gfxpayload=keep
 insmod gzio
 insmod part_gpt
 insmod ext2
 insmod fdt
 search --no-floppy --fs-uuid --set=root {uuid}
 devicetree {B}/{dtb.name}
 linux {B}/vmlinuz-7.1.5-sp11-render-parity-v4+ {' '.join(shlex.quote(x) for x in command)}
 initrd {B}/initrd.img-7.1.5-sp11-fullio-v19c
}}
"""
 syntax=BUILD/"grub-syntax.txt";syntax.write_text("\n".join(grub.splitlines()[2:])+"\n")
 run(["grub-script-check",syntax]);write(grub,G,"0755")
 returning=f"""#!/usr/bin/env bash
set -Eeuo pipefail
if grep -qw '{MARKER}' /proc/cmdline; then
  grub-reboot sp11-audio-fullio-v19c
  if test "${{REAR_GENERATION_WATCHDOG:-0}}" = 1; then
    printf 'WATCHDOG\n' > {D}/WATCHDOG-FIRED
    dmesg > {D}/PRIVATE-WATCHDOG-DMESG.txt
    sync
    systemctl reboot --force --force
  else
    printf 'service_result=%s\nexit_code=%s\nexit_status=%s\n' "${{SERVICE_RESULT:-unknown}}" "${{EXIT_CODE:-unknown}}" "${{EXIT_STATUS:-unknown}}" > {D}/SERVICE-RESULT.txt
    dmesg > {D}/PRIVATE-DMESG.txt
    sync
    systemctl reboot --no-block
  fi
fi
"""
 write(returning,D/"return-golden.sh");assets.append(sudo("sha256sum",D/"return-golden.sh").split()[0]+"  "+str(D/"return-golden.sh"))
 unit=f"""[Unit]
Description=SP11 opt-in native automatic exposure400 requests, one candidate use
Wants=grub-initrd-fallback.service grub2-common.service
After=grub-initrd-fallback.service grub2-common.service
Before=display-manager.service
ConditionKernelCommandLine={MARKER}

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {D}/run-once.py
ExecStopPost={D}/return-golden.sh
TimeoutStartSec=120
TimeoutStopSec=10
KillMode=control-group

[Install]
WantedBy=multi-user.target
"""
 watchdog=f"""[Unit]
Description=SP11 rear diagnostic independent Golden-return watchdog
ConditionKernelCommandLine={MARKER}

[Service]
Type=oneshot
Environment=REAR_GENERATION_WATCHDOG=1
ExecStart={D}/return-golden.sh
"""
 timer=f"""[Unit]
Description=SP11 rear diagnostic 150-second return deadline
ConditionKernelCommandLine={MARKER}

[Timer]
OnBootSec=150
Unit={W.name}
AccuracySec=1

[Install]
WantedBy=timers.target
"""
 for text,path in [(unit,S),(watchdog,W),(timer,T)]:
  write(text,path,"0644");assets.append(sudo("sha256sum",path).split()[0]+"  "+str(path))
 assets.append(sudo("sha256sum",G).split()[0]+"  "+str(G))
 write("\n".join(assets)+"\n",D/"ASSETS.sha256","0600")
 write(run(["git","-C",ROOT,"rev-parse","HEAD"]),D/"EXPECTED-HEAD","0600")
 write(json.dumps(EXPECTED_GOLDEN,indent=2)+"\n",D/"GOLDEN-ASSET-HASHES.json","0600")
 sudo("systemd-analyze","verify",S,W,T)
 sudo("systemctl","daemon-reload");sudo("systemctl","enable",S.name,T.name)
 sudo("update-grub")
 assert ID in sudo("cat","/boot/grub/grub.cfg")
 assert "saved_entry=sp11-audio-fullio-v19c" in sudo("grub-editenv","/boot/grub/grubenv","list")
 run([ROOT/"tools/camera-overlap-guard.sh","--require-clean-tracked","--require-golden","--require-no-camera-process"])
 sudo("sha256sum","-c",D/"ASSETS.sha256")
 print("PASS_REAR_GENERATION_ASSETS_PREPARED_UNARMED_NO_HARDWARE")
if __name__=="__main__":main()
