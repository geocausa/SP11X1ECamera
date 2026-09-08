// SPDX-License-Identifier: GPL-2.0-only
#include "native-aec-state.h"
#include <float.h>
#include <math.h>
#include <stddef.h>
#include <string.h>

/* From the separately verified BJ clean-room primitive. */
float e003i_log103_coordinate(uint64_t exposure);

static float f32bits(uint32_t u)
{
    float f;
    memcpy(&f, &u, sizeof(f));
    return f;
}

/* Force the same visible float32 boundaries used by the tuning evaluator. */
__attribute__((noinline)) static float fadd32(float a, float b)
{
    volatile float r = a + b;
    return r;
}
__attribute__((noinline)) static float fsub32(float a, float b)
{
    volatile float r = a - b;
    return r;
}
__attribute__((noinline)) static float fmul32(float a, float b)
{
    volatile float r = a * b;
    return r;
}
__attribute__((noinline)) static float fdiv32(float a, float b)
{
    volatile float r = a / b;
    return r;
}

struct target_region { float start, end, value; };
static const struct target_region framesa_target[] = {
    {   0.0f,  140.0f, 55.0f },
    { 160.0f,  270.0f, 50.0f },
    { 300.0f,  360.0f, 46.0f },
    { 370.0f,  410.0f, 40.0f },
    { 420.0f,  460.0f, 40.0f },
    { 500.0f, 1000.0f, 30.0f },
};

float e003i_framesa_target_low(float x)
{
    size_t i;
    const struct target_region *prev = &framesa_target[0];

    if (x < framesa_target[0].start)
        return framesa_target[0].value;

    for (i = 0; i < sizeof(framesa_target)/sizeof(framesa_target[0]); ++i) {
        const struct target_region *cur = &framesa_target[i];
        if (x < cur->start) {
            float t = fdiv32(fsub32(x, prev->end),
                             fsub32(cur->start, prev->end));
            return fadd32(fmul32(fsub32(1.0f, t), prev->value),
                          fmul32(t, cur->value));
        }
        if (x <= cur->end)
            return cur->value;
        prev = cur;
    }
    return framesa_target[(sizeof(framesa_target)/sizeof(framesa_target[0]))-1].value;
}

static int target_si(uint64_t source_exposure, float measured,
                     float target, uint64_t *out)
{
    const float epsilon = f32bits(0x33d6bf95U);
    float den = measured > epsilon ? measured : epsilon;
    float ratio = fdiv32(target, den);
    double product = (double)source_exposure * (double)ratio;

    if (!isfinite(product) || product < 0.0 || product > (double)UINT64_MAX)
        return -1;
    *out = (uint64_t)product;
    return 0;
}

float e003i_algorithm001_lux(float measured, float history_reference,
                             float previous_lux, float alpha)
{
    const float epsilon = f32bits(0x33d6bf95U);
    const float target = f32bits(0x42480000U); /* 50.0f */
    const float scale = f32bits(0x429bcc0cU);
    float den = measured > epsilon ? measured : epsilon;
    float num = target > epsilon ? target : epsilon;
    float ratio = fdiv32(num, den);
    float delta = 0.0f;
    float candidate;

    if (ratio > 0.0f)
        delta = (float)(log10((double)ratio) * (double)scale);

    candidate = fadd32(history_reference, delta);
    if (candidate < 0.0f)
        candidate = 0.0f;

    if (fabsf(previous_lux) >= 0.5f) {
        candidate = fadd32(fmul32(fsub32(1.0f, alpha), candidate),
                           fmul32(alpha, previous_lux));
    }
    return candidate;
}

void e003i_aec_state_init(struct e003i_aec_state *s,
                          float initial_lux_trigger,
                          float algorithm001_alpha)
{
    memset(s, 0, sizeof(*s));
    s->lux_trigger = initial_lux_trigger;
    s->algorithm001_alpha = algorithm001_alpha;
}

int e003i_aec_state_commit_exposure(struct e003i_aec_state *s,
                                    uint64_t frame_id,
                                    const uint64_t lanes[E003I_AEC_LANES])
{
    struct e003i_aec_history_entry *e;
    if (!s || !lanes)
        return -1;
    e = &s->history[frame_id % E003I_AEC_HISTORY_SLOTS];
    e->frame_id = frame_id;
    memcpy(e->lanes, lanes, sizeof(e->lanes));
    e->valid = 1;
    return 0;
}

static const struct e003i_aec_history_entry *history_get(
    const struct e003i_aec_state *s, uint64_t frame_id)
{
    const struct e003i_aec_history_entry *e =
        &s->history[frame_id % E003I_AEC_HISTORY_SLOTS];
    return (e->valid && e->frame_id == frame_id) ? e : NULL;
}

int e003i_aec_state_process(struct e003i_aec_state *s,
                            uint64_t frame_id,
                            float measured_luma,
                            uint64_t source_exposure_s1,
                            struct e003i_aec_request_result *out)
{
    const struct e003i_aec_history_entry *h3, *h1;
    struct e003i_aec_publication_entry *pub, *future;
    float lux_in, target, href, next;
    uint64_t si;

    if (!s || !out || frame_id < 3)
        return -1;
    h3 = history_get(s, frame_id - 3);
    if (!h3)
        return -2; /* fail closed: Algorithm001 F-3 history absent */

    memset(out, 0, sizeof(*out));
    out->frame_id = frame_id;
    lux_in = s->lux_trigger;
    target = e003i_framesa_target_low(lux_in);
    if (target_si(source_exposure_s1, measured_luma, target, &si))
        return -3;

    href = e003i_log103_coordinate(h3->lanes[E003I_AEC_S1_LANE]);
    next = e003i_algorithm001_lux(measured_luma, href, lux_in,
                                  s->algorithm001_alpha);

    out->lux_trigger_in = lux_in;
    out->target_low = target;
    out->measured_luma = measured_luma;
    out->frame_sa_safe_si = si;
    out->history_reference_frame = frame_id - 3;
    out->history_reference_s1_exposure = h3->lanes[E003I_AEC_S1_LANE];
    out->history_reference_log103 = href;
    out->next_lux_trigger = next;

    pub = &s->publication[frame_id % E003I_AEC_PUBLICATION_SLOTS];
    if (pub->valid && pub->frame_id == frame_id) {
        out->external_lux_valid = 1;
        out->external_lux = pub->lux;
        pub->valid = 0;
    }
    future = &s->publication[(frame_id + 2) % E003I_AEC_PUBLICATION_SLOTS];
    if (future->valid && future->frame_id != frame_id + 2)
        return -4;
    future->frame_id = frame_id + 2;
    future->lux = next;
    future->valid = 1;
    s->lux_trigger = next;

    if (frame_id > 0 && (h1 = history_get(s, frame_id - 1)) != NULL) {
        out->previous_exposure_valid = 1;
        out->previous_exposure_frame = frame_id - 1;
        memcpy(out->previous_exposure_lanes, h1->lanes,
               sizeof(out->previous_exposure_lanes));
    }
    return 0;
}
