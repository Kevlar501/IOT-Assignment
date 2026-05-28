#!/usr/bin/env python3
"""
mqtt_publisher.py
Centralized MQTT publishing module for the plant monitoring system.
"""

import paho.mqtt.client as mqtt
import time

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883

# -----------------------------
# INITIALISE MQTT CLIENT
# -----------------------------
client = mqtt.Client()

_connected = False


def _on_connect(client, userdata, flags, rc):
    global _connected
    if rc == 0:
        _connected = True
        print("[MQTT] Connected to broker.")
    else:
        print(f"[MQTT] Connection failed with code {rc}")


def _on_disconnect(client, userdata, rc):
    global _connected
    _connected = False
    print("[MQTT] Disconnected from broker.")


client.on_connect = _on_connect
client.on_disconnect = _on_disconnect

client.connect_async(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()


# -----------------------------
# PUBLISH WRAPPER
# -----------------------------
def publish(topic, payload):
    """
    Publishes a message to the MQTT broker.
    Automatically retries if disconnected.
    """
    global _connected

    if not _connected:
        print("[MQTT] Waiting for connection...")
        retries = 0
        while not _connected and retries < 10:
            time.sleep(0.2)
            retries += 1

    try:
        client.publish(topic, payload)
        print(f"[MQTT] Published: {topic} -> {payload}")
    except Exception as e:
        print(f"[MQTT] Publish error: {e}")