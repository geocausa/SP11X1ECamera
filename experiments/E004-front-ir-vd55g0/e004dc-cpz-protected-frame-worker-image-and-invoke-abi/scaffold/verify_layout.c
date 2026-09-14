#include <stddef.h>
#include "sp11-securepd-worker-abi.h"
#define A(c) _Static_assert((c), #c)
A(sizeof(struct sp11_securepd_loadalgo_packet) == 12);
A(offsetof(struct sp11_securepd_loadalgo_packet, paddr) == 0);
A(offsetof(struct sp11_securepd_loadalgo_packet, len) == 4);
A(offsetof(struct sp11_securepd_loadalgo_packet, type) == 8);
A(sizeof(struct sp11_securepd_mem_handle) == 24);
A(offsetof(struct sp11_securepd_mem_handle, addr) == 8);
A(offsetof(struct sp11_securepd_mem_handle, ion_fd) == 16);
A(sizeof(struct sp11_securepd_gaussian_packet) == 96);
A(offsetof(struct sp11_securepd_gaussian_packet, src_width) == 24);
A(offsetof(struct sp11_securepd_gaussian_packet, src_height) == 28);
A(offsetof(struct sp11_securepd_gaussian_packet, src_stride) == 32);
A(offsetof(struct sp11_securepd_gaussian_packet, dst) == 40);
A(offsetof(struct sp11_securepd_gaussian_packet, dst_stride) == 64);
A(offsetof(struct sp11_securepd_gaussian_packet, heap) == 72);
A(sizeof(struct sp11_securepd_persistent_buffer) == 12);
A(SP11_SECUREPD_ALGO == 4 && SP11_SECUREPD_STATIC_EXEC == 8);
int main(void) { return 0; }
