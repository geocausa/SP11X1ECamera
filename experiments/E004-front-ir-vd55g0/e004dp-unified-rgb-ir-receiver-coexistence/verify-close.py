#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess
D=Path(__file__).resolve().parent; E=D/'evidence'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
r=json.loads((D/'RESULT.json').read_text()); s=json.loads((E/'SUMMARY.json').read_text()); a=json.loads((E/'ATTEMPT1-PASS.json').read_text())
need(r['status']=='PASS_THREE_CAMERA_BIND_CSIPHY0_WINDOWS_96_OF_96_GOLDEN_RETURN_RETIRED','result status')
need(s['status']==r['status'],'summary status')
need(a['status']=='PASS_THREE_CAMERA_BIND_CSIPHY0_WINDOWS_96_OF_96_RECEIVER_ONLY','attempt status')
need(r['attempt_count']==1 and r['same_boot_retry_performed'] is False,'attempt policy')
need(r['candidate_boot_id']==s['candidate_boot_id']==a['boot_id']=='1ae2e209-cd0f-4169-9c48-25f1a61f00e9','candidate boot')
need(r['golden_return_boot_id']==s['golden_return_boot_id']=='c3bd50f5-aaa6-41f5-8045-89f3e6e202de','Golden boot')
need(r['three_sensor_entities_bound'] and a['three_sensor_entities_bound'],'three sensor bind')
need(r['clients']=={'ir':'2-0060','rear':'3-0010','front':'1-0010'},'clients')
need(r['immutable_sensor_links']==3 and r['rgb_route_state']=='neutral' and r['ir_downstream_link']=='none','routing')
need(all(r['sensor_runtime_suspended'].values()),'runtime suspend')
need(r['receiver']=={'expected_registers':96,'matching_registers':96,'mismatching_registers':0,'powered_off':True},'receiver')
for k in ('ir_sensor_stream_callback_performed','rgb_stream_performed','csid_stream_callback_performed','vfe_stream_callback_performed','capture_stream_performed','illumination_performed','linux_secureisp','kernel_fault_or_warning'):
    need(r[k] is False,k)
need(r['golden_return_pass'] and r['candidate_retired'],'cleanup')
# Every ignored live artifact copied into evidence must hash exactly as recorded.
cp=subprocess.run(['sha256sum','-c','RAW-EVIDENCE.sha256'],cwd=E,text=True,capture_output=True)
need(cp.returncode==0,'evidence hashes '+cp.stdout+cp.stderr)
pre=(E/'RUNTIME-PREFLIGHT.txt').read_text();need('status=PASS_READY_FOR_THREE_SENSOR_BIND_RECEIVER_ONLY' in pre,'preflight');need('ir_client_path=/sys/bus/i2c/devices/2-0060' in pre and 'rear_client_path=/sys/bus/i2c/devices/3-0010' in pre and 'front_client_path=/sys/bus/i2c/devices/1-0010' in pre,'preflight clients')
media=(E/'MEDIA.txt').read_text(errors='replace')
for ent in ('sp11-vd55g0 2-0060 (1 pad, 1 link, 0 routes)','ov13858 3-0010 (1 pad, 1 link, 0 routes)','imx681 1-0010 (1 pad, 1 link, 0 routes)'):need(ent in media,'media entity '+ent)
for link in ('-> "msm_csiphy0":0 [ENABLED,IMMUTABLE]','-> "msm_csiphy1":0 [ENABLED,IMMUTABLE]','-> "msm_csiphy2":0 [ENABLED,IMMUTABLE]'):need(link in media,'media link '+link)
route=subprocess.run([str(D/'route-state.py'),str(E/'MEDIA.txt'),'--expect','neutral'],text=True,capture_output=True);need(route.returncode==0,'route '+route.stdout+route.stderr)
log=(E/'RUNTIME-DMESG.txt').read_text(errors='replace')
for marker in (
 'SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596 patch=552 safe_config=42 extclk=19200000 mipi=840000000 link_freq=420000000 pixel_rate=84000000 line=1200 frame=1955 roi=644x604 gpio=01,02,01,01 final_state=SW_STBY stream=0 illumination=0',
 'E004J_CSIPHY0_DPHY_WINDOWS_PARITY link_freq=420000000 timer=266666667 lane_mask=0x81 settle=0x10 ctrl11_21=ff,fe,e6,df,df,fc,fb,9b,7f,bf,ff',
 'E004T_CSIPHY0_READBACK: expected=96 matches=96 mismatches=0 timer_clk_rate=266666667 lane_mask_reg=0x00000081 settle_lane0=0x00000010 common_ctrl7=0x0000007a',
 'E004T_RECEIVER_END: result=0 receiver_off=1 csiphy_power_off=1 sensor_pm_suspended=1 sensor_stream_call=0 csid_stream_call=0 vfe_stream_call=0 illumination=0'):
    need(marker in log,'dmesg '+marker)
for bad in ('E004T_CSIPHY0_MISMATCH','E004T_SENSOR_PM_CHANGED','SP11_VD55G0_NATIVE_STREAM_BLOCK','WARNING:','Call trace:','Oops:','BUG:','IOMMU fault','ILLUMINATION_ON'):
    need(bad not in log,'bad dmesg '+bad)
need('status=PASS_GOLDEN_RETURN' in (E/'GOLDEN-RETURN.txt').read_text(),'Golden record');need('status=PASS_CANDIDATE_RETIRED' in (E/'RETIRE.txt').read_text(),'retire record')
# Current machine must still be protected Golden and candidate fully absent.
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'current boot not Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True);need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'current GRUB')
need(not Path('/boot/sp11-7.1.5-camera-e004dp-unified-rgb-ir-receiver').exists(),'candidate boot present');need(not Path('/etc/grub.d/99zzzzzz_sp11_camera_e004dp_unified_rgb_ir_receiver').exists(),'candidate entry present')
for m in ('qcom_camss','imx681','ov13858','sp11_vd55g0','e004t_csiphy_readback_test','i2c_qcom_cci'):need(not Path('/sys/module',m).exists(),'camera module active '+m)
print('E004dp CLOSE VERIFY: PASS (three-camera coexistence + Windows 96/96 receiver + Golden return + retired)')
