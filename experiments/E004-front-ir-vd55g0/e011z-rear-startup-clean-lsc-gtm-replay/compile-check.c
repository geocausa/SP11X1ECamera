#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include <errno.h>
#include <assert.h>
typedef uint8_t u8; typedef uint32_t u32; typedef uint64_t u64;
#define BIT(n) (1U << (n))
#define __used __attribute__((used))
#define E006G_LSC_BYTES 884
#define E006G_GTM_BYTES 2048
#define E007Y_STARTUP_PACKETS 4
#define E006Z_EPOCH_STARTUP 1
#define E007I_LSC_VALID_SELECTOR1 BIT(0)
#define E007I_LSC_VALID_SELECTOR2 BIT(1)
#define E007I_LSC_VALID_ALL (E007I_LSC_VALID_SELECTOR1|E007I_LSC_VALID_SELECTOR2)
#define E007Q_GTM_VALID BIT(0)

struct scalar_state { u64 request_id; u8 epoch_kind; u8 startup_phase; };
struct e007d_rear_register_state { struct scalar_state scalar; };
struct e007f_rear_dmi_state { u8 dummy; };
struct e007i_rear_lsc_wire_state {
    u64 request_id; u32 valid_mask;
    u8 selector1[E006G_LSC_BYTES]; u8 selector2[E006G_LSC_BYTES];
};
struct e007i_rear_dmi_state {
    struct e007f_rear_dmi_state dmi;
    struct e007i_rear_lsc_wire_state lsc;
};
struct e007q_rear_gtm_wire_state { u64 request_id; u32 valid_mask; u8 payload[E006G_GTM_BYTES]; };
struct e007q_rear_dmi_state {
    struct e007i_rear_dmi_state dmi;
    struct e007q_rear_gtm_wire_state gtm;
};
struct e007s_rear_dmi_state { struct e007q_rear_dmi_state dmi; };
struct e007t_rear_dmi_state { struct e007s_rear_dmi_state dmi; };
struct e007u_rear_dmi_state { struct e007t_rear_dmi_state dmi; };
struct e007v_rear_dmi_state { struct e007u_rear_dmi_state dmi; };
struct e008o_rear_packet_semantics {
    struct e007d_rear_register_state regs;
    struct e007v_rear_dmi_state dmi;
    u64 request_id; bool ready;
};
struct e008o_rear_semantic_set {
    struct e008o_rear_packet_semantics packet[E007Y_STARTUP_PACKETS];
    bool sealed;
};
static int e008o_rear_validate_semantic_set(struct e008o_rear_semantic_set *s)
{
    unsigned int p;
    if (!s || !s->sealed) return -EINVAL;
    for (p=0;p<4;p++) {
        struct e007q_rear_dmi_state *q=&s->packet[p].dmi.dmi.dmi.dmi.dmi;
        if (!s->packet[p].ready || s->packet[p].request_id < 4) return -EINVAL;
        if (s->packet[p].regs.scalar.request_id != s->packet[p].request_id ||
            s->packet[p].regs.scalar.startup_phase != p) return -EPROTO;
        if (q->gtm.request_id != s->packet[p].request_id ||
            q->dmi.lsc.request_id != s->packet[p].request_id) return -EPROTO;
    }
    return 0;
}
#include "camss-e011z-rear-startup-adaptive-bind.inc"

int main(void)
{
    struct e008o_rear_packet_semantics base[4] = {0};
    struct e008o_rear_semantic_set out;
    struct e011z_rear_startup_adaptive_wire wire;
    unsigned int p, i;
    memset(&wire, 0, sizeof(wire));
    for (i=0;i<E006G_LSC_BYTES;i++) {
        wire.lsc_selector1[0][i]=0x10; wire.lsc_selector2[0][i]=0x20;
        wire.lsc_selector1[1][i]=0x11; wire.lsc_selector2[1][i]=0x21;
    }
    memset(wire.gtm,0x33,sizeof(wire.gtm));
    for (p=0;p<4;p++) {
        base[p].request_id=4+p;
        base[p].regs.scalar.request_id=4+p;
        base[p].regs.scalar.epoch_kind=E006Z_EPOCH_STARTUP;
        base[p].regs.scalar.startup_phase=p;
    }
    assert(e011z_rear_bind_startup_adaptive(&out,base,&wire)==0);
    for (p=0;p<4;p++) {
        struct e007q_rear_dmi_state *q=&out.packet[p].dmi.dmi.dmi.dmi.dmi;
        unsigned int s=p ? 1 : 0;
        assert(out.packet[p].request_id==4+p);
        assert(q->dmi.lsc.selector1[0]==wire.lsc_selector1[s][0]);
        assert(q->dmi.lsc.selector2[0]==wire.lsc_selector2[s][0]);
        assert(q->gtm.payload[0]==0x33);
    }
    return 0;
}
