/* SPDX-License-Identifier: MIT */
#ifndef SP11_SECUREPD_NATIVE_API_H
#define SP11_SECUREPD_NATIVE_API_H
#include <stdint.h>

struct sp11_dsc_feat_priv;
struct sp11_securepd_mailbox { uint8_t opaque[32]; };

enum sp11_securepd_mb_type { SP11_MB_CREATE=0, SP11_MB_RETRIEVE=1 };
enum sp11_qurt_cache_mode { SP11_QURT_MEM_CACHE_WRITEBACK=7 };

extern int secure_pd_mb_get(struct sp11_securepd_mailbox *mb, char *name,
                            unsigned char type, unsigned char id);
extern int secure_pd_mb_receive(struct sp11_securepd_mailbox *mb, void *buf,
                                unsigned int len, unsigned int *received_len);
extern int secure_pd_mb_send(struct sp11_securepd_mailbox *mb, void *buf,
                             unsigned int len);
extern int secure_pd_mb_delete(struct sp11_securepd_mailbox *mb);
extern void get_secure_channel_handle(struct sp11_dsc_feat_priv **handle);
extern int dsc_verify_buffer(struct sp11_dsc_feat_priv *handle,
                             unsigned int type,
                             unsigned long long paddr,
                             unsigned int len);
extern int secure_pd_mapping_create_64(unsigned int *vaddr,
                                        unsigned long long paddr,
                                        unsigned int len,
                                        unsigned char cache_mode,
                                        unsigned char permission);
extern int secure_pd_mapping_delete_64(unsigned int vaddr,
                                        unsigned int len);
extern int secure_pd_thread_create(char *name, void *stack,
                                    unsigned int stack_size,
                                    unsigned short priority,
                                    void (*entry)(void *), void *arg,
                                    unsigned int *thread_id);
extern void qurt_sleep(unsigned long long usec);

#endif
