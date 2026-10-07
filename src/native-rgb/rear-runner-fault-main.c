static bool host_authorized;
static void reset(void) {
 for(unsigned i=0;i<alloc_n;i++)free(allocations[i]);
 memset(allocations,0,sizeof(allocations));alloc_n=0;
 seq=fail_at=failed=materializations=released_commands=unsafe_release=pm_refs=stopped=stopped_at=release_at=malformed_at=mark_fail=allocation_count=allocation_fail=0;
 attempted=halted=0;memset(faultable,0,sizeof(faultable));
}
static int run_case(int fail,int allocation,bool authorized) {
 reset();host_authorized=authorized;
 struct camss c;memset(&c,0,sizeof(c));for(int i=0;i<2;i++)c.vfe[i].camss=&c;
 struct v4l2_subdev sensor={.id=9};struct e008l_rear_command_set commands={0};
 struct e008k_rear_request req={.sensor=&sensor,.commands=&commands,.first_request_generation=1};
 struct e008k_rear_result result;
 commands.allocated=commands.prepared=true;
 for(unsigned p=0;p<4;p++){
  commands.packet_request_id[p]=req.packet_request_id[p]=10+p;
  commands.packet[p].out.bl_count=1;
  commands.packet[p].out.bl[0].dma=1000+p;commands.packet[p].out.bl[0].bytes=16;
 }
 fail_at=fail;allocation_fail=allocation;
 int ret=e008k_rear_run_unreachable(&c.vfe[1],&req,&result);
 if(!authorized){CHECK(ret==-EOPNOTSUPP);CHECK(!attempted && !halted && pm_refs==0);}
 else if(!ret){
  CHECK(result.both_frames_complete && result.owner_released && result.dma_reclaimed);
  CHECK(!pm_refs);CHECK((halted&attempted)==attempted);
 }else{
  CHECK((halted&attempted)==attempted);
  if(attempted){CHECK(unsafe_release>0);CHECK(pm_refs==(result.dma_reclaimed&&result.ledgers_released?0:1));}
  else CHECK(!pm_refs && !unsafe_release);
 }
 if(fail)CHECK(failed);
 return ret;
}
int main(void) {
 CHECK(run_case(0,0,false)==-EOPNOTSUPP);
 CHECK(run_case(0,0,true)==0);int stages=seq,injected=0;
 bool points[256];memcpy(points,faultable,sizeof(points));
 for(int n=1;n<=stages;n++)if(points[n]){
  CHECK(run_case(n,0,true)!=0);injected++;
 }
 CHECK(run_case(0,1,true)==-ENOMEM);
 reset();
 printf("{\"assertions\":%u,\"lifecycle_steps\":%d,\"injected_failures\":%d,\"partial_start_stop_attempts_complete\":true,\"lifecycle_helpers_and_reclaim_mocked\":true,\"runtime_denial_bypassed_only_in_host_test\":true,\"hardware_proof\":false}\n",assertions,stages,injected);
 return 0;
}
