#!/usr/bin/env python3
import time
import threading
import datetime
from sense_hat import SenseHat
from picamera2 import Picamera2
import cv2
import numpy as np
from mqtt_publisher import publish
from blynkapi import Blynk # type: ignore
from camera_capture import capture_frame, save_image

# -----------------------------
# CONFIGURATION
# -----------------------------
# Temperature Thresholds (°C)
TEMP_LOW = 5.0
TEMP_HIGH = 30.0
# Humidity Thresholds (%)
HUM_LOW = 30.0
HUM_HIGH = 80.0
SUPPRESSION_HOURS = 3
MQTT_BROKER = "broker.hivemq.com"
BLYNK_TOKEN = "YOUR_BLYNK_TOKEN"

# -----------------------------
# INITIALISE HARDWARE
# -----------------------------
sense = SenseHat()
sense.clear()

picam = Picamera2()
picam.configure(picam.create_still_configuration())
picam.start()

blynk = Blynk(BLYNK_TOKEN)

''' MQTT handled by mqtt_publisher.py '''

# -----------------------------
# STATE VARIABLES
# -----------------------------
alert_suppressed_until = None
led_flashing = False
stop_flashing = False

# -----------------------------
# LED FLASHING THREAD
# -----------------------------
def flash_leds():
    global led_flashing, stop_flashing
    led_flashing = True
    while not stop_flashing:
        sense.clear((255, 0, 0))
        time.sleep(3)
        sense.clear()
        time.sleep(12)
    sense.clear()
    led_flashing = False

# -----------------------------
# MOTION DETECTION
# -----------------------------
def detect_motion(prev_frame, curr_frame, threshold=25_000):
    diff = cv2.absdiff(prev_frame, curr_frame)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 25, 255, cv2.THRESH_BINARY)
    movement = np.sum(thresh)
    return movement > threshold

# -----------------------------
# JOYSTICK ACKNOWLEDGEMENT
# -----------------------------
def joystick_event(event):
    global alert_suppressed_until, stop_flashing

    if event.action == "pressed":
        alert_suppressed_until = datetime.datetime.now() + datetime.timedelta(hours=SUPPRESSION_HOURS)
        stop_flashing = True
        blynk.update("V6", 1)   # suppression ON
        blynk.update("V5", 0)   # clear motion alert
        publish("plant/alert", "Alert acknowledged, suppression active")
        print("Alert acknowledged. Suppression active.")

sense.stick.direction_any = joystick_event

# -----------------------------
# MAIN LOOP
# -----------------------------
def main():
    global stop_flashing, alert_suppressed_until

    prev_frame = picam.capture_array()
    time.sleep(0.2)

    while True:

        # Suppression check (calculated before Blynk updates)
        suppression_active = (
            alert_suppressed_until is not None and
            datetime.datetime.now() < alert_suppressed_until
        )

        # Read sensors
        temp = sense.get_temperature()
        hum = sense.get_humidity()
        pres = sense.get_pressure()

        # Publish to MQTT
        publish("plant/temperature", temp)
        publish("plant/humidity", hum)
        publish("plant/pressure", pres)

        # Update Blynk
        blynk.update("V1", 1 if temp < TEMP_LOW else 0) # low temp alert
        blynk.update("V2", 1 if temp > TEMP_HIGH else 0) # high temp alert
        blynk.update("V3", 1 if hum < HUM_LOW else 0) # low humidity alert
        blynk.update("V4", 1 if hum > HUM_HIGH else 0) # high humidity alert
        blynk.update("V5", 0)   # reset motion alert each loop
        blynk.update("V6", 1 if suppression_active else 0)   # suppression indicator

        # Threshold alert checks
        if not suppression_active:

            if temp < TEMP_LOW:
                publish("plant/alert", "Temperature LOW")

            if temp > TEMP_HIGH:
                publish("plant/alert", "Temperature HIGH")

            if hum < HUM_LOW:
                publish("plant/alert", "Humidity LOW")

            if hum > HUM_HIGH:
                publish("plant/alert", "Humidity HIGH")

            # LED flashing for ANY threshold alert
            if (temp < TEMP_LOW or temp > TEMP_HIGH or hum < HUM_LOW or hum > HUM_HIGH):
                if not led_flashing:
                    stop_flashing = False
                    threading.Thread(target=flash_leds, daemon=True).start()

        # Motion detection
        curr_frame = picam.capture_array()
        if detect_motion(prev_frame, curr_frame):
            publish("plant/alert", "Motion detected")
            blynk.update("V5", 1)

        prev_frame = curr_frame

        time.sleep(1)

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sense.clear()
        picam.stop()