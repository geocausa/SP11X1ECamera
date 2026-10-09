#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Install verified one-use rear diagnostic boot assets; never arm or reboot."""
import hashlib,json,shlex,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];PROJECT=ROOT.parents[1]
BUILD=PROJECT/"02-kernel/native-rgb-rear-generation-20261007-47"
PRIVATE=ROOT.parent/"private/NATIVE-REAR-GENERATION-20261007-47"
LIBBUILD=PROJECT/"02-kernel/libcamera-native-rgb-rear-v4l2-20261008-04"
D=Path("/var/lib/sp11-camera-native-rear-generation-20261007-36")
B=Path("/boot/sp11-7.1.5-camera-native-rear-generation-20261007-36")
G=Path("/etc/grub.d/99zzzzzz_sp11_camera_native_rear_generation_20261007_36")
S=Path("/etc/systemd/system/sp11-camera-native-rear-generation-20261007-36.service")
T=Path("/etc/systemd/system/sp11-camera-native-rear-generation-20261007-36-watchdog.timer")
W=Path("/etc/systemd/system/sp11-camera-native-rear-generation-20261007-36-watchdog.service")
F=Path("/lib/firmware/qcom/sp11/rear-generation-20261007-36.bin")
ID="sp11-camera-native-rear-generation-20261007-36"
MARKER="sp11_camera_native_rear_generation_20261007_36=1"
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
 manifest=json.loads((ROOT/"src/native-rgb/rear-windows-ccif/registers.json").read_text())
 assert result["source_validated_non_address_CSR_count"]==len(manifest["VFE1_registers"])
 for relative,entry in result["modules"].items():
  assert sha(BUILD/relative)==entry["sha256"]
  assert run(["modinfo","-F","vermagic",BUILD/relative]).strip()==entry["vermagic"]
 for relative,digest in result["staged_sources"].items():assert sha(BUILD/relative)==digest
 assert json.loads((BUILD/"offline-runner-01.json").read_text())["status"]=="PASS_REAL_GRAPH_ADMISSION_FORMAT_READBACK_AND_PROBE_COMPILE"
 assert json.loads((BUILD/"csr-whitelist-hosted-01.json").read_text())["status"]=="PASS_EXACT_VFE680_NAMED_SCALAR_WHITELIST"
 noc=json.loads((BUILD/"noc-clock-hosted-01.json").read_text())
 assert noc["status"]=="PASS_ACTUAL_CANDIDATE_NOC_FLOOR_SHARED_PARENT_CCF_FAILURE_MODELS"
 geometry=json.loads((BUILD/"linear-geometry-hosted-01.json").read_text())
 assert geometry["linear_FULL_NV12"] is True and geometry["FULL_output_bits"]==8
 assert geometry["fixture_and_translation_unit_resolve_actual_staged_includes"] is True
 linear=json.loads((BUILD/"linear-nv12-hosted-01.json").read_text())
 assert linear["status"]=="PASS_ACTUAL_REAR_LINEAR_LAYOUT_BUS_AND_LEDGER"
 assert linear["FULL_compression_register_writes"]==0
 pin=json.loads((BUILD/"clean-lifecycle-hosted-01.json").read_text())
 assert pin["status"]=="PASS_CANDIDATE_CLEAN_STOP_RELEASE_AND_FAILURE_STOP_MODELS"
 assert pin["successful_reclaim_mock_call_checked"] is True
 assert json.loads((BUILD/"public-reclaim-hosted-01.json").read_text())["status"]=="PASS_ACTUAL_REAR_COHERENT_AND_PUBLIC_LEASE_ALL_OR_NONE_RECLAIM"
 assert json.loads((BUILD/"lease-hosted-01.json").read_text())["status"]=="PASS_ACTUAL_REAR_RETAINED_DMABUF_MAPPING_LEASE"
 assert json.loads((BUILD/"dma-hosted-01.json").read_text())["status"]=="PASS_ACTUAL_REAR_VB2_MAPPED_SG_APERTURE_ADMISSION"
 assert pin["successful_stop_helpers_called_once_checked"] is True
 assert json.loads((BUILD/"public-lifecycle-hosted-01.json").read_text())["status"]=="PASS_ACTUAL_PUBLIC_REAR_RUNNER_LIFECYCLE_FAILURE_MODELS"
 transport=json.loads((BUILD/"transport-hosted-01.json").read_text())
 assert transport["status"]=="PASS_ACTUAL_REAR_TRANSPORT_HELPER_PREDICATE_NO_PACKET_FIELD_OR_ACK_WRITES"
 assert transport["exact_rear_SW_reset_and_other_mode_combined_reset_admission_checked"] is True
 assert transport["exact_rear_route_before_reset_and_generic_front_unchanged_checked"] is True
 assert transport["path_config_after_packet0_guard_and_11_atomic_failures_checked"] is True
 assert transport["sensor_mode"]=="mode1"
 mode=json.loads((BUILD/"sensor-mode-hosted-01.json").read_text())
 assert mode["status"]=="PASS_SOURCE_SENSOR_MODES_MATCH_LOCAL_ORACLE"
 vfe=json.loads((BUILD/"vfe-hosted-02.json").read_text())
 assert vfe["status"]=="PASS_REAL_SHARED_VFE_PREFIX_REAR_ADMISSION_AND_READBACK"
 assert vfe["full_and_same_SP11_observed_readback_models_checked"] is True
 event=json.loads((BUILD/"event-queue-hosted-01.json").read_text())
 assert event["status"]=="PASS_ACTUAL_REAR_SPSC_EVENT_QUEUE_WRAP_OVERFLOW_AND_THREADED_PUBLICATION"
 observed=json.loads((BUILD/"live-observe-hosted-01.json").read_text())
 assert observed["status"]=="PASS_ACTUAL_REAR_LIVE_REPLACEMENT_READ_ONLY_OBSERVATION"
 assert observed["DMA_release_or_reuse_authority"] is False
 retired=json.loads((BUILD/"live-retire-hosted-01.json").read_text())
 assert retired["status"]=="PASS_ACTUAL_LIVE_REAR_FULL_MAPPING_RETIREMENT_AND_AUX_PINNING"
 assert retired["actual_old_auxiliary_live_release_checked"] is True
 assert json.loads((BUILD/"public-reclaim-hosted-01.json").read_text())["actual_live_retired_auxiliary_zero_state_cleanup_checked"] is True
 assert json.loads((BUILD/"offline-runner-01.json").read_text())["negative_live_auxiliary_retirement_cases"]==13
 assert json.loads((BUILD/"public-reclaim-hosted-01.json").read_text())["actual_retired_old_FULL_and_remaining_DMA_cleanup_checked"] is True
 assert json.loads((BUILD/"command-receipts-hosted-01.json").read_text())["status"]=="PASS_ACTUAL_EXACT_COMMAND_ALLOCATION_REQUEST_OWNER_AND_22_BL_RECEIPTS"
 assert json.loads((BUILD/"command-fifo-hosted-01.json").read_text())["status"]=="PASS_ACTUAL_SERIALIZED_FIFO_RECEIPT_CAPTURE_AND_CURRENT_CHECK"
 assert json.loads((BUILD/"offline-runner-01.json").read_text())["negative_command_receipt_cases"]==13
 assert json.loads((BUILD/"command-retire-hosted-01.json").read_text())["status"]=="PASS_ACTUAL_LIVE_COMMAND_RETIREMENT_AND_POST_STOP_ZERO_STATE_RELEASE"
 assert json.loads((BUILD/"offline-runner-01.json").read_text())["negative_live_command_retirement_cases"]==16
 assert json.loads((BUILD/"offline-runner-01.json").read_text())["negative_rolling_queue_cases"]==17
 assert json.loads((BUILD/"waitqueue-hosted-01.json").read_text())["status"]=="PASS_ACTUAL_REAR_QBUF_START_JOIN_INITIALIZED_WAITQUEUE"
 assert json.loads((BUILD/"output-update-hosted-01.json").read_text())["status"]=="PASS_ACTUAL_SOURCE_LOCKED_REAR_RUP_AUP_OWNER_GUARDS"
 assert json.loads((BUILD/"session-gate-hosted-01.json").read_text())["status"]=="PASS_ACTUAL_BOUNDED_SESSION_GATES_AND_CLEAN_PROOF_POISONING"
 assert json.loads((BUILD/"restart-runtime-hosted-02.json").read_text())["status"]=="PASS_THREE_SESSION_GATE_PARSER_FAILURE_ADMISSION"
 queue=json.loads((BUILD/"rear-queue-hosted-01.json").read_text())
 assert queue["status"]=="PASS_ACTUAL_REAR_ROLLING_QUEUE_LEDGER_RETIREMENT_AND_BUFFER_REUSE"
 assert len(queue["results"])==2 and all(r["live_frames"]==80 and r["negative_cases"]==211 for r in queue["results"])
 for name,digest in EXPECTED_GOLDEN.items():
  assert sudo("sha256sum",GOLDEN/name).split()[0]==digest
 dtb=PROJECT/"02-kernel/native-pipeline-20261007-05/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb"
 assert sha(dtb)=="3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb"
 ir=ROOT/"src/sp11-camera-stack/authority/sp11-vd55g0-production.ko"
 assert sha(ir)=="4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72"
 profile=PRIVATE/"profile-output/p0-input-0.bin";assert profile.is_file()
 library=json.loads((LIBBUILD/"build-result.json").read_text())
 assert library["status"]=="PASS_REAR_PUBLIC_LIBCAMERA_TRANSPORT_BUILD_NOT_INSTALLED"
 assert len(library["tests"])==6 and all(v["result"]=="OK" for v in library["tests"])
 assert sha(ROOT/"src/native-rgb/rear-libcamera/capture-queue.cpp")==library["capture_source_sha256"]
 for relative,digest in library["built_outputs"].items():assert sha(LIBBUILD/relative)==digest
 for relative,digest in library["staged_sources"].items():
  assert sha(PROJECT/"06-camera/reference/libcamera-native-rgb-rear-v4l2-20261008-04"/relative)==digest
 probe=LIBBUILD/"capture"
 run([probe,"--help"])
 sudo("install","-d","-m","0700",D,D/"modules",D/"lib")
 sudo("install","-d","-m","0755",B,F.parent)
 pairs=[
  (probe,D/"capture","0700"),
  (LIBBUILD/"src/libcamera/libcamera.so.0.7.0",D/"lib/libcamera.so.0.7","0600"),
  (LIBBUILD/"src/libcamera/base/libcamera-base.so.0.7.0",D/"lib/libcamera-base.so.0.7","0600"),
  (ROOT/"src/native-rgb/rear-v4l2/run-rear-restart.py",D/"run-once.py","0700"),
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
 command+=["sp11_entry=7.1.5-sp11-camera-native-rear-generation-20261007-36",MARKER,
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
Description=SP11 three same-boot rear libcamera sessions, one candidate use
Wants=grub-initrd-fallback.service grub2-common.service
After=grub-initrd-fallback.service grub2-common.service
Before=display-manager.service
ConditionKernelCommandLine={MARKER}

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {D}/run-once.py
ExecStopPost={D}/return-golden.sh
TimeoutStartSec=75
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
Description=SP11 rear diagnostic 90-second return deadline
ConditionKernelCommandLine={MARKER}

[Timer]
OnBootSec=90
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
