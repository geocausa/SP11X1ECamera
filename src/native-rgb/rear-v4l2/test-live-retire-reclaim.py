#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Actual rear reclaim admission for coherent and retained public FULL outputs."""
from pathlib import Path
import argparse,importlib.util,json,os,subprocess,tempfile
HERE=Path(__file__).resolve().parent
EXTRA=r"""
static void make_public(unsigned s){
 struct e008d_rear_dma_set *set=&pair.dma[s];
 set->full.cpu=NULL;set->full.size=NATIVE_REAR_NV12_BYTES;set->full.dma=0x10000000+s*0x2000000;
 set->public_full=(struct native_rear_video_lease){.dbuf=&cam,.attachment=&cam,.table=&cam,
  .span={set->full.dma,set->full.dma+NATIVE_REAR_NV12_UV_OFFSET,12443648},
  .acquired=true,.exposed=true};
}
"""
MATRIX=r"""
 for(unsigned kind=0;kind<3;kind++){
  init();if(kind!=1)make_public(0);if(kind!=0)make_public(1);
  CHECK(e011i_rear_reclaim_after_stop(&cam,&vfe,&pair,7,&result)==0);CHECK(releases==2);
 }
 for(unsigned s=0;s<2;s++)for(unsigned f=0;f<12;f++){
  init();make_public(0);make_public(1);
  struct e008d_rear_dma_set *set=&pair.dma[s];
  struct native_rear_video_lease *lease=&set->public_full;
  switch(f){
   case 0:lease->acquired=false;break;case 1:lease->dbuf=NULL;break;
   case 2:lease->attachment=NULL;break;case 3:lease->table=NULL;break;
   case 4:lease->span.y_iova=0;break;case 5:lease->span.uv_iova++;break;
   case 6:lease->span.mapped_bytes=NATIVE_REAR_NV12_BYTES-1;break;
   case 7:set->full.cpu=&cam;break;case 8:set->full.size--;break;
   case 9:set->full.dma++;break;case 10:lease->exposed=false;break;case 11:lease->stop_proven=true;break;
  }
  struct e008h_rear_prime_pair before=pair;
  CHECK(e011i_rear_reclaim_after_stop(&cam,&vfe,&pair,7,&result)!=0);
  CHECK(releases==0&&!memcmp(&before,&pair,sizeof(pair)));negative_cases++;
 }
 for(unsigned mask=0;mask<15;mask++){
  init();make_public(0);make_public(1);
  result.csid_quiesced=mask&1;result.bus_stopped=mask&2;result.rtcdm_stopped=mask&4;result.source_stopped=mask&8;
  struct e008h_rear_prime_pair before=pair;
  CHECK(e011i_rear_reclaim_after_stop(&cam,&vfe,&pair,7,&result)!=0);
  CHECK(releases==0&&!memcmp(&before,&pair,sizeof(pair)));negative_cases++;
 }
"""

RETIRED_EXTRA=r"""
static void make_retired(void){
 make_public(0);make_public(1);
 struct e008d_rear_dma_set *d=&pair.dma[0];
 d->public_full_retired=true;d->retired_owner_epoch=7;d->retired_request_generation=1;
 d->full.in_flight=false;memset(&d->public_full,0,sizeof(d->public_full));
 pair.frame[0].slot[0].owned_base_iova=d->full.dma;
 pair.frame[0].slot[1].owned_base_iova=d->full.dma+NATIVE_REAR_NV12_UV_OFFSET;
 result.live_full_retired=true;
}
"""
RETIRED_MATRIX=r"""
 init();make_retired();CHECK(e011i_rear_reclaim_after_stop(&cam,&vfe,&pair,7,&result)==0);CHECK(releases==2);
 for(unsigned field=0;field<18;field++){
  init();make_retired();struct e008d_rear_dma_set *d=&pair.dma[0];
  switch(field){
   case 0:result.live_full_retired=false;break;case 1:d->public_full_retired=false;break;
   case 2:d->retired_aux_stop_proven=true;break;case 3:d->retired_owner_epoch++;break;
   case 4:d->retired_request_generation++;break;case 5:d->full.in_flight=true;break;
   case 6:d->full.cpu=&cam;break;case 7:d->full.size--;break;case 8:d->full.dma++;break;
   case 9:d->public_full.dbuf=&cam;break;case 10:d->public_full.attachment=&cam;break;
   case 11:d->public_full.table=&cam;break;case 12:d->public_full.acquired=true;break;
   case 13:d->public_full.exposed=true;break;case 14:d->public_full.stop_proven=true;break;
   case 15:d->public_full.span.y_iova=1;break;case 16:pair.frame[0].slot[1].owned_base_iova++;break;
   case 17:pair.dma[1].public_full_retired=true;break;
  }
  struct e008h_rear_prime_pair before=pair;
  CHECK(e011i_rear_reclaim_after_stop(&cam,&vfe,&pair,7,&result)!=0);
  CHECK(releases==0&&!memcmp(&before,&pair,sizeof(pair)));negative_cases++;
 }
 for(unsigned mask=0;mask<15;mask++){
  init();make_retired();
  result.csid_quiesced=mask&1;result.bus_stopped=mask&2;result.rtcdm_stopped=mask&4;result.source_stopped=mask&8;
  struct e008h_rear_prime_pair before=pair;
  CHECK(e011i_rear_reclaim_after_stop(&cam,&vfe,&pair,7,&result)!=0);
  CHECK(releases==0&&!memcmp(&before,&pair,sizeof(pair)));negative_cases++;
 }
"""

