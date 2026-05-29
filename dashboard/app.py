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
# CSV LOGGING
# -----------------------------
def log_sensor_data():
    os.makedirs("../data", exist_ok=True)
    path = "../data/sensor_log.csv"

    write_header = not os.path.exists(path)

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

        # Motion alert
        if payload == "Motion detected":
            state["motion"] = 1
        else:
            state["motion"] = 0

    # Log sensor values
    log_sensor_data()

# -----------------------------
# MQTT THREAD
# -----------------------------
def mqtt_thread():
    client = mqtt.Client()
    client.on_message = on_message
    client.connect("broker.hivemq.com", 1883, 60)

    client.subscribe("plant/temperature")
    client.subscribe("plant/humidity")
    client.subscribe("plant/pressure")
    client.subscribe("plant/alert")

    client.loop_forever()

threading.Thread(target=mqtt_thread, daemon=True).start()

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
    return send_file("../data/latest.jpg", mimetype="image/jpeg")

# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)