#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent; BASE=HERE.parent; REPO=HERE.parents[3]
def sh(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
am=BASE/'am-imx681-exposure-cluster-fix'; ao=BASE/'ao-paired-stats-audit-helper'; ai=BASE/'ai-deadline-hardened-live-r5-r6-runtime'; an=BASE/'an-bounded-imx681-control-runtime'; b=REPO/'experiments/E003-front-imx681-cphy/e003h-six-frame-request6-0074-candidate'
assets={
 'camss':BASE/'z-live-3a-runtime/qcom-camss-e003i-y.ko',
 'imx681':am/'imx681.ko',
 'dtb':b/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb',
 'producer':BASE/'ae-bounded-live-trigger-iq-producer/live-iq-producer.py',
 'ao_helper':ao/'e003i-ao-six-frame-live-iq.c',
 'ao_proof':ao/'PROOF.json',
 'am_source':am/'imx681.c','am_oracle':am/'windows-oracle/oracle.py','am_proof':am/'PROOF.json'
}
want={
 'camss':'42538dce9a27eadbf95ed09cd07ca526b006598a0263b0f2b3b953b973aad32b',
 'imx681':'c2b63b747176d3e8a7f8ee658833e0c1806fad9e03185840208ff5e466ce6ba8',
 'dtb':'019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f',
 'producer':'c56b4b5d832d4fd64531a62c8036f097a172fdde61255aa0751b971b0ab070f9',
 'ao_helper':'b3a8969ec93575118acc43fd3ba6c39ace3a23d66f9bddb9caa714df58f7b91b',
 'ao_proof':'cc272dc1303fcb684fdca60b649af387ae2467b88f14855c48c219bdb262d779',
 'am_source':'50c0612d8c4ce0fed5ce2d36f909ec9f3f193241611766aedc24272328e79e19',
 'am_oracle':'2dffc0370dbc19345bbfc09d80bd7ea6919259a371fc7f35e6b4cf65fe5fad9f',
 'am_proof':'423b8464d02312f4c420c9083ba9f8c39505177d131b2998116e78a955764834'}
for n,p in assets.items(): need(p.is_file(),f'missing {n}: {p}')
for n,h in want.items(): need(sh(assets[n])==h,f'{n} SHA drift: {sh(assets[n])}')
amres=json.loads((am/'RESULT.json').read_text()); aores=json.loads((ao/'RESULT.json').read_text()); aires=json.loads((ai/'RESULT.json').read_text()); anres=json.loads((an/'RESULT.json').read_text())
need(amres['status']=='PASS' and amres['al_failure_closed_offline'],'AM result')
need(aores['status']=='PASS' and aores['an_parent_race_closed_offline'],'AO result')
need(aores['collector']['started_before_streamon'] and aores['collector']['order']=='3A then TLBG' and not aores['collector']['dqbuf_coupled_reads'],'AO topology')
need(aires['status']=='PASS_LIVE_DYNAMIC_R5_R6' and aires['safety']['golden_return']['status']=='PASS','AI baseline')
need(anres['status']=='FAIL_LIVE_PARENT_PAIRED_SNAPSHOT_RACE','AN classification')
need(anres['live_control_runtime_closed'] and anres['exact_sensor_transaction_pass'],'AN live AM proof')
need(anres['producer']['status']=='PASS' and anres['producer']['r5_submitted'] and anres['producer']['r6_submitted'],'AN producer proof')
need(anres['safety']['golden_return']['status']=='PASS','AN Golden return')
print('AP_VERIFY=PASS')
for n,p in assets.items(): print(n,sh(p),p)
