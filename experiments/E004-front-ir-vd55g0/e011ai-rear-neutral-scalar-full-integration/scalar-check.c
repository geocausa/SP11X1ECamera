/* SPDX-License-Identifier: MIT */
/* Host-only scalar producer, binary private input/output; no camera access. */
#include <stdio.h>
#include <stdlib.h>
#include "scalar-producer.h"
_Static_assert(sizeof(struct e011ai_scalar_inputs)==56,"input wire");
_Static_assert(sizeof(struct e011ai_scalar_output)==28,"output wire");
int main(void) {
    struct e011ai_scalar_inputs in;
    while(fread(&in,sizeof(in),1,stdin)==1) {
        struct e011ai_scalar_output out;
        if(e011ai_produce_scalar(&in,&out))return 2;
        if(fwrite(&out,sizeof(out),1,stdout)!=1)return 3;
    }
    return ferror(stdin)?4:0;
}
