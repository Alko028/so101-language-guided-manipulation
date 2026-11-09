# SO-101 Language-Guided Manipulation Project

A 16-week plan to build a supervised tabletop robot prototype that turns natural-language pick-and-place requests into perception and reusable SO-101 skills.

## Start here

- [Detailed 16-week roadmap](docs/PROJECT_ROADMAP.md)
- [Experiment log](docs/EXPERIMENT_LOG.md)

## Project approach

Use modular components: language-to-task parsing, object detection/localization, calibrated tabletop geometry, bounded motion skills, and visual verification. Keep ACT as an evaluated learned skill; do not treat it as a language model or open-world object recognizer.

## Live camera object detection

The first perception preview reads the Follower wrist camera and draws boxes, class names, confidence scores, and FPS. It uses text-prompted YOLOE so the target list can include objects such as a pen or tape measure without training a custom detector first. It only reads camera frames and never sends robot motor commands.

From the activated `(lerobot)` Conda environment, install the pinned vision dependencies once:

```powershell
python -m pip install -r requirements-vision.txt
```

Then run it from this repository folder:

```powershell
python .\scripts\realtime_object_detection.py --camera 0
```

Press `Q` or `Esc` to quit; press `S` to save an annotated frame under the ignored `outputs/vision_captures/` folder. The first launch downloads the YOLOE weights and text encoder. It searches the default prompt list; change it for other objects:

```powershell
python .\scripts\realtime_object_detection.py --camera 0 --classes "pen,mouse,tape measure,pencil case,keyboard,bottle,cup,book,phone,person"
```

Text prompts let the model try classes outside its fixed COCO label set, but zero-shot recognition can miss objects or draw incorrect boxes. If detection of a specific object is unreliable, the next step is to collect labeled examples and fine-tune a detector for that object.

## Repository boundaries

This repository tracks project documentation and project-specific source/configuration. The `lerobot/` checkout is the upstream Hugging Face repository and is kept separate. Large recordings, local calibration files, Hugging Face caches, checkpoints, credentials, and virtual environments are excluded; use dataset/model storage or Git LFS intentionally when needed.

## Current milestone

- [x] Complete first ACT tape-measure-to-pencil-case pilot and record observed generalization limits.
- [ ] Create a fixed-camera tabletop perception baseline.
- [x] Add a wrist-camera live object-detection preview script (dependency installation and camera run remain to be confirmed).
- [ ] Build and evaluate safe pick/place skills.
- [ ] Connect validated language instructions to the skill executor.
