#!/usr/bin/env python3
"""
camera_capture.py
Reusable camera module for capturing frames and saving images.
Designed for Raspberry Pi using Picamera2 and OpenCV.
"""

from picamera2 import Picamera2
import cv2
import time
import os

# -----------------------------
# INITIALISE CAMERA
# -----------------------------
picam = Picamera2()

config = picam.create_still_configuration(
    main={"size": (640, 480)},
    lores={"size": (320, 240)},
    display=None
)

picam.configure(config)
picam.start()
time.sleep(1)  # Camera warm-up


# -----------------------------
# CAPTURE A FRAME (NumPy array)
# -----------------------------
def capture_frame():
    """Returns a single frame as a NumPy array."""
    return picam.capture_array()


# -----------------------------
# SAVE IMAGE (latest + history)
# -----------------------------
def save_image():
    """
    Saves two images:
    1. ../data/latest.jpg  (for dashboard live view)
    2. ../data/images/<timestamp>.jpg  (for history)
    Returns (latest_path, history_path)
    """

    # Capture frame
    frame = picam.capture_array()

    # Save latest
    latest_path = "../data/latest.jpg"
    cv2.imwrite(latest_path, frame)

    # Save timestamped history image
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    history_path = f"../data/images/{timestamp}.jpg"
    cv2.imwrite(history_path, frame)

    return latest_path, history_path


# -----------------------------
# CLEAN SHUTDOWN
# -----------------------------
def shutdown_camera():
    """Stops the camera safely."""
    picam.stop()