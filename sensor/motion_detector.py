#!/usr/bin/env python3
import time
import cv2
import numpy as np
from picamera2 import Picamera2
from mqtt_publisher import publish

# -----------------------------
# CONFIGURATION
# -----------------------------
MOTION_THRESHOLD = 15_000
FRAME_DELAY = 0.2  # seconds between frames
MQTT_TOPIC = "plant/alert"

# -----------------------------
# INITIALISE CAMERA
# -----------------------------
picam = Picamera2()
picam.configure(picam.create_still_configuration())
picam.start()

# -----------------------------
# MOTION DETECTION FUNCTION
# -----------------------------
def detect_motion(prev_frame, curr_frame, threshold=MOTION_THRESHOLD):
    diff = cv2.absdiff(prev_frame, curr_frame)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 25, 255, cv2.THRESH_BINARY)
    movement = np.sum(thresh)
    print("Movement:", movement)  # Debugging output (explain this in video demo)
    return movement > threshold

# -----------------------------
# MAIN LOOP
# -----------------------------
def main():
    prev_frame = picam.capture_array()
    time.sleep(FRAME_DELAY)

    while True:
        curr_frame = picam.capture_array()

        if detect_motion(prev_frame, curr_frame):
            publish(MQTT_TOPIC, "Motion detected")
            print("[MOTION] Motion detected")

        prev_frame = curr_frame
        time.sleep(FRAME_DELAY)

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        picam.stop()
        print("Motion detector stopped.")