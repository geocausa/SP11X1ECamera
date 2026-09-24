/* SPDX-License-Identifier: MIT */
#include "camss-e004pz-front-owner-observer.inc"
#include <assert.h>
#include <inttypes.h>
#include <stdio.h>

static unsigned int checks;
#define CHECK(x) do {checks++;assert((x));}while(0)

int main(void)
{
	struct e004pz_front_observer o;
	e004pz_u64 epoch = 0, next_epoch = 0;
	e004pz_front_observer_init(&o);
	CHECK(e004pz_front_runner_begin(&o, false, &epoch)==-EINVAL);
	CHECK(e004pz_front_runner_begin(&o, true, &epoch)==0 && epoch==1);
	CHECK(e004pz_front_runner_begin(&o, true, &next_epoch)==-EBUSY &&
	      next_epoch==0);
	/* Two prior REAL original physical Windows samples: front 0x271,
	 * rear 0x2F1, both masks bit7-enabled. Neither is a DMA fence.
	 */
	CHECK(e004pz_observe_csid1_status(&o,true,0x271)==E004PZ_IRQ_NO_BF);
	CHECK(e004pz_observe_csid1_status(&o,false,0x2f1)==E004PZ_IRQ_UNATTRIBUTED);
	CHECK(o.session_front_bf_count==0 &&
	      o.lifetime_unattributed_bf_count==1);
	CHECK(e004pz_observe_csid1_status(&o,true,0x2f1)==
	      E004PZ_IRQ_FRONT_ROUTE_SCOPED);
	CHECK(o.last_front_bf_epoch==epoch && o.session_front_bf_count==1);
	CHECK(e004pz_front_runner_end(&o,epoch+1,true)==-ESTALE &&
	      o.front_runner_active);
	CHECK(e004pz_front_runner_end(&o,epoch,true)==0 &&
	      !o.front_runner_active && o.last_owner_epoch==1);
	CHECK(e004pz_observe_csid1_status(&o,true,0x80)==E004PZ_IRQ_UNATTRIBUTED);
	CHECK(e004pz_front_runner_begin(&o,true,&next_epoch)==0 && next_epoch==2);
	CHECK(o.session_front_bf_count==0 && o.lifetime_front_bf_count==1);
	CHECK(e004pz_front_runner_end(&o,epoch,true)==-ESTALE);
	CHECK(e004pz_front_runner_end(&o,next_epoch,false)==-EIO &&
	      o.unsafe_stop_pinned && o.front_runner_active);
	CHECK(e004pz_front_runner_begin(&o,true,&epoch)==-ESHUTDOWN);
	CHECK(e004pz_observe_csid1_status(&o,true,0x80)==E004PZ_IRQ_UNATTRIBUTED);
	CHECK(e004pz_front_runner_end(&o,next_epoch,true)==-ESHUTDOWN);
	CHECK(e004pz_rear_processed_isp_authorize()==-EOPNOTSUPP);

	/* Independently allocated offline observer: 2 exact route labels ×
	 * the entire 16-bit latched-status domain, no camera/MMIO access.
	 */
	e004pz_front_observer_init(&o);
	CHECK(e004pz_front_runner_begin(&o,true,&epoch)==0 && epoch==1);
	for (unsigned int mode=0; mode<2; mode++) {
		for (unsigned int status=0; status<65536; status++) {
			bool bit7=(status & E004PZ_CSID1_BF_STATUS_BIT)!=0;
			bool route=mode==0;
			enum e004pz_irq_result want =
				!bit7 ? E004PZ_IRQ_NO_BF :
				route ? E004PZ_IRQ_FRONT_ROUTE_SCOPED :
				E004PZ_IRQ_UNATTRIBUTED;
			CHECK(e004pz_observe_csid1_status(&o,route,status)==want);
		}
	}
	CHECK(o.session_front_bf_count==32768);
	CHECK(o.lifetime_unattributed_bf_count==32768);
	CHECK(e004pz_front_runner_end(&o,epoch,true)==0);
	CHECK(e004pz_rear_processed_isp_authorize()==-EOPNOTSUPP);
	printf("PASS_E004PZ_FRONT_RUNNER_ONLY_131072_STATUS_ROUTE_CASES_%u_ASSERTIONS_NO_WM16_DMA_FENCE_REAR_DENIED\n",checks);
	return 0;
}