def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True);a=p.parse_args();assert not a.report.exists()
 spec=importlib.util.spec_from_file_location("coherent_reclaim_test",HERE.parent/"rear-generation/test-reclaim.py");base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
 layout=(a.staged/"camss-vfe-e004nt-rear-4k-buffer.inc").read_text();macros=layout[layout.index('#include "native-rear-nv12-layout.h"'):layout.index("/* Compile-time fit")]
 wm=(a.staged/"camss-vfe-e004nu-rear-ten-wm.inc").read_text();wm=wm[wm.index("#define VFE680_E004NU_REAR_CLIENTS"):wm.index("static bool __used")]
 dma=(a.staged/"camss-vfe-e008d-rear-dma.inc").read_text()
 aux=dma[dma.index("static const u8 e008d_rear_aux_wms"):dma.index("static const struct vfe680_e004nu_rear_wm_static *")]
 types=base.TYPES.replace("bool in_flight;};","bool in_flight;u64 dma;};",1)
 lease_types="""struct native_rear_video_dma {u32 y_iova,uv_iova;u64 mapped_bytes;};
struct native_rear_video_lease {void *dbuf,*attachment,*table;struct native_rear_video_dma span;bool acquired,exposed,stop_proven;};
"""
 types=types.replace("struct e008d_rear_dma_set {",lease_types+"struct e008d_rear_dma_set {struct native_rear_video_lease public_full;")
 types=types.replace("CHECK(!set->full.in_flight);releases++;","CHECK(!set->full.in_flight);CHECK(!set->public_full.acquired||set->public_full.stop_proven);releases++;")
 types=types.replace("VFE680_E004NT_REAR_TOTAL_BYTES,true};","VFE680_E004NT_REAR_TOTAL_BYTES,true,0};")
 types=types.replace("bool allocated,prepared_disabled;};","bool allocated,prepared_disabled;u64 retired_owner_epoch,retired_request_generation;bool public_full_retired,retired_aux_stop_proven;};")
 types=types.replace("struct e007z_rear_frame {","struct e007z_rear_slot {u32 owned_base_iova,owned_bytes,programmed_image_iova;};\nstruct e007z_rear_frame {")
 types=types.replace("bool active,faulted;};","bool active,faulted;struct e007z_rear_slot slot[10];};")
 types=types.replace("7,s+1,0,true,false}",".owner_epoch=7,.request_generation=s+1,.active=true}")
 types=types.replace("owner_released,dma_reclaimed;};","owner_released,dma_reclaimed,live_full_retired;};")
 types=types.replace("{true,true,true,true,false,false};","{true,true,true,true,false,false,false};")
 types=types.replace("CHECK(!set->full.in_flight);","CHECK(!set->full.in_flight);CHECK(!set->public_full_retired||set->retired_aux_stop_proven);")

 auxiliary=(a.staged/"native-rear-live-aux-retire.inc").is_file()
 if auxiliary:
  types=types.replace("bool public_full_retired,retired_aux_stop_proven;","bool public_full_retired,retired_aux_stop_proven,auxiliary_live_retired;")
  types=types.replace("live_full_retired;","live_full_retired,live_aux_retired;")
  types=types.replace("{true,true,true,true,false,false,false};","{true,true,true,true,false,false,false,false};")
  types=types.replace("struct aux {void *cpu;size_t size;u8 wm;};","struct aux {void *cpu;size_t size;u8 wm;u64 dma;};")
  types=types.replace("(struct aux){&cam,c->frame_incr,c->wm}","(struct aux){&cam,c->frame_incr,c->wm,0}")
 if (a.staged/"native-rear-command-retired.inc").exists():
  types=types.replace("struct e008l_rear_command_set {","struct e008l_rear_command_set {bool live_retired;u64 retired_owner;")
  # Explicit command-tombstone model, exercised against actual allocation by test-command-retire.py.
  types+="\nstatic bool native_rear_live_commands_retired_valid(const struct e008l_rear_command_set *s,u64 owner){return s&&s->live_retired&&owner&&s->retired_owner==owner;}\n"
 if (a.staged/"native-rear-queue.inc").exists():
  types=types.replace("struct e008k_rear_result {","struct e008k_rear_result {u32 queue_handoffs;")
  # Designated initializers preserve the original physical-stop model.
  types=types.replace("{true,true,true,true,false,false,false,false};","{.csid_quiesced=true,.bus_stopped=true,.rtcdm_stopped=true,.source_stopped=true};")
 fn=base.function;lease=(a.staged/"native-rear-video-lease.inc").read_text()
 code=base.PRE+macros+wm+aux+types
 code+="static bool "+fn(lease,"native_rear_video_lease_valid")
 code+="static int "+fn(lease,"native_rear_video_lease_stop")
 code+="static bool "+fn(dma,"native_rear_dma_full_valid")
 code+="static bool "+fn((a.staged/"camss-vfe-e008h-rear-prime.inc").read_text(),"e008h_rear_both_complete")
 code+="static bool "+fn((a.staged/"native-rear-live-retire.inc").read_text(),"native_rear_live_full_retired_valid")
 if auxiliary:
  code+="static bool "+fn((a.staged/"native-rear-live-aux-retire.inc").read_text(),"native_rear_live_aux_retired_valid")
 code+="static int "+fn((a.staged/"native-rear-reclaim.inc").read_text(),"e011i_rear_reclaim_after_stop")
 code+="static int "+fn((a.staged/"camss-vfe-e008l-rear-command-dma.inc").read_text(),"e008l_rear_command_release")
 main=base.MAIN.replace(" struct e008l_rear_command_set commands=",MATRIX+" struct e008l_rear_command_set commands=")
 main=main.replace(" struct e008l_rear_command_set commands=",RETIRED_MATRIX+" struct e008l_rear_command_set commands=")
 main=main.replace("{true,true,true,true,false,false};","{true,true,true,true,false,false,false};")
 if auxiliary:
  main=main.replace("{true,true,true,true,false,false,false};","{true,true,true,true,false,false,false,false};")
  extra=(HERE/"test-live-aux-reclaim-tail.c").read_text()
  declarations,aux_matrix=extra.split("/* MATRIX */")
  main=main.replace(" struct e008l_rear_command_set commands=",aux_matrix+" struct e008l_rear_command_set commands=")
  code+=EXTRA+RETIRED_EXTRA+declarations+main
 else:
  code+=EXTRA+RETIRED_EXTRA+main
 results=[]
 with tempfile.TemporaryDirectory(prefix="native-rear-public-reclaim-") as name:
  d=Path(name);(d/"test.c").write_text(code)
  for cc in ["gcc","clang"]:
   binary=d/cc
   r=subprocess.run([cc,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g","-fsanitize=address,undefined","-fno-omit-frame-pointer","-fno-pie","-no-pie","-I"+str(a.staged),str(d/"test.c"),"-o",str(binary)],capture_output=True,text=True)
   if r.returncode:raise RuntimeError(r.stderr)
   r=subprocess.run([str(binary)],capture_output=True,text=True,check=True)
   results.append(dict(compiler=cc,ASAN_UBSAN_Werror=True,result=json.loads(r.stdout),stderr=r.stderr))
 report=dict(status="PASS_ACTUAL_REAR_COHERENT_AND_PUBLIC_LEASE_ALL_OR_NONE_RECLAIM",
  actual_reclaimer_lease_valid_stop_and_FULL_predicate=True,DMA_frees_and_owner_query_are_host_models=True,
  both_public_and_mixed_coherent_public_checked=True,invalid_either_lease_or_any_stop_flag_leaves_both_sets_unchanged=True,
  hardware_access=False,actual_retired_old_FULL_and_remaining_DMA_cleanup_checked=True,results=results)
 report["actual_live_retired_auxiliary_zero_state_cleanup_checked"]=auxiliary
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
