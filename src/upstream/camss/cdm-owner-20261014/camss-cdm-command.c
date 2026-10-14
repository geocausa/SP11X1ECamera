// SPDX-License-Identifier: GPL-2.0-only
/*
 * Adapt retained native coherent command allocation/unused cleanup to one
 * independent typed REG_CONT program. Prior functional source/evidence:
 * docs/UPSTREAM-COMMAND-OWNER-PRIOR-AUDIT-20261014.json.
 * No runtime caller, MMIO constructor, raw payload input or exposed free API.
 */
#include <linux/dma-mapping.h>
#include <linux/lockdep.h>
#include <linux/mm.h>
#include <linux/module.h>
#include <linux/slab.h>
#include "camss-cdm-command.h"

struct camss_cdm21_program {
	struct camss_cdm21_power *power;
	struct device *dma_dev;
	struct sp11_cdm21_command command;
	void *cpu;
	dma_addr_t dma;
	bool retained;
	bool attempted;
};

/* Caller already owns power then CDM mutexes. Transfer pre-acquired independent
 * allocation/device/module holds, without publishing a mutable command pointer.
 */
static int cdm21_program_retain(void *context,
			       const struct sp11_cdm21_command *command)
{
	struct camss_cdm21_program *program = context;
	const struct sp11_cdm21_command *owned;

	if (!program || !command || !program->power)
		return -EINVAL;
	lockdep_assert_held(&program->power->lock);
	lockdep_assert_held(&program->power->cdm->lock);
	owned = &program->command;
	if (program->retained || !program->attempted ||
	    program->power->programs != 1 ||
	    program->dma_dev != program->power->dev ||
	    command->cpu != owned->cpu || command->dma != owned->dma ||
	    command->capacity != owned->capacity || command->bytes != owned->bytes ||
	    command->owner != owned->owner || command->request != owned->request)
		return -EPERM;
	program->retained = true;
	return 0;
}

int camss_cdm21_program_create(struct camss_cdm21_power *power,
			      u64 owner, u64 request,
			      const struct sp11_front_minimal *mode,
			      struct camss_cdm21_program **out)
{
	struct camss_cdm21_program *program;
	struct sp11_front_minimal next;
	struct camss_cdm21 *cdm;
	size_t capacity = PAGE_ALIGN(SP11_FRONT_MINIMAL_BYTES);
	int ret;

	if (!power || !power->initialized || !owner || !request || !mode || !out)
		return -EINVAL;
	if (sp11_cdm_overlap(out, sizeof(*out), power, sizeof(*power)) ||
	    sp11_cdm_overlap(out, sizeof(*out), mode, sizeof(*mode)) || *out)
		return -EINVAL;
	next = *mode;
	ret = sp11_front_minimal_validate(&next);
	if (ret)
		return ret;
	mutex_lock(&power->lock);
	cdm = power->cdm;
	if (!cdm || !cdm->initialized || cdm->power_owner != power) {
		ret = -EPERM;
		goto unlock_power;
	}
	mutex_lock(&cdm->lock);
	if (power->fault || cdm->quarantined) {
		ret = -EIO;
		goto unlock;
	}
	if (power->programs || cdm->active || cdm->command_held) {
		ret = -EBUSY;
		goto unlock;
	}
	program = kzalloc(sizeof(*program), GFP_KERNEL);
	if (!program) {
		ret = -ENOMEM;
		goto unlock;
	}
	if (!try_module_get(THIS_MODULE)) {
		ret = -ENODEV;
		goto free_program;
	}
	program->dma_dev = get_device(power->dev);
	if (!program->dma_dev) {
		ret = -ENODEV;
		goto put_module;
	}
	program->cpu = dma_alloc_coherent(program->dma_dev, capacity,
					&program->dma, GFP_KERNEL);
	if (!program->cpu) {
		ret = -ENOMEM;
		goto put_device;
	}
	/* Validate the whole allocation, including padding, before any narrowing. */
	if (!program->dma || (program->dma & 3) ||
	    program->dma > 0xffffffffULL ||
	    capacity > 0x100000000ULL - program->dma) {
		ret = -ERANGE;
		goto free_dma;
	}
	memset(program->cpu, 0, capacity);
	ret = sp11_front_minimal_commands(program->cpu, capacity, &next);
	if (ret)
		goto free_dma;
	program->command.cpu = program->cpu;
	program->command.dma = program->dma;
	program->command.capacity = capacity;
	program->command.bytes = SP11_FRONT_MINIMAL_BYTES;
	program->command.owner = owner;
	program->command.request = request;
	ret = sp11_cdm21_command_validate(&program->command);
	if (ret)
		goto free_dma;
	program->power = power;
	power->programs = 1;
	*out = program;
	goto unlock;
free_dma:
	memzero_explicit(program->cpu, capacity);
	dma_free_coherent(program->dma_dev, capacity, program->cpu, program->dma);
put_device:
	put_device(program->dma_dev);
put_module:
	module_put(THIS_MODULE);
free_program:
	kfree(program);
unlock:
	mutex_unlock(&cdm->lock);
unlock_power:
	mutex_unlock(&power->lock);
	return ret;
}

