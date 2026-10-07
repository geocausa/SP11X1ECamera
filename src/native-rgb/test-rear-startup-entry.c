/* SPDX-License-Identifier: GPL-2.0-only */
/* Real full composition/materialization and real E008N single-use wrapper. */
#include "rear-startup-host-fixture.h"
#include <stdatomic.h>
#define U64_MAX UINT64_MAX
typedef struct { atomic_int value; } atomic_t;
#define ATOMIC_INIT(x) { x }
static int atomic_cmpxchg(atomic_t *a,int old,int value){
 atomic_compare_exchange_strong(&a->value,&old,value);return old;
}
struct v4l2_subdev { int host_fixture; };
/* RUNNER_TYPES */
static unsigned runner_calls;
static int route_error;
static int e008k_rear_validate_route(struct camss *c,struct v4l2_subdev *s){
 if(route_error)return route_error;
 return c&&s?0:-EINVAL;
}
/* PREPARED_VALIDATOR */
static int e008k_rear_run_unreachable(struct vfe_device *v,
 struct e008k_rear_request *req,struct e008k_rear_result *result){
 (void)v;(void)req;(void)result;runner_calls++;return -EIO;
}
#include "camss-vfe-e008n-rear-single-use.inc"
#include "native-rear-startup-entry.inc"
static unsigned tests;
#define CHECK(x) do {tests++;if(!(x)){fprintf(stderr,"FAIL %d: %s\n",__LINE__,#x);abort();}}while(0)
static void putn(u64 value,u8 *p,unsigned n){for(unsigned i=0;i<n;i++)p[i]=(u8)(value>>(8*i));}
/* SYNTHETIC_INITIALIZER */
/* Only a host fixture resets consumption to explore independent error cases.
 * Production has no reset and remains one-use for the lifetime of its module.
 */
static void reset_host(void){atomic_store(&e008n_rear_consumed.value,0);route_error=0;full_fail_after=-1;}
int main(void){
 struct device d={1};struct camss c={&d};struct vfe_device v={&c};
 struct v4l2_subdev sensor={1};
 struct native_rear_startup_input *input=calloc(1,sizeof(*input));CHECK(input);
 struct native_rear_startup_request req={.sensor=&sensor,.input=input,.first_request_generation=1};
 struct native_rear_startup_result result,before;
 initialize(input);memset(&result,0xa5,sizeof(result));before=result;
 req.first_request_generation=U64_MAX;
 CHECK(native_rear_startup_run_once_unreachable(&v,&req,&result)==-EINVAL);
 CHECK(!memcmp(&result,&before,sizeof(result)));CHECK(!full_allocations);
 CHECK(!atomic_load(&e008n_rear_consumed.value));req.first_request_generation=1;
 input->statistics.packet[3].awb.threshold_b=0x40000;
 CHECK(native_rear_startup_run_once_unreachable(&v,&req,&result)==-ERANGE);
 CHECK(!result.composed&&!result.once.identity_consumed&&!full_allocations);
 CHECK(!atomic_load(&e008n_rear_consumed.value));
 initialize(input);
 CHECK(native_rear_startup_run_once_unreachable(&v,&req,&result)==-EOPNOTSUPP);
 CHECK(result.composed&&result.once.identity_consumed);
 CHECK(result.once.command_arena_allocated&&result.once.preflight_materialized);
 CHECK(result.once.command_arena_released&&!result.once.reboot_required);
 CHECK(!runner_calls&&!full_allocations);
 CHECK(native_rear_startup_run_once_unreachable(&v,&req,&result)==-EALREADY);
 CHECK(result.composed&&!result.once.identity_consumed&&!full_allocations);
 unsigned fault_cases=0;
 for(int nth=0;nth<32;nth++){
  reset_host();full_fail_after=nth;
  int ret=native_rear_startup_run_once_unreachable(&v,&req,&result);
  full_fail_after=-1;
  CHECK(ret==-ENOMEM||ret==-EOPNOTSUPP);
  CHECK(!full_allocations&&!runner_calls&&!result.once.reboot_required);
  if(ret==-EOPNOTSUPP)CHECK(result.once.preflight_materialized&&result.once.command_arena_released);
  fault_cases++;
 }
 reset_host();route_error=-ENOLINK;
 CHECK(native_rear_startup_run_once_unreachable(&v,&req,&result)==-ENOLINK);
 CHECK(result.composed&&result.once.identity_consumed);
 CHECK(result.once.command_arena_allocated&&result.once.command_arena_released);
 CHECK(!result.once.preflight_materialized&&!result.once.reboot_required);
 CHECK(!runner_calls&&!full_allocations);
 reset_host();CHECK(native_rear_startup_run_once_unreachable(&v,NULL,&result)==-EINVAL);
 CHECK(native_rear_startup_run_once_unreachable(&v,&req,NULL)==-EINVAL);
 free(input);
 printf("NATIVE_REAR_STARTUP_ENTRY_PASS assertions=%u allocation_fault_cases=%u real_single_use_wrapper=1 runtime_calls=%u hardware_access=0\n",tests,fault_cases,runner_calls);
 return 0;
}
