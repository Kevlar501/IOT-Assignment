#!/usr/bin/env python3
"""
app.py
Flask dashboard for the IoT Plant Monitoring System.
Subscribes to MQTT topics and serves live data to the frontend.
"""

from flask import Flask, render_template, jsonify, send_file
import paho.mqtt.client as mqtt
import threading
import time
import csv
import os

app = Flask(__name__)

# -----------------------------
# SHARED STATE (updated by MQTT)
# -----------------------------
state = {
    "temperature": None,
    "humidity": None,
    "pressure": None,
    "alert": None,
    "motion": 0,
    "temp_low": 0,
    "temp_high": 0,
    "hum_low": 0,
    "hum_high": 0,
    "suppression": 0
}

# -----------------------------
# CSV LOGGING (Every 30 Seconds)
# -----------------------------
def log_sensor_data():
    """Logs the consolidated state data at scheduled intervals."""
    # Ensure all key values are populated before writing a log entry
    if state["temperature"] is None or state["humidity"] is None or state["pressure"] is None:
        return
        
    os.makedirs("../data", exist_ok=True)
    path = "../data/sensor_log.csv"

    write_header = not os.path.exists(path)

    try:
        with open(path, "a", newline="") as f:
            writer = csv.writer(f)
            if write_header:
                writer.writerow(["timestamp", "temperature", "humidity", "pressure"])
            writer.writerow([
                time.strftime("%Y-%m-%d %H:%M:%S"),
                state["temperature"],
                state["humidity"],
                state["pressure"]
            ])
    except IOError as e:
        print(f"[Storage Error] Failed writing data entry to disk: {e}")

# -----------------------------
# MQTT CALLBACKS
# -----------------------------
def on_message(client, userdata, msg):
    topic = msg.topic
    payload = msg.payload.decode()

    if topic == "plant/temperature":
        state["temperature"] = float(payload)

    elif topic == "plant/humidity":
        state["humidity"] = float(payload)

    elif topic == "plant/pressure":
        state["pressure"] = float(payload)

    elif topic == "plant/alert":
        state["alert"] = payload

        # Motion alert logic matching hardware flags
        if "Motion detected" in payload:
            state["motion"] = 1
        elif "Alert acknowledged" in payload:
            state["motion"] = 0
            state["suppression"] = 1
            
        # Parse threshold indicators to synchronize with dashboard widgets
        if "Temperature LOW" in payload: state["temp_low"] = 1
        if "Temperature HIGH" in payload: state["temp_high"] = 1
        if "Humidity LOW" in payload: state["hum_low"] = 1
        if "Humidity HIGH" in payload: state["hum_high"] = 1

# -----------------------------
# BACKGROUND THREADS
# -----------------------------
def mqtt_thread():
    # FIX 1: Native support for your environment's modern Paho MQTT 2.x API 
    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)

    client.subscribe("plant/temperature")
    client.subscribe("plant/humidity")
    client.subscribe("plant/pressure")
    client.subscribe("plant/alert")

    client.loop_forever()

def continuous_logger():
    """FIX 2: Handles CSV logging safely on an isolated 30-second loop."""
    while True:
        time.sleep(30)
        log_sensor_data()

# Start background services smoothly
threading.Thread(target=mqtt_thread, daemon=True).start()
threading.Thread(target=continuous_logger, daemon=True).start()

# -----------------------------
# ROUTES
# -----------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/data")
def data():
    return jsonify(state)

@app.route("/latest.jpg")
def latest_image():
    # FIX 3: Prevents internal 500 error crashes if camera hasn't shot a baseline frame yet
    path = "../data/latest.jpg"
    if not os.path.exists(path):
        return send_file(os.devnull, mimetype="image/jpeg")
    return send_file(path, mimetype="image/jpeg")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    # Disable debug reloader to prevent duplication of your background MQTT threads
    app.run(host="0.0.0.0", port=5000, debug=False)