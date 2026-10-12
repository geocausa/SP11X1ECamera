#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compare the owned disabled CSID plan with unchanged GPL decoder/config code."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import tempfile


def verified(root, manifest):
    sources = {}
    for pin in manifest["files"]:
        rel = Path(pin["path"])
        if rel.is_absolute() or ".." in rel.parts: raise ValueError("invalid reference path")
        path = root / rel
        if not path.is_file() or any(p.is_symlink() for p in [root, path, *path.parents]):
            raise ValueError("invalid reference file")
        raw = path.read_bytes()
        blob = hashlib.sha1(("blob " + str(len(raw)) + "\0").encode() + raw).hexdigest()
        if (len(raw) != pin["bytes"] or hashlib.sha256(raw).hexdigest() != pin["sha256"]
                or blob != pin["git_blob_sha1"]):
            raise ValueError("reference identity differs")
        if rel.name in sources: raise ValueError("duplicate reference name")
        sources[rel.name] = raw.decode()
    if len(sources) != 6: raise ValueError("incomplete reference")
    return sources


def balanced(text, start):
    begin = text.index("{", start)
    depth, end = 1, begin + 1
    while depth:
        depth += (text[end] == "{") - (text[end] == "}")
        end += 1
    return text[start:end]


def function(text, name):
    match = re.search(r"(?:static\s+)?(?:int|bool)\s+" + name + r"\s*\(", text)
    if not match: raise ValueError("public function missing: " + name)
    return balanced(text, match.start())


