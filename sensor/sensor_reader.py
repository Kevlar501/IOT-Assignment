#!/usr/bin/env python3
import time
import threading
import datetime
from sense_hat import SenseHat
import BlynkLib # type: ignore

# ─── MODULAR SUB-SCRIPT IMPORTS ───
from mqtt_publisher import publish
from camera_capture import picam, capture_frame, save_image
from motion_detector import detect_motion

# -----------------------------
# CONFIGURATION
# -----------------------------
TEMP_LOW = 5.0
TEMP_HIGH = 30.0
HUM_LOW = 30.0
HUM_HIGH = 80.0
SUPPRESSION_HOURS = 3
MQTT_BROKER = "broker.hivemq.com" 
BLYNK_TOKEN = "WWlwQhgFrBN01q9Dm9tdM4UCcpWZD5Fb"

# -----------------------------
# INITIALISE HARDWARE
# -----------------------------
sense = SenseHat()
sense.clear()

blynk = BlynkLib.Blynk(BLYNK_TOKEN, server="blynk.cloud", port=80)

# -----------------------------
# STATE VARIABLES
# -----------------------------
alert_suppressed_until = None
led_flashing = False
stop_flashing = False
prev_frame = None

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
# JOYSTICK ACKNOWLEDGEMENT
# -----------------------------
def joystick_event(event):
    global alert_suppressed_until, stop_flashing

    if event.action == "pressed":
        alert_suppressed_until = datetime.datetime.now() + datetime.timedelta(hours=SUPPRESSION_HOURS)
        stop_flashing = True
        blynk.virtual_write(6, 1)      
        publish("plant/alert", "Alert acknowledged, suppression active")
        print("Alert acknowledged. Suppression active.")
sense.stick.direction_any = joystick_event

# -----------------------------
# BLYNK REMOTE SUPPRESSION CONTROL (V6)
# -----------------------------
def remote_suppression_control(value):
    global alert_suppressed_until, stop_flashing

    state = int(value[0])

    if state == 1:
        alert_suppressed_until = datetime.datetime.now() + datetime.timedelta(hours=SUPPRESSION_HOURS)
        stop_flashing = True
        publish("plant/alert", "Remote suppression activated")
        print("Remote suppression activated")
    else:
        alert_suppressed_until = None
        stop_flashing = True
        publish("plant/alert", "Remote suppression deactivated")
        print("Remote suppression deactivated")

    # Keep Blynk LED in sync
    blynk.virtual_write(6, state)

# Register the handler explicitly
blynk.on(6, remote_suppression_control)

# -----------------------------
# TASK 1: ENVIRONMENTAL SENSORS (Every 30 Seconds)
# -----------------------------
def read_environmental_sensors():
    global alert_suppressed_until, led_flashing, stop_flashing
    
    try:
        suppression_active = (
            alert_suppressed_until is not None and
            datetime.datetime.now() < alert_suppressed_until
        )

        temp = sense.get_temperature()
        hum = sense.get_humidity()
        pres = sense.get_pressure()

        # Publish data to MQTT
        publish("plant/temperature", temp)
        publish("plant/humidity", hum)
        publish("plant/pressure", pres)

        # Send data to Blynk
        blynk.virtual_write(1, 1 if temp < TEMP_LOW else 0) 
        blynk.virtual_write(2, 1 if temp > TEMP_HIGH else 0) 
        blynk.virtual_write(3, 1 if hum < HUM_LOW else 0) 
        blynk.virtual_write(4, 1 if hum > HUM_HIGH else 0) 
        blynk.virtual_write(6, 1 if suppression_active else 0)
        blynk.virtual_write(7, temp)
        blynk.virtual_write(8, hum)
        blynk.virtual_write(9, pres)   

        if not suppression_active:
            alert_triggered = False
            
            if temp < TEMP_LOW: 
                publish("plant/alert", "Temperature LOW")
                alert_triggered = True
            if temp > TEMP_HIGH: 
                publish("plant/alert", "Temperature HIGH")
                alert_triggered = True
            if hum < HUM_LOW: 
                publish("plant/alert", "Humidity LOW")
                alert_triggered = True
            if hum > HUM_HIGH: 
                publish("plant/alert", "Humidity HIGH")
                alert_triggered = True

            # Run save_image() if environmental constraints are breached
            if alert_triggered:
                save_image()
                if not led_flashing:
                    stop_flashing = False
                    threading.Thread(target=flash_leds, daemon=True).start()
    finally:
        threading.Timer(30.0, read_environmental_sensors).start()

# -----------------------------
# TASK 2: LIVE MOTION CAMERA POLLING (Every 1 Second)
# -----------------------------
def run_camera_motion_check():
    global prev_frame
    
    try:
        # Use capture_frame() utility from camera_capture.py
        curr_frame = capture_frame()
        
        # This routes directly to motion_detector.py logic
        if prev_frame is not None and detect_motion(prev_frame, curr_frame):
            publish("plant/alert", "Motion detected")
            blynk.virtual_write(5, 1)
            
            # Explicitly trigger image write to update latest.jpg on disk
            save_image()
        else:
            blynk.virtual_write(5, 0) 
            
        prev_frame = curr_frame
    finally:
        threading.Timer(1.0, run_camera_motion_check).start()

# -----------------------------
# MAIN LOOP
# -----------------------------
def main():
    global prev_frame
    
    # Grab initial baseline matrix slice
    prev_frame = capture_frame()

    # Kick off both background loop intervals
    read_environmental_sensors()
    run_camera_motion_check()

    print("IoT Gateway active and running. Modular scripts synchronized.")
    while True:
        blynk.run()  
        time.sleep(0.05)

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sense.clear()
        picam.stop()