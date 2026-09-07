#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent; BASE=HERE.parent; REPO=HERE.parents[3]
def sh(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
aj=BASE/'aj-imx681-exposure-controls'
ai=BASE/'ai-deadline-hardened-live-r5-r6-runtime'
b=REPO/'experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate'
assets={
 'camss':BASE/'z-live-3a-runtime/qcom-camss-e003i-y.ko',
 'imx681':aj/'imx681.ko',
 'dtb':b/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb',
 'producer':BASE/'ae-bounded-live-trigger-iq-producer/live-iq-producer.py',
 'capture_source':BASE/'ae-bounded-live-trigger-iq-producer/e003i-ae-six-frame-live-iq.c',
 'aj_source':aj/'imx681.c',
 'aj_oracle':aj/'windows-oracle/oracle.py',
}
want={
 'camss':'42538dce9a27eadbf95ed09cd07ca526b006598a0263b0f2b3b953b973aad32b',
 'imx681':'15855b65512a15e66a732b1bf023fa8935a86b937426e2f590e161d25944bd54',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'producer':'c56b4b5d832d4fd64531a62c8036f097a172fdde61255aa0751b971b0ab070f9',
 'capture_source':'0648650a6f7c75d9ea644079e130a28d7ccf56c366df5fedc97364c91161903d',
 'aj_source':'143b2eb661331f0e4aa1717f7b71f607465890e2b01b306fffc7b9e85c0e13de',
 'aj_oracle':'2dffc0370dbc19345bbfc09d80bd7ea6919259a371fc7f35e6b4cf65fe5fad9f',
}
for n,p in assets.items(): need(p.is_file(),f'missing {n}: {p}')
for n,h in want.items(): need(sh(assets[n])==h,f'{n} SHA drift: {sh(assets[n])}')
ajres=json.loads((aj/'RESULT.json').read_text())
aires=json.loads((ai/'RESULT.json').read_text())
akres=json.loads((BASE/'ak-bounded-imx681-control-runtime/RESULT.json').read_text())
need(ajres['status']=='PASS_STATIC_OFFLINE','AJ static result')
need(ajres['claims']['four_control_cluster_implemented'] and ajres['claims']['mode2_default_identity_preserved'],'AJ claims')
need(aires['status']=='PASS_LIVE_DYNAMIC_R5_R6','AI live baseline')
need(aires['safety']['golden_return']['status']=='PASS','AI Golden return')
need(akres['status']=='FAIL_PRESTREAM_DISCOVERY_EACCES','AK consumed classification')
need(not akres['camera_stream_executed'] and not akres['failure']['streamon_reached'],'AK no-stream boundary')
need(akres['safety']['golden_return']['status']=='PASS','AK Golden return')
print('AL_VERIFY=PASS')
for n,p in assets.items(): print(n,sh(p),p)
