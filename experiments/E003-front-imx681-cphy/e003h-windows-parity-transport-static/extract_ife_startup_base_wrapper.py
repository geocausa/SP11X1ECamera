#!/usr/bin/env python3
import hashlib
import json
import re
import struct
from pathlib import Path

HERE = Path(__file__).resolve().parent
E003 = HERE.parent

EXPECTED = {
    "derived": "7b400bc1402e6b6d6b8f1fba7bbbae1888fe6ee6d37798cb301cedd739840801",
    "initial": "0444e1d40c19b34bebf9c150aa3681fb1261a74997338adfa0c6dee5ee1d8a8a",
    "steady": "3bcf4efe34c891dcc6bc78c3cefc94d916ffd71e27dab81e75493f9ed320dce4",
    "csid_order": "d433307f97f97d2a1bdcf27b47fd9010e78b7fbb3ab75dfe78aad78c886cd19d",
    "0042": "32b2236f38977564936e9f69942c5892008375a45e3e87328eec2ca50538d201",
    "0043": "ab2f5df944dd60a8be716eb52703ba46f654386fa65c2f1308811d7ee5403abd",
    "0044": "d848302d307e4b3c36da5fa3766a58721c13f4c2b4c65a0ef3e083fc4dd3f6db",
}

PATHS = {
    "derived": HERE / "windows-ife-startup-base-wrapper-derived.json",
    "initial": HERE / "windows-ife-cdm" / "initial-ife-cdm-summary.json",
    "steady": HERE / "vfe1-epoch0-cdm-batches-oracle.json",
    "csid_order": HERE / "windows-csid1-config-rup-enable-order-oracle.json",
    "0042": E003 / "e003h-csid1-ipp-start-parity-candidate" / "RUNTIME-CSID1-0042-DMESG.txt",
    "0043": E003 / "e003h-csid1-prepare-rup-enable-parity-candidate" / "RUNTIME-CSID1-0043-DMESG.txt",
    "0044": E003 / "e003h-csid1-common-lifecycle-0044-candidate" / "RUNTIME-CSID1-0044-DMESG.txt",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def require(cond, msg):
    if not cond:
        raise SystemExit(f"FAIL: {msg}")


for name, path in PATHS.items():
    require(path.is_file(), f"missing {name}: {path}")
    require(sha256(path) == EXPECTED[name], f"hash drift for {name}")

derived = load_json(PATHS["derived"])
initial = load_json(PATHS["initial"])
steady = load_json(PATHS["steady"])
csid_order = load_json(PATHS["csid_order"])

facts = derived["facts"]
require(derived["source"]["sha256"] ==
        "64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c",
        "qccamisp source identity drift")
require(facts["special_bl_before_descriptor_loop"] is True,
        "Windows pre-descriptor BL no longer proven")
require(facts["special_bl_bytes"] == 4 and facts["special_bl_length_minus_1"] == 3,
        "Windows pre-descriptor BL size drift")
require(facts["special_bl_uses_ife_cdm_handle_at_ctx_plus_0x98"] is True,
        "Windows special BL CDM handle ownership drift")
require(facts["ordinary_descriptor_length_minus_1"] == "descriptor_length - 1",
        "ordinary descriptor BL semantics drift")

cdm = initial["cdm_decode"]
require(cdm["change_base_commands"] == 0, "startup main unexpectedly contains CHANGE_BASE")
require(cdm["current_base_proven_by_windows_mmio_crosscheck"] == "0x0ac71000 (VFE1)",
        "startup main Windows base proof drift")
require(cdm["base_crosscheck"]["packet3_plus_0x90"] == "0x00000001",
        "packet3 +0x90 signature drift")
require(cdm["base_crosscheck"]["route_oracle_live_plus_0x90"] == "0x00000001",
        "VFE1 live +0x90 crosscheck drift")

word = 0x0800F000
word_sha = hashlib.sha256(struct.pack("<I", word)).hexdigest()
steady_sha = steady["steady_companion_bls"]["bl0_change_base_sha256"]
require(word_sha == steady_sha,
        "0x0800f000 no longer byte-identical to captured Windows VFE1 CHANGE_BASE BL0")
require(any(v["lengths"][0] == "0x4" for v in steady["capture"]["steady_vector_counts"]),
        "steady four-byte BL0 shape drift")
require(csid_order["accepted"] is True, "CSID prepare/RUP/enable oracle not accepted")

mask_re = re.compile(r"epoch0-timeout .*?buf=[0-9a-fA-F]{8}/([0-9a-fA-F]{8})")
masks = {}
for run in ("0042", "0043", "0044"):
    text = PATHS[run].read_text(errors="replace")
    m = mask_re.search(text)
    require(m is not None, f"missing {run} timeout BUF_DONE mask")
    masks[run] = "0x" + m.group(1).lower()
require(masks == {"0042": "0x0001ffff", "0043": "0x00000001", "0044": "0x00000001"},
        f"Linux mask differential drift: {masks}")

out = {
    "schema": "sp11-e003h-windows-ife-startup-base-wrapper-oracle-v1",
    "accepted": True,
    "classification": {
        "special_wrapper_presence_order_size": "WINDOWS_REVERSED",
        "startup_main_active_base_vfe1": "WINDOWS_OBSERVED_CROSSCHECK",
        "exact_wrapper_word_0x0800f000":
            "WINDOWS_REVERSED_PLUS_INDEPENDENT_WINDOWS_BL_BYTE_IDENTITY",
        "linux_0042_0043_0044_mask_differential": "LINUX_OBSERVED",
    },
    "windows_queue_contract": {
        "dal_ife_process_iq_packet_rva": "0x26838",
        "add_bl_helper_rva": "0x22200",
        "ife_cdm_handle_context_offset": "0x98",
        "pre_descriptor_bl_bytes": 4,
        "pre_descriptor_bl_length_minus_one": 3,
        "ordinary_descriptor_bl_rule": "descriptor_length_minus_one",
        "startup_main_change_base_command_count": 0,
        "startup_main_active_base": "VFE1 0x0ac71000",
    },
    "wrapper_command": {
        "cdm_word": "0x0800f000",
        "semantic": "CHANGE_BASE 0x0000f000 -> VFE1 0x0ac71000",
        "little_endian_sha256": word_sha,
        "captured_windows_steady_bl0_sha256": steady_sha,
        "byte_identity_to_captured_windows_bl0": True,
        "raw_startup_kmd_word_directly_captured": False,
        "basis": [
            "Windows queues exactly one four-byte KMD BL before ordinary IFE startup descriptor BLs",
            "captured startup main BLs contain zero CHANGE_BASE commands",
            "same-machine Windows MMIO proves startup main BLs execute VFE1-relative",
            "the exact little-endian 0x0800f000 word hashes identically to an independently captured same-machine Windows four-byte VFE1 CHANGE_BASE BL0",
            "hardware RT-CDM FIFO metadata has no per-client target register-base selector",
        ],
    },
    "linux_failure_prediction": {
        "packet3_vfe_relative_offset_0x90_value": "0x00000001",
        "0042_timeout_buf_done_mask": masks["0042"],
        "0043_timeout_buf_done_mask": masks["0043"],
        "0044_timeout_buf_done_mask": masks["0044"],
        "0042_hide_mechanism":
            "0042 rewrote Windows CSID masks late after startup2/startup3, hiding an earlier mis-based +0x90=1 write",
        "0043_reveal_mechanism":
            "0043 moved CSID prepare/masks before startup2/startup3; packet3 then leaves +0x90=1 visible if the VFE1 CHANGE_BASE wrapper is omitted",
        "bare_startup_submission_is_invalid": True,
    },
    "linux_consequence": {
        "required_native_change":
            "prepend a Linux-owned four-byte 0x0800f000 CHANGE_BASE BL before each startup main packet 0..3",
        "do_not_modify":
            "captured startup main packet bytes, selector-2 priming batches, CSID companions or steady Epoch0 batch structure",
        "do_not_add": "speculative late CSID BUF_DONE mask repair",
        "runtime_authorized": False,
    },
    "source_evidence": {
        "derived_windows_disassembly": {
            "path": str(PATHS["derived"].relative_to(HERE.parent.parent.parent.parent)),
            "sha256": EXPECTED["derived"],
            "driver_sha256": derived["source"]["sha256"],
        },
        "initial_ife_cdm_summary_sha256": EXPECTED["initial"],
        "steady_batch_oracle_sha256": EXPECTED["steady"],
        "windows_csid_prepare_order_sha256": EXPECTED["csid_order"],
        "linux_runtime_0042_dmesg_sha256": EXPECTED["0042"],
        "linux_runtime_0043_dmesg_sha256": EXPECTED["0043"],
        "linux_runtime_0044_dmesg_sha256": EXPECTED["0044"],
    },
}

out_path = HERE / "windows-ife-startup-base-wrapper-oracle.json"
out_path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
print(json.dumps(out, indent=2, sort_keys=True))
print("ORACLE_SHA256=" + sha256(out_path))
