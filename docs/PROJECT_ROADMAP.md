# SO-101 Language-Guided Manipulation

Build a modular tabletop robot system that accepts a natural-language instruction, identifies the requested object with a camera, and executes validated pick-and-place skills on a SO-101 arm.

## Current status (2026-10-31)

- SO-101 Leader and Follower are assembled, wired, calibrated, and have completed stable teleoperation.
- Wrist camera is available and has worked at 640x480, 30 FPS.
- A first ACT model was trained from 50 episodes for picking up a white tape measure and placing it on a pink pencil case.
- The model succeeded in the trained scene, but was sensitive to object position and background changes. The current ACT model is not language-conditioned and does not provide object-class understanding.
- PC GPU previously detected as NVIDIA GeForce RTX 5080. Keep the LeRobot environment separate from any Isaac Lab environment.

## Product goal

Given an instruction such as “pick up the pen and put it in the pencil case,” the system should:

1. Parse the request into a constrained task representation.
2. Detect and localize the requested object and destination.
3. Check reachability and safety constraints.
4. Call reusable `find`, `pick`, `place`, and `verify` skills.
5. Observe the result and stop or request help if the task fails.

The language model will select and sequence skills. It will not send raw motor commands. The initial environment is a fixed tabletop with stable camera mounts and diffuse lighting.

## Proposed architecture

`Text instruction -> task parser -> scene perception -> task executor/skill library -> SO-101 controller -> visual verification`

- **Language:** natural language to validated JSON/task schema; start with typed text, add speech later.
- **Perception:** fixed overhead RGB camera for scene-level object detection/localization; wrist camera as a close-up view if useful. Use a pretrained detector first, then label/fine-tune if it misses the user's objects.
- **Geometry:** calibrate the tabletop image to a tabletop coordinate frame, then map safe targets into the robot workspace. Do not infer metric grasp coordinates from a detector bounding box alone.
- **Skills:** use scripted/geometric control for predictable tabletop motions; use ACT as a learned skill where demonstrations add value. Keep the current tape-measure ACT policy as a baseline, not as a general object-understanding system.
- **Simulation (optional stretch):** Isaac Lab for controlled simulation and large-scale learning experiments after a real tabletop baseline works. Isaac Gym is legacy/deprecated; use Isaac Lab for new NVIDIA simulation work.

## Hardware and software assumptions

- Existing SO-101 Leader/Follower, power supplies, wrist camera, Windows dual-boot computer with RTX 5080.
- Add a rigidly mounted overhead USB camera; use the existing wrist camera as a secondary view. Start at 640x480/30 FPS and steady diffuse lighting.
- Keep a reachable way to cut Follower power during autonomous tests.
- Keep the existing `(lerobot)` Conda environment for LeRobot. Create a separate environment for Isaac Lab or other incompatible toolchains.
- Never commit Hugging Face caches, calibration files, raw videos, private keys/tokens, or large model checkpoints to ordinary Git. Store datasets/checkpoints separately (e.g. Hugging Face dataset/model repos or Git LFS when explicitly needed); commit small manifests and evaluation summaries here.

## Schedule and weekly acceptance criteria

Planning anchor: Monday, November 2, 2026. The plan is 16 weeks (about four months), with a working prototype targeted by February 21, 2027. If weekly availability changes, keep the sequence and shift dates rather than skipping safety and evaluation gates.

### Week 1 — Nov 2–8: project baseline and safety

- Create and version the project repository; document robot IDs/ports, camera IDs, environment versions, and safe power-off procedure without storing secrets.
- Reproduce teleoperation and wrist-camera display; record current ACT baseline results on the trained layout.
- Define the tabletop workspace, prohibited zones, and an evaluation sheet.
- **Deliverable / gate:** README setup notes; at least 5 controlled baseline trials recorded; no uncontrolled movement or collisions.

### Week 2 — Nov 9–15: stable scene camera

