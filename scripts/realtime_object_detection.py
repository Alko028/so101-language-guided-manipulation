"""Show live object detections from a USB camera; this script never controls motors."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import cv2
import numpy as np
import torch
from ultralytics import YOLOE


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Draw YOLO object-detection boxes over a live camera feed."
    )
    parser.add_argument("--camera", type=int, default=0, help="OpenCV camera index (default: 0).")
    parser.add_argument("--width", type=int, default=640, help="Requested camera width.")
    parser.add_argument("--height", type=int, default=480, help="Requested camera height.")
    parser.add_argument(
        "--model", default="yoloe-26n-seg.pt", help="Ultralytics YOLOE model/weights path."
    )
    parser.add_argument(
        "--classes",
        default="pen,mouse,tape measure,pencil case,keyboard,bottle,cup,book,phone,person",
        help="Comma-separated text prompts to detect.",
    )
    parser.add_argument("--confidence", type=float, default=0.35, help="Minimum detection confidence.")
    parser.add_argument("--image-size", type=int, default=640, help="YOLO inference image size.")
    parser.add_argument(
        "--device",
        default="auto",
        help="Inference device: auto, cpu, or a CUDA device such as 0 (default: auto).",
    )
    return parser.parse_args()


def open_camera(index: int, width: int, height: int) -> cv2.VideoCapture:
    # DirectShow is the backend that worked for this Windows camera previously.
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF]
    for backend in backends:
        camera = cv2.VideoCapture(index, backend)
        if camera.isOpened():
            camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            camera.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            ok, _ = camera.read()
            if ok:
                return camera
        camera.release()

    raise RuntimeError(
        f"Could not open camera index {index}. Close other camera apps and check the index "
        "with `lerobot-find-cameras opencv`."
    )


def fit_to_window(frame: np.ndarray, window_name: str) -> np.ndarray:
    """Resize only for display, preserving the camera image's aspect ratio."""
    _, _, target_width, target_height = cv2.getWindowImageRect(window_name)
    if target_width <= 0 or target_height <= 0:
        target_height, target_width = frame.shape[:2]

    frame_height, frame_width = frame.shape[:2]
    scale = min(target_width / frame_width, target_height / frame_height)
    display_width = max(1, round(frame_width * scale))
    display_height = max(1, round(frame_height * scale))
    interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
    resized = cv2.resize(frame, (display_width, display_height), interpolation=interpolation)

    canvas = np.zeros((target_height, target_width, 3), dtype=np.uint8)
    left = (target_width - display_width) // 2
    top = (target_height - display_height) // 2
    canvas[top : top + display_height, left : left + display_width] = resized
    return canvas


def main() -> None:
    args = parse_args()
    device = args.device
    if device == "auto":
        device = "0" if torch.cuda.is_available() else "cpu"

    classes = [name.strip() for name in args.classes.split(",") if name.strip()]
    print(f"Loading {args.model} on {device}...")
    print("On first run, Ultralytics may download model weights and a text encoder.")
    model = YOLOE(args.model)
    model.set_classes(classes)
    print("Looking for: " + ", ".join(classes))

    camera = open_camera(args.camera, args.width, args.height)
    print(f"Camera {args.camera} connected. Press Q or Esc to quit; press S to save a frame.")

    window_name = "SO-101 live object detection (camera only; no motor control)"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(window_name, 960, 720)
    capture_dir = Path(__file__).resolve().parents[1] / "outputs" / "vision_captures"
    previous_time = time.perf_counter()
    fps_ema = 0.0

    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                print("Camera frame read failed; stopping preview.")
                break

            result = model.predict(
                source=frame,
                imgsz=args.image_size,
                conf=args.confidence,
                device=device,
                verbose=False,
            )[0]
            annotated = frame.copy()

            if result.boxes is not None:
                boxes = result.boxes.xyxy.cpu().tolist()
                class_ids = result.boxes.cls.int().cpu().tolist()
                confidences = result.boxes.conf.cpu().tolist()
                for box, class_id, score in zip(boxes, class_ids, confidences):
                    x1, y1, x2, y2 = (int(value) for value in box)
                    class_name = result.names[class_id]
                    label = f"{class_name} {score:.2f}"
                    cv2.rectangle(annotated, (x1, y1), (x2, y2), (40, 220, 80), 2)
                    (text_w, text_h), baseline = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 2
                    )
                    top = max(0, y1 - text_h - baseline - 6)
                    cv2.rectangle(
                        annotated,
                        (x1, top),
                        (x1 + text_w + 8, y1),
                        (40, 220, 80),
                        thickness=-1,
                    )
                    cv2.putText(
                        annotated,
                        label,
                        (x1 + 4, y1 - baseline - 3),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55,
                        (0, 0, 0),
                        2,
                        cv2.LINE_AA,
                    )

            now = time.perf_counter()
            instant_fps = 1.0 / max(now - previous_time, 1e-6)
            fps_ema = instant_fps if fps_ema == 0 else 0.9 * fps_ema + 0.1 * instant_fps
            previous_time = now
            cv2.putText(
                annotated,
                f"FPS {fps_ema:.1f} | device {device}",
                (10, 25),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.65,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )
            cv2.imshow(window_name, fit_to_window(annotated, window_name))

            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
            if key == ord("s"):
                capture_dir.mkdir(parents=True, exist_ok=True)
                image_path = capture_dir / f"detection_{time.strftime('%Y%m%d_%H%M%S')}.jpg"
                cv2.imwrite(str(image_path), annotated)
                print(f"Saved annotated frame: {image_path}")
    finally:
        camera.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
