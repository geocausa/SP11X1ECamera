/* SPDX-License-Identifier: MIT */
/* The EXACT native candidate header is compiled and exercised under C11. */
#include "camss-vfe-e004pv-bf-owner-ring.inc"
#include <assert.h>
#include <stdio.h>
#include <errno.h>

static unsigned int checks;
#define CHECK(expr) do { ++checks; assert((expr)); } while (0)

static struct e004pv_bf_completion proof(e004pv_u64 owner, e004pv_u64 frame,
					 e004pv_u64 token, e004pv_u16 tag)
{
	return (struct e004pv_bf_completion) {
		.owner_epoch = owner, .frame_epoch = frame,
		.fifo8_queue_token = token,
		.outstanding_wm16_queue_token = token,
		.wm16_tag = tag, .fifo_index = 8, .event_id = 0x0f,
		.wm_id = 16, .fifo8_entry_verified = true,
		.outstanding_wm16_match_nonnull = true,
		.same_owner_and_frame_verified = true,
		.independently_trusted_wm16_irq_and_ack = true,
		.dma_iommu_safe_for_exact_buffer = true,
		.all_other_five_groups_completed = true,
	};
}

static struct e004pv_bf_stop_fence stop_fence(e004pv_u64 owner)
{
	return (struct e004pv_bf_stop_fence) {
		.owner_epoch = owner, .source_input_quiescent = true,
		.all_wms_bus_stopped = true,
		.irq_masked_acknowledged_drained = true,
		.all_generation_dma_complete = true,
		.iommu_surface_safe = true,
		.independent_same_owner_hw_evidence = true,
	};
}

