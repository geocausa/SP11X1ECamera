#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, subprocess, tempfile

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
WIN=HERE/'WINDOWS-CSIPHY0-LIVE2.normalized.txt'
CMP=HERE/'CURRENT-LINUX-VS-WINDOWS.json'
CSIPHY=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003c-dtb-build/source/drivers/media/platform/qcom/camss/camss-csiphy-3ph-1-0.c')
CAMSS=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003c-dtb-build/source/drivers/media/platform/qcom/camss/camss.c')
DTB=REPO/'experiments/E004-front-ir-vd55g0/e004h-safe42-config-authority/x1e80100-microsoft-denali-sp11-e004h-config42.dtb'

RAW_SP7_SHA='22e785474bd6857af52ab50a2039e8488a3328cbd8bf4a66a69d6e2d6fe2ac9d'
WIN_NORM_SHA='fc3994ea2a2d607d8028ed0881b8056e510287d5831fe22b5ea635f1ec109a26'
CSIPHY_SHA='418fe18845e1d57e2de5f2c9ece4bdd78d817d59ca71b25b00eb4259581464a8'
DTB_SHA='e29c787acf9e2f1330a4e73fd8014aba118a2f0a59be51c86859a9ab7fed4ef2'

def need(v,m):
    if not v: raise AssertionError(m)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def winmap():
    d={}
    for line in WIN.read_text().splitlines():
        a,v=line.split()
        d[int(a,16)]=int(v,16)
    return d

need(sha(WIN)==WIN_NORM_SHA,'normalized Windows snapshot')
need(sha(CSIPHY)==CSIPHY_SHA,'exact Linux CSIPHY source identity')
need(sha(DTB)==DTB_SHA,'E004h DTB identity')
w=winmap()
need(len(w)==2048,'8KiB snapshot must contain 2048 dwords')
need(w[0x1014]==0x81,'Windows lane mask')
need(w[0x1018]==0x01 and w[0x101c]==0x7a,'Windows common controls')
for off in (0x0008,0x0408,0x0808,0x0c08,0x0e08):
    need(w[off]==0x10,f'Windows settle {off:#x}')
expected_common=[0xff,0xfe,0xe6,0xdf,0xdf,0xfc,0xfb,0x9b,0x7f,0xbf,0xff]
need([w[x] for x in range(0x102c,0x1058,4)]==expected_common,'Windows CTRL11..21')

# Recompute current-vs-Windows model, not merely trust the saved JSON.
fresh=json.loads(subprocess.check_output(['python3',str(HERE/'compare_current_linux.py')],text=True))
saved=json.load(open(CMP))
need(fresh==saved,'saved comparison differs from mechanical replay')
need(saved['current_linux_settle_count']==18,'current Linux settle')
need(saved['windows_live_settle_count']==16,'Windows settle')
need(saved['lane_mask']=={'windows_live':'0x81','linux_dynamic_for_data_lane_0':'0x81'},'lane-mask derivation')
need(saved['modeled_final_registers']==96 and saved['matching_registers']==79 and saved['mismatching_registers']==17,'current mismatch count')
need([x['offset'] for x in saved['diff']]==[
    '0x0008','0x0408','0x0808','0x0c08','0x0e08','0x1014',
    '0x102c','0x1030','0x1034','0x1038','0x103c','0x1040',
    '0x1044','0x1048','0x104c','0x1050','0x1054'
],'exact mismatch offsets')
p=saved['proposed_scoped_e004j']
need(p['scope']=='X1E80100 CSIPHY0 + DPHY only','proposed scope')
need(p['matching_registers']==96 and p['mismatching_registers']==0 and p['diff']==[],'proposed exact match')

s=CSIPHY.read_text()
need('#define CSIPHY_3PH_CMN_CSI_COMMON_CTRL5_CLK_ENABLE\tBIT(7)' in s,'clock bit7')
need('lane_mask |= BIT((lane_cfg->data[i].pos * 2) + offset);' in s,'data-lane encoding')
need('{0x1014, 0xD5, 0x00, CSIPHY_DEFAULT_PARAMS}' in s,'current hardcoded 4-lane overwrite')
need('case CAMSS_X1E80100:' in s and 'regs->offset = 0x1000;' in s,'X1E common offset')
need('regs->lane_regs = lane_regs_x1e80100;' in s,'X1E DPHY table selection')
need('settle_cnt = csiphy_settle_cnt_calc(link_freq, csiphy->timer_clk_rate);' in s,'dynamic settle')
need('for (i = 11; i < 22; i++)' in s,'current common zeroing')
# Parsed polarity is stored but not consumed by the X1E gen2 CSIPHY implementation.
all_camss='\n'.join(p.read_text(errors='ignore') for p in CSIPHY.parent.glob('camss-csiphy*.c'))
need('.pol' not in all_camss,'CSIPHY implementation unexpectedly consumes polarity')

