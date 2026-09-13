#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, subprocess, glob

D=Path(__file__).resolve().parent
P=D.parent
RAW=D/'raw/E004_IR_CSID_ROUTE_ORACLE_20260913.log'
HOLDER=D/'E004-IR-RouteHolder.ps1'
TRANS=D/'E004_IR_ROUTE_HOLDER_20260913.txt'
RES=D/'WINDOWS-SECUREISP-RESOURCE-PROOF.txt'
EX=D/'extract_ir_secure_route.py'
SUM=D/'WINDOWS-IR-SECURE-ROUTE-SUMMARY.json'
R=D/'RESULT.json'

H={
 RAW:'d63a755a97acfbb0b4a5f51cdcd557df0da482332fbd556a742d1a8c06101787',
 HOLDER:'d2a987cfb441f12d775cf711ff9585290ce04f81842b6dedeb0fc7230a124652',
 TRANS:'b7854a0bdfb56c229d2e0ef5a3e6fc507cfe03ecaf07e9d264d72e9c57d8128c',
 RES:'3934dea5013db9ecfe1c855dd6c52507a68f4c961be7b4afa3bcc71a667ea89b',
 EX:'2970f6823053f8c094930c0a7ce91eed85d66c0aa863c1d721690436ce3d2bcd',
 SUM:'66c111bba4a9b24376fccc995477224fdcc67124e51efad8176855ee2edf5c0b',
}
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
for p,h in H.items(): need(sha(p)==h,'hash drift '+str(p))

# Extractor must be deterministic and regenerate the exact accepted summary.
before=SUM.read_bytes()
subprocess.run(['python3',str(EX)],check=True,stdout=subprocess.DEVNULL)
need(SUM.read_bytes()==before,'extractor output not deterministic')
need(sha(SUM)==H[SUM],'summary hash after regeneration')

s=json.load(open(SUM))
need(s['status']=='PASS_WINDOWS_IR_STANDARD_CAMSS_BYPASSED_SECUREISP_PRESENT_PROTECTED','summary status')
w=s['winrt']
need(w['device']=='Surface IR Camera Front' and w['source_kind']=='Infrared','IR identity')
need((w['subtype'],w['width'],w['height'],w['fps_num'],w['fps_den'])==('NV12',644,604,60,1),'IR mode')
need(w['start_async']=='Success' and w['acquired_frames']==12 and w['stop_async']=='Success','real frame lifecycle')

# Standard observable CAMSS remains inactive/default even with real frames consumed.
c=s['comparisons']
need(all(v==0 for v in c['live1_vs_live2_mismatches'].values()),'LIVE1/LIVE2 CAMSS mismatch')
need(c['live_wrapper_io_path_cfg0']=={
 'csid0':'0x00000001','csid1':'0x00000001','csid2':'0x00000001','output_ife_en_any':False
},'wrapper route')
need(c['vfe_live_all_zero'] is True,'VFE active')
need(c['e003g_windows_inactive_csid0_sha256_le32']=='f4cdd9594c9e63600c087a6bc653ebce05468e1d6ce0f9a20b7d10cd81afc60a','inactive reference hash')
need(all(c['ir_csid_equal_to_e003g_inactive_default'].values()),'IR CSID differs from inactive default')
for phase in ('LIVE1','LIVE2'):
    for reg in ('CSID0','CSID1','CSID2'):
        need(s['regions'][phase][reg]['nonzero_dwords']==79,'CSID nonzero count')
        need(s['regions'][phase][reg]['image_sha256_le32']=='f4cdd9594c9e63600c087a6bc653ebce05468e1d6ce0f9a20b7d10cd81afc60a','CSID image')
    for reg in ('VFE0','VFE1'):
        need(s['regions'][phase][reg]['nonzero_dwords']==0,'VFE nonzero')
for phase in ('POST1','POST2'):
    expected={'WRAPPER':1024,'CSID0':2048,'CSID1':2048,'CSID2':2048,'VFE0':4096,'VFE1':4096}
    for reg,n in expected.items():
        need(s['regions'][phase][reg]['sentinel_0x80000000_dwords']==n,'post sentinel '+phase+'/'+reg)

