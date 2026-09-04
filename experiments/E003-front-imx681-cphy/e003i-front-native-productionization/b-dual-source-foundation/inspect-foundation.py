#!/usr/bin/env python3
from pathlib import Path
import json,hashlib,subprocess
HERE=Path(__file__).resolve().parent
P=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src')
M=json.loads((HERE/'BUILD-MANIFEST.json').read_text())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mod(p,key):
    for l in subprocess.check_output(['modinfo',str(p)],text=True).splitlines():
        if l.startswith(key+':'): return l.split(':',1)[1].strip()
assert M['accepted'] and not M['runtime_authorized']
assert sha(P/'drivers/media/i2c/imx681.c')==M['imx681']['source_sha256']
assert mod(P/'drivers/media/i2c/imx681.ko','srcversion')==M['imx681']['expected_oracle_srcversion']
assert mod(P/'drivers/media/platform/qcom/camss/qcom-camss.ko','srcversion')==M['camss']['expected_oracle_srcversion']
D=(P/'arch/arm64/boot/dts/qcom/x1-microsoft-denali.dtsi').read_text(); H=(P/'arch/arm64/boot/dts/qcom/hamoa.dtsi').read_text()
for x in ['compatible = "ovti,ov13858";','compatible = "sony,imx681";','port@1 {','port@2 {','"rt_cdm1"','<0 0x0ac26000 0 0x1000>','<0 0x0ac62000 0 0xf000>','<0 0x0ac71000 0 0xf000>']:
    assert x in D,x
for x in ['<&apps_smmu 0x800 0x60>','<&apps_smmu 0x820 0x60>','<&apps_smmu 0x840 0x60>','<&apps_smmu 0x860 0x60>','<&apps_smmu 0x18a0 0x00>']:
    assert x in H,x
print('E003I_DUAL_SOURCE_FOUNDATION=PASS')
print('CAMSS_SRCVERSION='+M['camss']['expected_oracle_srcversion'])
print('IMX681_SRCVERSION='+M['imx681']['expected_oracle_srcversion'])
print('RUNTIME_AUTHORIZED=false')
