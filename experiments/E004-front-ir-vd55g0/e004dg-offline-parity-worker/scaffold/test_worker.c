#include <stdio.h>
#include <string.h>
#include "sp11-parity-worker.h"

static int failures;
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"FAIL %s:%d: %s\n",__FILE__,__LINE__,#x); failures++; } } while (0)

static struct sp11_worker_request base_req(uint8_t *dst, size_t dn, const uint8_t *src, size_t sn)
{
	struct sp11_worker_request r = {0};
	r.dst_base=dst; r.dst_extent=dn; r.src=src; r.src_extent=sn;
	r.width=4; r.height=2; r.payload_offset=3;
	r.captured_extent=15; r.serialized_extent=15;
	return r;
}

int main(void)
{
	uint8_t src[16], dst[32], before[32];
	struct sp11_worker_request r;
	int i, ret;
	for (i=0;i<16;i++) src[i]=(uint8_t)(0x10+i);

	memset(dst,0x55,sizeof(dst)); r=base_req(dst,sizeof(dst),src,sizeof(src)); r.synthetic_fill=1;
	ret=sp11_parity_worker_run(&r); CHECK(ret==SP11_WORKER_OK);
	for(i=0;i<3;i++) CHECK(dst[i]==0x55);
	for(i=3;i<11;i++) CHECK(dst[i]==100);
	for(i=11;i<15;i++) CHECK(dst[i]==0x80);

	memset(dst,0x66,sizeof(dst)); r=base_req(dst,sizeof(dst),src,sizeof(src)); r.request_id=9;
	ret=sp11_parity_worker_run(&r); CHECK(ret==SP11_WORKER_OK);
	CHECK(memcmp(dst+3,src,8)==0);
	for(i=11;i<15;i++) CHECK(dst[i]==0x80);

	memset(dst,0x77,sizeof(dst)); memcpy(before,dst,sizeof(dst)); r=base_req(dst,sizeof(dst),src,sizeof(src)); r.request_id=10;
	ret=sp11_parity_worker_run(&r); CHECK(ret==SP11_WORKER_ESWAB_PENDING);
	CHECK(memcmp(dst,before,sizeof(dst))==0);

	memset(dst,0,sizeof(dst)); r=base_req(dst,sizeof(dst),src,sizeof(src)); r.serialized_extent=14;
	CHECK(sp11_parity_worker_run(&r)==SP11_WORKER_EBOUNDS);
	r=base_req(dst,sizeof(dst),src,7); CHECK(sp11_parity_worker_run(&r)==SP11_WORKER_EBOUNDS);
	r=base_req(dst,sizeof(dst),src,sizeof(src)); r.payload_offset=16; CHECK(sp11_parity_worker_run(&r)==SP11_WORKER_EBOUNDS);
	r=base_req(dst,sizeof(dst),src,sizeof(src)); r.width=0; CHECK(sp11_parity_worker_run(&r)==SP11_WORKER_EINVAL);

	if (failures) return 1;
	puts("E004dg host vectors: PASS");
	return 0;
}
