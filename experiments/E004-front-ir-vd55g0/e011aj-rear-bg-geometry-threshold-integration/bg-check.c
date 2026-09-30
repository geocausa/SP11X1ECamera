/* SPDX-License-Identifier: MIT */
/* Native differential wire is private on SP11; no captured register input. */
#include <stdio.h>
#include "bg-producer.h"
int main(void) {
    struct e011aj_bg_input in;
    struct e011aj_bg_output out;
    while(fread(&in,sizeof(in),1,stdin)==1) {
        if(e011aj_produce_bg(&in,&out)) return 2;
        if(fwrite(&out,sizeof(out),1,stdout)!=1) return 3;
    }
    return ferror(stdin)?4:0;
}