- Mount a fixed overhead webcam so the whole reachable tabletop, objects, and arm are visible; keep wrist camera available.
- Fix exposure/focus/lighting where supported; check multiple camera indices and log the working configuration.
- Capture a small set of scenes with the mat/background present and absent, without moving the camera.
- **Deliverable / gate:** camera setup diagram/photo and reproducible dual-camera preview; scene remains visible through the task.

### Week 3 — Nov 16–22: object vocabulary and perception baseline

- Define the initial object classes: pen, mouse, tape measure, pencil case/container.
- Run a pretrained detector on saved images; measure whether each object is detected under the fixed scene setup.
- If the tape measure or other target class is missed, annotate a small representative image set and fine-tune/evaluate a detector.
- **Deliverable / gate:** detector outputs class, confidence, and bounding box for the initial objects; record misses instead of silently selecting the wrong object.

### Week 4 — Nov 23–29: tabletop coordinate calibration

- Define tabletop axes and a safe robot-reachable rectangle.
- Calibrate image-to-table coordinates using known points or a printed calibration target; verify on several measured tabletop points.
- Estimate localization error and reject targets outside the calibrated/reachable area.
- **Deliverable / gate:** documented transform and target-localization error; no autonomous actuation yet from unverified coordinates.

### Week 5 — Nov 30–Dec 6: safe motion primitives

- Implement bounded joint/Cartesian motions for open gripper, approach, descend, close, lift, and return-to-safe-pose.
- Set conservative speeds, joint limits, workspace limits, and a visible emergency power cutoff procedure.
- Test each primitive with no object first, then with an easy-to-grasp object under direct supervision.
- **Deliverable / gate:** each primitive runs on command, stays inside the safe workspace, and can be stopped promptly.

### Week 6 — Dec 7–13: known-coordinate pick and place

- Implement `pick(x,y)` and `place(x,y)` using calibrated table coordinates and known object/target heights.
- Separate approach, grasp, lift, transfer, release, and retreat so failures can be diagnosed by stage.
- Run repeated trials at a central, easy position; log success and failure stage.
- **Deliverable / gate:** repeatable pick-and-place at one known location, with success rate and failure notes reported over at least 10 attempts.

### Week 7 — Dec 14–20: position coverage experiment

- Expand the ACT dataset with near/center/far and left/center/right tape-measure placements relative to the pouch; include varied successful wrist orientations.
- Keep background, lighting, camera pose, and pouch position fixed so position is the only changed factor.
- Compare the original ACT model against the expanded-data model using held-out positions.
- **Deliverable / gate:** position grid, dataset manifest, per-cell success results; retain model/checkpoint outside Git.

### Week 8 — Dec 21–27: perception-to-motion integration

- Connect detector output to calibrated table coordinates and then to the safe pick primitive.
- Add confidence threshold, target-class selection, reachability check, and “ask/stop” behavior for ambiguous detections.
- Test with one object class and two or more positions before enabling multi-object selection.
- **Deliverable / gate:** “find tape measure and pick it” works from vision-derived location in supervised trials; no motion on low-confidence detection.

### Week 9 — Dec 28–Jan 3: robust pick skill

- Improve gripper approach and wrist pose for the tape measure; document graspable handle orientation and failures.
- Add visual confirmation of object lift or a conservative timeout/abort path.
- Evaluate held-out positions and object orientations.
- **Deliverable / gate:** report pickup success separately from placement success; failures stop safely.

### Week 10 — Jan 4–10: reusable placement and verification

- Implement destination localization and `place(target)` skill for pouch/container.
- Add a post-release camera check that the object is in the target region; add bounded retry or safe stop, not unlimited retries.
- Evaluate full pick-and-place with the existing task.
- **Deliverable / gate:** task completion is only counted when visual verification confirms placement; report at least 10 attempts.

### Week 11 — Jan 11–17: controlled background generalization

- Keep object positions fixed and test multiple backgrounds/mats and modest lighting changes.
- Improve detector robustness with representative examples/augmentation if needed; compare RGB detector localization and ACT behavior separately.
- Avoid changing background and object position simultaneously.
- **Deliverable / gate:** background matrix with detection and manipulation outcomes; identify whether perception or control causes each failure.

