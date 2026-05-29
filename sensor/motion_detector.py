#!/usr/bin/env python3
import cv2
import numpy as np

# -----------------------------
# CONFIGURATION
# -----------------------------
MOTION_THRESHOLD = 25000

# -----------------------------
# CORE LOGIC
# -----------------------------
def detect_motion(prev_frame, curr_frame, threshold=MOTION_THRESHOLD):
    """
    Computes absolute difference between two frames to detect movement.
    """
    if prev_frame is None or curr_frame is None:
        return False
        
    diff = cv2.absdiff(prev_frame, curr_frame)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 25, 255, cv2.THRESH_BINARY)
    movement = cv2.countNonZero(thresh)
    
    # Debugging output useful for video demo
    # print(f"[Debug] Calculated movement metric: {movement}")  

    # Evaluate if motion occurred
    is_motion = movement > threshold

    # Debugging output - ONLY prints when motion is detected
    if is_motion:
        print(f"[Debug] Motion detected! Movement metric: {movement} (Threshold: {threshold})")  
        
    return is_motion