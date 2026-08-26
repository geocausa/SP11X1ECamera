# Development workflow

## Branch/state model

`main` is the durable last-proven project state and documentation baseline. Unproven runtime work happens in an experiment branch/worktree and is only promoted once its result is understood.

Experiment IDs are monotonic: `E000`, `E001`, ...

Suggested branch form: `agent/camera-E001-windows-oracle-map`.

## Before an experiment

Create `experiments/E###-slug/README.md` containing the question/hypothesis, evidence, exact base revision, intended delta, expected observation, rollback and artifact/hash table.

For boot-impacting work, preserve the pre-experiment checkpoint before installation.

## Candidate boot policy

The FullIO v19c entry stays the saved default until camera work reaches a deliberately promoted stable checkpoint.

A camera candidate should use its own kernel release string, `/lib/modules/<release>` tree, `/boot/sp11-...camera-E###/` payload, GRUB entry ID, DTB and initrd hashes.

Use a one-shot candidate boot where practical. A failed camera experiment must not require reconstructing the audio Golden.

## Runtime evidence bundle

Capture at least:

- `uname -r` and `/proc/cmdline`;
- DTB/kernel/initrd hashes;
- `dmesg` camera/CCI/CSI/IOMMU/clock/regulator lines;
- `media-ctl -p` if a media device exists;
- `v4l2-ctl --all` and formats if a video node exists;
- exact test command and result;
- reboot/crash signature if applicable.

## Promotion rule

Do not call something “working” based on enumeration alone. Record the strongest proven boundary: probes, powers, identifies, starts PHY, receives SOF, captures frames, stable repeated streaming, etc.

## Session handoff

Before ending a long session or when chat context becomes unreliable:

1. finish or explicitly mark the current experiment incomplete;
2. update `PROJECT_STATE.md`;
3. update `state/project.yaml` (`current_experiment`, `next_experiment`, `next_action`);
4. commit/push;
5. ensure the local workspace pointer still identifies this repository.