def reference_header(sources):
    common = sources["cam_ife_csid_common.c"]
    driver = sources["cam_ife_csid_hw_ver2.c"]
    hw = sources["cam_ife_csid680.h"]
    defs = sources["cam_defs.h"]
    names = ["cam_ife_csid_ver2_disable_sof_retime",
             "cam_ife_csid_ver2_program_init_cfg1_pxl_path",
             "cam_ife_csid_ver2_init_config_pxl_path"]
    functions = [function(driver, name) for name in names]
    decoder = function(common, "cam_ife_csid_get_format_ipp_ppp")
    code = "\n".join(functions)
    fields = {var: sorted(set(re.findall(var + r"->(\w+)", code)))
              for var in ("cmn_reg", "path_reg")}
    cmn_name = re.search(r"\.cmn_reg\s*=\s*&(\w+)", hw).group(1)
    blocks = {}
    for key, name in (("cmn_reg", cmn_name), ("path_reg", "cam_ife_csid_680_ipp_reg_info")):
        start = re.search(r"\b" + name + r"\s*=\s*\{", hw).start()
        blocks[key] = balanced(hw, start)
    values = {}
    for key, block in blocks.items():
        values[key] = {}
        for field in fields[key]:
            match = re.search(r"\." + field + r"\s*=\s*([^,\n]+)", block)
            # Absent members of a static C initializer are zero.
            values[key][field] = match.group(1).strip() if match else "0"
    required = set(re.findall(r"\bCAM_FORMAT_[A-Z0-9_]+\b", decoder))
    macro_defs = dict(re.findall(r"^#define\s+(\w+)\s+([^\n]+)", defs + "\n" +
                                sources["cam_ife_csid_common.h"], re.M))
    required |= set(re.findall(r"\bCAM_IFE_CSID_[A-Z0-9_]+\b", code))
    required -= {"CAM_IFE_CSID_CLC_MEM_BASE_ID", "CAM_IFE_CSID_MULTI_VC_DT_GRP_0",
                 "CAM_IFE_CSID_MULTI_VC_DT_GRP_1"}
    for table in values.values():
        for expr in table.values(): required |= set(re.findall(r"\bCAM_[A-Z0-9_]+\b", expr))
    macro_text = ""
    for name in sorted(required):
        if name not in macro_defs: raise ValueError("public constant missing: " + name)
        expr = macro_defs[name].split("/*", 1)[0].strip()
        if "\\" in expr: raise ValueError("unsupported multiline constant")
        macro_text += f"#define {name} {expr}\n"
    scalar_structs = ""
    scalar_init = ""
    for key, typename in (("cmn_reg", "cam_ife_csid_ver2_common_reg_info"),
                          ("path_reg", "cam_ife_csid_ver2_path_reg_info")):
        scalar_structs += "struct " + typename + " { " + "; ".join("u32 " + f for f in fields[key]) + "; };\n"
        var = "public_common" if key == "cmn_reg" else "public_path"
        scalar_init += "static struct " + typename + " " + var + " = {\n" + ",\n".join(
            "." + f + "=" + values[key][f] for f in fields[key]) + "\n};\n"
    path_format_fields = sorted(set(re.findall(r"path_format->(\w+)", decoder)))
    format_struct = "struct cam_ife_csid_path_format { " + "; ".join("u32 " + f for f in path_format_fields) + "; };\n"
    # Test-only resource IDs/indexes and structure adapters are not hardware ABI.
    glue = r'''
#define __iomem
#define BIT(n) (1U << (n))
#define CAM_DBG(...) ((void)0)
#define CAM_ERR(...) ((void)0)
#define CAM_IFE_CSID_CLC_MEM_BASE_ID 0
#define CAM_IFE_CSID_MULTI_VC_DT_GRP_0 0
#define CAM_IFE_CSID_MULTI_VC_DT_GRP_1 1
#define CAM_IFE_PIX_PATH_RES_PPP 1
#define CAM_ISP_RESOURCE_STATE_INIT_HW 1
'''
    adapters = r'''
struct cam_ife_csid_ver2_path_cfg {
    u32 cid, crop_enable, drop_enable, frame_id_dec_en, horizontal_bin, qcfa_bin,
        vertical_bin, vfr_en, ts_comb_vcdt_en, sfe_shdr, lcr_en;
    struct cam_ife_csid_path_format path_format[2];
};
struct cam_ife_csid_ver2_reg_info {
    struct cam_ife_csid_ver2_common_reg_info *cmn_reg;
    struct cam_ife_csid_ver2_path_reg_info *path_reg[1];
    void *ipp_mc_reg;
};
struct cam_hw_soc_info { void *soc_private; struct {void *mem_base;} reg_map[1]; };
struct cam_csid_soc_private { int unused; };
struct cam_ife_csid_cid_data { struct {u32 vc, dt, valid;} vc_dt[2]; };
struct public_hw_info { struct cam_hw_soc_info soc_info; };
struct public_core_info { void *csid_reg; };
struct cam_ife_csid_ver2_hw {
    struct public_hw_info *hw_info;
    struct public_core_info *core_info;
    struct cam_ife_csid_cid_data cid_data[4];
    struct {u32 binning_enabled, rdi_lcr_en;} flags;
    struct {u32 debug_val;} debug_info;
};
struct cam_isp_resource_node { u32 res_id, res_state; void *res_priv; };
static u8 public_mmio[1024];
static u32 public_mmio_words[256], public_mmio_first[256];
static bool public_mmio_seen[256];
static u32 public_reg_index(const void *address) {
    size_t offset = (unsigned long)address - (unsigned long)public_mmio;
    assert(offset < sizeof(public_mmio) && !(offset & 3)); return (u32)(offset / 4);
}
static void cam_io_w_mb(u32 value, void *address) {
    u32 index = public_reg_index(address);
    if (!public_mmio_seen[index]) public_mmio_first[index] = value;
    public_mmio_seen[index] = true; public_mmio_words[index] = value;
}
static u32 cam_io_r_mb(const void *address) {return public_mmio_words[public_reg_index(address)];}
static void cam_ife_csid_ver2_res_master_slave_cfg(struct cam_ife_csid_ver2_hw *hw, u32 id) {
    (void)hw; (void)id; assert(!"unsupported HDR reference fixture");
}
struct public_csid_words {u32 cfg0_before_enable, cfg1;};
'''
    wrapper = r'''
static struct public_csid_words public_csid_ipp(u32 vc, u32 id) {
    struct cam_ife_csid_ver2_path_cfg cfg = {.cid=id};
    struct cam_ife_csid_ver2_reg_info reg = {.cmn_reg=&public_common, .path_reg={&public_path}};
    struct public_core_info core = {.csid_reg=&reg};
    struct public_hw_info info = {.soc_info={.reg_map={{public_mmio}}}};
    struct cam_ife_csid_ver2_hw hw = {.core_info=&core, .hw_info=&info};
    struct cam_isp_resource_node res = {.res_priv=&cfg};
    hw.cid_data[id].vc_dt[0].vc = vc; hw.cid_data[id].vc_dt[0].dt = 0x2b;
    assert(!cam_ife_csid_get_format_ipp_ppp(CAM_FORMAT_MIPI_RAW_10, &cfg.path_format[0]));
    assert(cfg.path_format[0].decode_fmt == 2 && cfg.path_format[0].plain_fmt == 1);
    memset(public_mmio_words, 0, sizeof(public_mmio_words));
    memset(public_mmio_first, 0, sizeof(public_mmio_first));
    memset(public_mmio_seen, 0, sizeof(public_mmio_seen));
    assert(!cam_ife_csid_ver2_init_config_pxl_path(&hw, &res));
    assert(public_mmio_seen[public_path.cfg0_addr/4] && public_mmio_seen[public_path.cfg1_addr/4]);
    assert(public_mmio_words[public_path.cfg0_addr/4] & BIT(public_common.path_en_shift_val));
    return (struct public_csid_words){public_mmio_first[public_path.cfg0_addr/4],
                                     public_mmio_words[public_path.cfg1_addr/4]};
}
'''
    offsets = ["cfg0_addr", "multi_vcdt_cfg0_addr", "cfg1_addr", "frm_drop_pattern_addr",
               "frm_drop_period_addr", "irq_subsample_pattern_addr", "irq_subsample_period_addr"]
    addresses = []
    for name in offsets:
        addresses.append(int(re.search(r"\." + name + r"\s*=\s*(0x[0-9a-fA-F]+)", blocks["path_reg"]).group(1), 16))
    address_text = "static const u32 public_ipp_offsets[7] = {" + ",".join(hex(a) for a in addresses) + "};\n"
    copyright = common[:common.index("#include")]
    # The unchanged public function has an unused soc_private assignment.
    # Suppress that reference-only diagnostic, keeping our production code strict.
    warning = '#pragma GCC diagnostic push\n#pragma GCC diagnostic ignored "-Wunused-but-set-variable"\n'
    return (copyright + glue + macro_text + scalar_structs + format_struct + adapters + scalar_init +
            decoder + "\n" + warning + code + '\n#pragma GCC diagnostic pop\n' + wrapper + address_text)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference-dir", required=True, type=Path)
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    manifest = json.loads((here / "csid680-ipp-reference-20261012.json").read_text())
    sources = verified(args.reference_dir, manifest)
    reference = reference_header(sources)
    results = []
    with tempfile.TemporaryDirectory(prefix="sp11-csid680-ipp-") as directory:
        tmp = Path(directory)
        (tmp / "csid-reference.h").write_text(reference)
        rejected = 0
        for mode in ("changed", "missing", "symlink"):
            root = tmp / mode; root.mkdir()
            for i, pin in enumerate(manifest["files"]):
                path = root / pin["path"]; path.parent.mkdir(parents=True, exist_ok=True)
                if i == 0 and mode == "missing": continue
                if i == 0 and mode == "symlink": path.symlink_to((args.reference_dir / pin["path"]).resolve())
                else: path.write_text(sources[Path(pin["path"]).name] + ("\n" if i == 0 and mode == "changed" else ""))
            try: verified(root, manifest)
            except ValueError: rejected += 1
            else: raise ValueError("pin rejection failed")
        for cc in ("gcc", "clang"):
            if not shutil.which(cc): raise RuntimeError("compiler missing: " + cc)
            exe = tmp / cc
            subprocess.run([cc, "-std=c11", "-O1", "-g", "-Wall", "-Wextra", "-Werror",
                            "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-I", str(tmp),
                            str(here / "test-csid680-ipp.c"), "-o", str(exe)],
                           check=True, capture_output=True, text=True)
            run = subprocess.run([str(exe)], check=True, capture_output=True, text=True)
            results.append({"compiler": cc, "status": "PASS", "asan": True, "ubsan": True,
                            "detail": run.stdout.strip(), "actual_public_functions_compiled": 4})
    hashes = {name: hashlib.sha256((here / name).read_bytes()).hexdigest()
              for name in ["sp11-csid680-ipp.h", "sp11-cdm.h"]}
    print(json.dumps({"schema": "sp11-csid680-ipp-tests-v1", "tests": results,
                      "public_source_files_verified": 6, "reference_pin_rejections": rejected,
                      "production_header_sha256": hashes, "register_writes": 7,
                      "target": "CSID680_IPP_ONLY", "private_input_read": False,
                      "hardware_access": False, "path_enabled": False,
                      "complete_startup_provider": False, "runtime_dependencies_removed": False}, indent=2))


if __name__ == "__main__":
    try: main()
    except subprocess.CalledProcessError as error:
        print(error.stderr or error.stdout)
        raise
