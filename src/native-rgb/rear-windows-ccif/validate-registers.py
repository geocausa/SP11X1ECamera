#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Validate named read-only CSR probes against the retained exact GPL VFE680 layout."""
import argparse, copy, hashlib, json, re
from pathlib import Path

HEADER = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/qcom-camera-kernel-KleeUI/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe17x/cam_vfe680.h")
HERE = Path(__file__).resolve().parent
MODULE_AUDIT = HERE.parents[2] / "docs/NATIVE-RGB-REAR-SPARSE-REGISTER-SOURCE-AUDIT-20261008.json"
MODULE_AUDIT_SHA = "78cf38ccd5263820e296b087d7ce2db58a33ee8659576169543c81e3089b031d"
MODULE_DLL = Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll")
MODULE_DLL_SHA = "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
MODULE_CONTROL_MAP = {"sparse_pd": {"cfg0": 0x6960}, "lcr": {"cfg0": 0x6b60}}

WM_FIELDS = {"cfg", "frame_incr", "image_cfg_0", "image_cfg_1", "image_cfg_2",
             "packer_cfg", "frame_header_cfg", "irq_subsample_period",
             "irq_subsample_pattern", "framedrop_period", "framedrop_pattern"}
TOP_FIELDS = {"core_cfg_" + str(n) for n in range(7)} | {
    "stats_throttle_cfg_" + str(n) for n in range(3)} | {
    "period_cfg", "irq_sub_pattern_cfg", "epoch0_pattern_cfg",
    "epoch1_pattern_cfg", "epoch_height_cfg", "ipp_violation_status", "pdaf_violation_status"}
BUS_FIELDS = {"ubwc_static_ctrl", "ccif_violation_status",
              "overflow_status", "image_size_violation_status"}

def fields(text):
    return {n: int(v, 16) for n, v in
            re.findall(r"\.(\w+)\s*=\s*(0x[0-9a-fA-F]+)", text)}

def layout(text):
    top = re.search(r"vfe680_top_common_reg\s*=\s*\{(.*?)\n\};", text, re.S)
    bus = re.search(r"vfe680_bus_hw_info\s*=\s*\{\s*\.common_reg\s*=\s*\{(.*?)\.num_client", text, re.S)
    irq = re.search(r"vfe680_bus_irq_reg\[2\]\s*=\s*\{(.*?)\n\};", text, re.S)
    if not all([top, bus, irq]):
        raise ValueError("exact layout anchors missing")
    maps = {"top": fields(top[1]), "bus": fields(bus[1])}
    regs = re.findall(r"\{([^{}]+)\}", irq[1], re.S)
    if len(regs) != 2:
        raise ValueError("IRQ layout drift")
    for n, reg in enumerate(regs):
        f = fields(reg)
        maps["bus"]["irq_mask_" + str(n)] = f["mask_reg_offset"]
        maps["bus"]["irq_status_" + str(n)] = f["status_reg_offset"]
    for n in [0, 1, 2, 3, 20, 23]:
        block = re.search(r"/\* BUS Client " + str(n) +
                          r" [^*]+\*/\s*\{(.*?)\n\s*\},", text, re.S)
        if not block:
            raise ValueError("client layout missing")
        maps["wm" + str(n)] = fields(block[1])
    return maps

def verify(manifest, maps):
    records = manifest["VFE1_registers"]
    seen = set()
    for record in records:
        section, name = record["section"], record["name"]
        offset = int(record["offset"], 16)
        if offset in seen:
            raise ValueError("duplicate read")
        seen.add(offset)
        allowed = TOP_FIELDS if section == "top" else (
            BUS_FIELDS | {"irq_mask_0", "irq_mask_1", "irq_status_0", "irq_status_1"}
            if section == "bus" else WM_FIELDS if section in maps and section.startswith("wm") else set())
        if section in MODULE_CONTROL_MAP:
            allowed = {"cfg0"}
        if name not in allowed or maps.get(section, {}).get(name) != offset:
            raise ValueError("unsupported field, address slot, or offset/name mismatch")
    if manifest["VFE1_offsets"] != [r["offset"] for r in records]:
        raise ValueError("flat whitelist mismatch")
    if manifest["CSID1_offsets"] != ["0x340", "0x344", "0x348"]:
        raise ValueError("CSID scalar scope drift")
    return len(records)

def source_layout(text):
    maps = layout(text)
    audit_raw = MODULE_AUDIT.read_bytes()
    if hashlib.sha256(audit_raw).hexdigest() != MODULE_AUDIT_SHA:
        raise ValueError("module source audit drift")
    audit = json.loads(audit_raw)
    if audit["driver_sha256"] != MODULE_DLL_SHA or hashlib.sha256(MODULE_DLL.read_bytes()).hexdigest() != MODULE_DLL_SHA:
        raise ValueError("same-SP11 module source identity mismatch")
    if audit["SparsePD_subcommand_range"] != [{"register_offset": "0x6960", "register_words": 1}] or audit["LCR_config_ranges"][0] != {"register_offset": "0x6b60", "register_words": 1}:
        raise ValueError("single scalar module control source mismatch")
    maps.update(MODULE_CONTROL_MAP)
    return maps

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", type=Path, default=HERE / "registers.json")
    p.add_argument("--header", type=Path, default=HEADER)
    p.add_argument("--report", type=Path, required=True)
    a = p.parse_args()
    if a.report.exists():
        raise SystemExit("report already exists")
    raw = a.header.read_bytes()
    maps = source_layout(raw.decode())

    manifest = json.loads(a.manifest.read_text())
    count = verify(manifest, maps)
    negatives = 0
    for section, name, offset in [
        ("sparse_pd", "cfg0", "0x6964"),
        ("sparse_pd", "image_addr", "0x6960"),
        ("lcr", "cfg0", "0x6b64"),
        ("bus", "irq_status_0", "0xc18"),
        ("wm20", "frame_header_addr", "0x2220"),
        ("wm23", "image_addr", "0x2504"),
        ("wm20", "meta_cfg", "0x2244"),
        ("wm20", "cfg", "0x2204"),
    ]:
        bad = copy.deepcopy(manifest)
        bad["VFE1_registers"].append({"section": section, "name": name, "offset": offset})
        bad["VFE1_offsets"].append(offset)
        try:
            verify(bad, maps)
        except ValueError:
            negatives += 1
        else:
            raise AssertionError("unsafe probe accepted")
    bad = copy.deepcopy(manifest)
    bad["VFE1_registers"].append(bad["VFE1_registers"][0].copy())
    bad["VFE1_offsets"].append(bad["VFE1_offsets"][0])
    try:
        verify(bad, maps)
    except ValueError:
        negatives += 1
    else:
        raise AssertionError("duplicate accepted")
    report = {"status": "PASS_EXACT_VFE680_NAMED_SCALAR_WHITELIST",
              "VFE_registers": count, "CSID_registers": 3, "negative_cases": negatives,
              "source_sha256": hashlib.sha256(raw).hexdigest(),
              "address_or_clear_command_fields_allowed": False,
              "hardware_access": False,
              "module_source_audit_sha256": MODULE_AUDIT_SHA,
              "module_source_DLL_sha256": MODULE_DLL_SHA,
              "module_scope": "two exact CFG0 control words only"}
    a.report.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report))

if __name__ == "__main__":
    main()
