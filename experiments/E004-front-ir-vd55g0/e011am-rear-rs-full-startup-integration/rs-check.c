/* SPDX-License-Identifier: MIT */
#include <stdio.h>
#include "rs-producer.h"
int main(void) {
    struct e011am_rs_input in;struct e011am_rs_output out;size_t n;
    while((n=fread(&in,1,sizeof(in),stdin))!=0) {
        if(n!=sizeof(in)||e011am_produce_rs(&in,&out)) return 2;
        if(fwrite(&out,1,sizeof(out),stdout)!=sizeof(out)) return 3;
    }
    return ferror(stdin)?4:0;
}
