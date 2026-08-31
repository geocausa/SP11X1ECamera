#!/usr/bin/env python3
import hashlib,json,pathlib,re,subprocess,sys
D=pathlib.Path(__file__).resolve().parent
R=D.parents[2]
M=json.load(open(D/'asset-manifest.json'))
P=D/'package-inspection.json'
BOOT=pathlib.Path('/boot/sp11-7.1.5-camera-e003h-camnoc300-0056')
ENTRY=pathlib.Path('/etc/grub.d/99t_sp11_camera_e003h_camnoc300_0056')
sha=lambda p:hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def need(c,m):
    if not c: raise SystemExit('FAIL: '+m)
need(M['accepted'] and not M['runtime_authorized'],'manifest acceptance')
need(M['static_commit']=='1f83a00ced3087cf35f8e6269026b164a07ed986','static commit')
need(M['static_inspection_sha256']=='a971108097f87354032f9b13765ea5b6dc775f89c8fece214e6bd36472593ee1','static inspection')
need(M['linux_0055_analysis_sha256']=='9fdba6fad49d493d8eafb4a97a658323e70e09b20f2a110a06457bb9496d96b0','0055 analysis')
for rel,h in M['assets'].items(): need(sha(D/rel)==h,'asset '+rel)
need(M['assets']['qcom-camss.ko']=='072aae4359a77e3eb41847cda2f34a9355bc1a9e68e8c0fd2a0a422bf4e18f05','0056 CAMSS')
need(M['assets']['imx681.ko']=='a12693a18bf2e4108dd309af68da189a2ea394a734a0c6a3c1d624ac44dea3dc','frozen sensor')
b=M['behavior_delta']; need(b['new_clock_rate_requests']==1 and b['clock_rate_hz']==300000000 and b['camera_register_changes']==0 and b['sensor_changes']==0 and b['csid_changes']==0 and b['vfe_register_changes']==0 and b['rtcdm_changes']==0 and b['dt_changes']==0,'behavior delta')
install=(D/'install-candidate.sh').read_text(); runtime=(D/'runtime-preflight.sh').read_text(); load=(D/'load-candidate.sh').read_text(); run=(D/'run-once.sh').read_text(); watch=(D/'camnoc-watch.py').read_text()
need('grub-reboot' not in install,'installer can arm')
need('sp11-camera-e003h-camnoc300-0056-one-shot' in install and 'sp11_camera_e003h_camnoc300_0056=1' in install,'boot identity')
need(load.index('"$NEW/runtime-preflight.sh"') < load.index('insmod "$NEW/qcom-camss.ko"'),'preflight ordering')
need(run.count('sudo -n "$HELPER" "$VIDEO" "$TRIGGER" "$OUT"')==1,'helper call count')
need('RUN exists; retry forbidden' in run and 'trap \'sync; sudo -n systemctl reboot\' EXIT' in run,'no-retry/reboot')
need('mmap.PROT_READ' in watch and 'mmap.PROT_WRITE' not in watch,'watcher read-only')
need('seen_live_300=1' in run,'300 MHz runtime criterion')
need('CAMERA_PROGRAMMING_DELTA=CAMNOC_RT_CCF_300MHZ_ONLY' in run,'runtime delta label')
head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(); origin=subprocess.check_output(['git','-C',str(R),'rev-parse','origin/experiment/e003-front-imx681-cphy'],text=True).strip(); need(head==origin,'HEAD/origin')
need(subprocess.run(['git','-C',str(R),'merge-base','--is-ancestor',M['static_commit'],head]).returncode==0,'static ancestry')
env=subprocess.check_output(['grub-editenv','list'],text=True,stderr=subprocess.DEVNULL); need('saved_entry=sp11-audio-fullio-v19c\n' in env,'Golden saved'); need(not re.search(r'^next_entry=.+',env,re.M),'candidate armed')
mods=subprocess.check_output(['lsmod'],text=True); need(not any(x in mods for x in ('qcom_camss','imx681','ov13858')),'camera modules loaded')
installed=BOOT.is_dir() and ENTRY.is_file()
if installed:
    need(sha(BOOT/'vmlinuz-7.1.5-sp11-render-parity-v4+')==M['golden']['kernel_sha256'],'installed kernel')
    need(sha(BOOT/'initrd.img-7.1.5-sp11-camera-e003h-camnoc300-0056')==M['golden']['initrd_sha256'],'installed initrd')
    need(sha(BOOT/'x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb')==M['assets']['x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'],'installed DTB')
    et=ENTRY.read_text(); need('sp11-camera-e003h-camnoc300-0056-one-shot' in et and 'sp11_camera_e003h_camnoc300_0056=1' in et,'installed entry identity'); need('exec tail -n +3 $0' in et,'installed entry header')
need(not (D/'AUTHORIZATION.json').exists(),'authorization present')
need(not (D/'RUNTIME-CAMNOC300-0056-RUN.txt').exists(),'runtime already exists')
out={'schema':'sp11-e003h-camnoc-rate-parity-0056-package-inspection-v1','accepted':True,'candidate_boot_installed':installed,'candidate_boot_armed':False,'runtime_authorized':False,'head':head,'static_commit':M['static_commit'],'asset_manifest_sha256':sha(D/'asset-manifest.json'),'camss_sha256':M['assets']['qcom-camss.ko'],'sensor_sha256':M['assets']['imx681.ko'],'dtb_sha256':M['assets']['x1e80100-microsoft-denali-sp11-e003h-pix-frontonly.dtb'],'camnoc_rate_hz':300000000,'new_clock_rate_requests':1,'camera_register_changes':0,'single_helper_enforced':True,'same_boot_retry_refused':True,'immediate_golden_reboot':True,'camnoc_observer_read_only':True}
P.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out,indent=2,sort_keys=True))
