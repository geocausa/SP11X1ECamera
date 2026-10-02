/* SPDX-License-Identifier: MIT */
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "cold-aec-source.h"
#include "../e011al-rear-bg-weight-quad-integration/weight-quad-producer.h"
static unsigned long checks;
#define CHECK(x) do { if (!(x)) { fprintf(stderr,"check at %u\n",__LINE__);exit(1); } checks++; } while (0)
static void reject(const unsigned char *wire,size_t size,unsigned major,
    unsigned minor,unsigned count,int expected)
{
    uint32_t out[3]={0xa5a5a5a5,0xa5a5a5a5,0xa5a5a5a5},saved[3];
    memcpy(saved,out,sizeof(out));
    CHECK(e011bw_decode_invariant_cold_weights(wire,size,major,minor,count,out)==expected);
    CHECK(!memcmp(out,saved,sizeof(out)));
}
int main(void)
{
    unsigned char wire[404],changed[404];uint32_t bits[3];
    while (fread(wire,1,404,stdin)==404) {
        int result=e011bw_decode_invariant_cold_weights(wire,404,0,0,4,bits);
        if (fwrite(&result,sizeof(result),1,stdout)!=1) return 2;
        if (!result) {
            struct e011al_weight_quad_input in={{bits[0],bits[1],bits[2]},0};
            struct e011al_weight_quad_output out;
            CHECK(e011al_produce_weight_quad(&in,&out)==0);
            CHECK(fwrite(bits,sizeof(bits),1,stdout)==1);
            CHECK(fwrite(out.aec_weight_q4,3,1,stdout)==1);
            reject(NULL,404,0,0,4,-EINVAL);
            reject(wire,403,0,0,4,-EINVAL);reject(wire,405,0,0,4,-EINVAL);
            reject(wire,404,1,0,4,-EINVAL);reject(wire,404,0,1,4,-EINVAL);
            reject(wire,404,0,0,3,-EINVAL);reject(wire,404,0,0,5,-EINVAL);
            CHECK(e011bw_decode_invariant_cold_weights(wire,404,0,0,4,NULL)==-EINVAL);
            for(unsigned grid=1;grid<4;grid++) for(unsigned lane=0;lane<3;lane++) {
                memcpy(changed,wire,404);changed[101*grid+20+4*lane]^=1;
                reject(changed,404,0,0,4,-EOPNOTSUPP);
            }
            const uint32_t bad[]={0x80000001,0xbf000000,0x3f800001,0x7f800000,0xff800000,0x7fc00000,0xffffffff};
            for(unsigned lane=0;lane<3;lane++) for(unsigned k=0;k<7;k++) {
                memcpy(changed,wire,404);
                for(unsigned grid=0;grid<4;grid++) {
                    uint32_t v=bad[k];
                    for(unsigned byte=0;byte<4;byte++) changed[101*grid+20+4*lane+byte]=(unsigned char)(v>>(8*byte));
                }
                reject(changed,404,0,0,4,-ERANGE);
            }
        }
    }
    fprintf(stderr,"checks=%lu\n",checks);return ferror(stdin)?3:0;
}
