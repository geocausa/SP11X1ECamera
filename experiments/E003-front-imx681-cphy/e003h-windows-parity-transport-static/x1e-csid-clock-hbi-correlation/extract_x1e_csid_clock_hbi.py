#!/usr/bin/env python3
import hashlib,json,re
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT')
REPO=ROOT/'06-camera/SP11X1ECamera'
SRC=ROOT/'02-kernel/sp11-camera-e002k-d-src'
CSID=SRC/'drivers/media/platform/qcom/camss/camss-csid.c'
CAMSS=SRC/'drivers/media/platform/qcom/camss/camss.c'
CAMCC=SRC/'drivers/clk/qcom/camcc-x1e80100.c'
TRANSPORT=REPO/'experiments/E003-front-imx681-cphy/e003e-mode0-standby/TRANSPORT-METADATA.md'
LINUX=REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-rupdone-no-regupdate-0051-candidate/runtime-0051-analysis.json'
WINDOWS=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-csid1-bit14-history/windows-csid1-bit14-history-oracle.json'
EOF=REPO/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-linux-first-eof-geometry-boundary/first-eof-geometry-boundary-oracle.json'
EXPECTED={
 'csid':'df0d2a0aa92078da7d86e1a96d2ff3b9c0876e702e14f8e172676a1f0371acd2',
 'camss':'5a920032e138eee1154c4b9ae1846a445e02fbac3e7626a4245797502e73b793',
 'camcc':'c9d0c54bbfd4de4d27e814a06332c950f23b75dbaac327180a3a245628c01477',
 'transport':'9796c92d718dd894248bf35926f2330c81636c531c0c8cb95b8db1d2f35aa3c8',
 'linux':'2e1fbd740073b98e9e86ef477f1986d9b7e94a26a5e486f4386197b8e331f9d1',
 'windows':'f7523499e06332e588418218bb4eac71069e01c237c0c35f27c3bec6968f3db5',
 'eof':'db4476e159872f9005a127d84ea41032191402de2709a0835d2c2c5fbc9dffde',
}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def chk(k,p):
 g=sha(p)
 if g!=EXPECTED[k]: die(f'{k} hash drift {g}')
