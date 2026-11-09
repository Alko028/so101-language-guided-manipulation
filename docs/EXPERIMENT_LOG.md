# Experiment Log

## 2026-11-08 — live wrist-camera detection preview added

Added a camera-only script using Ultralytics YOLOE text prompts. It displays bounding boxes, class labels, confidence scores, and FPS, and can save annotated frames under the ignored `outputs/vision_captures/` directory. Installed Ultralytics 8.4.208 in the existing `(lerobot)` environment and pinned OpenCV to 4.12.0.88 to stay on the OpenCV 4.x line. `pip check` reported no broken requirements. The camera window and actual object-detection quality have not yet been confirmed in a live run.

## 2026-10-31 — ACT tape measure pick-and-place baseline

### Task and setup
SO-101 Follower with wrist camera; pick up the white tape measure and place it on the pink pencil case. The initial ACT dataset contained 50 episodes. Training produced a policy that could perform the task in the familiar trained scene.

### Observations

1. When the tape measure stayed within approximately the trained tabletop region, the arm could pick it up and place it on the pencil case.
2. Moving the tape measure closer or farther reduced reliability. The wrist did not consistently lift/rotate to approach the tape measure handle from a useful orientation.
3. Removing the training mat/background and exposing a plain black background caused the policy to stop working reliably; performance was better with the training background restored.

### Initial interpretation
The demonstrations likely covered a narrow range of relative object positions, wrist poses, and backgrounds. The ACT behavior appears to rely on visual/action patterns in the demonstrated scene and has not shown robust semantic or out-of-distribution generalization. These are observations from a small initial experiment, not proof of an architectural limit.

### Follow-up
- Expand object position and wrist-orientation coverage while holding background and camera fixed.
- Then vary background separately while holding object positions fixed.
- Log perception errors separately from motion/grasp errors.
