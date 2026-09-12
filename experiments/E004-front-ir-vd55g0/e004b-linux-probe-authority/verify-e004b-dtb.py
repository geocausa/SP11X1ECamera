#!/usr/bin/env python3
from __future__ import annotations
import hashlib, importlib.util, json, re, subprocess, tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SP11 = REPO.parents[1]
KERNEL = SP11 / "02-kernel/sp11-camera-e002k-d-src"
IB = REPO / "experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ib-unified-current-golden-rear-front-dtb/x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb"
HVB = REPO / "experiments/E003-front-imx681-cphy/e003i-front-native-productionization/hv-current-golden-camera-dtb-merge/build-hv-dtb.py"
BUILDER = HERE / "build-e004b-dtb.py"
OUT = HERE / "x1e80100-microsoft-denali-sp11-e004b-ir-probe.dtb"
AUTH_VERIFY = REPO / "experiments/E004-front-ir-vd55g0/e004a-windows-authority/verify.py"
AUTH_JSON = REPO / "experiments/E004-front-ir-vd55g0/e004a-windows-authority/WINDOWS-AUTHORITY.json"
TRANSLATION = HERE / "LINUX-TRANSLATION.json"

IB_SHA = "5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321"
OUT_SHA = "2b9ff2265606aa95006e3c952597c496367106e00aa1e2d1ec1e75b8f9e485e6"
SOURCE_HASHES = {
    "drivers/regulator/qcom-rpmh-regulator.c": "036a42419906dadc79e5465286923642bc55aa68786448f270e9ed60399634c2",
    "drivers/pinctrl/qcom/pinctrl-x1e80100.c": "e9cb954059a9d182d096c2641b6c42550225aec6048bd6ac70420b689705982b",
    "drivers/i2c/busses/i2c-qcom-cci.c": "b7df5a44d585d0d7c9d8ed7db6353ac5a52e1464200b0d9ff25b6eb9d1af8f6c",
    "include/dt-bindings/clock/qcom,x1e80100-camcc.h": "efd89f72f0d526c93400f62d056394fb837c314d1af778255dacb79278cdd846",
    "include/linux/i2c.h": "f36f4c56bd2d85d314687efcc03a8451d9a4e1ac53b45834030c645672e91867",
}

REGROOT = "/soc@0/rsc@17500000/regulators-8"
TLMM = "/soc@0/pinctrl@f100000"
CCI0 = "/soc@0/cci@ac15000"
I2C0 = CCI0 + "/i2c-bus@0"
CCI_DEF = TLMM + "/cci0-default-state"
CCI_SLEEP = TLMM + "/cci0-sleep-state"
IR_PIN = TLMM + "/front-ir-vd55g0-default-state"
IR = I2C0 + "/camera@60"
IR_EP = IR + "/port/endpoint"
CAMSS = "/soc@0/isp@acb7000"
PORTS = CAMSS + "/ports"
CAM_EP = PORTS + "/port@0/endpoint"
REAR = "/soc@0/cci@ac15000/i2c-bus@1/camera@10"
FRONT = "/soc@0/cci@ac16000/i2c-bus@1/camera@10"

EXPECTED_NEW = {
    REGROOT + "/ldo2", REGROOT + "/ldo4", REGROOT + "/ldo7",
    CCI_DEF + "/cci0-i2c0-pins", CCI_SLEEP + "/cci0-i2c0-pins",
    IR_PIN, IR_PIN + "/mclk-pins", IR_PIN + "/reset-pins",
    IR, IR + "/port", IR_EP, PORTS + "/port@0", CAM_EP,
}
EXPECTED_SYMBOLS = {
    "vreg_l2m_ir": REGROOT + "/ldo2",
    "vreg_l4m_ir": REGROOT + "/ldo4",
    "vreg_l7m_ir": REGROOT + "/ldo7",
    "front_ir_vd55g0_default": IR_PIN,
    "vd55g0_ir": IR,
    "vd55g0_ir_ep": IR_EP,
    "camss_csiphy0_ep": CAM_EP,
}


def need(value, message):
    if not value:
        raise AssertionError(message)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


spec = importlib.util.spec_from_file_location("hv", HVB)
hv = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hv)


def strings(raw):
    return [x.decode() for x in raw.split(b"\0") if x]


def ref_path(tree, n2p, raw):
    vals = hv.u32s(raw)
    need(len(vals) == 1 and vals[0] in n2p, "single phandle reference")
    return n2p[vals[0]]


