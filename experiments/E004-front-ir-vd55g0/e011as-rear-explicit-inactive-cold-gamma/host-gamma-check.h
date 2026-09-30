/* SPDX-License-Identifier: GPL-2.0-only */
/* Host-only tests of actual selected materializer, encoders and validation. */
static unsigned int as_calls, as_gamma_calls, as_fail_at;
static int as_callback(u8 *dst,size_t bytes,u8 selector)
{
	as_calls++;
	if (selector == 2)
		as_gamma_calls++;
	memset(dst, 0x37, bytes); /* prove failed producer bytes are cleared */
	return as_calls == as_fail_at ? -EIO : 0;
}
static int as_lsc(void *ctx,u8 selector,u8 *dst,size_t bytes)
{
	(void)ctx;(void)selector;
	return as_callback(dst,bytes,0);
}
static int as_gtm(void *ctx,u8 *dst,size_t bytes)
{
	(void)ctx;return as_callback(dst,bytes,0);
}
static int as_bf(void *ctx,u8 selector,u8 *dst,size_t bytes)
{
	(void)ctx;return as_callback(dst,bytes,selector);
}
static int as_stable(void *ctx,u16 reg,u8 selector,u8 *dst,size_t bytes)
{
	(void)ctx;(void)reg;(void)selector;(void)dst;(void)bytes;return 0;
}
static void e011as_host_gamma_checks(void)
{
	const struct e006g_rear_producer_ops mock={
		.lsc=as_lsc,.gtm=as_gtm,.bfstats=as_bf,.stable=as_stable};
	const struct e007f_rear_dmi_upstream_ops upstream={
		.lsc=as_lsc,.gtm=as_gtm,.stable=as_stable};
	struct e006g_rear_dynamic_payloads d={0}, zero={0}, saved;
	struct e007f_rear_dmi_state f={.upstream=&upstream};
	struct e006g_rear_dmi_slot slot={.dmi_reg=0xbc08,.selector=2,
		.payload_bytes=128,.kind=E006G_PAYLOAD_BF_GAMMA};
	u8 buf[128],keep[128];
	struct e006g_rear_slot_buffer out={.cpu=buf,.bytes=128};
	as_calls=as_gamma_calls=as_fail_at=0;
	CHECK(e011as_rear_prepare_dynamic_selected(&mock,NULL,&d,false)==0);
	CHECK(as_calls==4 && as_gamma_calls==0);
	CHECK(d.materialized && !d.bf_gamma_materialized);
	CHECK(!memcmp(d.bf_gamma,zero.bf_gamma,sizeof(d.bf_gamma)));
	memset(buf,0xa5,sizeof(buf));memcpy(keep,buf,sizeof(buf));
	CHECK(e006g_rear_fill_slot(&mock,NULL,&d,&slot,&out)==-EOPNOTSUPP);
	CHECK(!memcmp(buf,keep,sizeof(buf)));
	saved=d;as_calls=0;
	CHECK(e011as_rear_prepare_dynamic_selected(&mock,NULL,&d,false)==-EINVAL);
	CHECK(!as_calls && !memcmp(&d,&saved,sizeof(d)));

	for(unsigned int active=0;active<2;active++)
		for(unsigned int failure=1;failure<=(active?5U:4U);failure++) {
			memset(&d,0,sizeof(d));as_calls=as_gamma_calls=0;as_fail_at=failure;
			CHECK(e011as_rear_prepare_dynamic_selected(&mock,NULL,&d,active)==-EIO);
			CHECK(!memcmp(&d,&zero,sizeof(d)));
		}
	as_calls=as_gamma_calls=as_fail_at=0;memset(&d,0,sizeof(d));
	CHECK(e006g_rear_prepare_dynamic(&mock,NULL,&d)==0);
	CHECK(as_calls==5 && as_gamma_calls==1 && d.bf_gamma_materialized);
	CHECK(e006g_rear_fill_slot(&mock,NULL,&d,&slot,&out)==0);
	for(unsigned int i=0;i<sizeof(buf);i++)CHECK(buf[i]==0x37);

	/* Real BF encoder plus recursive integration accepts explicit absence. */
	f.bfstats25.roi_count=25;f.bfstats25.gamma_inactive=true;
	CHECK(e007f_rear_validate_dmi_integration(&f)==0);
	memset(&d,0,sizeof(d));
	CHECK(e007f_rear_prepare_dynamic(&f,&d)==0);
	CHECK(d.materialized && !d.bf_gamma_materialized);
	CHECK(!memcmp(d.bf_gamma,zero.bf_gamma,sizeof(d.bf_gamma)));
	memset(buf,0xa5,sizeof(buf));
	CHECK(e007e_bfstats25_dmi(&f.bfstats25,2,buf,sizeof(buf))==-EOPNOTSUPP);
	CHECK(!memcmp(buf,keep,sizeof(buf)));
	f.bfstats25.gamma_valid=true;
	CHECK(e007f_rear_validate_dmi_integration(&f)!=0);
	CHECK(e007e_bfstats25_dmi(&f.bfstats25,2,buf,sizeof(buf))==-EOPNOTSUPP);
	f.bfstats25.gamma_valid=false;
	for(unsigned int i=0;i<32;i++) {
		f.bfstats25.gamma[i]=1;
		CHECK(e007f_rear_validate_dmi_integration(&f)!=0);
		f.bfstats25.gamma[i]=0;
	}
	f.bfstats25.gamma_inactive=false;
	CHECK(e007f_rear_validate_dmi_integration(&f)==-EOPNOTSUPP);
	f.bfstats25.gamma_valid=true;
	for(unsigned int i=0;i<32;i++)f.bfstats25.gamma[i]=512*i;
	CHECK(e007f_rear_validate_dmi_integration(&f)==0);
	CHECK(e007e_bfstats25_dmi(&f.bfstats25,2,buf,sizeof(buf))==0);
	memset(&d,0,sizeof(d));
	CHECK(e007f_rear_prepare_dynamic(&f,&d)==0);
	CHECK(d.bf_gamma_materialized);
	CHECK(!memcmp(buf,d.bf_gamma,sizeof(buf)));
}
