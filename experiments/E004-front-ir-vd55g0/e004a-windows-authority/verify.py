#!/usr/bin/env python3
from pathlib import Path
import hashlib
import json
import re
import struct
import sys

D = Path(__file__).resolve().parent
REPO = D.parents[2]
SP11_ROOT = REPO.parents[1]
sys.path.insert(0, str(D))
from extract_windows_vd55g0 import extract as extract_windows, extract_patch_bytes

PKG = SP11_ROOT / "00-RE-archive/sp11-driverdump/surfacecamauxsensor_extension8380.inf_arm64_84ddd55dc933cac9/com.surface.sensormodule.aux_vd55g0_MSHW0492.bin"
MIPI_SYS = SP11_ROOT / "00-RE-archive/sp11-driverdump/qccammipicsi8380.inf_arm64_9b873143bb427aef/qccammipicsi8380.sys"
AUX_SYS = SP11_ROOT / "00-RE-archive/sp11-driverdump/surfacecamauxsensor8380.inf_arm64_7d23cd8fdfa9b39f/surfacecamauxsensor8380.sys"

EXPECTED = {
    "package_sha256": "e574db7eb28231d3fa4f5eee5c1861919125d8ec7a753fc7a0708606e1f1a794",
    "mipi_sys_sha256": "033f5b1431ad4c76a12ac3b7f0a5be42e460a03bcff40d249511b3034786d407",
    "aux_sys_sha256": "e5b6b064f39cf239ab07e22ca2434e3c08c93b691dc7d27cebb90861226efa75",
    "patch_sha256": "5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321",
    "packet_sha256": "81e96e0470cbfa58065eba12ea1a998349b306111f2edee296d7044a69146cdd",
    "logs": {
        "E004_IR_MIPI_CONTEXT_20260912.log": "97b6f23898d8d4d5ba1ef840fc0da0fbbfb787145dc1531e5b1b216dd1f658ca",
        "E004_IR_LIVE_20260912.log": "add3797f0592203ee18c18d00d3f330f91f0ee183dd0d9bd07cf0b4aa9bd1279",
        "E004_IR_LIVE2_20260912.log": "22e785474bd6857af52ab50a2039e8488a3328cbd8bf4a66a69d6e2d6fe2ac9d",
        "E004_IR_IDLE_20260912.log": "ac754900942c7ccfe16dbbd0e231a766ed3a2f5cd3377707d189a9512ff21424",
        "E004_IR_COLDBOOT2_20260912.log": "b912fbf3635edac0ab22b37b1d7f485ad822ca5a71373a4754ee547c50b5aa5d",
    },
}


def need(value, message):
    if not value:
        raise AssertionError(message)


