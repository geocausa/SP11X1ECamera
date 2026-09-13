#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, subprocess

D=Path(__file__).resolve().parent
H={
 'RUNTIME-PREFLIGHT.txt':'2249433b5b09bdcf1b540f2640eb5d189e5c29789a49fa4c37ee4e597cc1fe8b',
 'ATTEMPT1-CONSUMED.marker':'f093ec60f7ed1858e85e8e13e90578a8082e571a3264e9e4cc3739d1818f610a',
 'RUNTIME-DMESG.txt':'3569ac32b811d09aa29ddad1dc8e724b01d72753b9e3550974329e943abca901',
 'MEDIA.txt':'90f9b5890b72bd19f40a9b859e1ffac016eec26171d56c3316b822851ba09972',
 'CONTROLS.txt':'ab88635fe37b11e71c2e762a99e400e47738f7815965a0ebeb3d0e4dd6d5bf12',
 'RECEIVER-READBACK.txt':'e0ec8680419acbf7ca83904ea604544e6ff102d8d2bee7c9f64cfb3b906e8196',
 'ATTEMPT1-PASS.json':'5fd6aa04660815f40f5d4ee3255f3fd98304808e7790cd4ca66091ccf21f6246',
 'GOLDEN-RETURN.txt':'7276fb87b75dd4f07303470a11d6a777b35f86382de0845059ad68a1c0a2c6b8',
 'RETIRE.txt':'8204514b782ddbe7e19cef2d58a87a506731c171cbdd251c9c3b0dcecfae04a6',
}
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for n,h in H.items(): need(sha(D/n)==h,'evidence hash '+n)
a=json.load(open(D/'ATTEMPT1-PASS.json'))
need(a['status']=='PASS_CSIPHY0_WINDOWS_96_OF_96_RECEIVER_ONLY','attempt')
need(a['precheck_or_load_failure']==0,'load/precheck')
need(a['sensor_windows_state_pass'] is True and a['sensor_data_writes']==596,'sensor state')
need(a['sensor_runtime_suspended_before_receiver'] is True,'sensor before')
need(a['media_graph_pass'] is True and a['controls_pass'] is True,'graph/controls')
need(a['camss_e004j_parameter_armed'] is True,'CAMSS param')
need(a['receiver_programming_marker_pass'] is True,'programming marker')
need(a['receiver_expected_registers']==96 and a['receiver_register_matches']==96 and a['receiver_register_mismatches']==0,'96/96')
need(a['receiver_readback_pass'] is True and a['receiver_powered_off'] is True,'receiver lifecycle')
need(a['sensor_runtime_suspended_after_receiver'] is True,'sensor after')
need(a['sensor_stream_callback_performed'] is False,'sensor stream callback')
need(a['csid_stream_callback_performed'] is False and a['vfe_stream_callback_performed'] is False,'downstream stream callbacks')
need(a['capture_stream_performed'] is False and a['illumination_performed'] is False,'capture/illumination')
need(a['kernel_fault_or_warning'] is False,'kernel fault/warning')
pre=(D/'RUNTIME-PREFLIGHT.txt').read_text()
client=re.search(r'^i2c_client_name=([0-9]+-0060)$',pre,re.M)
need(client,'dynamic client')
client_name=client.group(1)
need('i2c_address=0x60' in pre and 'compatible=microsoft,sp11-vd55g0' in pre,'identity')
need(a['discovered_i2c_client']==client_name,'client mismatch')
log=(D/'RUNTIME-DMESG.txt').read_text()
for marker in (
 'SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596 patch=552 safe_config=42 extclk=19200000 mipi=840000000 link_freq=420000000 pixel_rate=84000000 line=1200 frame=1955 roi=644x604 gpio=01,02,01,01 final_state=SW_STBY stream=0 illumination=0',
 f'E004T_RECEIVER_PRECHECK: sensor={client_name} sensor_pm=suspended csiphy=msm_csiphy0 id=0 phy=DPHY lanes=1 lane0_pos=0 downstream_link=none fmt=Y10_1X10/644x604',
 'E004J_CSIPHY0_DPHY_WINDOWS_PARITY link_freq=420000000 timer=266666667 lane_mask=0x81 settle=0x10 ctrl11_21=ff,fe,e6,df,df,fc,fb,9b,7f,bf,ff',
 'E004T_CSIPHY0_READBACK: expected=96 matches=96 mismatches=0 timer_clk_rate=266666667 lane_mask_reg=0x00000081 settle_lane0=0x00000010 common_ctrl7=0x0000007a',
 'E004T_RECEIVER_END: result=0 receiver_off=1 csiphy_power_off=1 sensor_pm_suspended=1 sensor_stream_call=0 csid_stream_call=0 vfe_stream_call=0 illumination=0',
): need(marker in log,'missing marker '+marker)
for bad in ('E004T_CSIPHY0_MISMATCH','E004T_SENSOR_PM_CHANGED','SP11_VD55G0_NATIVE_STREAM_BLOCK','WARNING:','Call trace:','Oops:','BUG:','STREAM_START','ILLUMINATION_ON'):
    need(bad not in log,'forbidden marker '+bad)
