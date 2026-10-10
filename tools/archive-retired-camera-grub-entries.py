#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Archive dormant camera menu scripts, validate replacement, atomically install.

Keeps all boot images and evidence. Never sets boot defaults or reboots.
"""
import datetime,hashlib,json,os,re,shutil,stat,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SCRIPTS=Path('/etc/grub.d')
CFG=Path('/boot/grub/grub.cfg')
ENV=Path('/boot/grub/grubenv')
ARCHIVE=Path('/var/lib/sp11-grub-retired-camera-20261010-01')
PREFIX='99zzzzzz_sp11_camera_'

def need(ok,reason):
    if not ok:raise RuntimeError(reason)

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def entries(s):return [x for x in s.splitlines() if re.match(r'\s*(menuentry|submenu) ',x)]

def main():
    need(os.geteuid()==0,'root required')
    subprocess.run([str(ROOT/'tools/camera-overlap-guard.sh'),'--require-clean-tracked','--require-golden','--require-no-camera-process'],check=True)
    state=json.loads((ROOT.parents[1]/'CURRENT-CAMERA-WORKSPACE.txt').read_text())
    need(state['experiment_armed'] is False and state['pending_attempt'] is None,'no pending test allowed')
    active=subprocess.check_output(['systemctl','list-units','--all','--plain','--no-legend','--no-pager'],text=True)
    need(not any('camera' in x.lower() and any(v in x.split() for v in ('active','activating','deactivating')) for x in active.splitlines()),'active camera unit')
    grubenv=subprocess.check_output(['grub-editenv',str(ENV),'list'],text=True).splitlines()
    need('saved_entry=sp11-audio-fullio-v19c' in grubenv and not any(x.startswith('next_entry=') and x!='next_entry=' for x in grubenv),'Golden saved default and empty one-shot required')
    need(not ARCHIVE.exists() and CFG.is_file() and not CFG.is_symlink(),'fresh archive and regular config required')
    inventory={p.name:{'sha256':sha(p),'mode':stat.S_IMODE(p.stat().st_mode)} for p in SCRIPTS.iterdir() if p.is_file()}
    candidates=sorted(p for p in SCRIPTS.iterdir() if p.is_file() and p.name.startswith(PREFIX) and p.stat().st_mode&0o111)
    need(len(candidates)==73,'expected audited73 dormant camera entries')
    removed=[]
    for p in candidates:
        need(not p.is_symlink(),'regular camera menu script required')
        e=entries(p.read_text());need(len(e)==1 and e[0].startswith('menuentry ') and "--id 'sp11-camera-" in e[0],'exact camera entry scope required')
        removed.extend(e)
    before=CFG.read_text();before_entries=entries(before)
    need(len(before_entries)==81 and all(before_entries.count(x)==1 for x in removed),'audited menu changed')
    retained=[x for x in before_entries if x not in removed]
    need(len(retained)==8,'eight non-camera menu/submenu records expected')
    need(any("'sp11-audio-fullio-v19c'" in x for x in retained) and any("'osprober-efi-2A36-6A1E'" in x for x in retained),'Golden and Windows IDs required')
    protected={str(p):sha(p) for p in (Path('/boot/sp11-7.1.5-audio-fullio-v19c')).iterdir() if p.is_file()}
    original_config_sha=sha(CFG);original_env_sha=sha(ENV);original_config_mode=stat.S_IMODE(CFG.stat().st_mode)
    ARCHIVE.mkdir(mode=0o700);(ARCHIVE/'scripts').mkdir(mode=0o700)
    shutil.copy2(CFG,ARCHIVE/'grub.cfg.before');shutil.copy2(ENV,ARCHIVE/'grubenv.before')
    (ARCHIVE/'grub.cfg.before').chmod(0o600);(ARCHIVE/'grubenv.before').chmod(0o600)
    report={'identity':'E-GRUB-CAMERA-MENU-CLEANUP-20261010-01','status':'PREPARED','source_head':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),'archive_directory':str(ARCHIVE),'before_records':len(before_entries),'removed_camera_entries':len(removed),'retained_records':retained,'archived_scripts':{p.name:inventory[p.name] for p in candidates},'Golden_hashes':protected,'before_grub_cfg_sha256':original_config_sha,'before_grubenv_sha256':original_env_sha,'boot_assets_deleted':False,'evidence_deleted':False,'reboot_performed':False,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    (ARCHIVE/'PLAN.json').write_text(json.dumps(report,indent=2)+'\n');(ARCHIVE/'PLAN.json').chmod(0o600)
    moved=[];installed=False
    try:
        need(sha(CFG)==original_config_sha and sha(ENV)==original_env_sha,'live boot state changed during audit')
        for p in candidates:
            need(sha(p)==inventory[p.name]['sha256'],'menu script changed during audit')
            p.rename(ARCHIVE/'scripts'/p.name);moved.append(p)
        candidate=ARCHIVE/'grub.cfg.candidate'
        with (ARCHIVE/'generation.log').open('x') as log:
            subprocess.run(['grub-mkconfig','-o',str(candidate)],stdout=log,stderr=subprocess.STDOUT,check=True)
        subprocess.run(['grub-script-check',str(candidate)],check=True)
        need(entries(candidate.read_text())==retained,'retained menu records differ or camera entry remains')
        need(sha(ENV)==original_env_sha and sha(CFG)==original_config_sha,'default or live config changed by generation')
        for name,v in inventory.items():
            path=ARCHIVE/'scripts'/name if name.startswith(PREFIX) else SCRIPTS/name
            need(sha(path)==v['sha256'] and stat.S_IMODE(path.stat().st_mode)==v['mode'],'original script changed')
        need(all(sha(Path(p))==h for p,h in protected.items()),'Golden asset changed')
        temporary=CFG.with_name('grub.cfg.camera-cleanup-20261010-01.tmp');need(not temporary.exists(),'replacement collision')
        with temporary.open('xb') as f:
            f.write(candidate.read_bytes());f.flush();os.fsync(f.fileno())
        temporary.chmod(original_config_mode);os.replace(temporary,CFG);installed=True
        fd=os.open(CFG.parent,os.O_DIRECTORY)
        try:os.fsync(fd)
        finally:os.close(fd)
        subprocess.run(['grub-script-check',str(CFG)],check=True)
        need(entries(CFG.read_text())==retained and sha(ENV)==original_env_sha,'installed config or environment mismatch')
        report.update(status='PASS73_DORMANT_CAMERA_ENTRIES_ARCHIVED_VALIDATED_MENU_INSTALLED',after_records=len(retained),after_menuentries=sum(x.lstrip().startswith('menuentry ') for x in retained),after_submenus=sum(x.lstrip().startswith('submenu ') for x in retained),after_grub_cfg_sha256=sha(CFG),saved_default_unchanged=True,next_entry_empty=True,protected_Golden_unchanged=True,all_archived_script_bytes_modes_unchanged=True)
    except BaseException:
        for p in moved:
            need(not p.exists(),'rollback script collision');(ARCHIVE/'scripts'/p.name).rename(p)
        if installed:
            rollback=CFG.with_name('grub.cfg.camera-cleanup-20261010-01.rollback');need(not rollback.exists(),'rollback collision');shutil.copyfile(ARCHIVE/'grub.cfg.before',rollback);rollback.chmod(original_config_mode);os.replace(rollback,CFG)
        report['status']='FAILED_ROLLED_BACK';raise
    finally:
        (ARCHIVE/'RESULT.json').write_text(json.dumps(report,indent=2)+'\n');(ARCHIVE/'RESULT.json').chmod(0o600)
    print(json.dumps({k:v for k,v in report.items() if k not in ('archived_scripts','Golden_hashes')}))

if __name__=='__main__':main()