int camss_cdm21_program_submit(struct camss_cdm21_power *power,
			      struct camss_cdm21_program *program,
			      struct sp11_cdm21_receipt *receipt)
{
	struct camss_cdm21_retention retention;
	int ret;

	if (!power || !power->initialized || !program || !receipt)
		return -EINVAL;
	mutex_lock(&power->lock);
	if (program->power != power || program->dma_dev != power->dev ||
	    power->programs != 1) {
		ret = -EPERM;
		goto unlock;
	}
	if (program->attempted || program->retained) {
		ret = -EALREADY;
		goto unlock;
	}
	if (sp11_cdm_overlap(receipt, sizeof(*receipt), program, sizeof(*program))) {
		ret = -EINVAL;
		goto unlock;
	}
	/* A failed admission is still a consumed software attempt. No retry API. */
	program->attempted = true;
	retention.hold = cdm21_program_retain;
	retention.context = program;
	ret = camss_cdm21_submit_owned(power->cdm, power, &program->command,
				      &retention, receipt);
unlock:
	mutex_unlock(&power->lock);
	return ret;
}

int camss_cdm21_program_destroy_unused(struct camss_cdm21_power *power,
				      struct camss_cdm21_program **owned)
{
	struct camss_cdm21_program *program;
	struct camss_cdm21 *cdm;
	bool released = false;
	int ret = 0;

	if (!power || !power->initialized || !owned || !*owned)
		return -EINVAL;
	mutex_lock(&power->lock);
	cdm = power->cdm;
	if (!cdm || !cdm->initialized || cdm->power_owner != power) {
		ret = -EPERM;
		goto unlock_power;
	}
	mutex_lock(&cdm->lock);
	program = *owned;
	if (program->power != power || program->dma_dev != power->dev ||
	    power->programs != 1) {
		ret = -EPERM;
		goto unlock;
	}
	/* Independent backend identity also refuses a lost software retained flag. */
	if (program->retained || cdm->retained_command.cpu == program->command.cpu) {
		ret = -EBUSY;
		goto unlock;
	}
	memzero_explicit(program->cpu, program->command.capacity);
	dma_free_coherent(program->dma_dev, program->command.capacity,
			  program->cpu, program->dma);
	put_device(program->dma_dev);
	power->programs = 0;
	*owned = NULL;
	kfree(program);
	released = true;
unlock:
	mutex_unlock(&cdm->lock);
unlock_power:
	mutex_unlock(&power->lock);
	if (released)
		module_put(THIS_MODULE);
	return ret;
}

int camss_cdm21_power_detach_ready(struct camss_cdm21_power *power)
{
	struct camss_cdm21 *cdm;
	int ret = 0;

	if (!power || !power->initialized)
		return -EINVAL;
	mutex_lock(&power->lock);
	cdm = power->cdm;
	if (!cdm || !cdm->initialized || cdm->power_owner != power) {
		ret = -EPERM;
		goto unlock_power;
	}
	mutex_lock(&cdm->lock);
	if (power->programs || power->held || power->touched || power->fault ||
	    cdm->active || cdm->command_held || cdm->reset.epoch || cdm->quarantined)
		ret = -EBUSY;
	mutex_unlock(&cdm->lock);
unlock_power:
	mutex_unlock(&power->lock);
	return ret;
}
