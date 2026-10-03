#!/usr/bin/env python3
"""Validate same-SP11 private source pins, Windows observations and Golden return."""
from pathlib import Path
import hashlib,importlib.util,json,re,struct,subprocess
import pefile
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
D=R.parent/"private/E011DN-explore"
W=D/"windows-recovered"
def j(p):return json.loads(p.read_text(encoding="utf-8-sig"))
def text(p):
 b=p.read_bytes();return b.decode("utf-16" if b[:2] in (b"\xff\xfe",b"\xfe\xff") else "utf-8-sig",errors="replace")
def run(a):
 r=subprocess.run(a,capture_output=True,text=True);assert r.returncode==0,(a,r.returncode);return r.stdout
before=j(D/"E011DN-20261003-1926A/PRE-BOOT-GUARD.private.json")
assert before["base_commit"]=="f9669dd0809f2188232174fd30478101fe7d1e34"
hashes={n:hashlib.sha256((Path("/boot/sp11-7.1.5-audio-fullio-v19c")/n).read_bytes()).hexdigest() for n in before["Golden_payload_hashes"]}
assert hashes==before["Golden_payload_hashes"]
efi=run(["sudo","-n","efibootmgr"])
assert efi==before["EFI"] and "BootNext" not in efi
grub=run(["sudo","-n","grub-editenv","/boot/grub/grubenv","list"])
assert grub==before["GRUB"]
boot=Path("/proc/sys/kernel/random/boot_id").read_text().strip()
assert boot!=before["boot_id"]
for n,o in before["historical"].items():
 assert run(["git","-C",str(R.parent/n),"rev-parse","HEAD"]).strip()==o["head"]
 assert run(["git","-C",str(R.parent/n),"status","--porcelain=v1","--untracked-files=all"])==o["status"]
assert not any(x.split()[0] in ("ntfs","ntfs3","fuseblk") for x in run(["findmnt","-rn","-o","FSTYPE,TARGET"]).splitlines())
guard={"status":"PASS_GOLDEN_RETURN_EFI_GRUB_HASHES_HISTORY_EXACT","boot_id":boot,"before_boot_id":before["boot_id"],"Golden_payload_hashes":hashes,"Windows_partition_unmounted":True,"persistent_EFI_and_GRUB_unchanged":True}
(D/"GUARD-SAFE.json").write_text(json.dumps(guard,indent=2)+"\n")
spec=importlib.util.spec_from_file_location("dn_image",R/"experiments/E004-front-ir-vd55g0/e011ai-rear-neutral-scalar-full-integration/native-private.py")
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
blob=m.DLL.read_bytes();assert hashlib.sha256(blob).hexdigest()==m.DLL_SHA
pe=pefile.PE(data=blob)
pins=j(D/"REGISTRY-PINS-SAFE.json")
chosen=("0x5df780","0x5c0a58","0x5b80a8","0x5bffd8","0x5de700")
functions={f["entry_RVA"]:dict(bytes=f["bytes"],sha256=f["sha256"]) for f in pins["functions"] if f["entry_RVA"] in chosen}
assert len(functions)==5
for a,f in functions.items():assert hashlib.sha256(pe.get_data(int(a,16),f["bytes"])).hexdigest()==f["sha256"]
writes=[x for x in pins["global_references"] if x["access"]=="write" and x["field_RVA"] in ("0x17350e0","0x17350e4","0x17350e8","0x17350ec")]
assert len(writes)==4 and all(x["function_RVA"]=="0x5de700" for x in writes)
default_table=0x1330a68
defaults=list(struct.unpack("<3Q",pe.get_data(default_table,24)))
defaults=[a-pe.OPTIONAL_HEADER.ImageBase for a in defaults]
assert defaults==[0x1de30,0x1df30,0x1df90]
assert struct.unpack("<Q",pe.get_data(0x1626898,8))[0]-pe.OPTIONAL_HEADER.ImageBase==default_table
assert pe.DIRECTORY_ENTRY_LOAD_CONFIG.struct.GuardCFCheckFunctionPointer-pe.OPTIONAL_HEADER.ImageBase==0xf7e7b8
assert struct.unpack("<Q",pe.get_data(0xf7e7b8,8))[0]-pe.OPTIONAL_HEADER.ImageBase==0x1a8c0
attempts=[]
for suffix,handles in (("A",69),("B",449)):
 identity="E011DN-20261003-1926"+suffix
 here=W/identity
 a=j(here/"ATTEMPT-SAFE.json")
 log=text(W/(identity+"-holder.log"))
 assert a["camera_start_success"] and a["camera_stop_pass"] and a["holder_done"]
 assert a["valid_handles"]==handles and a["cdb_count"]==0 and a["task_state"]=="Ready" and not a["target_pid_alive"]
 assert len(re.findall(r"START_BEGIN",log))==len(re.findall(r"START_STATUS=Success",log))==1
 assert len(re.findall(r"STOP_PASS",log))==len(re.findall(r"E011DN_HOLDER_END",log))==1
 assert (W/(identity+"-holder")/"SCRIPT-ENTRY-CONSUMED.marker").is_file()
 obs=text(here/"cdb-observer.raw")
 assert len(re.findall(r"^E011DN_COPY_BEFORE ",obs,re.M))==len(re.findall(r"^E011DN_COPY_AFTER ",obs,re.M))==0
 attempts.append({"identity":identity,"status":a["status"],"camera_starts":1,"valid_4k_handle_acquisitions":handles,"stop_dispose_done":True,"camera_task_removed":True,"debugger_process_absent":True,"target_service_process_absent":True,"RS_copy_samples":0})