sec=s['secureisp']
need(sec['device']=='Qualcomm(R) Spectra(TM) 395 SecureISP Device','SecureISP identity')
need(sec['driver']=='qccamsecureisp8380.sys' and sec['status']=='Started','SecureISP driver')
need(sec['physical_window']=='0x0acca000..0x0accdfff' and sec['size_bytes']==0x4000,'SecureISP aperture')
need(sec['irq_resources']==[392,391],'SecureISP IRQs')
need(sec['kd_direct_readable_during_live_frames'] is False,'direct KD readability')
need(sec['kd_uncached_readable_during_live_frames'] is False,'uncached KD readability')
for m in ('qccamisp8380','qccamsecureisp8380','qccammipicsi8380','surfacecamauxsensor8380','surfacecamavs8380'):
    need(m in sec['live_modules_proved'],'missing live module '+m)

con=s['conclusion']
need(con['standard_camss_csid_active'] is False and con['standard_camss_vfe_active'] is False,'standard CAMSS conclusion')
need(con['real_ir_frames_delivered'] is True,'frame conclusion')
need(con['secureisp_present_and_started'] is True and con['secureisp_mmio_protected_from_kd'] is True,'SecureISP conclusion')
need(con['secure_internal_route_proven'] is False,'overclaim: secure route marked proven')

# Prior gates establish receiver parity and explain why this Windows oracle was required.
ew=json.load(open(P/'e004w-csiphy0-readback-runtime-r2/RESULT.json'))
need(ew['status']=='PASS_CSIPHY0_WINDOWS_96_OF_96_GOLDEN_RETURN_RETIRED','E004w')
ex=json.load(open(P/'e004x-csid-route-gate/RESULT.json'))
need(ex['status']=='BLOCKED_PENDING_SAME_MACHINE_WINDOWS_IR_CSID_ROUTE_ORACLE','E004x')

r=json.load(open(R))
need(r['status']=='PASS_WINDOWS_IR_STANDARD_CAMSS_BYPASSED_SECUREISP_PRESENT_PROTECTED','result')
need(r['secureisp']['internal_route_proven'] is False,'result overclaim')
need(r['parity_boundary']['linux_normal_camss_ir_is_windows_1_to_1_parity'] is False,'normal CAMSS parity overclaim')
need(r['parity_boundary']['exact_secure_internal_route_unresolved'] is True,'secure boundary')

# Current machine must be unchanged Golden.
need(Path('/proc/sys/kernel/osrelease').read_text().strip()=='7.1.5-sp11-render-parity-v4+','current kernel')
need('/boot/sp11-7.1.5-audio-fullio-v19c/' in Path('/proc/cmdline').read_text(),'Golden BOOT_IMAGE')
env=subprocess.check_output(['sudo','-n','grub-editenv','/boot/grub/grubenv','list'],text=True)
need('saved_entry=sp11-audio-fullio-v19c\n' in env,'saved entry')
need('next_entry=\n' in env,'one-shot not consumed/empty')
mods=Path('/proc/modules').read_text()
for m in ('qcom_camss','sp11_vd55','e004t','vd55g0','imx681','ov13858','i2c_qcom_cci'):
    need(m not in mods,'camera module active '+m)
need(not glob.glob('/dev/media*') and not glob.glob('/dev/video*'),'camera nodes present')

print('E004Y_VERIFY=PASS REAL_IR_FRAMES=12')
print('E004Y_STANDARD_CAMSS=INACTIVE CSID0_1_2=WINDOWS_INACTIVE_DEFAULT VFE0_1=ZERO')
print('E004Y_SECUREISP=QCOM0CCC STARTED APERTURE=0xACCA000..0xACCDFFF KD_READABLE=NO')
print('E004Y_SECURE_INTERNAL_ROUTE=UNRESOLVED NORMAL_CAMSS_PARITY=NO')
print('E004Y_GOLDEN_RETURN=PASS CAMERA_MODULES=NO MEDIA_NODES=NO')
