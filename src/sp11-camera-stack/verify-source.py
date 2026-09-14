#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re
D=Path(__file__).resolve().parent;R=D.parents[1]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(v,m):
    if not v:raise AssertionError(m)
p=json.loads((D/'PROVENANCE.json').read_text())
need(sha(D/'authority/ib-unified-rear-front.dtb')==p['dt']['rgb_input_sha256'],'RGB DT input')
need(sha(D/'authority/ir-native-bind.dtb')==p['dt']['ir_input_sha256'],'IR DT input')
need(sha(D/'fdt_authority.py')==p['dt']['fdt_helper_sha256'],'FDT helper')
need(sha(D/'authority/ov13858.c')==p['rear_ov13858']['source_sha256'],'rear source')
need(sha(D/'authority/ov13858-production.ko')==p['rear_ov13858']['runtime_module_sha256'],'rear module')
cam=(R/'src/front-imx681/kernel/camss/camss-csiphy-3ph-1-0.c').read_text()
for tok in ('module_param_named(e004j_ir_dphy_windows_parity','CAMSS_X1E80100','csiphy->id == 0','V4L2_MBUS_CSI2_DPHY'):
    need(tok in cam,'CAMSS gate '+tok)
need('static bool csiphy_x1e_ir_dphy_windows_parity;' in cam,'gate default')
front=json.loads((R/'src/front-imx681/PROVENANCE.json').read_text())
need(front['authority']['camss_module_sha256']==p['modules']['qcom_camss_sha256'],'CAMSS authority')
need(front['authority']['imx681_module_sha256']==p['modules']['imx681_sha256'],'IMX authority')
need(sha(R/'src/front-imx681/userspace/iq/live-iq-producer.py')==p['front_imx681']['producer_sha256'],'producer')
need(sha(R/'src/front-imx681/userspace/iq/vendor/experiments/E003-front-imx681-cphy/e003i-front-native-productionization/el-calibrated-awb-scalar-join/awb_scalar.py')==p['front_imx681']['awb_sha256'],'AWB')
b=(D/'build-hardware-authority.sh').read_text()
for tok in ('KERNEL_SOURCE="${KERNEL_SOURCE:?','KERNEL_BUILD="${KERNEL_BUILD:?','HARDWARE-MANIFEST.sha256','SP11_CAMERA_HARDWARE_AUTHORITY=PASS','4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72'):
    need(tok in b,'builder '+tok)
print('SP11 CAMERA STACK SOURCE VERIFY: PASS')