### Week 12 — Jan 18–24: skill library and task schema

- Define validated JSON schema, e.g. `{action: pick_place, object: pen, destination: pencil_case}`.
- Create callable skills such as `find_object`, `pick`, `place`, and `verify`; define inputs, outputs, failure codes, and limits.
- Test fixed, manually specified commands before adding an LLM.
- **Deliverable / gate:** executor can run a fixed sequence of validated skills without the language model issuing motor commands.

### Week 13 — Jan 25–31: language-to-task parser

- Connect an LLM to transform a small set of natural-language commands into the schema.
- Use a strict allowlist of actions/classes/locations and validate every parsed command before execution.
- Test paraphrases, missing targets, multiple matching objects, and unsupported requests; ambiguous cases must ask a question.
- **Deliverable / gate:** text instruction produces a valid plan or a safe clarification; no raw motor output from the LLM.

### Week 14 — Feb 1–7: multi-object tabletop demo

- Add the pen and mouse as target classes; verify object localization and reachable poses one class at a time.
- Test commands such as “pick the pen,” “put the mouse in the pencil case,” and “place the tape measure on the pouch.”
- Record confusion cases and add labeled images or task examples where required.
- **Deliverable / gate:** supervised end-to-end demo across the supported object/task list, with per-command results.

### Week 15 — Feb 8–14: robustness and optional Isaac Lab study

- Run a structured evaluation over target positions, backgrounds, and command paraphrases; only vary one factor per test group.
- If the real-world baseline is stable, create a small Isaac Lab SO-101 tabletop scene and compare a simulated skill or collect simulated demonstrations. Keep this as a stretch task; do not block the main prototype on simulator installation or sim-to-real transfer.
- **Deliverable / gate:** evaluation report and a clear decision on whether simulation is useful for the next iteration.

### Week 16 — Feb 15–21: final integration and project handoff

- Run the complete instruction → perception → skill selection → pick/place → verification pipeline under the fixed tabletop conditions.
- Report success rate, object/localization errors, completion time, safe-stop behavior, and known limitations.
- Record a short demo, update setup instructions, architecture diagram, experiment log, and next-step backlog.
- **Deliverable / gate:** reproducible prototype and honest evaluation; no claim of unrestricted/general-purpose manipulation.

## Evaluation protocol

Track every trial with date, command, object, object position/orientation, destination, background/lighting, detection confidence and localization error, skill stages completed, success/failure stage, safety stop, and notes.

Report at minimum:

- Object detection recall / wrong-target rate for supported classes.
- Table localization error in centimeters.
- Pickup, placement, and full-task success rates separately.
- Results on trained positions versus held-out positions/backgrounds.
- Number of unsafe motions/collisions (target: zero).

Use supervised real-robot trials with an accessible power cutoff. Begin with low speed and one change at a time. Do not test a new model unattended.

## Risks and scope boundaries

- ACT success in one fixed scene does not establish object semantics or broad generalization.
- Pixel bounding boxes need calibration and geometric reasoning before they become safe robot targets.
- A wrist camera moves with the arm; use a fixed scene camera for stable tabletop localization.
- Isaac Lab provides simulation and learning tools, but sim-to-real transfer requires matching robot dynamics, camera geometry, friction, object properties, and control timing.
- An LLM can misparse commands; schema validation, allowlists, reachability checks, and safe failure behavior are required.
- The 16-week result is a controlled tabletop prototype, not a general-purpose household robot.

## Reference links

- LeRobot imitation learning: https://huggingface.co/docs/lerobot/main/il_robots
- LeRobot cameras: https://huggingface.co/docs/lerobot/main/en/cameras
- LeRobot ACT: https://huggingface.co/docs/lerobot/act
- Isaac Lab: https://docs.nvidia.com/isaaclab/isaac-lab
- Isaac Lab SO-101 simulated data collection: https://nvidia.github.io/IsaacCapture/main/integrations/lerobot/data_collection_sim.html