b=W/"E011DN-20261003-1926B"
module=j(b/"MODULE-SAFE.json");pre=j(b/"PRE-START-SAFE.json")
assert module["image_sha256"]==m.DLL_SHA and module["ready"] and not module["start_consumed"]
assert pre["armed"] and pre["bp_exact"] and pre["bp_rvas"]==["0x7414b0","0x7414cc"] and pre["errors"]==0
cap=b/"capture"
assert sorted(x.name for x in cap.iterdir())==["READY_META.bin","READY_PLATFORM.bin","READY_TAGS.bin"]
tags=(cap/"READY_TAGS.bin").read_bytes();meta=(cap/"READY_META.bin").read_bytes();platform=(cap/"READY_PLATFORM.bin").read_bytes()
assert (len(tags),len(meta),len(platform))==(28,64,24)
assert struct.unpack("<7I",tags)==(0,)*7
bound=struct.unpack_from("<I",meta,0)[0];descriptor=struct.unpack_from("<Q",meta,56)[0]
assert bound!=0 and descriptor!=0
base=int(module["base"],16)
live=[p-base for p in struct.unpack("<3Q",platform)]
assert live==defaults
bad=re.findall(r"Syntax error|Numeric expression missing|Memory access error|Could not|Cannot open|Couldn't",text(b/"cdb-observer.raw"))
assert not bad
observed={"experiment":"E011DN","status":"PASS_BOUNDED_READY_REGISTRY_SNAPSHOT_RS_COPY_UNOBSERVED","image_sha256":m.DLL_SHA,
"accepted_observation_identity":"E011DN-20261003-1926B","excluded_RS_attempt_identity":"E011DN-20261003-1926A",
"snapshot_stage":"initialized rear NV12 3840x2160 reader ready before Start; source process suspended by user-mode attach",
"snapshot_bytes":{"runtime_tags":28,"metadata_registry":64,"platform_callbacks":24},
"runtime_tag_cell_count":7,"runtime_tag_nonzero_count":0,"selected_RS_tag_cell_RVA":"0x17a30f4","selected_RS_tag_initialized":False,
"metadata_bound_RVA":"0x17350e0","metadata_bound_nonzero":True,"metadata_descriptor_pointer_RVA":"0x1735118","metadata_descriptor_pointer_nonnull":True,
"platform_pointer_cell_RVA":"0x1626898","file_default_table_RVA":"0x1330a68","platform_callback_RVAs":[hex(x) for x in live],"platform_callbacks_match_file_default":True,
"source_function_pins":functions,"metadata_bound_writer_reference":next(x for x in writes if x["field_RVA"]=="0x17350e0"),
"GuardCFCheckFunctionPointer_cell_RVA":"0xf7e7b8","cold_CFG_check_target_RVA":"0x1a8c0","cold_CFG_check_is_not_resource_constructor":True,
"attempts":attempts,"same_Windows_boot":True,"Windows_boots":1,"reboots":2,"camera_starts":2,"RS_copy_samples":0,
"registry_snapshot_qualified":True,"original_metadata_initializer_execution_qualified":False,"selected_runtime_tag_initialization_qualified":False,
"populated_RS_identity_generation_lifetime_qualified":False,"live_query_or_reader_execution_proven":False,"absence_of_RS_across_other_processes_or_profiles_proven":False,
"normal_AFD_input_authority_closed":False,"complete_deterministic_source_bootstrap_closed":False,"independent_enabled_output_retirement_proven":False,
"native_rear_runtime_allowed":False,"optical_material_saved":False,"kernel_debugger_halts":0,"production_code_changed":False,
"private_raw_material_exported":False,"Golden_guard_status":guard["status"],"next_experiment":"E011DO",
"next_action":"Qualify original 5DE700 metadata registry initialization with explicit allocation, descriptor ownership and default callback contracts; separately resolve selected reader request/profile path before another fresh-boot RS observation."}
observed["private_nonoptical_evidence_hashes"]={f"{identity}/{f.relative_to(W/identity)}":hashlib.sha256(f.read_bytes()).hexdigest() for identity in ("E011DN-20261003-1926A","E011DN-20261003-1926B") for f in (W/identity).rglob("*") if f.is_file()}
(D/"OBSERVATION-SAFE.json").write_text(json.dumps(observed,indent=2)+"\n")
print(json.dumps({"status":observed["status"],"source_pins_verified":len(functions),"snapshot_bytes":116,"starts":2,"valid_handle_acquisitions":[69,449],"RS_copy_samples":0,"Golden_guard":guard["status"],"private_originals_exported":False}))
