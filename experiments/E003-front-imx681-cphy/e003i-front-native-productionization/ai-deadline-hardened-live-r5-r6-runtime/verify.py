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
 'deadline_proof':BASE/'ae-bounded-live-trigger-iq-producer/prove-live-deadline-hardening.py',
 'deadline_manifest':BASE/'ae-bounded-live-trigger-iq-producer/LIVE-DEADLINE-HARDENING.json',
 'composer':BASE/'e-template-free-capsule/build-template-free-0076-capsules.py',
 'epoch0_parser':BASE/'e-template-free-capsule/parse-epoch0-log.py',
}
want={
 'camss':'42538dce9a27eadbf95ed09cd07ca526b006598a0263b0f2b3b953b973aad32b',
 'imx681':'a12693a18bf2e4108dd309af68da189a2ea394a734a0c6a3c1d624ac44dea3dc',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'producer':'c56b4b5d832d4fd64531a62c8036f097a172fdde61255aa0751b971b0ab070f9',
 'capture_helper_source':'0648650a6f7c75d9ea644079e130a28d7ccf56c366df5fedc97364c91161903d',
 'control_shim':'46c8b80ff770ff01e8086a3b5da5a9ebd778e1a3f3f47bbe1b7e5e931a0dcce9',
 'selector_proof':'81a64f30781f1e88bff6e14f5930626dcafa255b5611c11a11be73eafa3237e8',
 'selector_manifest':'4029eae684d32242751d033ee02d274103a8ec5709bb24563c39cc524b60a941',
 'deadline_proof':'11fda6e8e7ad9ebd6d47b5dd64f368850fd710b716c14da5fa0ea962b418dcde',
 'deadline_manifest':'ef6ebc8f8099b686d0d33d3dd64775d4a2eb454d00a7c448d55ac077bd0c26c6',
 'composer':'873e89f8ad5d824901919aa72535e5367e3551443348d651392cd68bdaf7c3cb',
 'epoch0_parser':'f0cb769dd546783c765a62bffd78ebcc5d56aef2421151690be6e3bcf43630ad',
}
for n,p in assets.items():need(p.is_file(),f'missing {n} {p}')
for n,h in want.items():need(sh(assets[n])==h,f'{n} SHA drift')
ac=json.loads((BASE/'ac-clean-cct-reconstruction/RESULT.json').read_text())
ad=json.loads((BASE/'ad-native-live-trigger-core/RESULT.json').read_text())
ae=json.loads((BASE/'ae-bounded-live-trigger-iq-producer/RESULT.json').read_text())
sel=json.loads((BASE/'ae-bounded-live-trigger-iq-producer/SELECTOR-EXPANSION.json').read_text())
dead=json.loads((BASE/'ae-bounded-live-trigger-iq-producer/LIVE-DEADLINE-HARDENING.json').read_text())
ah=json.loads((BASE/'ah-bounded-live-r5-r6-runtime/RESULT.json').read_text())
need(ac['status']=='PASS' and ac['gates']['cct_gate_closed'],'AC CCT proof')
need(ad['status']=='PASS' and ad['differential']['all_six_bit_exact'],'AD trigger proof')
need(ae['status']=='PASS' and ae['deadline_pass'],'AE retained-Z proof')
need(sel['status']=='PASS' and sel['claims']['retained_z_unchanged'] and sel['claims']['actual_ag_gap_supported'],'expanded selector proof')
need(dead['status']=='PASS' and dead['fixture_free'],'deadline hardening proof')
need(dead['scheduler']=={'cpu':11,'nice':-20,'scheduler':0},'deadline scheduler')
need(dead['acceptance']['G2_p95_under_budget'] and dead['acceptance']['G3_p95_under_budget'],'deadline p95')
need(dead['acceptance']['G2_max_under_budget'] and dead['acceptance']['G3_max_under_budget'],'deadline max')
need(dead['acceptance']['deadline_evidence_io_deferred'] and dead['acceptance']['state_reset_after_prewarm'],'deadline live invariants')
need(ah['status']=='FAIL_LIVE_R5_SUBMIT_EBUSY_AFTER_DEADLINE' and ah['camera_stream_executed'],'AH failure classification')
need(ah['r5_computed'] and not ah['r5_submitted'] and not ah['r6_submitted'],'AH submission state')
need(ah['offline_replay_of_exact_ah_snapshots']['r5_sha256']=='493117d029bac7910b41292e738685fdfe5a22ec52676fb415a27bfbb3c46ca5','AH R5 replay')
need(ah['offline_replay_of_exact_ah_snapshots']['r6_predicted_sha256']=='dac798043c9d14e8118bbed803bb2b3aa7f1a7532d2e4838ee88790c69c18115','AH R6 replay')
need(ah['safety']['golden_return']['status']=='PASS','AH Golden return')
print('AI_VERIFY=PASS')
for n,p in assets.items():print(n,sh(p),p)