rb=(D/'RECEIVER-READBACK.txt').read_text()
need(f'i2c_client_name={client_name}' in rb,'receiver client')
need('runtime_status=suspended' in rb and 'runtime_usage=0' in rb,'sensor runtime PM')
need('camss_e004j_param=Y' in rb,'CAMSS parameter')
need('E004T_CSIPHY0_READBACK: expected=96 matches=96 mismatches=0' in rb,'readback summary')
need('E004T_RECEIVER_END: result=0 receiver_off=1 csiphy_power_off=1 sensor_pm_suspended=1' in rb,'receiver end')
media=(D/'MEDIA.txt').read_text()
need(f'sp11-vd55g0 {client_name} (1 pad, 1 link, 0 routes)' in media,'sensor entity')
need('-> "msm_csiphy0":0 [ENABLED,IMMUTABLE]' in media,'sensor->CSIPHY0 link')
need('fmt:Y10_1X10/644x604' in media,'format')
need('status=PASS' in (D/'GOLDEN-RETURN.txt').read_text(),'Golden return')
need('status=PASS_CANDIDATE_RETIRED' in (D/'RETIRE.txt').read_text(),'retire')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'current boot not Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')
need(not Path('/boot/sp11-7.1.5-camera-e004w-csiphy0-readback-r2').exists(),'candidate boot present')
need(not Path('/etc/grub.d/99zzzzzz_sp11_camera_e004w_csiphy0_readback_r2').exists(),'candidate entry present')
for m in ('qcom_camss','sp11_vd55g0','e004t_csiphy_readback_test','i2c_qcom_cci'):
    need(not Path('/sys/module',m).exists(),'camera module active '+m)
r=json.load(open(D/'RESULT.json'))
need(r['status']=='PASS_CSIPHY0_WINDOWS_96_OF_96_GOLDEN_RETURN_RETIRED','final result')
need(r['receiver']['matching_registers']==96 and r['receiver']['mismatching_registers']==0,'final receiver')
need(r['kernel_fault_or_warning'] is False,'final kernel')
need(r['golden_return_pass'] is True and r['candidate_retired'] is True,'final cleanup')
print('E004W_RUNTIME_VERIFY=PASS ATTEMPTS=1')
print('E004W_SENSOR=WINDOWS_STATE_PASS WRITES=596 SUSPENDED_BEFORE_AND_AFTER=YES')
print('E004W_CSIPHY0=WINDOWS_96/96 LINK420M TIMER266666667 LANE_MASK=0x81 SETTLE=0x10')
print('E004W_RECEIVER_OFF=YES KERNEL_WARN_OR_FAULT=NO')
print('E004W_SENSOR_STREAM=NO CSID_STREAM=NO VFE_STREAM=NO CAPTURE=NO ILLUMINATION=NO')
print('E004W_GOLDEN_RETURN=PASS CANDIDATE_RETIRED=YES')