def seq_ref(tree, n2p, prop, raw):
    vals = hv.u32s(raw)
    cp = hv.seq_cellprop(prop)
    need(cp is not None, "not sequential ref: " + prop)
    out = []
    i = 0
    while i < len(vals):
        ph = vals[i]
        need(ph in n2p, f"{prop}: missing provider {ph:#x}")
        p = n2p[ph]
        count = hv.u32s(tree[p][cp])[0]
        need(i + 1 + count <= len(vals), f"{prop}: truncated")
        out.append((p, tuple(vals[i + 1:i + 1 + count])))
        i += 1 + count
    return out


def normalized_warnings(path):
    with tempfile.TemporaryDirectory(prefix="e004b-dtc-") as td:
        cp = subprocess.run(
            ["dtc", "-I", "dtb", "-O", "dtb", str(path), "-o", str(Path(td) / "x.dtb")],
            text=True, capture_output=True, check=True
        )
    return sorted(line.split(": Warning ", 1)[1] for line in cp.stderr.splitlines() if ": Warning " in line)


def source_checks():
    t = json.load(open(TRANSLATION))
    need(t["parent_unified_dtb_sha256"] == IB_SHA, "translation parent")
    for rel, expected in SOURCE_HASHES.items():
        p = KERNEL / rel
        need(sha(p) == expected, "translation source hash " + rel)
        need(t["kernel_translation_sources"][rel] == expected, "translation JSON hash " + rel)

    reg = (KERNEL / "drivers/regulator/qcom-rpmh-regulator.c").read_text()
    for token in (
        'RPMH_VREG("ldo2",  LDO,  2, &pmic5_nldo502,   "vdd-l1-l2")',
        'RPMH_VREG("ldo4",  LDO,  4, &pmic5_pldo502ln, "vdd-l3-l4")',
        'RPMH_VREG("ldo7",  LDO,  7, &pmic5_pldo502,   "vdd-l7")',
        "REGULATOR_LINEAR_RANGE(528000, 0, 127, 8000)",
        "REGULATOR_LINEAR_RANGE(1800000, 0,  2,  200000)",
        "REGULATOR_LINEAR_RANGE(1504000, 0, 255, 8000)",
    ):
        need(token in reg, "PM8010 translation token: " + token)
    need(528000 + 78 * 8000 == 1_152_000, "LDO2 quantized setpoint")
    need((1_150_000 - 528000) % 8000 != 0, "Windows 1.150V must be unrepresentable")

    pin = (KERNEL / "drivers/pinctrl/qcom/pinctrl-x1e80100.c").read_text()
    for token in (
        "[96] = PINGROUP(96, cam_mclk",
        "[101] = PINGROUP(101, cci_i2c",
        "[102] = PINGROUP(102, cci_i2c",
        "[109] = PINGROUP(109, cci_timer0",
    ):
        need(token in pin, "X1E pin translation " + token)

    hdr = (KERNEL / "include/dt-bindings/clock/qcom,x1e80100-camcc.h").read_text()
    need(re.search(r"#define\s+CAM_CC_MCLK0_CLK\s+71\b", hdr), "MCLK0 clock ID")

    i2c_h = (KERNEL / "include/linux/i2c.h").read_text()
    need(re.search(r"#define\s+I2C_MAX_FAST_MODE_FREQ\s+400000\b", i2c_h), "FAST=400k constant")
    cci = (KERNEL / "drivers/i2c/busses/i2c-qcom-cci.c").read_text()
    need("if (val == I2C_MAX_FAST_MODE_FREQ)" in cci and "master->mode = I2C_MODE_FAST;" in cci, "CCI FAST selection")