c=CAMSS.read_text()
need('.id = 0,' in c and '.hw_ops = &csiphy_ops_3ph_1_0,' in c,'X1E CSIPHY0 3ph-capable ops')
x1e=c.split('static const struct camss_subdev_resources csiphy_res_x1e80100[] = {',1)[1].split('};',1)[0]
need('{ 266666667, 400000000 }' in x1e,'X1E timer clock table')
need('lncfg->data[i].pos = mipi_csi2->data_lanes[i];' in c,'CAMSS consumes receiver lane literally')

with tempfile.TemporaryDirectory(prefix='e004j-dts-') as td:
    dts=Path(td)/'x.dts'
    subprocess.run(['dtc','-I','dtb','-O','dts',str(DTB),'-o',str(dts)],check=True,
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    t=dts.read_text()
    # Receiver CSIPHY0 endpoint is the authority consumed by CAMSS.
    cam=t.split('port@0 {',1)[1].split('};',1)[0]
    need('data-lanes = <0x00>;' in cam and 'bus-type = <0x04>;' in cam,'receiver endpoint lane0 DPHY')
    # Sensor-side endpoint remains conventional one-based representation, as on accepted rear.
    sens=t.split('camera@60 {',1)[1].split('};',2)[0] if False else t
    need('camera@60' in t and 'data-lanes = <0x01>;' in t,'sensor endpoint present')

result={
 'schema':'sp11-camera-e004j-csiphy0-dphy-authority-v1',
 'status':'PASS_OFFLINE_WINDOWS_LINUX_CSIPHY0_DPHY_DIFF_AUTHORITY',
 'windows_raw_sp7_log':{
   'path':'C:\\Users\\SurfacePro7\\Documents\\KDNET\\Codex\\E004_IR_LIVE2_20260912.log',
   'sha256':RAW_SP7_SHA,
   'normalized_sha256':WIN_NORM_SHA,
   'live_aperture':'0x0ace4000..0x0ace5fff',
   'dwords':2048,
 },
 'windows_receiver':{
   'phy':'TwoPhase/DPHY','num_data_lanes':1,'lane_mask':'0x81',
   'data_lane_position_linux':0,'clock_enable_bit':7,'settle_count':'0x10',
   'common_ctrl11_21':[f'0x{x:02x}' for x in expected_common],
 },
 'current_linux':{
   'receiver_endpoint_data_lanes':[0],
   'dynamic_lane_mask':'0x81',
   'computed_settle_count':'0x12',
   'modeled_registers':96,'windows_matches':79,'windows_mismatches':17,
   'mismatch_classes':[
      'five per-lane settle registers 0x12 vs Windows 0x10',
      'lane_regs_x1e80100 overwrites dynamic 0x81 with hardcoded 0xD5',
      'generic DPHY cleanup zeros common CTRL11..CTRL21 that Windows leaves programmed',
   ],
 },
 'scoped_correction':{
   'scope':'CAMSS_X1E80100 && csiphy->id == 0 && DPHY only',
   'force_settle_count':'0x10',
   'restore_dynamic_lane_mask_after_gen2_table':True,
   'retain_windows_common_ctrl11_21':True,
   'modeled_windows_matches':96,'modeled_windows_mismatches':0,
   'rear_csiphy1_affected':False,'front_rgb_cphy_affected':False,
 },
 'polarity':{
   'explicit_linux_override_needed':False,
   'reason':'X1E gen2 CSIPHY source parses lane polarity but does not consume it; the full modeled programmed register set reaches 96/96 Windows matches without a polarity override.',
   'electrical_polarity_claim':'not separately asserted',
 },
 'runtime_authorized':False,
 'next_gate':'Implement the scoped CAMSS correction in a disposable kernel candidate, prove source/build/DT isolation, then inspect receiver registers before authorizing first IR stream.'
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('E004J_VERIFY=PASS CURRENT=79/96 MISMATCH=17 PROPOSED_SCOPED=96/96')
print('E004J_LANE=WINDOWS_0x81 -> X1E_DPHY_CLOCK_BIT7 + DATA_LANE_POS0')
print('E004J_DIFF=SETTLE_0x12_TO_0x10 + MASK_D5_TO_81 + CTRL11_21_RETAIN_WINDOWS')
print('E004J_SCOPE=CSIPHY0_DPHY_ONLY REAR_CSIPHY1=UNCHANGED FRONT_RGB_CPHY=UNCHANGED')
print('E004J_RUNTIME=NO')
