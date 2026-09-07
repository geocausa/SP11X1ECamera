#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,sys
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
}
want={'camss':'42538dce9a27eadbf95ed09cd07ca526b006598a0263b0f2b3b953b973aad32b','imx681':'a12693a18bf2e4108dd309af68da189a2ea394a734a0c6a3c1d624ac44dea3dc','dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f'}
for n,p in assets.items():need(p.is_file(),f'missing {n} {p}')
for n,h in want.items():need(sh(assets[n])==h,f'{n} SHA drift')
# Producer checkpoints are committed and must still declare PASS.
ad=json.loads((BASE/'ad-native-live-trigger-core/RESULT.json').read_text());ae=json.loads((BASE/'ae-bounded-live-trigger-iq-producer/RESULT.json').read_text());ac=json.loads((BASE/'ac-clean-cct-reconstruction/RESULT.json').read_text())
need(ad['status']=='PASS' and ad['differential']['all_six_bit_exact'],'AD trigger proof')
need(ae['status']=='PASS' and ae['deadline_pass'],'AE producer proof')
need(ac['status']=='PASS' and ac['gates']['cct_gate_closed'],'AC CCT proof')
print('AF_VERIFY=PASS')
for n,p in assets.items():print(n,sh(p),p)
