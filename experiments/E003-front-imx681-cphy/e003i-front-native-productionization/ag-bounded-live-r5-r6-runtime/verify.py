#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent;BASE=HERE.parent;REPO=HERE.parents[3]
def sh(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v:raise SystemExit('FAIL: '+m)
assets={
 'camss':BASE/'z-live-3a-runtime/qcom-camss-e003i-y.ko',
 'imx681':REPO/'experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate/imx681.ko',
 'dtb':REPO/'experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate/x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb',
 'producer':BASE/'ae-bounded-live-trigger-iq-producer/live-iq-producer.py',
 'capture_helper_source':BASE/'ae-bounded-live-trigger-iq-producer/e003i-ae-six-frame-live-iq.c',
 'control_shim':BASE/'ae-bounded-live-trigger-iq-producer/v4l2-control-shim.c',
 'composer':BASE/'e-template-free-capsule/build-template-free-0076-capsules.py',
 'epoch0_parser':BASE/'e-template-free-capsule/parse-epoch0-log.py',
 'composer_inspector':BASE/'e-template-free-capsule/inspect-template-free-composer.py',
}
want={
 'camss':'42538dce9a27eadbf95ed09cd07ca526b006598a0263b0f2b3b953b973aad32b',
 'imx681':'a12693a18bf2e4108dd309af68da189a2ea394a734a0c6a3c1d624ac44dea3dc',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'producer':'0af0e0284dbf99d3a9f0fcad0a2294ab75a3ee246d96a141e7aec1f24df4d7df',
 'capture_helper_source':'0648650a6f7c75d9ea644079e130a28d7ccf56c366df5fedc97364c91161903d',
 'control_shim':'46c8b80ff770ff01e8086a3b5da5a9ebd778e1a3f3f47bbe1b7e5e931a0dcce9',
 'composer':'873e89f8ad5d824901919aa72535e5367e3551443348d651392cd68bdaf7c3cb',
 'epoch0_parser':'f0cb769dd546783c765a62bffd78ebcc5d56aef2421151690be6e3bcf43630ad',
 'composer_inspector':'81334776dd810e3591f5e9fcb50b25c5084223e73a2e87fdea3d319d88321f4e',
}
for n,p in assets.items():need(p.is_file(),f'missing {n} {p}')
for n,h in want.items():need(sh(assets[n])==h,f'{n} SHA drift')
builder=assets['composer'].read_text();parser=assets['epoch0_parser'].read_text()
need('extract_vfe1_epoch0_cdm_batches.py' not in builder,'composer disassembly extractor dependency')
need('from capstone' not in builder and 'import capstone' not in builder,'composer Capstone dependency')
need('from capstone' not in parser and 'import capstone' not in parser,'Epoch0 parser Capstone dependency')
# Producer checkpoints and AF negative checkpoint must still be internally consistent.
ad=json.loads((BASE/'ad-native-live-trigger-core/RESULT.json').read_text())
ae=json.loads((BASE/'ae-bounded-live-trigger-iq-producer/RESULT.json').read_text())
ac=json.loads((BASE/'ac-clean-cct-reconstruction/RESULT.json').read_text())
af=json.loads((BASE/'af-bounded-live-r5-r6-runtime/RESULT.json').read_text())
need(ad['status']=='PASS' and ad['differential']['all_six_bit_exact'],'AD trigger proof')
need(ae['status']=='PASS' and ae['deadline_pass'],'AE producer proof')
need(ac['status']=='PASS' and ac['gates']['cct_gate_closed'],'AC CCT proof')
need(af['status']=='FAIL_PRESTREAM_PRODUCER_DEPENDENCY' and not af['camera_stream_executed'],'AF failure classification')
need(af['golden_return']['status']=='PASS','AF Golden return')
print('AG_VERIFY=PASS')
for n,p in assets.items():print(n,sh(p),p)
