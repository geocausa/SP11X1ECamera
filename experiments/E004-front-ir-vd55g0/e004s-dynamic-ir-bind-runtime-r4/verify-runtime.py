#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, subprocess

D=Path(__file__).resolve().parent

EXPECTED_HASHES={
 'RUNTIME-PREFLIGHT.txt':'beb68df23dc45ea46393e3fb0113a079433dd36ba9c523c574a1e0f3d8312be5',
 'ATTEMPT1-CONSUMED.marker':'bd574ff720005b9c8d765dc47612c4d825c743e29a626c28297b33c89eaa220b',
 'RUNTIME-DMESG.txt':'d58be41be8b33c069b334de32650085ff4d2c7eb5b78e6bff9b30ad49d6a4330',
 'MEDIA.txt':'90f9b5890b72bd19f40a9b859e1ffac016eec26171d56c3316b822851ba09972',
 'CONTROLS.txt':'ab88635fe37b11e71c2e762a99e400e47738f7815965a0ebeb3d0e4dd6d5bf12',
 'STREAM-BLOCK.txt':'a3b78026ffbad4f2d896c070fefed72c1cf7dec96fb4580f72becd433d218b09',
 'ATTEMPT1-PASS.json':'3ff1805ce7d160b290899c1bf9afca954c4fa45c6b812533831fac6bfdcd7aed',
 'GOLDEN-RETURN.txt':'bc124e038fb6437323b0e96ac9575b6816036f62c4321ed6317366f3a8c3ffec',
 'RETIRE.txt':'704ad7a4edbccbd332fe73f2cc5865ee9a0f4c2fca38db51c3cd65540b98983c',
}

def need(v,m):
    if not v:
        raise AssertionError(m)

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

for name,h in EXPECTED_HASHES.items():
    need(sha(D/name)==h,'evidence hash '+name)

a=json.load(open(D/'ATTEMPT1-PASS.json'))
need(a['status']=='PASS_DYNAMIC_ID_NATIVE_BIND_GRAPH_CONTROLS_STREAM_BLOCKED','attempt PASS')
need(a['precheck_or_load_failure']==0,'runtime load failure')
need(a['device_identity_pass'] is True,'dynamic identity')
need(a['sensor_windows_state_pass'] is True,'sensor Windows state')
need(a['media_graph_pass'] is True,'media graph')
need(a['sensor_entity_one_link'] is True and a['immutable_enabled_link_to_csiphy0'] is True,'sensor link')
need(a['sensor_format_visible'] is True and a['subdev_node_registered'] is True,'format/subdev')
need(a['controls_pass'] is True,'typed controls')
need(a['runtime_suspended'] is True and a['same_client_end_to_end'] is True,'runtime/client')
need(a['camss_e004j_parameter_armed'] is True,'CAMSS parity parameter')
need(a['camss_receiver_programming_invoked'] is False,'receiver programming')
need(a['direct_sensor_s_stream_result']=='-EOPNOTSUPP','direct stream refusal')
need(a['kernel_fault_or_warning'] is False,'kernel warning/fault')
need(a['capture_stream_performed'] is False and a['illumination_performed'] is False,'capture/illumination')

pre=(D/'RUNTIME-PREFLIGHT.txt').read_text()
client=re.search(r'^i2c_client_name=([0-9]+-0060)$',pre,re.M)
path=re.search(r'^i2c_client_path=(/sys/bus/i2c/devices/[0-9]+-0060)$',pre,re.M)
need(client and path,'dynamic preflight client')
client_name=client.group(1)
need(path.group(1).endswith('/'+client_name),'client path/name mismatch')
need('i2c_address=0x60' in pre and 'compatible=microsoft,sp11-vd55g0' in pre,'identity tuple')
need(a['discovered_i2c_client']==client_name,'attempt/preflight client mismatch')

log=(D/'RUNTIME-DMESG.txt').read_text()
for marker in (
 'SP11_VD55G0_NATIVE_ID_GATE=PASS model_be=0x3047 revision=0x1111_CUT1 writes=0',
 'SP11_VD55G0_NATIVE_PATCH_BEGIN start=0x2000 bytes=552 sha256=5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321',
 'SP11_VD55G0_NATIVE_STROBE_BASELINE=PASS reg=0x0468 value=0x02 write_authorized=0',
 'SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596 patch=552 safe_config=42 extclk=19200000 mipi=840000000 link_freq=420000000 pixel_rate=84000000 line=1200 frame=1955 roi=644x604 gpio=01,02,01,01 final_state=SW_STBY stream=0 illumination=0',
 'SP11_VD55G0_NATIVE_POWER_OFF reset_asserted=1 stream=0 illumination=0',
 'SP11_VD55G0_NATIVE_BIND=PASS format=Y10_1X10 size=644x604 link_freq=420000000 pixel_rate=84000000 line=1200 frame=1955 stream_capable=0 illumination_capable=0',
 'E004S_V4L2_CONTRACT: link_idx=0 link_freq=420000000 pixel_rate=84000000 hblank=556 vblank=1351 mbus_ret=0 type=5 lanes=1 mbus_link_freq=420000000',
 'SP11_VD55G0_NATIVE_STREAM_BLOCK=PASS requested=1 reason=E004l_bind_only stream=0 illumination=0',
 'E004S_STREAM_BLOCK_TEST: s_stream(1) ret=-95 expected=-95',
):
    need(marker in log,'missing dmesg marker '+marker)
