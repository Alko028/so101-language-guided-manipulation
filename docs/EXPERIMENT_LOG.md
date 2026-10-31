# Experiment Log

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