def main():
    subprocess.run(["python3", str(AUTH_VERIFY)], check=True, stdout=subprocess.DEVNULL)
    authority = json.load(open(AUTH_JSON))
    need(authority["routing"]["csiphy_index"] == 0, "Windows CSIPHY0")
    need(authority["routing"]["windows_lane_mask"] == "0x81", "Windows lane mask")
    need(authority["routing"]["physical_data_lane_mapping"] == "Lane0", "Windows lane0")
    need(authority["routing"]["lane_polarity"] == "NO_INVERSION_PROVEN", "Windows polarity evidence")
    need(authority["mode"]["mipi_data_rate_bps"] == 840_000_000, "Windows MIPI rate")
    need(authority["power"]["mclk_hz"] == 19_200_000 and authority["power"]["reset_gpio"] == 109, "Windows MCLK/reset")
    source_checks()

    need(sha(IB) == IB_SHA, "IB identity")
    need(sha(OUT) == OUT_SHA, "E004b DTB identity")
    parent = hv.parse_fdt(IB)
    out = hv.parse_fdt(OUT)
    pn, on = set(parent), set(out)
    need(on - pn == EXPECTED_NEW, "exact 13-node addition")
    need(not (pn - on), "parent node removed")
    need((len(parent), len(out)) == (1437, 1450), "node counts")

    # Parent bytes must be unchanged except the intentional FAST rate and new aliases.
    for path in sorted(pn):
        pp, op = parent[path], out[path]
        if path == I2C0:
            need(set(pp) == set(op), "i2c0 property set drift")
            for key, value in pp.items():
                if key == "clock-frequency":
                    continue
                need(op[key] == value, "i2c0 parent drift " + key)
            need(hv.u32s(op["clock-frequency"]) == [400_000], "CCI0 master0 FAST rate")
        elif path == "/__symbols__":
            need(not (set(pp) - set(op)), "parent symbol removed")
            for key, value in pp.items():
                need(op[key] == value, "pre-existing symbol drift " + key)
            need(set(op) - set(pp) == set(EXPECTED_SYMBOLS), "exact symbol additions")
        else:
            need(pp == op, "parent property drift " + path)

    oph, opath = hv.phandle_map(out)
    need(len(oph) == len(set(oph)), "duplicate phandle")
    for name, path in EXPECTED_SYMBOLS.items():
        need(strings(out["/__symbols__"][name]) == [path], "symbol " + name)

    # PM8010 rails and quantization.
    for node, uv, name in (
        (REGROOT + "/ldo2", 1_152_000, "vreg_l2m_ir_1p152"),
        (REGROOT + "/ldo4", 1_800_000, "vreg_l4m_ir_1p8"),
        (REGROOT + "/ldo7", 2_800_000, "vreg_l7m_ir_2p8"),
    ):
        need(strings(out[node]["regulator-name"]) == [name], "rail name " + node)
        need(hv.u32s(out[node]["regulator-min-microvolt"]) == [uv], "rail min " + node)
        need(hv.u32s(out[node]["regulator-max-microvolt"]) == [uv], "rail max " + node)

    # CCI0 master0 pin states; master1 parent bytes were already proven unchanged.
    for node, bias in (
        (CCI_DEF + "/cci0-i2c0-pins", "bias-pull-up"),
        (CCI_SLEEP + "/cci0-i2c0-pins", "bias-pull-down"),
    ):
        need(strings(out[node]["pins"]) == ["gpio101", "gpio102"], "CCI0 master0 pins")
        need(strings(out[node]["function"]) == ["cci_i2c"], "CCI0 master0 mux")
        need(hv.u32s(out[node]["drive-strength"]) == [2], "CCI0 master0 drive")
        need(bias in out[node] and len(out[node][bias]) == 0, "CCI0 master0 bias")

    mclk = IR_PIN + "/mclk-pins"
    need(strings(out[mclk]["pins"]) == ["gpio96"], "MCLK0 pin")
    need(strings(out[mclk]["function"]) == ["cam_mclk"], "MCLK0 mux")
    need(hv.u32s(out[mclk]["drive-strength"]) == [4], "MCLK0 drive")
    need("bias-disable" in out[mclk] and "output-enable" in out[mclk], "MCLK0 electrical state")
    reset = IR_PIN + "/reset-pins"
    need(strings(out[reset]["pins"]) == ["gpio109"], "reset pin")
    need(strings(out[reset]["function"]) == ["gpio"], "reset mux")

    # Probe-only device properties.
    need(strings(out[IR]["compatible"]) == ["microsoft,sp11-vd55g0-idprobe"], "probe-only compatible")
    need(hv.u32s(out[IR]["reg"]) == [0x60], "IR I2C address")
    need(seq_ref(out, oph, "clocks", out[IR]["clocks"]) == [("/soc@0/clock-controller@ade0000", (71,))], "MCLK0 reference")
    need(seq_ref(out, oph, "reset-gpios", out[IR]["reset-gpios"]) == [(TLMM, (109, 1))], "reset GPIO spec")
    need(ref_path(out, oph, out[IR]["pinctrl-0"]) == IR_PIN, "IR pinctrl")
    need(ref_path(out, oph, out[IR]["VCORE-supply"]) == REGROOT + "/ldo2", "VCORE rail")
    need(ref_path(out, oph, out[IR]["VDDIO-supply"]) == REGROOT + "/ldo4", "VDDIO rail")
    need(ref_path(out, oph, out[IR]["VANA-supply"]) == REGROOT + "/ldo7", "VANA rail")
    need(not any(k.startswith("st,") for k in out[IR]), "no ST illumination/sync properties")
    need("lane-polarities" not in out[IR_EP], "no invented lane polarity")

    need(hv.u32s(out[IR_EP]["bus-type"]) == [4], "sensor DPHY")
    need(hv.u32s(out[IR_EP]["data-lanes"]) == [1], "sensor logical lane1")
    need(hv.u32s(out[IR_EP]["link-frequencies"]) == [0, 420_000_000], "420MHz link")
    need(hv.u32s(out[CAM_EP]["bus-type"]) == [4], "CAMSS DPHY")
    need(hv.u32s(out[CAM_EP]["data-lanes"]) == [0], "CAMSS physical lane0")
    need(ref_path(out, oph, out[IR_EP]["remote-endpoint"]) == CAM_EP, "sensor remote")
    need(ref_path(out, oph, out[CAM_EP]["remote-endpoint"]) == IR_EP, "CAMSS remote")
    need(set(subprocess.check_output(["fdtget", "-l", str(OUT), PORTS], text=True).split()) == {"port@0", "port@1", "port@2"}, "CAMSS ports 0/1/2")

    # Accepted RGB nodes remain raw-identical because they are parent nodes.
    for path in (REAR, REAR + "/port", REAR + "/port/endpoint", FRONT, FRONT + "/port", FRONT + "/port/endpoint", PORTS + "/port@1", PORTS + "/port@1/endpoint", PORTS + "/port@2", PORTS + "/port@2/endpoint"):
        need(out[path] == parent[path], "RGB parent drift " + path)

    need(normalized_warnings(OUT) == normalized_warnings(IB), "DTC warning regression")

    with tempfile.TemporaryDirectory(prefix="e004b-rebuild-") as td:
        rebuilt = Path(td) / "out.dtb"
        subprocess.run(["python3", str(BUILDER), "--parent", str(IB), "--hv-builder", str(HVB), "--out", str(rebuilt)], check=True, stdout=subprocess.DEVNULL)
        need(sha(rebuilt) == OUT_SHA, "deterministic rebuild")

    result = {
        "schema": "sp11-camera-e004b-ir-probe-dtb-v1",
        "status": "PASS_OFFLINE_E004B_IR_PROBE_DTB_AUTHORITY",
        "windows_authority": "E004a Windows-only oracle PASS",
        "parent_ib_dtb_sha256": IB_SHA,
        "output_dtb_sha256": OUT_SHA,
        "parent_nodes": len(parent),
        "output_nodes": len(out),
        "added_nodes": 13,
        "rgb_parent_semantics_byte_exact": True,
        "route": "CCI0/master0 -> I2C 0x60 -> CSIPHY0 D-PHY Lane0+Clk",
        "i2c_clock_hz": 400000,
        "mclk": {"resource": "CAM_CC_MCLK0_CLK", "id": 71, "hz": 19200000, "tlmm": 96},
        "reset_gpio": 109,
        "rails": {
            "LDO4_M_VDDIO_uV": 1800000,
            "LDO2_M_windows_request_uV": 1150000,
            "LDO2_M_linux_hw_setpoint_uV": 1152000,
            "LDO2_M_quantization_delta_uV": 2000,
            "LDO7_M_VANA_uV": 2800000,
        },
        "transport": {"data_lanes": 1, "receiver_lane": 0, "link_frequency_hz": 420000000, "lane_polarity": "NO_INVERSION_PROVEN"},
        "probe_compatible": "microsoft,sp11-vd55g0-idprobe",
        "pristine_st_driver_can_bind": False,
        "illumination_properties_present": False,
        "windows_aeob_delay_unit": "UNRESOLVED",
        "linux_runtime_performed": False,
        "runtime_authorized": False,
        "next_gate": "Build and verify a write-free VD55G0 identity/revision probe module; then package a one-shot candidate before any live power-on.",
    }
    (HERE / "DT-RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print("E004B_DTB_VERIFY=PASS SHA256=" + OUT_SHA)
    print("E004B_PARENT_PRESERVATION=PASS RGB=BYTE_EXACT ADDED_NODES=13")
    print("E004B_ROUTE=PASS CCI0_MASTER0 I2C=0x60 FAST=400k MCLK0=GPIO96 RESET=GPIO109 CSIPHY0_LANE0")
    print("E004B_POWER=PASS VDDIO=1.800V VCORE=1.152V(Windows-request-1.150V-quantized) VANA=2.800V")
    print("E004B_SAFETY=PASS PROBE_COMPAT_ONLY ST_BIND=NO ILLUMINATION=NO RUNTIME=NO")


if __name__ == "__main__":
    main()