def main():
 for k,p in [('csid',CSID),('camss',CAMSS),('camcc',CAMCC),('transport',TRANSPORT),('linux',LINUX),('windows',WINDOWS),('eof',EOF)]: chk(k,p)
 csid=CSID.read_text(); camss=CAMSS.read_text(); camcc=CAMCC.read_text(); tr=TRANSPORT.read_text()
 if 'link_freq = camss_get_link_freq(&csid->subdev.entity, fmt->bpp, csid->phy.lane_cnt, cphy);' not in csid: die('C-PHY link-frequency call drift')
 for n in ('"csi0"','"csi1"','"csi2"','"csi3"'):
  if n not in csid: die('legacy scaled-clock name drift')
 if '"csid"' in csid[csid.index('if (!strcmp(clock->name, "csi0")'):csid.index('u64 min_rate = link_freq / 4;')]: die('csid unexpectedly recognized by scaled branch')
 if 'u64 min_rate = link_freq / 4;' not in csid or 'camss_add_clock_margin(&min_rate);' not in csid: die('rate math drift')
 if 'clk_set_rate(clock->clk, clock->freq[0]);' not in csid: die('generic first-rate branch drift')
 x1=camss[camss.index('static const struct camss_subdev_resources csid_res_x1e80100[]'):camss.index('static const struct camss_subdev_resources vfe_res_x1e80100[]')]
 if x1.count('"csid", "csid_csiphy_rx"') != 5: die('X1E CSID clock names/count drift')
 if x1.count('{ 300000000, 400000000, 480000000 }') < 10: die('X1E 300/400/480 tables drift')
 if 'fixed V4L2 `link_freq = 1,200,000,000 Hz`' not in tr: die('front link frequency evidence drift')
 for table in ('ftbl_cam_cc_csid_clk_src','ftbl_cam_cc_cphy_rx_clk_src'):
  i=camcc.index('static const struct freq_tbl '+table)
  block=camcc[i:i+500]
  for rate in (300000000,400000000,480000000):
   if f'F({rate},' not in block: die(f'{table} missing {rate}')
 link=1_200_000_000
 min_unmargined=link//4
 min_margin=min_unmargined*105//100
 table=[300_000_000,400_000_000,480_000_000]
 selected=next(r for r in table if min_margin < r)
 actual_generic=table[0]
 if (min_unmargined,min_margin,selected,actual_generic)!=(300_000_000,315_000_000,400_000_000,300_000_000): die('rate calculation drift')
 lx=json.loads(LINUX.read_text()); wx=json.loads(WINDOWS.read_text()); ex=json.loads(EOF.read_text())
 if not ex['classification']['prior_first_epoch_geometry_divergence_boundary_superseded']: die('EOF boundary oracle not accepted')
 wh=int(wx['bounded_end']['hbi'],16)
 # Linux error-time HBI is preserved in the 0051 run via equality to 0050/0049; analysis carries source hashes but not HBI itself.
 # Pin raw Linux HBI through the 0051 dmesg hash-protected analysis source record indirectly by requiring the known accepted value in project state evidence file.
 dmesg=REPO/'experiments/E003-front-imx681-cphy/e003h-csid1-rupdone-no-regupdate-0051-candidate/RUNTIME-RUPCLEAR-0051-DMESG.txt'
 line=next((z for z in dmesg.read_text().splitlines() if 'line-error=0a500f00/02c502c0/00000000' in z),None)
 if not line: die('Linux HBI evidence missing')
 lh=0x02c502c0
 w_hi,w_lo=(wh>>16)&0xffff,wh&0xffff
 l_hi,l_lo=(lh>>16)&0xffff,lh&0xffff
 predicted_hi=l_hi*selected/actual_generic
 predicted_lo=l_lo*selected/actual_generic
 err_hi=abs(w_hi-predicted_hi); err_lo=abs(w_lo-predicted_lo)
 ratio_hi=w_hi/l_hi; ratio_lo=w_lo/l_lo
 if err_hi>2 or err_lo>3: die(f'HBI 4/3 correlation drift hi={err_hi} lo={err_lo}')
 out={
  'schema':'sp11-e003h-x1e-csid-clock-hbi-correlation-v1','accepted':True,'source_sha256':EXPECTED,
  'front_transport':{'link_freq_hz':link,'cphy_trios':1,'raw_bpp':10},
  'linux_clock_selection':{
   'scaled_branch_recognized_names':['csi0','csi1','csi2','csi3'],
   'x1e_clock_names':['csid','csid_csiphy_rx'],
   'x1e_names_enter_scaled_branch':False,
   'generic_branch_sets_first_rate':True,
   'x1e_rate_table_hz':table,
   'proven_programmed_request_hz':actual_generic,
   'link_derived_unmargined_hz':min_unmargined,
   'link_derived_with_5pct_margin_hz':min_margin,
   'rate_algorithm_would_select_hz':selected,
   'camcc_has_distinct_300_400_480_rates':True,
  },
  'hbi_correlation':{
   'windows_raw':'0x03b203ad','linux_raw':'0x02c502c0',
   'windows_halves':[w_hi,w_lo],'linux_halves':[l_hi,l_lo],
   'windows_over_linux_ratio':[ratio_hi,ratio_lo],
   'target_400_over_300_ratio':4/3,
   'linux_halves_scaled_400_over_300':[predicted_hi,predicted_lo],
   'absolute_tick_error_to_windows':[err_hi,err_lo],
   'both_half_ranges_preserve_width_5':(w_hi-w_lo==5 and l_hi-l_lo==5),
  },
  'classification':{
   'linux_x1e_front_csid_300mhz_request_proven':True,
   'linux_link_derived_required_rate_is_400mhz':True,
   'x1e_clock_name_mismatch_bypasses_link_scaling':True,
   'hbi_ratio_matches_400_to_300_within_three_ticks':True,
   'direct_windows_400mhz_clock_vote_observed':False,
   'windows_400mhz_is_strongly_correlated_not_directly_proven':True,
   'clock_rate_delta_is_plausibly_causal_for_completed_frame_crop_failure':True,
   'hardware_runtime_authorized':False,
   'speculative_crop_register_write_justified':False,
  },
  'next_gate':'Represent and inspect the smallest X1E front-only clock correction that causes CSID1 core/RX clocks to select 400MHz for the proven 1.2GHz one-trio C-PHY link, without touching crop/RUP/VFE/sensor programming. Do not execute hardware until package + separate authorization. Direct Windows clock-vote proof remains desirable but is not required to establish the Linux internal rate-selection defect.'
 }
 blob=json.dumps(out,indent=2,sort_keys=True)+'\n'
 here=Path(__file__).parent
 (here/'x1e-csid-clock-hbi-correlation-oracle.json').write_text(blob)
 (here/'EXTRACT.txt').write_text(blob)
 print(blob,end='')
if __name__=='__main__': main()