ident=re.search(r'E004S_DEVICE_IDENTITY: dev=([0-9]+-0060) addr=0x60 compatible=microsoft,sp11-vd55g0',log)
need(ident and ident.group(1)==client_name,'kernel/shell identity mismatch')
for bad in ('E004J_CSIPHY0_DPHY_WINDOWS_PARITY','WARNING:','Call trace:','Oops:','BUG:','STREAM_START','ILLUMINATION_ON'):
    need(bad not in log,'forbidden runtime marker '+bad)

media=(D/'MEDIA.txt').read_text()
sensor=f'sp11-vd55g0 {client_name}'
need(f'{sensor} (1 pad, 1 link, 0 routes)' in media,'sensor entity')
need('-> "msm_csiphy0":0 [ENABLED,IMMUTABLE]' in media,'CSIPHY0 immutable link')
need('fmt:Y10_1X10/644x604' in media,'sensor format')
need(re.search(r'device node name /dev/v4l-subdev\d+',media) is not None,'subdev node')

ctrl=(D/'CONTROLS.txt').read_text()
for marker in ('vertical_blanking','value=1351','horizontal_blanking','value=556',
               '420000000','pixel_rate','value=84000000'):
    need(marker in ctrl,'control '+marker)

block=(D/'STREAM-BLOCK.txt').read_text()
need(f'i2c_client_name={client_name}' in block,'stream-block client')
need('runtime_status=suspended' in block and 'runtime_usage=0' in block,'runtime PM')
need('camss_e004j_param=Y' in block,'CAMSS param')
need('E004S_STREAM_BLOCK_TEST: s_stream(1) ret=-95 expected=-95' in block,'stream block evidence')

need((D/'ATTEMPT1-CONSUMED.marker').read_text().strip(),'attempt marker empty')
need('status=PASS' in (D/'GOLDEN-RETURN.txt').read_text(),'Golden return')
need('camera_modules=absent' in (D/'GOLDEN-RETURN.txt').read_text(),'Golden modules')
need('status=PASS_CANDIDATE_RETIRED' in (D/'RETIRE.txt').read_text(),'candidate retired')

r=json.load(open(D/'RESULT.json'))
need(r['status']=='PASS_DYNAMIC_ID_NATIVE_BIND_GRAPH_CONTROLS_STREAM_BLOCK_GOLDEN_RETURN_RETIRED','final result')
need(r['sensor']['sensor_data_writes']==596 and r['sensor']['runtime_pm']=='suspended','sensor result')
need(r['graph']['pass'] is True and r['graph']['sensor_entity_links']==1,'graph result')
need(r['direct_sensor_stream_result']=='-EOPNOTSUPP','stream result')
need(r['camss_receiver_programming_invoked'] is False and r['illumination_performed'] is False,'safety result')
need(r['golden_return_pass'] is True and r['candidate_retired'] is True,'cleanup result')

need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'current boot not Golden')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env and 'next_entry=\n' in env,'Golden/no next')
need(not Path('/boot/sp11-7.1.5-camera-e004s-dynamic-ir-bind-r4').exists(),'candidate boot still present')
need(not Path('/etc/grub.d/99zzzzzz_sp11_camera_e004s_dynamic_ir_bind_r4').exists(),'candidate GRUB entry still present')
for m in ('qcom_camss','sp11_vd55g0','e004s_stream_block_test','i2c_qcom_cci'):
    need(not Path('/sys/module',m).exists(),'camera module active on Golden '+m)

print('E004S_RUNTIME_VERIFY=PASS ATTEMPTS=1 DYNAMIC_IDENTITY=PASS CLIENT='+client_name)
print('E004S_SENSOR=WINDOWS_STATE_PASS WRITES=596 FINAL=SW_STBY RUNTIME_SUSPENDED=YES')
print('E004S_GRAPH=PASS ONE_LINK=CSIPHY0_ENABLED_IMMUTABLE FORMAT=Y10_644x604')
print('E004S_V4L2=LINK420M PIX84M HBLANK556 VBLANK1351 DPHY1 STREAM_BLOCK=-95')
print('E004S_KERNEL_WARN=NO RECEIVER_PROGRAMMING=NO CAPTURE=NO ILLUMINATION=NO')
print('E004S_GOLDEN_RETURN=PASS CANDIDATE_RETIRED=YES')