int main(void)
{
	struct e004pv_bf_ring r;
	struct e004pv_bf_completion p;
	struct e004pv_bf_stop_fence s;
	e004pv_bf_ring_init(&r);
	CHECK(e004pv_bf_owner_begin(&r, 1, false) == -EAGAIN);
	CHECK(e004pv_bf_owner_begin(&r, 1, true) == 0);
	CHECK(e004pv_bf_owner_begin(&r, 2, true) == -EBUSY);
	CHECK(e004pv_bf_enqueue(&r, 1, 1, 0, 1, true) == -EINVAL);
	CHECK(e004pv_bf_enqueue(&r, 1, 1, 101, 1, false) == -EIO);
	CHECK(r.count == 0 && r.last_frame_epoch == 0);
	CHECK(e004pv_bf_enqueue(&r, 2, 1, 101, 1, true) == -ESTALE);
	for (unsigned int i=0; i<E004PV_DEPTH; i++) {
		CHECK(e004pv_bf_enqueue(&r, 1, 1+i, 101+i, (e004pv_u16)(1+i), true)==0);
		CHECK(r.count==i+1);
	}
	CHECK(e004pv_bf_enqueue(&r, 1, 5, 105, 5, true) == -ENOSPC);
	CHECK(e004pv_bf_enqueue(&r, 1, 4, 104, 4, true) == -ESTALE);
	p=proof(1,1,101,1);
	CHECK(e004pv_bf_confirm_and_pop(&r, NULL) == -EINVAL);
	p.fifo8_queue_token=999;
	CHECK(e004pv_bf_confirm_and_pop(&r,&p)==-ESTALE && r.count==4);
	p.fifo8_queue_token=101;
	p.outstanding_wm16_queue_token=999;
	CHECK(e004pv_bf_confirm_and_pop(&r,&p)==-ESTALE && r.count==4);
	p.outstanding_wm16_queue_token=101;
	p.wm16_tag=2;
	CHECK(e004pv_bf_confirm_and_pop(&r,&p)==-ESTALE && r.count==4);
	p.wm16_tag=1;
	p.fifo_index=9;
	CHECK(e004pv_bf_confirm_and_pop(&r,&p)==-EINVAL && r.count==4);
	p.fifo_index=8;
	p.event_id=2;
	CHECK(e004pv_bf_confirm_and_pop(&r,&p)==-EINVAL && r.count==4);
	p.event_id=0x0f;
	p.wm_id=18;
	CHECK(e004pv_bf_confirm_and_pop(&r,&p)==-EINVAL && r.count==4);
	p.wm_id=16;
	CHECK(e004pv_bf_request_stop(&r,1)==0);
	CHECK(e004pv_bf_request_stop(&r,1)==-EALREADY);
	CHECK(e004pv_bf_enqueue(&r,1,5,105,5,true)==-ESHUTDOWN);
	s=stop_fence(1);
	CHECK(e004pv_bf_finish_stop(&r,&s)==-EBUSY);
	CHECK(e004pv_bf_confirm_and_pop(&r,&p)==0 && r.count==3);
	CHECK(e004pv_bf_confirm_and_pop(&r,&p)==-ESTALE && r.count==3);
	for (unsigned int i=1;i<E004PV_DEPTH;i++) {
		p=proof(1,1+i,101+i,(e004pv_u16)(1+i));
		CHECK(e004pv_bf_confirm_and_pop(&r,&p)==0);
	}
	CHECK(r.count==0);
	s.owner_epoch=2;
	CHECK(e004pv_bf_finish_stop(&r,&s)==-ESTALE);
	s.owner_epoch=1;
	s.iommu_surface_safe=false;
	CHECK(e004pv_bf_finish_stop(&r,&s)==-EAGAIN);
	s.iommu_surface_safe=true;
	CHECK(e004pv_bf_finish_stop(&r,&s)==0);
	CHECK(e004pv_bf_owner_begin(&r,1,true)==-ESTALE);
	CHECK(e004pv_bf_owner_begin(&r,2,true)==0);
	CHECK(e004pv_bf_enqueue(&r,2,1,201,1,true)==-ESTALE);
	CHECK(e004pv_bf_enqueue(&r,2,5,205,5,true)==0);
	p=proof(2,5,205,5);
	p.same_owner_and_frame_verified=false;
	CHECK(e004pv_bf_confirm_and_pop(&r,&p)==-EAGAIN);
	p.same_owner_and_frame_verified=true;
	CHECK(e004pv_bf_confirm_and_pop(&r,&p)==0);
	CHECK(e004pv_bf_request_stop(&r,2)==0);
	s=stop_fence(2);
	CHECK(e004pv_bf_finish_stop(&r,&s)==0);
	CHECK(e004pv_rear_isp_runtime_authorize()==-EOPNOTSUPP);

	/* Every combination of all six evidence fields: only all-true
	 * can remove a SOFTWARE entry, still never arm/retire a real DMA buffer.
	 */
	for (unsigned int bits=0;bits<64;bits++) {
		const e004pv_u64 owner=3+bits, frame=6+bits, token=1000+bits;
		e004pv_bf_ring_init(&r);
		CHECK(e004pv_bf_owner_begin(&r,owner,true)==0);
		CHECK(e004pv_bf_enqueue(&r,owner,frame,token,7,true)==0);
		p=proof(owner,frame,token,7);
		p.fifo8_entry_verified=(bits&(1u<<0))!=0;
		p.outstanding_wm16_match_nonnull=(bits&(1u<<1))!=0;
		p.same_owner_and_frame_verified=(bits&(1u<<2))!=0;
		p.independently_trusted_wm16_irq_and_ack=(bits&(1u<<3))!=0;
		p.dma_iommu_safe_for_exact_buffer=(bits&(1u<<4))!=0;
		p.all_other_five_groups_completed=(bits&(1u<<5))!=0;
		CHECK(e004pv_bf_confirm_and_pop(&r,&p)==(bits==63u?0:-EAGAIN));
		CHECK(r.count==(bits==63u?0u:1u));
		CHECK(e004pv_rear_isp_runtime_authorize()==-EOPNOTSUPP);
		if(bits!=63u){
			p=proof(owner,frame,token,7);
			CHECK(e004pv_bf_confirm_and_pop(&r,&p)==0);
		}
	}
	printf("PASS_E004PV_SHARED_KERNEL_C11_RING_64_EVIDENCE_PATTERNS_%u_ASSERTIONS_RUNTIME_REAR_DENIED\n",checks);
	return 0;
}
