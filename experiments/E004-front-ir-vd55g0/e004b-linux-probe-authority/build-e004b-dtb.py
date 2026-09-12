#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, importlib.util, shutil
from pathlib import Path

PARENT_SHA = "5e919d6bf778eb9eff5bf270447fa37f3c50ee16625c085c325e8d275d162321"

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
CAM_PORTS = CAMSS + "/ports"
CAM_EP = CAM_PORTS + "/port@0/endpoint"
REAR_EP = "/soc@0/cci@ac15000/i2c-bus@1/camera@10/port/endpoint"
REAR_CAM_EP = CAM_PORTS + "/port@1/endpoint"
CAMCC = "/soc@0/clock-controller@ade0000"

NEW_NODES = [
    REGROOT + "/ldo2", REGROOT + "/ldo4", REGROOT + "/ldo7",
    CCI_DEF + "/cci0-i2c0-pins", CCI_SLEEP + "/cci0-i2c0-pins",
    IR_PIN, IR_PIN + "/mclk-pins", IR_PIN + "/reset-pins",
    IR, IR + "/port", IR_EP,
    CAM_PORTS + "/port@0", CAM_EP,
]
PHANDLE_NODES = [
    REGROOT + "/ldo2", REGROOT + "/ldo4", REGROOT + "/ldo7",
    IR_PIN, IR_EP, CAM_EP,
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--parent", type=Path, required=True)
    ap.add_argument("--hv-builder", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    if sha(a.parent) != PARENT_SHA:
        raise SystemExit("IB parent identity drift: " + sha(a.parent))

    spec = importlib.util.spec_from_file_location("hv", a.hv_builder)
    hv = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hv)

    parent = hv.parse_fdt(a.parent)
    for path in NEW_NODES:
        if path in parent:
            raise SystemExit("new node already exists in parent: " + path)
    for path in (REGROOT, TLMM, CCI0, I2C0, CCI_DEF, CCI_SLEEP, CAM_PORTS, REAR_EP, REAR_CAM_EP, CAMCC):
        if path not in parent:
            raise SystemExit("required parent node missing: " + path)

    _, parent_paths = hv.phandle_map(parent)
    next_phandle = max(hv.phandle_map(parent)[0]) + 1
    phandles = {}
    for path in PHANDLE_NODES:
        phandles[path] = next_phandle
        next_phandle += 1

    shutil.copyfile(a.parent, a.out)
    for path in sorted(NEW_NODES, key=lambda p: (p.count("/"), p)):
        hv.create_node(a.out, path)

    def raw(node, prop, data):
        hv.set_raw(a.out, node, prop, data)

    def u32(node, prop, *values):
        raw(node, prop, hv.cells(list(values)))

    def string(node, prop, value):
        raw(node, prop, value.encode() + b"\0")

    def boolean(node, prop):
        raw(node, prop, b"")

    # Assign collision-free phandles first.
    for path, value in phandles.items():
        u32(path, "phandle", value)

    # PM8010 rails: Windows asks 1.150/1.800/2.800 V. LDO2's exact
    # PM8010 hardware grid is 8 mV from 528 mV, so Linux must use 1.152 V.
    rails = {
        REGROOT + "/ldo2": ("vreg_l2m_ir_1p152", 1_152_000),
        REGROOT + "/ldo4": ("vreg_l4m_ir_1p8", 1_800_000),
        REGROOT + "/ldo7": ("vreg_l7m_ir_2p8", 2_800_000),
    }
    for path, (name, uv) in rails.items():
        string(path, "regulator-name", name)
        u32(path, "regulator-min-microvolt", uv)
        u32(path, "regulator-max-microvolt", uv)

    # Extend the already-referenced CCI0 pin states with master0 only.
    for state, bias in ((CCI_DEF, "bias-pull-up"), (CCI_SLEEP, "bias-pull-down")):
        p = state + "/cci0-i2c0-pins"
        string(p, "pins", "gpio101\0gpio102".replace("\0", "\0"))
        # fdt stringlist is two NUL-terminated strings.
        raw(p, "pins", b"gpio101\0gpio102\0")
        string(p, "function", "cci_i2c")
        u32(p, "drive-strength", 2)
        boolean(p, bias)

    # MCLK0 -> GPIO96 is the X1E resource-to-pad translation. GPIO109 is
    # Windows-authoritative reset.
    mclk = IR_PIN + "/mclk-pins"
    string(mclk, "pins", "gpio96")
    string(mclk, "function", "cam_mclk")
    u32(mclk, "drive-strength", 4)
    boolean(mclk, "bias-disable")
    boolean(mclk, "output-enable")

    rst = IR_PIN + "/reset-pins"
    string(rst, "pins", "gpio109")
    string(rst, "function", "gpio")
    u32(rst, "drive-strength", 2)
    boolean(rst, "bias-disable")

    # QTI package says FAST; Linux CCI maps 400 kHz to I2C_MODE_FAST.
    u32(I2C0, "clock-frequency", 400_000)

    # Probe-only sensor node: deliberately does NOT use st,vd55g0 so the
    # pristine ST driver cannot bind and upload its non-Surface patch.
    string(IR, "compatible", "microsoft,sp11-vd55g0-idprobe")
    u32(IR, "reg", 0x60)
    camcc_ph = parent_paths[CAMCC]
    tlmm_ph = parent_paths[TLMM]
    u32(IR, "clocks", camcc_ph, 71)  # CAM_CC_MCLK0_CLK
    u32(IR, "reset-gpios", tlmm_ph, 109, 1)  # GPIO_ACTIVE_LOW
    u32(IR, "pinctrl-0", phandles[IR_PIN])
    string(IR, "pinctrl-names", "default")
    u32(IR, "VCORE-supply", phandles[REGROOT + "/ldo2"])
    u32(IR, "VDDIO-supply", phandles[REGROOT + "/ldo4"])
    u32(IR, "VANA-supply", phandles[REGROOT + "/ldo7"])

    # Sensor logical CSI-2 lane 1 -> Windows-proven first physical data lane.
    raw(IR_EP, "bus-type", parent[REAR_EP]["bus-type"])
    u32(IR_EP, "data-lanes", 1)
    raw(IR_EP, "link-frequencies", hv.cells([0, 420_000_000]))
    u32(IR_EP, "remote-endpoint", phandles[CAM_EP])

    # CAMSS receiver uses zero-based physical lane indices; lane0 is Windows-proven.
    port0 = CAM_PORTS + "/port@0"
    u32(port0, "reg", 0)
    raw(CAM_EP, "bus-type", parent[REAR_CAM_EP]["bus-type"])
    u32(CAM_EP, "data-lanes", 0)
    u32(CAM_EP, "remote-endpoint", phandles[IR_EP])

    # New aliases only; all pre-existing symbol bytes remain untouched.
    symbols = {
        "vreg_l2m_ir": REGROOT + "/ldo2",
        "vreg_l4m_ir": REGROOT + "/ldo4",
        "vreg_l7m_ir": REGROOT + "/ldo7",
        "front_ir_vd55g0_default": IR_PIN,
        "vd55g0_ir": IR,
        "vd55g0_ir_ep": IR_EP,
        "camss_csiphy0_ep": CAM_EP,
    }
    for name, path in symbols.items():
        string("/__symbols__", name, path)

    out = hv.parse_fdt(a.out)
    print("E004B_DTB_BUILD=PASS")
    print("PARENT_SHA256=" + sha(a.parent))
    print("OUTPUT_SHA256=" + sha(a.out))
    print("PARENT_NODES=" + str(len(parent)) + " OUTPUT_NODES=" + str(len(out)) + " ADDED=" + str(len(set(out) - set(parent))))
    print("NEW_PHANDLES=" + ",".join(f"{Path(k).name}:{v:#x}" for k, v in phandles.items()))
    print("IR_ROUTE=CCI0_MASTER0_I2C0x60_CSIPHY0_DPHY_LANE0_420MHz")
    print("IR_POWER=LDO4M_1p8_LDO2M_1p152_QUANTIZED_LDO7M_2p8_MCLK0_19p2_RESET109")


if __name__ == "__main__":
    main()
