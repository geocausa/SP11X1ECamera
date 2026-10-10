#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Prune only reproducible .o intermediates in the fixed retired e002k-d build.

Preserve all source, .ko, symbols, generated headers, scripts, media objects,
root vmlinux.o, vmlinux and configuration. No camera/reboot/power-policy action.
A complete private file-disposition manifest stays beside the retired build.
"""
import argparse,datetime,hashlib,json,os,stat,subprocess
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BUILD=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e002k-d-kernel-build')
SOURCE=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-src')
ALLOWED={'drivers','fs','net','sound','kernel','mm','lib','crypto','block','virt','security','ipc','init','io_uring'}
RECORD=BUILD/'OBJECT-CACHE-PRUNE-20261010-01.json'
GOLDEN=Path('/boot/sp11-7.1.5-audio-fullio-v19c')

def need(ok,why):
    if not ok: raise RuntimeError(why)

def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def free():
    v=os.statvfs(BUILD);return v.f_bavail*v.f_frsize

def fp(p):
    s=p.lstat()
    return [s.st_dev,s.st_ino,s.st_size,s.st_mtime_ns,s.st_ctime_ns,s.st_nlink,s.st_uid,s.st_mode]

def no_builders():
    builders={'make','ninja','cc1','cc1plus','clang','clang-18','clang-19','gcc','ld','ld.bfd','ld.lld'}
    for d in Path('/proc').glob('[0-9]*'):
        try: comm=(d/'comm').read_text().strip()
        except (FileNotFoundError,ProcessLookupError):continue
        need(comm not in builders,'concurrent compiler or builder: '+comm)

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--apply',action='store_true');args=parser.parse_args()
    need(os.geteuid()==0,'root diagnostic required')
    subprocess.run([str(ROOT/'tools/camera-overlap-guard.sh'),'--require-clean-tracked','--require-golden','--require-no-camera-process'],check=True)
    no_builders()
    need(BUILD.is_dir() and not BUILD.is_symlink() and SOURCE.is_dir(),'fixed build/source required')
    need(not RECORD.exists(),'disposition identity already used')
    make=(BUILD/'Makefile').read_text()
    need(str(SOURCE/'Makefile') in make and str(BUILD) in make,'exact external output-tree relationship required')
    preserved=[BUILD/n for n in ('.config','Module.symvers','System.map','vmlinux','vmlinux.unstripped','vmlinux.o','Makefile')]
    preserved += [GOLDEN/n for n in ('vmlinuz-7.1.5-sp11-render-parity-v4+','initrd.img-7.1.5-sp11-fullio-v19c','x1e80100-microsoft-denali-sp11-fullio-v19c.dtb')]
    hashes={str(p):sha(p) for p in preserved}
    ko={str(p.relative_to(BUILD)):fp(p) for p in BUILD.rglob('*.ko')}
    objects=[]
    for p in BUILD.rglob('*.o'):
        relative=p.relative_to(BUILD)
        if relative.parts[0] not in ALLOWED or relative.parts[:2]==('drivers','media'):continue
        s=p.lstat();need(stat.S_ISREG(s.st_mode) and s.st_uid==1000 and s.st_nlink==1,'unshared user-owned regular cache required')
        need(p.resolve().is_relative_to(BUILD),'candidate escaped fixed build')
        objects.append({'path':str(relative),'fingerprint':fp(p),'allocated_bytes':s.st_blocks*512})
    need(len(objects)>10000 and sum(x['allocated_bytes'] for x in objects)>10000000000,'expected large retired object-cache inventory required')
    report={'identity':'E-STORAGE-OLD-KERNEL-OBJECT-CACHE-20261010-01','status':'PLANNED','source_tree':str(SOURCE),'build_tree':str(BUILD),'source_head':subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),'kernel_source_head':subprocess.check_output(['git','-C',str(SOURCE),'rev-parse','HEAD'],text=True).strip(),'free_before_bytes':free(),'candidate_files':len(objects),'candidate_allocated_bytes':sum(x['allocated_bytes'] for x in objects),'preserved_key_artifact_sha256':hashes,'finished_modules_preserved':len(ko),'all_ko_stat_fingerprints_preserved':False,'all_source_preserved':True,'Golden_preserved':True,'media_objects_preserved':True,'rebuild_cost':'Future full-tree incremental builds must recompile removed objects; current native camera module builds use e003i/build-runtime-v4 headers instead.','objects':objects,'removed_files':0,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
    if not args.apply:
        print(json.dumps({k:v for k,v in report.items() if k not in ('objects','preserved_key_artifact_sha256')}));return
    no_builders();need(all(fp(BUILD/x['path'])==x['fingerprint'] for x in objects),'candidate changed during audit')
    os.umask(0o077)
    with RECORD.open('x') as f:
        json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    try:
        for x in objects:
            p=BUILD/x['path'];need(fp(p)==x['fingerprint'],'candidate changed before prune');p.unlink();report['removed_files']+=1
        need(all(sha(p)==hashes[str(p)] for p in preserved),'protected final artifact changed')
        now={str(p.relative_to(BUILD)):fp(p) for p in BUILD.rglob('*.ko')}
        need(now==ko,'finished module changed')
        need(all(not (BUILD/x['path']).exists() for x in objects),'cache disposition incomplete')
        report.update(status='PASS_REPRODUCIBLE_OBJECT_CACHE_REMOVED_FINAL_ARTIFACTS_UNCHANGED',all_ko_stat_fingerprints_preserved=True,free_after_bytes=free())
    finally:
        temporary=RECORD.with_suffix('.complete');need(not temporary.exists(),'temporary record collision')
        with temporary.open('x') as f:
            json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
        os.replace(temporary,RECORD)
    print(json.dumps({k:v for k,v in report.items() if k not in ('objects','preserved_key_artifact_sha256')}))

if __name__=='__main__':main()
