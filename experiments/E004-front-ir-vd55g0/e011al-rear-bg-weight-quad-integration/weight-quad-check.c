/* SPDX-License-Identifier: MIT */
#include <stdio.h>
#include "weight-quad-producer.h"
int main(void) {
    struct e011al_weight_quad_input in;
    struct e011al_weight_quad_output out;
    size_t n;
    while((n=fread(&in,1,sizeof(in),stdin))!=0) {
        if(n!=sizeof(in)||e011al_produce_weight_quad(&in,&out)) return 2;
        if(fwrite(&out,1,sizeof(out),stdout)!=sizeof(out)) return 3;
    }
    return ferror(stdin)?4:0;
}
