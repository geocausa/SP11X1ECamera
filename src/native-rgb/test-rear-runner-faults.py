#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fault-test actual staged E008K orchestration with explicit host-only mocks."""
import argparse,json,os,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def once(text,before,after):
 if text.count(before)!=1:raise RuntimeError("host extraction anchor drift")
 return text.replace(before,after,1)
def harness(stage):
 parent=(ROOT/"experiments/E004-front-ir-vd55g0/e011ar-rear-packet-isolated-runner/test-runner.c").read_text()
 prefix=parent[:parent.index('#include "camss-vfe-e011ar-rear-runner.inc"')]
 a=prefix.index("struct e007d_rear_register_state {")
 b=prefix.index("struct e008h_rear_prime_pair",a)
 prefix=prefix[:a]+"""struct e007y_rear_startup_output {u32 bl_count;struct {u32 dma;u16 bytes;}bl[2];};
struct e008l_rear_command_set {
 struct {struct e007y_rear_startup_output out;}packet[4];
 bool allocated,prepared;u64 packet_request_id[4];
};
static int native_rear_validate_prepared_commands(struct e008l_rear_command_set *c){
 if(!c||!c->allocated||!c->prepared)return -EINVAL;
 return step();
}
"""+prefix[b:]
 a=prefix.index("static int e008l_rear_command_alloc")
 b=prefix.index("static int e005y_vfe1_owner_acquire",a)
 prefix=prefix[:a]+prefix[b:]
 # Direct runner tests have no wrapper/semantic stubs or command rematerializer.
 prefix=prefix.replace("static int atomic_cmpxchg(int *p,int a,int b) {int old=*p;if(old==a)*p=b;return old;}","")
 prefix += "\nstatic int csid680_native_rear_configure(struct csid_device *c) {CHECK(c);attempted|=4;return step();}\n"
 prefix += "\nstatic int csid680_native_rear_after_packet0_configure(struct csid_device *c) {CHECK(c);attempted|=4;return step();}\n"
 core=(stage/"camss-vfe-e008k-rear-runner.inc").read_text()
 if "native_rear_vfe_configure" in core:
  prefix += "\nstatic int native_rear_vfe_configure(struct vfe_device *v) {CHECK(v);attempted|=2;return step();}\n"
 if "csid680_native_rear_generation_snapshot" in core:
  prefix += "\nstatic void csid680_native_rear_generation_snapshot(struct csid_device *c,const char *p) {CHECK(c&&p);}\n"
 if "native_rear_generation_vfe_snapshot" in core:
  prefix += "\nstatic void native_rear_generation_vfe_snapshot(struct vfe_device *v,const char *p) {CHECK(v&&p);}\n"
 a=core.index("static int\ne011i_rear_reclaim_after_stop(")
 b=core.index("static int\ne008k_rear_pair_stop_release(",a)
 core=core[:a]+"""/* Explicit mock: actual physical reclaim is not exercised here. */
static int e011i_rear_reclaim_after_stop(struct camss *c,struct vfe_device *v,
 struct e008h_rear_prime_pair *p,u64 epoch,const struct e008k_rear_result *r){
 CHECK(c&&v&&p&&epoch==41);
 CHECK(r->csid_quiesced&&r->bus_stopped&&r->rtcdm_stopped&&r->source_stopped);
 CHECK(!r->owner_released&&!r->dma_reclaimed);
 return step();
}
"""+core[b:]
 # The only authorization change exists in this disposable host translation unit.
 core=once(core,"return -EOPNOTSUPP;","return host_authorized ? 0 : -EOPNOTSUPP;")
 tail=(HERE/"rear-runner-fault-main.c").read_text()
 tail=once(tail,"static bool host_authorized;\n","")
 return prefix+"\nstatic bool host_authorized;\n"+core+"\n"+tail
def checked(args,env=None):
 r=subprocess.run(args,capture_output=True,text=True,env=env)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 return r
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True)
 a=p.parse_args()
 if a.report.exists():raise SystemExit("report already exists")
 results=[]
 with tempfile.TemporaryDirectory(prefix="sp11-rear-runner-fault-") as directory:
  tmp=Path(directory);source=tmp/"fault.c";source.write_text(harness(a.staged.resolve()))
  for compiler in ["gcc","clang"]:
   executable=shutil.which(compiler)
   if not executable:raise RuntimeError("required compiler absent")
   binary=tmp/compiler
   checked([executable,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g",
            "-fsanitize=address,undefined","-fno-omit-frame-pointer","-I"+str(a.staged),
            str(source),"-o",str(binary)])
   r=checked([str(binary)],env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",
                                   UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1"))
   results.append({"compiler":compiler,"ASAN_UBSAN_Werror":True,"result":json.loads(r.stdout),"stderr":r.stderr})
 report={"status":"PASS_HOSTED_ACTUAL_REAR_RUNNER_PARTIAL_START_FAILURES","results":results,
         "production_runtime_authorization_unchanged_denied":True,"hardware_access":False}
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
