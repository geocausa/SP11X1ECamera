/* Camera-free representative RAW10 test, no image frames or device IO. */
#include "../raw10_unpack.h"
#include <assert.h>
#include <stdio.h>
#include <stdint.h>
int main(void)
{
    const uint8_t row[] = {4,5,6,7,0xe4, 11,12,13,14,0x1b,0xaa,0xbb};
    const uint16_t want[] = {16,21,26,31,47,50,53,56};
    for (size_t i=0;i<8;i++) {
        uint16_t got=65535;
        assert(sp11_raw10_pixel(row,sizeof row,8,i,&got)==0);
        assert(got==want[i]);
    }
    uint16_t got=65535;
    assert(sp11_raw10_pixel(row,sizeof row,8,8,&got)==-1);
    assert(sp11_raw10_pixel(row,9,8,7,&got)==-1);
    assert(sp11_raw10_pixel(row,sizeof row,7,6,&got)==-1);
    assert(sp11_raw10_pixel(NULL,sizeof row,8,0,&got)==-1);
    assert(sp11_raw10_pixel(row,sizeof row,8,0,NULL)==-1);
    uint8_t front[4800] = {0};
    uint8_t rear[5104] = {0};
    /* Front last group occupies 4795..4799 exactly; rear last packed
       group ends at 5094 and bytes 5095..5103 are padding. */
    for (size_t i=5095;i<sizeof rear;i++) rear[i]=0xff;
    assert(sp11_raw10_pixel(front,sizeof front,3840,3839,&got)==0 && got==0);
    assert(sp11_raw10_pixel(rear,sizeof rear,4076,4075,&got)==0 && got==0);
    /* The sensor formats have padded or full-stride rows; only the packed
       group is decoded, never the padding nor arbitrary 8-bit proxy. */
    puts("RGB_RAW10_FULL_PRECISION_OFFLINE_TEST=PASS GROUP4_LSB_AND_ROW_PADDING");
    return 0;
}
