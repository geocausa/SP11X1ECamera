#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "sp11-swasf-cd90.h"
int main(void)
{
    static const int16_t p1[8]={0,68,136,204,272,340,408,476};
    static const uint8_t p3[8]={150,136,139,144,148,153,157,162};
    static const int16_t p4[8]={230,234,239,244,249,253,258,263};
    static const int16_t p5[8]={0,28,68,81,81,81,81,81};
    static const int16_t p6[8]={188,205,211,213,209,195,154,113};
    static const int16_t p7[8]={0,28,68,81,83,83,83,83};
    static const int32_t p8[8]={-857,-762,-619,-584,-603,-621,-611,-538};
    static const uint8_t p9[8]={20,31,47,65,82,100,117,134};
    static const int16_t p10[8]={0,68,136,204,272,340,408,476};
    static const int16_t p11[8]={256,256,256,256,256,256,256,256};
    static const int16_t p12[8]={256,256,256,256,256,256,256,256};
    static const uint8_t want[8]={0x00,0x00,0x05,0x18,0x29,0x3b,0x4c,0x5f};
    uint32_t tune[513]; uint8_t got[8]; FILE *f;
    f=fopen("oracle/windows-cd90-consistent/p13.bin","rb");
    if(!f || fread(tune,1,sizeof(tune),f)!=sizeof(tune)) return 2;
    fclose(f);
    sp11_swasf_cd90(p1,got,p3,p4,p5,p6,p7,p8,p9,p10,p11,p12,tune);
    if(memcmp(got,want,8)){int i;for(i=0;i<8;i++)fprintf(stderr,"%d got=%u want=%u\n",i,got[i],want[i]);return 1;}
    puts("E004dh CD90 consistent Windows capture: PASS");return 0;
}
