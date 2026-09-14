#include <stdio.h>
#include <string.h>
#include "sp11-loadalgo-camera-proxy.h"
int main(void){struct sp11_loadalgo_gaussian_call c;size_t h=sp11_securepd_camera_heap_required(644,604);if(sp11_loadalgo_camera_build_call(&c,0x1122334455667788ULL,10,583464,11,583464,12,(uint32_t)h,644,604))return 1;if(c.src_offset||c.dst_offset||c.heap_offset||c.mode_static)return 2;if(c.src_stride!=644||c.dst_stride!=644||c.dst_len!=583464||c.heap_len!=h)return 3;puts("E004dj shipped-proxy call contract: PASS");return 0;}
