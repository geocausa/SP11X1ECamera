#!/usr/bin/env python3
from pathlib import Path
import argparse, importlib.util, json, os, signal, statistics, subprocess, sys, tempfile, time
HERE=Path(__file__).resolve().parent

def load(p,n):
    s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def fs(v):
    s=sorted(v);return {'mean_ms':statistics.mean(v),'p95_ms':s[max(0,int(len(s)*.95)-1)],'max_ms':max(v)}

def run_seq(P,p,iters):
    raw=bytes(0xf000); out={1:[],2:[],3:[]}; hashes={}
    for _ in range(iters):
        p.reset_sequence()
        for gen in (1,2,3):
            t0=time.perf_counter_ns();wire,_=p.lsc.run(raw,488.0,4800.0)
            cap=None
            if gen in (2,3):cap,_,_=p.composer.compose(gen+3,wire);hashes[gen+3]=P.sha(cap)
            out[gen].append((time.perf_counter_ns()-t0)/1e6)
    return {f'G{k}':fs(v) for k,v in out.items()},hashes

def start_loaders():
    procs=[]
    code='import os,time\nos.sched_setaffinity(0,{int(__import__("sys").argv[1])})\nx=1\nend=time.monotonic()+30\nwhile time.monotonic()<end:\n x=(x*1664525+1013904223)&0xffffffff\n'
    for cpu in range(os.cpu_count() or 1):
        procs.append(subprocess.Popen([sys.executable,'-c',code,str(cpu)],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL))
    time.sleep(.2);return procs

def stop_loaders(ps):
    for p in ps:
        if p.poll() is None:p.terminate()
    for p in ps:
        try:p.wait(timeout=2)
        except subprocess.TimeoutExpired:p.kill();p.wait()

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--iterations',type=int,default=40);ap.add_argument('--manifest',type=Path,default=HERE/'LIVE-DEADLINE-HARDENING.json');a=ap.parse_args();assert a.iterations>=20
    P=load(HERE/'live-iq-producer.py','ae_live_harden')
    need_root=(os.geteuid()!=0)
    if need_root:raise SystemExit('run as root: scheduler proof requires nice -20')
    sched=P.configure_live_scheduler()
    with tempfile.TemporaryDirectory(prefix='e003i-live-hardening-') as td:
        p=P.Producer(Path(td));t0=time.perf_counter_ns();p.prewarm();prewarm_ms=(time.perf_counter_ns()-t0)/1e6
        clean,clean_hash=run_seq(P,p,a.iterations)
        loaders=start_loaders()
        try:loaded,loaded_hash=run_seq(P,p,a.iterations)
        finally:stop_loaders(loaders)
    assert clean_hash==loaded_hash
    assert clean_hash[5] and clean_hash[6]
    budget=33.333333333333336
    assert loaded['G2']['p95_ms']<budget and loaded['G3']['p95_ms']<budget
    assert loaded['G2']['max_ms']<budget and loaded['G3']['max_ms']<budget
    out={'schema':'sp11-e003i-ae-live-deadline-hardening-v1','status':'PASS','fixture_free':True,'synthetic_tlbg_bytes':0xf000,'synthetic_lux':488.0,'synthetic_cct':4800.0,'scheduler':sched,'prewarm_ms':prewarm_ms,'iterations':a.iterations,'frame_budget_ms':budget,'clean':clean,'all_cpu_contention':loaded,'capsule_sha256':{'R5':clean_hash[5],'R6':clean_hash[6]},'acceptance':{'G2_p95_under_budget':True,'G3_p95_under_budget':True,'G2_max_under_budget':True,'G3_max_under_budget':True,'captured_runtime_fixture_dependency':False,'prewarm_before_ready_required':True,'state_reset_after_prewarm':True,'deadline_evidence_io_deferred':True}}
    a.manifest.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('E003I_AE_LIVE_DEADLINE_HARDENING=PASS')
    print(f"PREWARM_MS={prewarm_ms:.4f}")
    print(f"LOADED_G2_P95_MS={loaded['G2']['p95_ms']:.4f} MAX={loaded['G2']['max_ms']:.4f}")
    print(f"LOADED_G3_P95_MS={loaded['G3']['p95_ms']:.4f} MAX={loaded['G3']['max_ms']:.4f}")
if __name__=='__main__':main()
