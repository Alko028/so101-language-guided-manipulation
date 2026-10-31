# SO-101 Language-Guided Manipulation Project

A 16-week plan to build a supervised tabletop robot prototype that turns natural-language pick-and-place requests into perception and reusable SO-101 skills.

## Start here

- [Detailed 16-week roadmap](docs/PROJECT_ROADMAP.md)
- [Experiment log](docs/EXPERIMENT_LOG.md)

## Project approach

Use modular components: language-to-task parsing, object detection/localization, calibrated tabletop geometry, bounded motion skills, and visual verification. Keep ACT as an evaluated learned skill; do not treat it as a language model or open-world object recognizer.

## Repository boundaries

This repository tracks project documentation and project-specific source/configuration. The `lerobot/` checkout is the upstream Hugging Face repository and is kept separate. Large recordings, local calibration files, Hugging Face caches, checkpoints, credentials, and virtual environments are excluded; use dataset/model storage or Git LFS intentionally when needed.

## Current milestone

- [x] Complete first ACT tape-measure-to-pencil-case pilot and record observed generalization limits.
- [ ] Create a fixed-camera tabletop perception baseline.
- [ ] Build and evaluate safe pick/place skills.
- [ ] Connect validated language instructions to the skill executor.

