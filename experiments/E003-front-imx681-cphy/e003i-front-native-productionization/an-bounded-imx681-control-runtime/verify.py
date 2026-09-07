#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent; BASE=HERE.parent; REPO=HERE.parents[3]
def sh(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
am=BASE/'am-imx681-exposure-cluster-fix'; ai=BASE/'ai-deadline-hardened-live-r5-r6-runtime'; al=BASE/'al-bounded-imx681-control-runtime'; b=REPO/'experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate'
assets={
 'camss':BASE/'z-live-3a-runtime/qcom-camss-e003i-y.ko',
 'imx681':am/'imx681.ko',
 'dtb':b/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb',
 'producer':BASE/'ae-bounded-live-trigger-iq-producer/live-iq-producer.py',
 'capture_source':BASE/'ae-bounded-live-trigger-iq-producer/e003i-ae-six-frame-live-iq.c',
 'am_source':am/'imx681.c','am_oracle':am/'windows-oracle/oracle.py','am_proof':am/'PROOF.json'
}
want={
 'camss':'42538dce9a27eadbf95ed09cd07ca526b006598a0263b0f2b3b953b973aad32b',
 'imx681':'c2b63b747176d3e8a7f8ee658833e0c1806fad9e03185840208ff5e466ce6ba8',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'producer':'c56b4b5d832d4fd64531a62c8036f097a172fdde61255aa0751b971b0ab070f9',
 'capture_source':'0648650a6f7c75d9ea644079e130a28d7ccf56c366df5fedc97364c91161903d',
 'am_source':'50c0612d8c4ce0fed5ce2d36f909ec9f3f193241611766aedc24272328e79e19',
 'am_oracle':'2dffc0370dbc19345bbfc09d80bd7ea6919259a371fc7f35e6b4cf65fe5fad9f',
 'am_proof':'423b8464d02312f4c420c9083ba9f8c39505177d131b2998116e78a955764834'}
for n,p in assets.items(): need(p.is_file(),f'missing {n}: {p}')
for n,h in want.items(): need(sh(assets[n])==h,f'{n} SHA drift: {sh(assets[n])}')
amres=json.loads((am/'RESULT.json').read_text()); aires=json.loads((ai/'RESULT.json').read_text()); alres=json.loads((al/'RESULT.json').read_text())
need(amres['status']=='PASS' and amres['al_failure_closed_offline'],'AM proof result')
need(amres['topology']=={'vblank':'standalone','cluster_master':'exposure','cluster':['exposure','analogue_gain','digital_gain']},'AM topology')
need(amres['cache_regression']['am_result']==3500,'AM cache regression')
need(aires['status']=='PASS_LIVE_DYNAMIC_R5_R6' and aires['safety']['golden_return']['status']=='PASS','AI baseline')
need(alres['status']=='FAIL_PRESTREAM_EXPOSURE_CACHE_CLOBBER' and not alres['camera_stream_executed'],'AL classification')
need(alres['safety']['golden_return']['status']=='PASS','AL Golden return')
print('AN_VERIFY=PASS')
for n,p in assets.items(): print(n,sh(p),p)
