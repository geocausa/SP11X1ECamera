#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess
D=Path(__file__).resolve().parent
def need(v,m):
    if not v: raise AssertionError(m)
need((D/'ATTEMPT1-CONSUMED.marker').is_file(),'consumed')
need(not (D/'ATTEMPT1-FAILURE.json').exists(),'failure record already exists')
pre=dict(x.split('=',1) for x in (D/'RUNTIME-PREFLIGHT.txt').read_text().splitlines() if '=' in x)
ir=Path(pre['ir_client_path']);rear=Path(pre['rear_client_path']);front=Path(pre['front_client_path'])
irn=ir.name;rn=rear.name;fn=front.name
log=(D/'RUNTIME-DMESG.txt').read_text(errors='replace');media=(D/'MEDIA.txt').read_text(errors='replace');rb=(D/'RECEIVER-READBACK.txt').read_text(errors='replace');ctrl=(D/'CONTROLS-IR.txt').read_text(errors='replace')
for marker in (
 'SP11_VD55G0_NATIVE_ID_GATE=PASS model_be=0x3047 revision=0x1111_CUT1 writes=0',
 'SP11_VD55G0_NATIVE_STROBE_BASELINE=PASS reg=0x0468 value=0x02 write_authorized=0',
 'SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596 patch=552 safe_config=42 extclk=19200000 mipi=840000000 link_freq=420000000 pixel_rate=84000000 line=1200 frame=1955 roi=644x604 gpio=01,02,01,01 final_state=SW_STBY stream=0 illumination=0',
 'SP11_VD55G0_NATIVE_BIND=PASS format=Y10_1X10 size=644x604 link_freq=420000000 pixel_rate=84000000 line=1200 frame=1955 stream_capable=0 illumination_capable=0',
 f'E004T_RECEIVER_PRECHECK: sensor={irn} sensor_pm=suspended csiphy=msm_csiphy0 id=0 phy=DPHY lanes=1 lane0_pos=0 downstream_link=none fmt=Y10_1X10/644x604',
 'E004J_CSIPHY0_DPHY_WINDOWS_PARITY link_freq=420000000 timer=266666667 lane_mask=0x81 settle=0x10 ctrl11_21=ff,fe,e6,df,df,fc,fb,9b,7f,bf,ff',
 'E004T_CSIPHY0_READBACK: expected=96 matches=96 mismatches=0 timer_clk_rate=266666667 lane_mask_reg=0x00000081 settle_lane0=0x00000010 common_ctrl7=0x0000007a',
 'E004T_RECEIVER_END: result=0 receiver_off=1 csiphy_power_off=1 sensor_pm_suspended=1 sensor_stream_call=0 csid_stream_call=0 vfe_stream_call=0 illumination=0',
): need(marker in log,'missing '+marker)
for bad in ('E004T_CSIPHY0_MISMATCH','E004T_SENSOR_PM_CHANGED','SP11_VD55G0_NATIVE_STREAM_BLOCK','MODE_SELECT=1 front transmission started','WARNING:','Call trace:','Oops:','BUG:','SError Interrupt','IOMMU fault','STREAM_START','ILLUMINATION_ON'):
    need(bad not in log,'forbidden '+bad)
# All three entities and immutable sensor links coexist.
for ent in (f'sp11-vd55g0 {irn} (1 pad, 1 link, 0 routes)',f'ov13858 {rn} (1 pad, 1 link, 0 routes)',f'imx681 {fn} (1 pad, 1 link, 0 routes)'): need(ent in media,'entity '+ent)
for link in ('-> "msm_csiphy0":0 [ENABLED,IMMUTABLE]','-> "msm_csiphy1":0 [ENABLED,IMMUTABLE]','-> "msm_csiphy2":0 [ENABLED,IMMUTABLE]'): need(link in media,'immutable '+link)
cp=subprocess.run([str(D/'route-state.py'),str(D/'MEDIA.txt'),'--expect','neutral'],text=True,capture_output=True);need(cp.returncode==0,'RGB route not neutral '+cp.stdout+cp.stderr)
# IR controls remain bind-only fixed mode authority.
for token in ('1351','556','420000000','84000000'): need(token in ctrl,'IR control '+token)
for p,name in ((ir,'IR'),(rear,'REAR'),(front,'FRONT')): need((p/'power/runtime_status').read_text().strip()=='suspended',name+' current PM')
for token in (f'ir_client={irn}',f'rear_client={rn}',f'front_client={fn}','ir_runtime_status=suspended','rear_runtime_status=suspended','front_runtime_status=suspended','camss_e004j_param=Y','E004T_CSIPHY0_READBACK: expected=96 matches=96 mismatches=0','E004T_RECEIVER_END: result=0 receiver_off=1 csiphy_power_off=1 sensor_pm_suspended=1'): need(token in rb,'readback '+token)
out={
 'schema':'sp11-camera-e004dp-attempt1-v1','status':'PASS_THREE_CAMERA_BIND_CSIPHY0_WINDOWS_96_OF_96_RECEIVER_ONLY','candidate_consumed':True,'same_boot_retry_performed':False,'golden_return_required':True,
 'clients':{'ir':irn,'rear':rn,'front':fn},'three_sensor_entities_bound':True,'immutable_sensor_links':3,'rgb_route_state':'neutral','ir_downstream_link':'none',
 'sensor_runtime_suspended':{'ir':True,'rear':True,'front':True},'camss_e004j_parameter_armed':True,'receiver_expected_registers':96,'receiver_register_matches':96,'receiver_register_mismatches':0,'receiver_powered_off':True,
 'ir_sensor_stream_callback_performed':False,'rgb_stream_performed':False,'csid_stream_callback_performed':False,'vfe_stream_callback_performed':False,'capture_stream_performed':False,'illumination_performed':False,'linux_secureisp':False,'kernel_fault_or_warning':False,
 'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),
}
(D/'ATTEMPT1-PASS.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('E004DP_VERIFY=PASS THREE_SENSOR_BIND=YES RGB_NEUTRAL=YES CSIPHY0_WINDOWS=96/96 RECEIVER_OFF=YES')
print('E004DP_STREAMS=NO CAPTURE=NO ILLUMINATION=NO SECUREISP=NO RETRY=NO')