def sha(path: Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def parse_kd_dwords(path: Path):
    out = {}
    rx = re.compile(
        r"^([0-9a-fA-F]{8})\x60([0-9a-fA-F]{8})\s+"
        r"([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})\s+"
        r"([0-9a-fA-F]{8})\s+([0-9a-fA-F]{8})"
    )
    for line in path.read_text(errors="replace").splitlines():
        m = rx.match(line)
        if not m:
            continue
        address = int(m.group(1) + m.group(2), 16)
        for index in range(4):
            out[address + index * 4] = int(m.group(3 + index), 16)
    return out


def pe_rva_to_offset(image: bytes, rva: int) -> int:
    pe = struct.unpack_from("<I", image, 0x3C)[0]
    need(image[pe : pe + 4] == b"PE\0\0", "PE signature")
    number_of_sections = struct.unpack_from("<H", image, pe + 6)[0]
    optional_size = struct.unpack_from("<H", image, pe + 20)[0]
    section_table = pe + 24 + optional_size
    for index in range(number_of_sections):
        off = section_table + index * 40
        virtual_size, virtual_address, raw_size, raw_ptr = struct.unpack_from("<IIII", image, off + 8)
        if virtual_address <= rva < virtual_address + max(virtual_size, raw_size):
            return raw_ptr + (rva - virtual_address)
    raise AssertionError(f"RVA 0x{rva:x} not mapped")


def pe_u32(image: bytes, rva: int) -> int:
    return struct.unpack_from("<I", image, pe_rva_to_offset(image, rva))[0]


def movz_w_imm16(word: int):
    # MOVZ Wd,#imm16,LSL #0 has fixed mask 0x7f800000 == 0x52800000.
    need((word & 0x7F800000) == 0x52800000, f"not MOVZ-W: 0x{word:08x}")
    shift = (word >> 21) & 0x3
    need(shift == 0, "unexpected MOVZ shift")
    return (word >> 5) & 0xFFFF, word & 0x1F


def parse_mipi_context(path: Path):
    text = path.read_text(errors="replace")
    need("===E004_MIPI_6028_HIT===" in text, "MIPI breakpoint marker")
    match = re.search(r"x0=([0-9a-fA-F]+)", text)
    need(match, "MIPI context pointer")
    base = int(match.group(1), 16)
    dwords = parse_kd_dwords(path)
    return base, dwords


def parse_csiphy_pair(live1: Path, live2: Path, idle: Path):
    a = parse_kd_dwords(live1)
    b = parse_kd_dwords(live2)
    c = parse_kd_dwords(idle)
    base = 0x0ACE4000
    keys = [base + 4 * i for i in range(2048)]
    need(all(k in a for k in keys), "live1 full 8 KiB CSIPHY0 aperture")
    need(all(k in b for k in keys), "live2 full 8 KiB CSIPHY0 aperture")
    need(all(k in c for k in keys), "idle full 8 KiB CSIPHY0 aperture")
    differences = [(k, a[k], b[k]) for k in keys if a[k] != b[k]]
    idle_sentinel = sum(c[k] == 0x80000000 for k in keys)
    return differences, idle_sentinel


def packet_patch(packet: bytes):
    need(len(packet) == 0x1310, "captured Windows sequential packet length")
    patch = bytearray()
    for index, address in enumerate(range(0x2000, 0x2228)):
        off = 0x1C + 8 * index
        got_address, data = struct.unpack_from("<II", packet, off)
        need(got_address == address, f"live patch address {index}: 0x{got_address:04x}")
        need(data <= 0xFF, f"live patch byte width at 0x{address:04x}")
        patch.append(data)
    return bytes(patch)


def main():
    authority = json.load(open(D / "WINDOWS-AUTHORITY.json"))
    result = json.load(open(D / "RESULT.json"))
    oracle = json.load(open(D / "E004_WINDOWS_ORACLE_SUMMARY_20260912.json"))

    # Pin exact Surface Windows inputs.
    need(PKG.is_file() and sha(PKG) == EXPECTED["package_sha256"], "exact Surface VD55G0 package")
    need(MIPI_SYS.is_file() and sha(MIPI_SYS) == EXPECTED["mipi_sys_sha256"], "exact QTI MIPI driver")
    need(AUX_SYS.is_file() and sha(AUX_SYS) == EXPECTED["aux_sys_sha256"], "exact Surface aux-sensor driver")

    # Derive timing and patch facts mechanically from the exact Windows sensor package.
    extracted = extract_windows(PKG)
    vals = extracted["decoded_register_values"]
    need(extracted["source_size"] == 136411, "Windows package size")
    need(extracted["largest_regsetting_count"] == 601, "Windows largest init regSetting count")
    need(vals["0x0220_le32"] == 19_200_000, "Windows ext clock")
    need(vals["0x0224_le32"] == 840_000_000, "Windows MIPI data rate")
    need(vals["0x0300_le16"] == 1200, "Windows line length")
    need(vals["0x0458_le16"] == 1955, "Windows frame length")
    static_patch = extract_patch_bytes(PKG)
    need(len(static_patch) == 552 and sha_bytes(static_patch) == EXPECTED["patch_sha256"], "Windows package patch")

    # Pin and parse the raw KD evidence copied byte-exact from SP7.
    for name, expected_hash in EXPECTED["logs"].items():
        need(sha(D / name) == expected_hash, "raw KD evidence hash: " + name)

    # Real Windows MIPI context at qccammipicsi8380+0x6028.
    mipi_base, mipi = parse_mipi_context(D / "E004_IR_MIPI_CONTEXT_20260912.log")
    need((mipi[mipi_base] & 0xFF) == 1, "Windows nNumOfDataLane == 1")
    need(mipi[mipi_base + 0x14] == 0x10, "Windows DPHY settle count 0x10")
    need(mipi[mipi_base + 0x18] == 840_000_000, "Windows live MIPI rate")
    need(mipi[mipi_base + 0x4C] == 0 and mipi[mipi_base + 0x54] == 0, "observed MIPI branch selectors")

    # Prove the installed QTI driver's D-PHY lane-mask family from exact ARM64 PE code.
    mipi_image = MIPI_SYS.read_bytes()
    strings = [
        b"CSIPhyRxLane pMipiCsiCtx->nNumOfDataLane = %d laneMask =%0x lanemaskofpreviouslane =%0x",
        b"CSIPhyWaitforRx Failed, Lane0Status = 0x%x, Lane2Status = 0x%x,Lane4Status = 0x%x, Lane6Status = 0x%x, ClkStatus = 0x%x",
        b"RecommendedSettleCount for DPHY DataRate = %d Mbps, SettleCount = 0x%08x",
    ]
    for token in strings:
        need(token in mipi_image, "QTI MIPI evidence string: " + token.decode())
    # The +0x4c=0/+0x54=0 D-PHY branch compares lane count 1/2/4,
    # then loads 0x81/0x85/0xd5 respectively at these RVAs.
    expected_code = {
        0x6844: 0x394002A2,  # ldrb w2,[x21]
        0x6848: 0x7100045F,  # cmp w2,#1
        0x6850: 0x7100085F,  # cmp w2,#2
        0x6858: 0x7100105F,  # cmp w2,#4
    }
    for rva, word in expected_code.items():
        need(pe_u32(mipi_image, rva) == word, f"QTI lane-count instruction RVA 0x{rva:x}")
    masks = {}
    for lanes, rva in ((4, 0x6860), (2, 0x6868), (1, 0x6870)):
        imm, reg = movz_w_imm16(pe_u32(mipi_image, rva))
        need(reg == 19, f"lane mask destination W19 at RVA 0x{rva:x}")
        masks[lanes] = imm
    need(masks == {1: 0x81, 2: 0x85, 4: 0xD5}, "QTI DPHY lane-mask family")
    # 0x81 = bit7 (Clk) + bit0 (first named data status Lane0).
    need((masks[1] & 0x81) == 0x81 and (masks[1] & ~0x81) == 0, "one-lane mask is Clk + Lane0")
    need((masks[2] ^ masks[1]) == 0x04 and (masks[4] ^ masks[2]) == 0x50, "lane-mask growth 1->2->4")

    # Full Windows CSIPHY0 live/idle receiver evidence.
    diffs, idle_sentinel = parse_csiphy_pair(
        D / "E004_IR_LIVE_20260912.log",
        D / "E004_IR_LIVE2_20260912.log",
        D / "E004_IR_IDLE_20260912.log",
    )
    need(len(diffs) == 1, "two live CSIPHY0 snapshots differ at one dword")
    need(diffs[0] == (0x0ACE4EF4, 0xC1, 0xC0), "expected live status-only delta")
    need(idle_sentinel == 2048, "idle CSIPHY0 is fully inaccessible sentinel")

    # The actual first-start Windows packet must carry the exact Surface patch.
    packet_path = D / "E004_IR_4C74_PACKET_20260912.bin"
    packet = packet_path.read_bytes()
    need(sha(packet_path) == EXPECTED["packet_sha256"], "cold-boot live InitialConfig packet hash")
    live_patch = packet_patch(packet)
    need(sha_bytes(live_patch) == EXPECTED["patch_sha256"], "live Windows patch hash")
    need(live_patch == static_patch, "live Windows patch equals exact Surface package patch")
    cold_text = (D / "E004_IR_COLDBOOT2_20260912.log").read_text(errors="replace")
    need("===E004_SEQ_4C20_INITIALCONFIG===" in cold_text, "cold InitialConfig marker")
    need("===E004_SEQ_4C74===" in cold_text and "LEN=1310" in cold_text, "cold 0x1310 sequential packet marker")

    # Cross-check machine-readable oracle generated from the raw evidence.
    need(oracle["mipi"]["lane_count"] == 1, "oracle lane count")
    need(oracle["mipi"]["data_rate_bps"] == 840_000_000, "oracle data rate")
    need(oracle["mipi"]["settle_count"] == 0x10, "oracle settle")
    need(oracle["mipi"]["lane_mask"] == "0x81", "oracle lane mask")
    need(oracle["mipi"]["polarity_inversion_proven"] is False, "do not invent polarity inversion")
    need(oracle["first_ir_initial_config"]["patch_sha256"] == EXPECTED["patch_sha256"], "oracle patch")
    need(oracle["csiphy0"]["live_diff_count"] == 1, "oracle CSIPHY reproducibility")
    need(oracle["windows_driver_hashes"]["qccammipicsi8380"] == EXPECTED["mipi_sys_sha256"], "oracle MIPI driver hash")
    need(oracle["windows_driver_hashes"]["surfacecamauxsensor8380"] == EXPECTED["aux_sys_sha256"], "oracle aux driver hash")

    # Published authority/result must match what was mechanically proven.
    need(authority["sensor_package_sha256"] == EXPECTED["package_sha256"], "authority package hash")
    need(authority["routing"]["csiphy_index"] == 0, "CSIPHY0")
    need(authority["routing"]["windows_lane_mask"] == "0x81", "authority lane mask")
    need(authority["routing"]["physical_data_lane_mapping"] == "Lane0", "authority Windows physical lane")
    need(authority["routing"]["lane_polarity"] == "NO_INVERSION_PROVEN", "authority polarity wording")
    mode = authority["mode"]
    need((mode["width"], mode["height"], mode["raw_bits"], mode["virtual_channel"]) == (644, 604, 10, 0), "mode")
    need(mode["mipi_data_rate_bps"] == 840_000_000 and mode["windows_observed_data_lanes"] == 1, "Windows transport")
    need(mode["derived_link_frequency_hz"] == 420_000_000, "D-PHY DDR link frequency")
    need(mode["mipi_data_rate_bps"] // mode["raw_bits"] == mode["output_pixel_clock_hz"] == 84_000_000, "pixel-rate relationship")
    need(authority["windows_first_ir_start"]["patch_transmitted"] is True, "Windows patch transmission recorded")
    need(authority["windows_first_ir_start"]["patch_sha256"] == EXPECTED["patch_sha256"], "authority live patch")
    need(authority["illumination_authorized"] is False, "illumination remains disabled")
    need(authority["linux_live_probe_performed"] is False and authority["linux_stream_performed"] is False, "Linux remains untouched")

    need(result["status"] == "PASS_WINDOWS_ORACLE_VD55G0_AUTHORITY_NO_LINUX_PROBE", "result status")
    need(result["windows_camera_runtime_performed"] is True, "Windows oracle runtime recorded")
    need(result["linux_probe_performed"] is False and result["linux_stream_performed"] is False, "no Linux runtime")
    need(result["windows_first_start_patch_policy"] == "RESOLVED_FOR_THIS_SP11", "patch policy result")
    need(result["windows_physical_lane_mapping"] == "Lane0+Clk / laneMask 0x81", "lane mapping result")

    print("E004A_VERIFY=PASS AUTHORITY=WINDOWS_ONLY SENSOR=VD55G0 I2C=0x60 DPHY=1LANE LANEMASK=0x81 LINK=420MHz")
    print("E004A_PATCH=PASS SOURCE_PACKAGE=552B LIVE_WINDOWS_PACKET=552B SHA256=" + EXPECTED["patch_sha256"])
    print("E004A_CSIPHY0=PASS LIVE_DWORDS=2048 REPEAT_DIFFS=1 IDLE_SENTINELS=2048")
    print("E004A_SAFETY=PASS LINUX_PROBE=NO LINUX_STREAM=NO ILLUMINATION=NO")


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


if __name__ == "__main__":
    main()
