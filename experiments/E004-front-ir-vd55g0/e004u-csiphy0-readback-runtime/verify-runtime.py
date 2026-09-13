#!/usr/bin/env python3
from pathlib import Path
import json, subprocess

D=Path(__file__).resolve().parent
P=D.parent
O=P/'e004o-ir-only-graph-authority'
J=P/'e004j-csiphy0-dphy-authority'
SRC=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003c-dtb-build/source/drivers/media/platform/qcom/camss/camss-csiphy-3ph-1-0.c')
CORE=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003c-dtb-build/source/drivers/media/platform/qcom/camss/camss-csiphy.c')

def need(v,m):
    if not v:
        raise AssertionError(m)

a=json.load(open(D/'ATTEMPT1-FAILURE.json'))
need(a['status']=='FAIL_BOUNDED_NO_RETRY','attempt status')
need(a['sensor_windows_state_pass'] is True and a['sensor_data_writes']==596,'sensor state')
need(a['sensor_runtime_suspended_before_receiver'] is True,'sensor pre-receiver suspend')
need(a['receiver_programming_marker_pass'] is False,'receiver programming unexpectedly passed')
need(a['receiver_readback_pass'] is False,'receiver readback unexpectedly passed')
need(a['sensor_stream_callback_performed'] is False,'sensor stream callback')
need(a['csid_stream_callback_performed'] is False,'csid stream callback')
need(a['vfe_stream_callback_performed'] is False,'vfe stream callback')
need(a['capture_stream_performed'] is False and a['illumination_performed'] is False,'capture/illumination')
need(a['kernel_fault_or_warning'] is True,'fault classification')

log=(D/'RUNTIME-DMESG.txt').read_text()
need('E004T_RECEIVER_PRECHECK: sensor=2-0060 sensor_pm=suspended csiphy=msm_csiphy0 id=0 phy=DPHY lanes=1 lane0_pos=0 downstream_link=none fmt=Y10_1X10/644x604' in log,'receiver precheck')
need('Unable to handle kernel paging request at virtual address ffff80008420e000' in log,'fault VA')
need('FSC = 0x07: level 3 translation fault' in log,'translation fault')
need('WnR = 1' in log,'write fault')
need('pc : csiphy_reset+0x3c/0x170 [qcom_camss]' in log,'fault PC')
need('lr : csiphy_set_power+0x154/0x3a0 [qcom_camss]' in log,'fault caller')
need('E004J_CSIPHY0_DPHY_WINDOWS_PARITY' not in log,'lane programming unexpectedly reached')
need('E004T_CSIPHY0_READBACK' not in log,'readback unexpectedly reached')
need('SP11_VD55G0_NATIVE_STREAM_BLOCK' not in log,'sensor stream callback')
need('STREAM_START' not in log and 'ILLUMINATION_ON' not in log,'stream/illumination')

src=SRC.read_text()
reset=src[src.index('static void csiphy_reset'):src.index('static irqreturn_t csiphy_isr')]
need('CSIPHY_3PH_CMN_CSI_COMMON_CTRLn(regs->offset, 0)' in reset,'reset common access')
init=src[src.index('static int csiphy_init'):src.index('const struct csiphy_hw_ops csiphy_ops_3ph_1_0')]
need('case CAMSS_X1E80100:' in init and 'regs->offset = 0x1000;' in init,'X1E common offset')
need('csiphy->base = devm_platform_ioremap_resource_byname(pdev, res->reg[0]);' in CORE.read_text(),'resource mapping')

dtb=O/'x1e80100-microsoft-denali-sp11-e004o-ir-only.dtb'
reg=subprocess.check_output(['fdtget','-t','x',str(dtb),'/soc@0/isp@acb7000','reg'],text=True).split()
names=subprocess.check_output(['fdtget','-t','s',str(dtb),'/soc@0/isp@acb7000','reg-names'],text=True).split()
cells=[int(x,16) for x in reg]
idx=names.index('csiphy0')
base=(cells[idx*4]<<32)|cells[idx*4+1]
size=(cells[idx*4+2]<<32)|cells[idx*4+3]
need(base==0x0ace4000 and size==0x1000,f'current CSIPHY0 resource {base:#x}/{size:#x}')
idx1=names.index('csiphy1')
base1=(cells[idx1*4]<<32)|cells[idx1*4+1]
need(base1==0x0ace6000,'CSIPHY1 base')
need(base+0x2000==base1,'8K correction would overlap or leave gap')

jr=json.load(open(J/'RESULT.json'))
need(jr['windows_raw_sp7_log']['live_aperture']=='0x0ace4000..0x0ace5fff','Windows aperture')
need(jr['windows_raw_sp7_log']['dwords']==2048,'Windows aperture dwords')

rb=(D/'RECEIVER-READBACK.txt').read_text()
need('runtime_status=suspended' in rb and 'runtime_usage=0' in rb,'sensor PM after fault')
need('camss_e004j_param=Y' in rb,'CAMSS param')
need('E004T_RECEIVER_PRECHECK' in rb,'receiver precheck summary')
need('E004T_CSIPHY0_READBACK' not in rb,'readback summary unexpectedly present')

need('status=PASS' in (D/'GOLDEN-RETURN.txt').read_text(),'Golden return')
need('status=PASS_CANDIDATE_RETIRED' in (D/'RETIRE.txt').read_text(),'candidate retired')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'current boot not Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')

r=json.load(open(D/'RESULT.json'))
need(r['status']=='FAIL_CSIPHY0_DT_APERTURE_4K_VS_REQUIRED_8K_GOLDEN_RETURN_RETIRED','final result')
need(r['linux_dt_csiphy0']['size']=='0x1000' and r['windows_csiphy0']['size']=='0x2000','resource result')
need(r['resource_overlap_after_fix'] is False,'resource overlap')
need(r['golden_return_pass'] is True and r['candidate_retired'] is True,'cleanup')

print('E004U_RUNTIME_VERIFY=PASS CLASS=CSIPHY0_DT_APERTURE_TOO_SMALL')
print('E004U_FAULT=CSIPHY_RESET BASE_PLUS_0x1000 UNMAPPED DT_SIZE=0x1000')
print('E004U_WINDOWS_APERTURE=0xACE4000..0xACE5FFF SIZE=0x2000 NEXT_CSIPHY1=0xACE6000')
print('E004U_SENSOR_STREAM=NO CSID_STREAM=NO VFE_STREAM=NO CAPTURE=NO ILLUMINATION=NO')
print('E004U_GOLDEN_RETURN=PASS CANDIDATE_RETIRED=YES RETRY=NO')
