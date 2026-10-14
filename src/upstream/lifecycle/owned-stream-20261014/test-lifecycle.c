/* SPDX-License-Identifier: GPL-2.0-only */
#include <assert.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#define ENOIOCTLCMD 515
#include "camss-video-lifecycle.h"

struct device { unsigned int id; };
struct fixture {
	struct device devices[CAMSS_VIDEO_MAX_SUBDEVS];
	bool live[CAMSS_VIDEO_MAX_SUBDEVS];
	int fail_start, fail_stop, unsupported;
	int log[64];
	unsigned int calls;
};

static int call(void *opaque, void *device, bool on)
{
	struct fixture *f = opaque;
	struct device *d = device;
	f->log[f->calls++] = (on ? 100 : 200) + d->id;
	if (on && (int)d->id == f->unsupported)
		return -ENOIOCTLCMD;
	if (on && (int)d->id == f->fail_start)
		return -EAGAIN;
	if (!on && (int)d->id == f->fail_stop)
		return -ETIMEDOUT;
	f->live[d->id] = on;
	return 0;
}

static void init(struct fixture *f, void **devices, unsigned int n)
{
	memset(f, 0, sizeof(*f));
	f->fail_start = f->fail_stop = f->unsupported = -1;
	for (unsigned int i = 0; i < n; i++) {
		f->devices[i].id = i;
		devices[i] = &f->devices[i];
	}
}

int main(void)
{
	unsigned int cases = 0;
	for (unsigned int n = 1; n <= CAMSS_VIDEO_MAX_SUBDEVS; n++) {
		struct fixture f;
		void *devices[CAMSS_VIDEO_MAX_SUBDEVS];
		unsigned int order[CAMSS_VIDEO_MAX_SUBDEVS];
		struct camss_video_lifecycle state = {0};
		init(&f, devices, n);
		for (unsigned int i = 0; i < n; i++)
			order[i] = i;
		assert(!camss_video_start_owned(&state, devices, n, &f, call));
		assert(!camss_video_stop_owned(&state, order, &f, call));
		assert(!state.count && !state.fault);
		for (unsigned int i = 0; i < n; i++)
			assert(!f.live[i]);
		cases++;

		for (unsigned int fail = 0; fail < n; fail++) {
			for (int stop = -1; stop < (int)fail; stop++) {
				memset(&state, 0, sizeof(state));
				init(&f, devices, n);
				f.fail_start = fail;
				f.fail_stop = stop;
				assert(camss_video_start_owned(&state, devices, n, &f, call) == -EAGAIN);
				assert(f.calls == fail + 1 + fail);
				for (unsigned int i = 0; i <= fail; i++)
					assert(f.log[i] == 100 + (int)i);
				for (unsigned int i = 0; i < fail; i++)
					assert(f.log[fail + 1 + i] == 200 + (int)fail - 1 - (int)i);
				assert(state.fault == (stop >= 0));
				for (unsigned int i = 0; i < n; i++)
					assert(f.live[i] == ((int)i == stop));
				if (stop >= 0) {
					unsigned int before = f.calls;
					assert(camss_video_start_owned(&state, devices, n, &f, call) == -EIO);
					assert(camss_video_stop_owned(&state, order, &f, call) == -EIO);
					assert(f.calls == before);
				} else {
					assert(!state.count);
				}
				cases++;
			}
		}

		for (unsigned int unsupported = 0; unsupported < n; unsupported++) {
			memset(&state, 0, sizeof(state));
			init(&f, devices, n);
			f.unsupported = unsupported;
			assert(!camss_video_start_owned(&state, devices, n, &f, call));
			assert(!camss_video_stop_owned(&state, order, &f, call));
			assert(f.calls == 2 * n - 1);
			assert(!state.fault && !state.count);
			cases++;
		}
		for (unsigned int stop = 0; stop < n; stop++) {
			memset(&state, 0, sizeof(state));
			init(&f, devices, n);
			assert(!camss_video_start_owned(&state, devices, n, &f, call));
			f.fail_stop = stop;
			assert(camss_video_stop_owned(&state, order, &f, call) == -ETIMEDOUT);
			assert(state.fault && state.stages[stop].owned);
			for (unsigned int i = 0; i < n; i++)
				assert(f.live[i] == (i == stop));
			assert(f.calls == 2 * n);
			cases++;
		}
		if (n > 1) {
			memset(&state, 0, sizeof(state));
			init(&f, devices, n);
			assert(!camss_video_start_owned(&state, devices, n, &f, call));
			order[1] = 0;
			unsigned int before = f.calls;
			assert(camss_video_stop_owned(&state, order, &f, call) == -EINVAL);
			assert(state.fault && f.calls == before);
			cases++;
		}
		memset(&state, 0, sizeof(state));
		init(&f, devices, n);
		assert(!camss_video_start_owned(&state, devices, n, &f, call));
		unsigned int before = f.calls;
		order[0] = n;
		assert(camss_video_stop_owned(&state, order, &f, call) == -EINVAL);
		assert(state.fault && f.calls == before);
		cases++;
	}

	struct camss_video_lifecycle state = {0};
	struct fixture f;
	void *devices[CAMSS_VIDEO_MAX_SUBDEVS];
	init(&f, devices, CAMSS_VIDEO_MAX_SUBDEVS);
	assert(camss_video_start_owned(&state, devices, 0, &f, call) == -EINVAL);
	assert(camss_video_start_owned(&state, devices, CAMSS_VIDEO_MAX_SUBDEVS + 1, &f, call) == -EINVAL);
	assert(!f.calls);
	cases += 2;
	puts("Lifecycle actual-header cases passed");
	printf("cases=%u\n", cases);
	return 0;
}
