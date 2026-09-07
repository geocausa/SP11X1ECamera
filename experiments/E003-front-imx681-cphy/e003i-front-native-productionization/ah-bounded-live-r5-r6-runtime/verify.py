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
 'selector_proof':BASE/'ae-bounded-live-trigger-iq-producer/prove-expanded-selector.py',
 'selector_manifest':BASE/'ae-bounded-live-trigger-iq-producer/SELECTOR-EXPANSION.json',
 'composer':BASE/'e-template-free-capsule/build-template-free-0076-capsules.py',
 'epoch0_parser':BASE/'e-template-free-capsule/parse-epoch0-log.py',
}
want={
 'camss':'42538dce9a27eadbf95ed09cd07ca526b006598a0263b0f2b3b953b973aad32b',
 'imx681':'a12693a18bf2e4108dd309af68da189a2ea394a734a0c6a3c1d624ac44dea3dc',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'producer':'f83dffed960146251a8fe4b21807a4130ed9367fb2e55f12d04c8dc98ddb22ca',
 'capture_helper_source':'0648650a6f7c75d9ea644079e130a28d7ccf56c366df5fedc97364c91161903d',
 'control_shim':'46c8b80ff770ff01e8086a3b5da5a9ebd778e1a3f3f47bbe1b7e5e931a0dcce9',
 'selector_proof':'81a64f30781f1e88bff6e14f5930626dcafa255b5611c11a11be73eafa3237e8',
 'selector_manifest':'4029eae684d32242751d033ee02d274103a8ec5709bb24563c39cc524b60a941',
 'composer':'873e89f8ad5d824901919aa72535e5367e3551443348d651392cd68bdaf7c3cb',
 'epoch0_parser':'f0cb769dd546783c765a62bffd78ebcc5d56aef2421151690be6e3bcf43630ad',
}
for n,p in assets.items():need(p.is_file(),f'missing {n} {p}')
for n,h in want.items():need(sh(assets[n])==h,f'{n} SHA drift')
ac=json.loads((BASE/'ac-clean-cct-reconstruction/RESULT.json').read_text())
ad=json.loads((BASE/'ad-native-live-trigger-core/RESULT.json').read_text())
ae=json.loads((BASE/'ae-bounded-live-trigger-iq-producer/RESULT.json').read_text())
sel=json.loads((BASE/'ae-bounded-live-trigger-iq-producer/SELECTOR-EXPANSION.json').read_text())
ag=json.loads((BASE/'ag-bounded-live-r5-r6-runtime/RESULT.json').read_text())
need(ac['status']=='PASS' and ac['gates']['cct_gate_closed'],'AC CCT proof')
need(ad['status']=='PASS' and ad['differential']['all_six_bit_exact'],'AD trigger proof')
need(ae['status']=='PASS' and ae['deadline_pass'],'AE retained-Z proof')
need(sel['status']=='PASS' and sel['claims']['retained_z_unchanged'] and sel['claims']['actual_ag_gap_supported'],'expanded selector proof')
need(sel['domains']['actual_ag']['expected_capsules']['5']=='b05698889f607d5786a441a7c85ef07b6f61852d20a1894ff8f4919b07051d94','actual AG R5 proof')
need(sel['domains']['actual_ag']['expected_capsules']['6']=='f694734412fe7cf4669fd1bfadb0f7eecc4d8f4b34f94f60a4a9068537dc546e','actual AG R6 proof')
need(ag['status']=='FAIL_LIVE_G1_CCT_SELECTOR_RANGE' and ag['camera_stream_executed'] and not ag['r5_submitted'] and not ag['r6_submitted'],'AG failure classification')
need(ag['safety']['golden_return']['status']=='PASS','AG Golden return')
print('AH_VERIFY=PASS')
for n,p in assets.items():print(n,sh(p),p)
